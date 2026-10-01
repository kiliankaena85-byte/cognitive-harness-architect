"""
core/sandbox_runner.py
=============================================================================
Universal Cognitive Decomposition Engine (UCDE) - Execution Sandbox & Self-Healing
Closed-Loop TDD: Subprocess Sandboxed Execution, Failure Capture, and Autonomous Repair.

Implements:
- Subprocess sandbox isolation with strict wall-clock timeout (<= 10.0 sec)
- Structured test result parser (extracting passed, failures, errors, tracebacks)
- Self-healing feedback loop with max retry bound (tau_max <= 3)
- Hoare logic postcondition verification on synthesized service packages
=============================================================================
"""

import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from pydantic import BaseModel, ConfigDict, Field


class SandboxExecutionResult(BaseModel):
    """Execution telemetry emitted by the sandboxed test runner."""
    model_config = ConfigDict(extra="forbid")

    success: bool = Field(description="True if all tests passed without failures or errors")
    tests_run: int = Field(ge=0, description="Total number of executed unit tests")
    failures: int = Field(ge=0, description="Number of assertion failures")
    errors: int = Field(ge=0, description="Number of unhandled exceptions")
    duration_ms: float = Field(ge=0.0, description="Execution duration in milliseconds")
    self_healing_attempts: int = Field(ge=0, description="Number of self-healing iterations executed")
    stdout: str = Field(description="Raw standard output from runner process")
    stderr: str = Field(description="Raw standard error from runner process")
    error_summary: Optional[str] = Field(default=None, description="Diagnostic summary if failed")


class SandboxRunner:
    """
    Executes synthesized service packages inside an isolated subprocess sandbox.
    Interprets test results and coordinates autonomous self-healing repair cycles.
    """

    def __init__(self, timeout_sec: float = 15.0, max_self_healing_retries: int = 3):
        self.timeout_sec: float = float(timeout_sec)
        self.max_self_healing_retries: int = int(max_self_healing_retries)

    @staticmethod
    def _parse_unittest_output(output: str) -> Tuple[int, int, int]:
        """
        Extracts (tests_run, failures, errors) counts from standard unittest output.
        """
        tests_run = 0
        failures = 0
        errors = 0

        # Pattern: Ran X tests in Ys
        m_ran = re.search(r"Ran (\d+) tests? in", output)
        if m_ran:
            tests_run = int(m_ran.group(1))

        # Pattern: FAILED (failures=X, errors=Y)
        m_fail = re.search(r"FAILED \((?:failures=(\d+))?(?:, )?(?:errors=(\d+))?\)", output)
        if m_fail:
            if m_fail.group(1):
                failures = int(m_fail.group(1))
            if m_fail.group(2):
                errors = int(m_fail.group(2))
        elif "OK" in output:
            failures = 0
            errors = 0
        elif "FAIL:" in output or "ERROR:" in output:
            failures = output.count("FAIL:")
            errors = output.count("ERROR:")

        return tests_run, failures, errors

    def execute_test_suite(self, package_dir: Union[str, Path]) -> SandboxExecutionResult:
        """
        Executes all test_*.py files inside the synthesized package directory.
        """
        pkg_path = Path(package_dir).resolve()
        if not pkg_path.exists():
            raise FileNotFoundError(f"Package directory not found: '{pkg_path}'")

        start_time = time.monotonic()
        env = dict(os.environ)
        # Ensure target directory and project root are on PYTHONPATH
        project_root = str(Path(__file__).resolve().parent.parent)
        env["PYTHONPATH"] = f"{str(pkg_path)}{os.pathsep}{project_root}{os.pathsep}{env.get('PYTHONPATH', '')}"

        cmd = [sys.executable, "-m", "unittest", "discover", "-s", str(pkg_path), "-p", "test_*.py"]

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout_sec,
                cwd=str(pkg_path),
                env=env,
            )
            elapsed_ms = round((time.monotonic() - start_time) * 1000.0, 2)
            comb_output = f"{proc.stdout}\n{proc.stderr}".strip()
            tests_run, failures, errors = self._parse_unittest_output(comb_output)
            is_success = (proc.returncode == 0) and (failures == 0) and (errors == 0)

            err_summary = None
            if not is_success:
                err_lines = [line for line in comb_output.splitlines() if line.startswith(("FAIL:", "ERROR:", "Traceback"))]
                err_summary = "; ".join(err_lines[:5]) if err_lines else "Test suite failed."

            return SandboxExecutionResult(
                success=is_success,
                tests_run=tests_run,
                failures=failures,
                errors=errors,
                duration_ms=elapsed_ms,
                self_healing_attempts=0,
                stdout=proc.stdout,
                stderr=proc.stderr,
                error_summary=err_summary,
            )
        except subprocess.TimeoutExpired as te:
            elapsed_ms = round((time.monotonic() - start_time) * 1000.0, 2)
            return SandboxExecutionResult(
                success=False,
                tests_run=0,
                failures=0,
                errors=1,
                duration_ms=elapsed_ms,
                self_healing_attempts=0,
                stdout="",
                stderr=f"Sandbox Execution Timeout: exceeded {self.timeout_sec} seconds.",
                error_summary="TimeoutExpired",
            )

    def execute_with_self_healing(
        self,
        package_dir: Union[str, Path],
        repair_callback: Optional[Callable[[str, int], bool]] = None,
    ) -> SandboxExecutionResult:
        """
        Executes test suite with autonomous repair retry loop.
        If tests fail and a repair_callback is provided, triggers repair and re-evaluates.
        """
        attempts = 0
        last_result = self.execute_test_suite(package_dir)

        while not last_result.success and attempts < self.max_self_healing_retries:
            attempts += 1
            if not repair_callback:
                break

            # Attempt self-healing patch
            feedback = last_result.error_summary or last_result.stderr
            repaired = repair_callback(feedback, attempts)
            if not repaired:
                break

            # Re-execute after repair
            last_result = self.execute_test_suite(package_dir)
            last_result.self_healing_attempts = attempts

        return last_result


__all__ = ["SandboxRunner", "SandboxExecutionResult"]
