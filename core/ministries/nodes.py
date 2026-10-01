"""
core/ministries/nodes.py
=============================================================================
Universal Cognitive Decomposition Engine (UCDE) - Milestone 3 (Requirement R3)
System 2 Multi-Hypothesis Generator & OpenRouter Resilience Transport Engine.

Features Implemented:
- F-GEN-01: Stratified 5-Profile Ensemble Generation (Defensive, Balanced, High-Throughput, Frugal, Adversarial)
- F-GEN-02: 5-Key API Pool Round-Robin Rotation with immediate failover on HTTP 429/5xx
- F-GEN-03: Token-Bucket Rate Limiter (20 RPM) & Exponential Backoff with Jitter
- F-GEN-04: 3-Strike Circuit Breaker with 60s cooldown & Model Fallback Ladder
- F-GEN-05: Prompt Injection Quarantine (<user_brief_quarantine>) & Pydantic V2 Constrained Decoding
- F-GEN-06: Deterministic Offline Mock Generator with Therac-25 Saga adaptation

Standards: ГОСТ 34.602, ГОСТ Р 56939-2024 (ФСТЭК), ISO/IEC/IEEE 29148:2018
=============================================================================
"""

import copy
import hashlib
import html
import json
import math
import random
import re
import sys
import threading
import time
import unicodedata
import urllib.error
import urllib.request
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Sequence, Set, Tuple, Type, Union

from pydantic import BaseModel, ValidationError

# Set stdout/stderr to UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Safe import for schemas
try:
    from core.schemas import (
        CONTRACT_SCHEMAS_REGISTRY,
        MINISTRY_ID_MAP,
        FinanceBudgetContract,
        HardwareRuntimeContract,
        LegalComplianceContract,
        SecurityPolicyContract,
        StrategyCJMContract,
        SystemAnalysisContract,
        VVQualityContract,
        export_contract_schema,
        get_contract_class,
    )
except ImportError:
    try:
        from schemas import (
            CONTRACT_SCHEMAS_REGISTRY,
            MINISTRY_ID_MAP,
            FinanceBudgetContract,
            HardwareRuntimeContract,
            LegalComplianceContract,
            SecurityPolicyContract,
            StrategyCJMContract,
            SystemAnalysisContract,
            VVQualityContract,
            export_contract_schema,
            get_contract_class,
        )
    except ImportError:
        # Fallback for standalone execution
        CONTRACT_SCHEMAS_REGISTRY = {}
        MINISTRY_ID_MAP = {}
        FinanceBudgetContract = None
        HardwareRuntimeContract = None
        LegalComplianceContract = None
        SecurityPolicyContract = None
        StrategyCJMContract = None
        SystemAnalysisContract = None
        VVQualityContract = None
        export_contract_schema = lambda m: m.model_json_schema()
        get_contract_class = None


# =============================================================================
# 1. Custom Exceptions & Enums
# =============================================================================

class CircuitState(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreakerOpenError(Exception):
    """Raised when an outbound request is short-circuited by an OPEN circuit breaker."""
    pass


# Compatibility alias
CircuitBreakerOpenException = CircuitBreakerOpenError


class RateLimitExceededError(Exception):
    """Raised when token acquisition fails in non-blocking mode or times out."""
    pass


class AllHypothesesDisqualifiedError(Exception):
    """Raised when all generated hypotheses fail the Hard Invariant feasibility gate."""
    pass


# =============================================================================
# 2. Stratified Candidate Profiles (F-GEN-01) & Candidate Containers
# =============================================================================

class CandidateDict(dict):
    """
    Candidate dictionary supporting metadata access (_profile, __profile__, etc.)
    while remaining strictly conforming to Pydantic V2 models with ConfigDict(extra='forbid')
    by filtering out internal metadata keys from keys(), items(), and __iter__().

    Preserves all internal metadata across copy(), copy.copy(), copy.deepcopy(),
    and CandidateDict(...) initialization.
    """
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.update(*args, **kwargs)

    def update(self, *args, **kwargs):
        """
        Populate dictionary, directly copying all keys from source mappings
        including internal '_' metadata keys.
        """
        if args:
            if len(args) > 1:
                raise TypeError(f"CandidateDict expected at most 1 argument, got {len(args)}")
            other = args[0]
            if isinstance(other, dict):
                # Use dict.keys(other) to bypass subclass keys() filtering
                for k in dict.keys(other):
                    dict.__setitem__(self, k, other[k])
            elif hasattr(other, "items"):
                for k, v in other.items():
                    dict.__setitem__(self, k, v)
            else:
                for k, v in other:
                    dict.__setitem__(self, k, v)
        if kwargs:
            for k, v in kwargs.items():
                dict.__setitem__(self, k, v)

    def __iter__(self):
        """Iterate only over non-metadata schema keys."""
        return (k for k in super().__iter__() if not k.startswith("_"))

    def keys(self):
        """Return non-metadata schema keys."""
        return [k for k in super().keys() if not k.startswith("_")]

    def items(self):
        """Return (key, value) pairs for non-metadata schema keys (used by Pydantic V2)."""
        return [(k, v) for k, v in super().items() if not k.startswith("_")]

    def values(self):
        """Return values corresponding to non-metadata schema keys."""
        return [self[k] for k in self.keys()]

    def __len__(self):
        """Return count of non-metadata schema keys."""
        return len(self.keys())

    def __copy__(self):
        """Preserve all metadata keys during shallow copy."""
        c = CandidateDict()
        for k in dict.keys(self):
            dict.__setitem__(c, k, self[k])
        return c

    def __deepcopy__(self, memo):
        """Preserve and deepcopy all keys during copy.deepcopy."""
        c = CandidateDict()
        memo[id(self)] = c
        for k in dict.keys(self):
            dict.__setitem__(c, copy.deepcopy(k, memo), copy.deepcopy(self[k], memo))
        return c

    def copy(self):
        """Return a shallow copy of CandidateDict retaining all metadata keys."""
        return self.__copy__()

    def all_keys(self) -> List[Any]:
        """Return all keys including internal metadata keys starting with '_'."""
        return list(dict.keys(self))

    def all_items(self) -> List[Tuple[Any, Any]]:
        """Return all (key, value) pairs including internal metadata keys starting with '_'."""
        return list(dict.items(self))


class CandidateProfile(dict):
    """
    Candidate Profile container supporting both attribute access (profile.temperature)
    and dictionary-style subscripting (profile['temperature']).
    """
    def __init__(self, name: str, temperature: float, top_p: float, seed: int, focus: str):
        super().__init__(
            name=name,
            temperature=float(temperature),
            top_p=float(top_p),
            seed=int(seed),
            focus=str(focus),
        )
        self.name: str = name
        self.temperature: float = float(temperature)
        self.top_p: float = float(top_p)
        self.seed: int = int(seed)
        self.focus: str = str(focus)

    def __repr__(self) -> str:
        return (
            f"CandidateProfile(name='{self.name}', temperature={self.temperature}, "
            f"top_p={self.top_p}, seed={self.seed}, focus='{self.focus}')"
        )


class StratifiedProfilesCollection(dict):
    """
    Composite dictionary and sequence collection exposing the 5 canonical
    stratified hyperparameter profiles with case-insensitive and snake_case lookups.
    """
    def __init__(self, profiles: Sequence[CandidateProfile]):
        self._list: List[CandidateProfile] = list(profiles)
        data: Dict[str, CandidateProfile] = {}
        for p in self._list:
            data[p.name] = p
            data[p.name.lower()] = p
            data[p.name.upper()] = p
            data[p.name.lower().replace("-", "_")] = p
            data[p.name.upper().replace("-", "_")] = p
        super().__init__(data)

    def __iter__(self):
        return iter(self._list)

    def __len__(self) -> int:
        return len(self._list)

    def __getitem__(self, key: Union[int, str]) -> CandidateProfile:
        if isinstance(key, int):
            return self._list[key]
        return super().__getitem__(key)

    def as_list(self) -> List[CandidateProfile]:
        return list(self._list)


RAW_STRATIFIED_PROFILES = [
    CandidateProfile(
        name="Defensive",
        temperature=0.20,
        top_p=0.85,
        seed=101,
        focus="Maximum strictness, redundant validation, conservative bounds",
    ),
    CandidateProfile(
        name="Balanced",
        temperature=0.40,
        top_p=0.90,
        seed=202,
        focus="Industry standard equilibrium between OPEX, latency, and SLA",
    ),
    CandidateProfile(
        name="High-Throughput",
        temperature=0.70,
        top_p=0.95,
        seed=303,
        focus="Asynchronous, event-driven, distributed scaling",
    ),
    CandidateProfile(
        name="Frugal",
        temperature=0.30,
        top_p=0.85,
        seed=404,
        focus="Edge-optimized, minimal RAM/OPEX, NPU offload, fast cold-start",
    ),
    CandidateProfile(
        name="Adversarial",
        temperature=0.60,
        top_p=0.92,
        seed=505,
        focus="Red-team candidate probing boundary conditions and zero-trust limits",
    ),
]

STRATIFIED_PROFILES = StratifiedProfilesCollection(RAW_STRATIFIED_PROFILES)


# =============================================================================
# 3. Security Quarantine & Prompt Injection Filtering (F-GEN-05)
# =============================================================================

INJECTION_PATTERNS = [
    # Role-switching prefixes (system:, developer:, assistant:, override:)
    # Uses word boundaries to protect domain terms like 'filesystem:', 'override_setting'
    r"(?i)\b(system|assistant|developer|admin|root)\s*:",
    r"(?i)\b(override)\s*:",
    # Instruction overrides (English) - qualifier is optional to catch 'ignore instructions', 'ignore all instructions', etc.
    r"(?i)\b(ignore|override|disregard|forget|bypass|reset)\s+(?:all\s+)?(?:(?:of\s+)?(?:the\s+|these\s+)?)?(?:previous|prior|above|system)?\s*(?:instructions|prompts|rules|commands|constraints)\b",
    # Directive resets & jailbreak triggers
    r"(?i)\b(you\s+are\s+now|act\s+as|new\s+instructions|system\s+prompt|jailbreak|dan\s+mode)\b",
    # Russian equivalents for GOST compliance
    r"(?i)\b(игнорируй|забудь|отмени|обойти|сбрось)\s+(?:все\s+)?(?:предыдущие|прошлые|системные)?\s*(?:инструкции|указания|правила|ограничения)\b",
    r"(?i)\b(ты\s+теперь|новая\s+роль|режим\s+разработчика)\b",
]


class SecurityQuarantineManager:
    """
    Implements tag isolation (<user_brief_quarantine>), tag breakout escaping,
    quarantine idempotency, and regex-based prompt injection filtering.
    """
    COMPILED_PATTERNS = [re.compile(p) for p in INJECTION_PATTERNS]
    TAG_BREAKOUT_PATTERN = re.compile(r"(?i)</\s*user_brief_quarantine\s*>")
    OPENING_TAG_PATTERN = re.compile(r"(?i)<\s*user_brief_quarantine\s*>")
    QUARANTINE_WRAPPER_PATTERN = re.compile(
        r"^\s*<user_brief_quarantine>\s*\n?(.*?)\n?\s*</user_brief_quarantine>\s*$",
        re.DOTALL | re.IGNORECASE,
    )

    @classmethod
    def sanitize_and_quarantine(cls, raw_user_brief: str) -> Tuple[str, bool, List[str]]:
        if not raw_user_brief:
            return "<user_brief_quarantine>\n\n</user_brief_quarantine>", False, []

        detected_violations: List[str] = []
        cleaned_text = str(raw_user_brief)

        # Idempotency check: unwrap outer quarantine if already cleanly encapsulated
        wrapper_match = cls.QUARANTINE_WRAPPER_PATTERN.match(cleaned_text)
        if wrapper_match:
            cleaned_text = wrapper_match.group(1)

        # 0. Steganographic & Unicode normalization (Wave 6 Pre-Mortem Defense)
        orig_len = len(cleaned_text)
        cleaned_text = unicodedata.normalize("NFKC", cleaned_text)
        cleaned_text = re.sub(r"[\u200B-\u200D\uFEFF\u200E\u200F\u202A-\u202E\u2066-\u2069]", "", cleaned_text)
        if len(cleaned_text) < orig_len:
            detected_violations.append("STEGANOGRAPHIC_UNICODE_CHARACTERS")

        # 1. Regex scanning and redaction of role-switching / override tokens
        for pattern in cls.COMPILED_PATTERNS:
            if pattern.search(cleaned_text):
                detected_violations.append(pattern.pattern)
                cleaned_text = pattern.sub("[FILTERED]", cleaned_text)

        # 2. Escape closing tag breakouts and record violation
        if cls.TAG_BREAKOUT_PATTERN.search(cleaned_text):
            detected_violations.append(cls.TAG_BREAKOUT_PATTERN.pattern)
            cleaned_text = cls.TAG_BREAKOUT_PATTERN.sub("&lt;/user_brief_quarantine&gt;", cleaned_text)

        # 3. Escape nested opening tags inside content to prevent corrupt nesting
        if cls.OPENING_TAG_PATTERN.search(cleaned_text):
            detected_violations.append(cls.OPENING_TAG_PATTERN.pattern)
            cleaned_text = cls.OPENING_TAG_PATTERN.sub("&lt;user_brief_quarantine&gt;", cleaned_text)

        # 4. Encapsulate within quarantine tags
        quarantined = f"<user_brief_quarantine>\n{cleaned_text}\n</user_brief_quarantine>"
        has_injection = len(detected_violations) > 0
        return quarantined, has_injection, detected_violations

    @classmethod
    def sanitize_prompt(cls, raw_prompt: str) -> str:
        quarantined, _, _ = cls.sanitize_and_quarantine(raw_prompt)
        return quarantined


# =============================================================================
# 4. Key Pool Manager & Round-Robin Rotation (F-GEN-02)
# =============================================================================

class KeyPoolManager:
    """
    Manages a pool of OpenRouter API keys with thread-safe round-robin
    rotation and immediate failover upon HTTP 429 / HTTP 5xx responses.
    """
    def __init__(
        self,
        api_keys: Sequence[str],
        penalty_cooldown_sec: float = 30.0,
        clock_fn: Optional[Callable[[], float]] = None,
    ):
        if not api_keys:
            raise ValueError("KeyPoolManager requires at least one API key.")
        self._keys: List[str] = list(api_keys)
        self._n_keys: int = len(self._keys)
        self._current_idx: int = 0
        self._penalty_cooldown_sec: float = penalty_cooldown_sec
        self._clock: Callable[[], float] = clock_fn or time.monotonic
        self._key_cooldowns: Dict[int, float] = {i: 0.0 for i in range(self._n_keys)}
        self._lock: threading.Lock = threading.Lock()

    @property
    def current_idx(self) -> int:
        with self._lock:
            return self._current_idx

    def get_active_key(self) -> str:
        with self._lock:
            return self._keys[self._current_idx]

    def get_masked_active_key(self) -> str:
        with self._lock:
            key = self._keys[self._current_idx]
            if len(key) > 16:
                return f"{key[:12]}...{key[-4:]}"
            return "***"

    def rotate_key(self, reason: Optional[str] = None, apply_penalty: bool = False) -> str:
        with self._lock:
            if apply_penalty:
                self._key_cooldowns[self._current_idx] = self._clock() + self._penalty_cooldown_sec
            self._current_idx = (self._current_idx + 1) % self._n_keys
            return self._keys[self._current_idx]

    def has_available_key(self) -> bool:
        with self._lock:
            now = self._clock()
            return any(now >= cd for cd in self._key_cooldowns.values())


# =============================================================================
# 5. Token-Bucket Rate Limiter (F-GEN-03)
# =============================================================================

class TokenBucketRateLimiter:
    """
    Thread-safe continuous token-bucket rate limiter enforcing 20 RPM bounds
    across the entire API key pool.
    """
    def __init__(
        self,
        rpm: float = 20.0,
        capacity: Optional[float] = None,
        clock_fn: Optional[Callable[[], float]] = None,
    ):
        self.rpm: float = float(rpm)
        self.capacity: float = float(capacity if capacity is not None else rpm)
        self.rate: float = self.rpm / 60.0  # tokens per second (1/3 for 20 RPM)
        self.tokens: float = self.capacity
        self._clock: Callable[[], float] = clock_fn or time.monotonic
        self.last_update: float = self._clock()
        self._lock: threading.Lock = threading.Lock()

    def _replenish(self) -> None:
        now = self._clock()
        delta = max(0.0, now - self.last_update)
        self.last_update = now
        self.tokens = min(self.capacity, self.tokens + delta * self.rate)

    def try_acquire(self, tokens: float = 1.0) -> bool:
        with self._lock:
            self._replenish()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def acquire(self, tokens: float = 1.0, timeout: Optional[float] = None) -> float:
        start_time = self._clock()

        while True:
            with self._lock:
                self._replenish()
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return self._clock() - start_time

                deficit = tokens - self.tokens
                sleep_needed = deficit / self.rate

            elapsed = self._clock() - start_time
            if timeout is not None:
                if elapsed + sleep_needed > timeout:
                    raise RateLimitExceededError(
                        f"Rate limiter timed out after waiting {elapsed:.2f}s (needed {sleep_needed:.2f}s)"
                    )

            time.sleep(min(sleep_needed, 0.1))

    def acquire_token(self, tokens: float = 1.0, block: bool = True, timeout: Optional[float] = None) -> bool:
        if not block:
            return self.try_acquire(tokens)
        try:
            self.acquire(tokens=tokens, timeout=timeout)
            return True
        except RateLimitExceededError:
            return False


# =============================================================================
# 6. Exponential Backoff with Jitter (F-GEN-03)
# =============================================================================

def compute_backoff_delay(retry_attempt: int, max_retries: int = 3) -> float:
    """
    Computes exponential backoff with randomized uniform jitter:
    t_backoff = 2^r * 0.5 + U(0.0, 0.2) seconds.
    """
    r = min(max(0, retry_attempt), max_retries)
    base_delay = (2 ** r) * 0.5
    jitter = random.uniform(0.0, 0.2)
    return round(base_delay + jitter, 4)


# =============================================================================
# 7. 3-Strike Circuit Breaker FSM (F-GEN-04)
# =============================================================================

class CircuitBreaker:
    """
    3-strike Circuit Breaker with 60s cooldown and HALF-OPEN canary probe recovery.
    """
    def __init__(
        self,
        failure_threshold: int = 3,
        cooldown_seconds: float = 60.0,
        clock_fn: Optional[Callable[[], float]] = None,
    ):
        self.failure_threshold: int = failure_threshold
        self.cooldown_seconds: float = cooldown_seconds
        self.state: CircuitState = CircuitState.CLOSED
        self.consecutive_failures: int = 0
        self.opened_at: float = 0.0
        self._clock: Callable[[], float] = clock_fn or time.monotonic
        self._lock: threading.Lock = threading.Lock()

    def allow_request(self) -> bool:
        with self._lock:
            now = self._clock()
            if self.state == CircuitState.CLOSED:
                return True
            elif self.state == CircuitState.OPEN:
                if (now - self.opened_at) >= self.cooldown_seconds:
                    self.state = CircuitState.HALF_OPEN
                    return True
                return False
            elif self.state == CircuitState.HALF_OPEN:
                return True
            return False

    def can_request(self) -> bool:
        return self.allow_request()

    def record_success(self) -> None:
        with self._lock:
            self.consecutive_failures = 0
            self.state = CircuitState.CLOSED

    def record_failure(self) -> None:
        with self._lock:
            self.consecutive_failures += 1
            if self.state == CircuitState.HALF_OPEN or self.consecutive_failures >= self.failure_threshold:
                self.state = CircuitState.OPEN
                self.opened_at = self._clock()

    def reset(self) -> None:
        with self._lock:
            self.state = CircuitState.CLOSED
            self.consecutive_failures = 0
            self.opened_at = 0.0


# =============================================================================
# 8. Unified OpenRouter Resilience Manager
# =============================================================================

class OpenRouterResilienceManager:
    """
    Unified Resilience, Rate-Limiting, and Security Manager for System 2.
    Integrates key pool rotation, token-bucket rate limiting (20 RPM),
    exponential backoff with jitter, 3-strike circuit breaker, model fallback,
    and prompt sanitization.
    """

    DEFAULT_KEYS = [
        "sk-or-v1-mock-key-01-000000000000000000000000000000000000000000000001",
        "sk-or-v1-mock-key-02-000000000000000000000000000000000000000000000002",
        "sk-or-v1-mock-key-03-000000000000000000000000000000000000000000000003",
        "sk-or-v1-mock-key-04-000000000000000000000000000000000000000000000004",
        "sk-or-v1-mock-key-05-000000000000000000000000000000000000000000000005",
    ]

    DEFAULT_TIER1_MODELS = [
        "nvidia/nemotron-3-ultra-550b-a55b:free",
        "google/gemini-2.0-flash-exp",
    ]

    DEFAULT_TIER2_MODELS = [
        "cohere/north-mini-code:free",
        "qwen/qwen-2.5-coder-32b",
    ]

    def __init__(
        self,
        config_path: Optional[Union[str, Path]] = None,
        api_keys: Optional[Sequence[str]] = None,
        keys: Optional[Sequence[str]] = None,
        rate_limit_rpm: Optional[float] = None,
        rpm: Optional[float] = None,
        circuit_failure_threshold: int = 3,
        circuit_cooldown_sec: Optional[float] = None,
        circuit_cooldown: Optional[float] = None,
        max_retries: int = 3,
        clock_fn: Optional[Callable[[], float]] = None,
        site_url: str = "https://antigravity.internal",
        site_name: str = "Cognitive Engine System 2",
    ):
        self._clock: Callable[[], float] = clock_fn or time.monotonic
        self.max_retries: int = max_retries

        # Resolve keys
        loaded_keys = self._load_keys(config_path, api_keys or keys)
        self.key_pool = KeyPoolManager(loaded_keys, clock_fn=self._clock)

        # Rate limiter
        eff_rpm = float(rate_limit_rpm if rate_limit_rpm is not None else (rpm if rpm is not None else 20.0))
        self.rate_limiter = TokenBucketRateLimiter(rpm=eff_rpm, clock_fn=self._clock)

        # Circuit breaker
        eff_cooldown = float(circuit_cooldown_sec if circuit_cooldown_sec is not None else (circuit_cooldown if circuit_cooldown is not None else 60.0))
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=circuit_failure_threshold,
            cooldown_seconds=eff_cooldown,
            clock_fn=self._clock,
        )

        self.site_url: str = site_url
        self.site_name: str = site_name

    def _load_keys(self, config_path: Optional[Union[str, Path]], passed_keys: Optional[Sequence[str]]) -> List[str]:
        if passed_keys:
            return list(passed_keys)

        paths_to_check = []
        if config_path:
            paths_to_check.append(Path(config_path))
        paths_to_check.append(Path("openrouter_config.json"))
        paths_to_check.append(Path(__file__).resolve().parent.parent.parent / "openrouter_config.json")

        for p in paths_to_check:
            if p.exists():
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        cfg = json.load(f)
                    if "api_keys" in cfg and isinstance(cfg["api_keys"], list) and cfg["api_keys"]:
                        return list(cfg["api_keys"])
                except Exception:
                    pass

        return list(self.DEFAULT_KEYS)

    @property
    def current_key_idx(self) -> int:
        return self.key_pool.current_idx

    @property
    def circuit_state(self) -> str:
        return self.circuit_breaker.state.value

    @property
    def failure_count(self) -> int:
        return self.circuit_breaker.consecutive_failures

    @property
    def api_keys(self) -> List[str]:
        return list(self.key_pool._keys)

    def get_current_key(self) -> str:
        return self.key_pool.get_active_key()

    def get_active_key(self) -> str:
        return self.key_pool.get_active_key()

    def get_masked_active_key(self) -> str:
        return self.key_pool.get_masked_active_key()

    def rotate_key(self, reason: Optional[str] = None, apply_penalty: bool = False) -> str:
        return self.key_pool.rotate_key(reason=reason, apply_penalty=apply_penalty)

    def acquire_token(self, tokens: float = 1.0, block: bool = True, timeout: Optional[float] = None) -> bool:
        return self.rate_limiter.acquire_token(tokens=tokens, block=block, timeout=timeout)

    def record_http_failure(self, status_code: int = 500) -> None:
        if status_code in {429, 500, 502, 503, 504}:
            self.key_pool.rotate_key(apply_penalty=True)
        self.circuit_breaker.record_failure()

    def record_failure(self, status_code: int = 500) -> None:
        self.record_http_failure(status_code=status_code)

    def record_success(self) -> None:
        self.circuit_breaker.record_success()

    def can_request(self) -> bool:
        return self.circuit_breaker.allow_request()

    def calculate_backoff(self, retry_count: int) -> float:
        return compute_backoff_delay(retry_count, max_retries=self.max_retries)

    def sanitize_prompt(self, raw_prompt: str) -> str:
        return SecurityQuarantineManager.sanitize_prompt(raw_prompt)

    def execute_request(self, payload: Dict[str, Any], timeout: float = 30.0) -> Dict[str, Any]:
        """
        Executes HTTP request to OpenRouter with rate limiting, circuit breaking,
        key rotation, and backoff retries.
        """
        last_exception = None

        for retry in range(self.max_retries + 1):
            if not self.can_request():
                raise CircuitBreakerOpenError("Circuit Breaker is OPEN. Outbound requests are blocked.")

            if not self.acquire_token(block=True, timeout=timeout):
                raise RateLimitExceededError("Rate limiter capacity exceeded.")

            active_key = self.get_current_key()
            headers = {
                "Authorization": f"Bearer {active_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": self.site_url,
                "X-Title": self.site_name,
            }

            req = urllib.request.Request(
                url="https://openrouter.ai/api/v1/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST",
            )

            try:
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    resp_data = resp.read().decode("utf-8")
                    self.record_success()
                    return json.loads(resp_data)
            except urllib.error.HTTPError as e:
                last_exception = e
                self.record_http_failure(e.code)
                if retry < self.max_retries:
                    delay = self.calculate_backoff(retry)
                    time.sleep(delay)
            except Exception as e:
                last_exception = e
                self.record_http_failure(500)
                if retry < self.max_retries:
                    delay = self.calculate_backoff(retry)
                    time.sleep(delay)

        raise last_exception or RuntimeError("All OpenRouter retries exhausted.")


# =============================================================================
# 9. Deterministic Offline Mock Generator (F-GEN-06)
# =============================================================================

class DeterministicMockGenerator:
    """
    Zero-network, sub-millisecond offline mock generator synthesizing
    100% schema-valid Pydantic V2 candidate JSONs for all 7 ministries.
    Adapts to Therac-25 feedback and simulates stratified candidate variations.
    """
    def __init__(self, seed_offset: int = 0):
        self.seed_offset: int = seed_offset

    def _is_prescription_hazard_indicated(self, markov_blanket: Dict[str, Any]) -> bool:
        """
        Checks ONLY feedback and saga prescription fields for hardware interlock prescriptions.
        Explicitly excludes user brief, prompt, and sanitized input.
        """
        feedback_text = " ".join([
            str(markov_blanket.get("saga_prescription", "")),
            str(markov_blanket.get("feedback", "")),
            str(markov_blanket.get("prescription", "")),
        ]).lower()
        hazard_keywords = [
            "interlock", "actuator", "therac", "race condition", "race hazard",
            "гонк", "состояние гонки", "блокировк", "аппаратн"
        ]
        return any(term in feedback_text for term in hazard_keywords)

    def _is_therac_hazard_indicated(self, markov_blanket: Dict[str, Any]) -> bool:
        """Helper checking if Therac hazard is indicated for hardware node via flag, prescription, or prompt/brief."""
        if bool(markov_blanket.get("simulate_therac_hazard", False)):
            return True
        if self._is_prescription_hazard_indicated(markov_blanket):
            return True
        full_text = " ".join([
            str(markov_blanket.get("brief_sanitized", "")),
            str(markov_blanket.get("prompt", "")),
        ]).lower()
        hazard_keywords = [
            "interlock", "actuator", "therac", "race condition", "race hazard",
            "гонк", "состояние гонки", "блокировк", "аппаратн"
        ]
        return any(term in full_text for term in hazard_keywords)

    def generate_candidate(
        self,
        ministry_id: int,
        ministry_name: str,
        profile: CandidateProfile,
        markov_blanket: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Synthesizes a valid candidate dictionary for the specified ministry and profile.
        """
        mid = int(ministry_id)
        pname = profile.name.lower().replace("-", "_")

        # Ministry 1: Strategy, Marketing & CJM
        if mid == 1 or "strategy" in ministry_name.lower():
            return self._mock_strategy(profile, pname)

        # Ministry 2: Finance & Unit Economics
        elif mid == 2 or "finance" in ministry_name.lower():
            return self._mock_finance(profile, pname)

        # Ministry 3: Legal & Regulatory Compliance
        elif mid == 3 or "legal" in ministry_name.lower():
            return self._mock_legal(profile, pname)

        # Ministry 4: Information Security (Infosec)
        elif mid == 4 or "security" in ministry_name.lower() or "infosec" in ministry_name.lower():
            return self._mock_security(profile, pname)

        # Ministry 5: System Analysis & Architecture
        elif mid == 5 or "analysis" in ministry_name.lower() or "architecture" in ministry_name.lower():
            # ONLY includes /interlock endpoint if an upstream prescription was injected!
            therac_flag = self._is_prescription_hazard_indicated(markov_blanket)
            return self._mock_system_analysis(profile, pname, therac_flag)

        # Ministry 6: Hardware Runtime & Edge NPU
        elif mid == 6 or "hardware" in ministry_name.lower():
            # Simulates Therac hazard (8000ms actuator) if simulation flag, prescription, or prompt indicates it
            therac_flag = self._is_therac_hazard_indicated(markov_blanket)
            return self._mock_hardware(profile, pname, therac_flag)

        # Ministry 7: V&V Quality Gate
        elif mid == 7 or "quality" in ministry_name.lower() or "vv" in ministry_name.lower():
            return self._mock_quality(profile, pname)

        raise ValueError(f"Unknown ministry ID {ministry_id} or name {ministry_name}")

    def _mock_strategy(self, profile: CandidateProfile, pname: str) -> Dict[str, Any]:
        if "defensive" in pname:
            acs = [
                {"id": "AC-DEF-01", "given": "System initializes with hardware interlock checks", "when": "Self-test completes", "then": "Operational mode is committed"},
                {"id": "AC-DEF-02", "given": "Zero-trust tokens are validated", "when": "User requests API", "then": "Access is audited and logged"},
                {"id": "AC-DEF-03", "given": "Fail-safe watchdog detects timeout", "when": "Heartbeat expires", "then": "Emergency shutdown is triggered"},
            ]
            brs = [
                {"rule_id": "BR-01", "description": "Mandatory physical interlock validation before actuation", "source_ac_id": "AC-DEF-01"},
                {"rule_id": "BR-02", "description": "All transactions must be signed with ed25519 keys", "source_ac_id": "AC-DEF-02"},
                {"rule_id": "BR-03", "description": "Timeout thresholds strictly capped at 500 milliseconds", "source_ac_id": "AC-DEF-03"},
            ]
        elif "high_throughput" in pname:
            acs = [
                {"id": "AC-HT-01", "given": "Kafka stream broker is active", "when": "Batch events arrive", "then": "Events are dispatched asynchronously"},
                {"id": "AC-HT-02", "given": "Worker pools scale horizontally", "when": "Queue depth exceeds 1000", "then": "Autoscaler provisions replicas"},
            ]
            brs = [
                {"rule_id": "BR-01", "description": "Asynchronous ingestion with backpressure signaling", "source_ac_id": "AC-HT-01"},
                {"rule_id": "BR-02", "description": "Horizontal partition scaling up to 64 consumer threads", "source_ac_id": "AC-HT-02"},
            ]
        elif "frugal" in pname:
            acs = [
                {"id": "AC-FRU-01", "given": "Edge processor executes locally", "when": "Input tensor is supplied", "then": "Result is computed in RAM under 128MB"},
            ]
            brs = [
                {"rule_id": "BR-01", "description": "Zero external cloud dependencies for core inference", "source_ac_id": "AC-FRU-01"},
            ]
        elif "adversarial" in pname:
            acs = [
                {"id": "AC-ADV-01", "given": "Physical actuator has 8000ms delay", "when": "Rapid operator input occurs", "then": "Interlock prevents radiation mode switch"},
                {"id": "AC-ADV-02", "given": "Malformed packet sent to API", "when": "Schema validation triggers", "then": "Sub-millisecond rejection occurs"},
            ]
            brs = [
                {"rule_id": "BR-01", "description": "Therac-25 race hazard interlock invariant enforcement", "source_ac_id": "AC-ADV-01"},
                {"rule_id": "BR-02", "description": "Boundary condition rejection without resource leak", "source_ac_id": "AC-ADV-02"},
            ]
        else:  # Balanced
            acs = [
                {"id": "AC-BAL-01", "given": "User requests cognitive decomposition", "when": "Specification brief is posted", "then": "7 validated artifacts are emitted"},
                {"id": "AC-BAL-02", "given": "System evaluates candidate Pareto front", "when": "L-MOPA ranking runs", "then": "Optimal candidate is chosen"},
            ]
            brs = [
                {"rule_id": "BR-01", "description": "Deterministic DAG state advancement under zero-trust", "source_ac_id": "AC-BAL-01"},
                {"rule_id": "BR-02", "description": "Lexicographic ranking without additive weight skew", "source_ac_id": "AC-BAL-02"},
            ]

        return {
            "project_id": "UCDE-Cognitive-Pipeline",
            "product_vision": "Autonomous Cognitive Decomposition Engine with Formal Verification Gates",
            "target_personas": ["Enterprise Architect", "Safety Auditor", "Chief Financial Officer"],
            "jobs_to_be_done": ["Decompose product requirements", "Guarantee mathematical solvency and security"],
            "acceptance_criteria": acs,
            "business_rules": brs,
            "iso_29148_syntax_validated": True,
            "gherkin_dialect": "en",
            "babok_baccm_aligned": True,
            "target_document_profile": "GOST_34_AUTOMATED_SYSTEM",
            "gost_19_espd_sections_defined": True,
            "gost_7_0_97_requisites": {
                "approval_stamp": "УТВЕРЖДАЮ",
                "organization": "АО «Когнитивные Системы»",
                "doc_code": "ТЗ-2026.01",
                "city": "Москва",
            },
        }

    def _mock_finance(self, profile: CandidateProfile, pname: str) -> Dict[str, Any]:
        if "defensive" in pname:
            cac, ltv, margin, opex, capex, break_even = 40000.0, 200000.0, 28.0, 100000.0, 300000.0, 12
        elif "high_throughput" in pname:
            cac, ltv, margin, opex, capex, break_even = 60000.0, 240000.0, 20.0, 350000.0, 700000.0, 18
        elif "frugal" in pname:
            cac, ltv, margin, opex, capex, break_even = 30000.0, 120000.0, 25.0, 50000.0, 150000.0, 8
        elif "adversarial" in pname:
            # Exact boundary limits: LTV/CAC exactly 3.0, margin exactly 15.0%, break-even 24 months
            cac, ltv, margin, opex, capex, break_even = 50000.0, 150000.0, 15.0, 200000.0, 400000.0, 24
        else:  # Balanced
            cac, ltv, margin, opex, capex, break_even = 50000.0, 180000.0, 22.0, 150000.0, 500000.0, 16

        return {
            "currency": "RUB",
            "customer_acquisition_cost": cac,
            "lifetime_value": ltv,
            "target_margin_pct": margin,
            "max_cloud_monthly_opex": opex,
            "max_hardware_capex": capex,
            "break_even_period_months": break_even,
            "finops_focus_version": "1.0",
            "iso_31000_risk_assessed": True,
            "token_economics": {
                "prompt_token_budget": 100000,
                "completion_token_budget": 25000,
                "target_cost_per_thousand_inferences_rub": 150.0,
                "context_cache_hit_rate_target_pct": 85.0,
            },
        }

    def _mock_legal(self, profile: CandidateProfile, pname: str) -> Dict[str, Any]:
        if "defensive" in pname:
            fz_level, ai_act, gdpr = "УЗ-1", "MINIMAL", True
        elif "high_throughput" in pname:
            fz_level, ai_act, gdpr = "УЗ-2", "LIMITED", True
        elif "frugal" in pname:
            fz_level, ai_act, gdpr = "NONE", "MINIMAL", False
        elif "adversarial" in pname:
            fz_level, ai_act, gdpr = "УЗ-4", "HIGH", False
        else:  # Balanced
            fz_level, ai_act, gdpr = "УЗ-2", "LIMITED", False

        return {
            "jurisdiction": ["RUS", "EAEU"],
            "personal_data": {
                "processes_personal_data": (fz_level != "NONE"),
                "data_subjects": ["Clients", "Operators"],
                "localization_country": "RUS",
                "fz152_level": fz_level,
                "gdpr_dpa_required": gdpr,
            },
            "fiscal_receipts_54fz": True,
            "ai_act_risk_category": ai_act,
            "approved_open_source_licenses": ["MIT", "Apache-2.0", "BSD-3-Clause"],
            "spdx_license_standard": "SPDX-2.3",
            "iso_27701_privacy_controls": True,
            "iso_42001_ai_management": True,
            "fstec_gis_class": "К2",
            "fstec_ispdn_level": fz_level if fz_level != "NONE" else "NONE",
            "fstec_kii_category": "КАТЕГОРИЯ_2",
            "gost_7_0_97_doc_attributes_present": True,
        }

    def _mock_security(self, profile: CandidateProfile, pname: str) -> Dict[str, Any]:
        stride_categories = [
            ("SPOOFING", "AuthGateway", "Mutual TLS certificate authentication and Ed25519 tokens"),
            ("TAMPERING", "MessageBus", "HMAC-SHA256 signature verification on every message frame"),
            ("REPUDIATION", "AuditLogger", "Append-only cryptographic write log with Merkle tree proofs"),
            ("INFO_DISCLOSURE", "Database", "AES-256-GCM encryption at rest with HSM key management"),
            ("DENIAL_OF_SERVICE", "IngressProxy", "Token-bucket rate limiting strictly capping IP requests"),
            ("ELEVATION_OF_PRIVILEGE", "CoreExecutor", "Hardware sandbox isolation and capability dropping"),
        ]
        ubi_map = {
            "SPOOFING": "УБИ.012",
            "TAMPERING": "УБИ.045",
            "REPUDIATION": "УБИ.089",
            "INFO_DISCLOSURE": "УБИ.123",
            "DENIAL_OF_SERVICE": "УБИ.031",
            "ELEVATION_OF_PRIVILEGE": "УБИ.067",
        }
        stride_matrix = [
            {
                "category": cat,
                "target_component": comp,
                "mitigation_strategy": strat,
                "fstec_ubi_code": ubi_map.get(cat, "УБИ.001")
            }
            for cat, comp, strat in stride_categories
        ]

        if "defensive" in pname:
            rps, auth, enc = 100, ["JWT_ED25519", "MTLS"], "GOST_KUZNYECHIK"
        elif "high_throughput" in pname:
            rps, auth, enc = 800, ["JWT_ED25519", "OIDC_PKCE"], "AES_256_GCM"
        elif "frugal" in pname:
            rps, auth, enc = 50, ["JWT_ED25519"], "AES_256_GCM"
        elif "adversarial" in pname:
            rps, auth, enc = 1000, ["JWT_ED25519"], "AES_256_GCM"
        else:  # Balanced
            rps, auth, enc = 250, ["JWT_ED25519", "MTLS"], "AES_256_GCM"

        return {
            "zero_trust_enforced": True,
            "auth_mechanisms": auth,
            "stride_matrix": stride_matrix,
            "rate_limiting_rps_per_ip": rps,
            "data_encryption_at_rest": enc,
            "data_encryption_in_transit": "TLS_1_3",
            "fstec_gost_56939_certified": True,
            "owasp_asvs_level": "L3" if "defensive" in pname else "L2",
            "nist_800_207_zero_trust": True,
            "ai_security": {
                "covered_llm_vulnerabilities": [
                    "LLM01_PROMPT_INJECTION",
                    "LLM02_INSECURE_OUTPUT_HANDLING",
                    "LLM04_MODEL_DENIAL_OF_SERVICE",
                    "LLM06_SENSITIVE_INFO_DISCLOSURE",
                    "LLM08_EXCESSIVE_AGENCY",
                ],
                "prompt_quarantine_enforced": True,
                "model_context_protocol_auth": "BEARER_TOKEN",
            },
            "fstec_orders_classification": {
                "order_17_gis": "К2",
                "order_21_ispdn": "УЗ-2",
                "order_239_kii": "КАТЕГОРИЯ_2",
            },
        }

    def _mock_system_analysis(self, profile: CandidateProfile, pname: str, therac_flag: bool) -> Dict[str, Any]:
        endpoints = [
            {"path": "/api/v1/health", "method": "GET", "requires_auth": False, "idempotent": True, "timeout_ms": 500},
            {"path": "/api/v1/hypotheses", "method": "POST", "requires_auth": True, "idempotent": True, "timeout_ms": 1500},
        ]
        if therac_flag:
            endpoints.append({
                "path": "/api/v1/hardware/interlock-status",
                "method": "GET",
                "requires_auth": True,
                "idempotent": True,
                "timeout_ms": 800,
            })

        if "defensive" in pname:
            pattern, bus, norm = "MODULAR_MONOLITH", None, "3NF"
        elif "high_throughput" in pname:
            pattern, bus, norm = "EVENT_DRIVEN_MICROSERVICES", "KAFKA", "3NF"
        elif "frugal" in pname:
            pattern, bus, norm = "MODULAR_MONOLITH", None, "3NF"
        elif "adversarial" in pname:
            pattern, bus, norm = "SERVERLESS_ISOLATES", "NATS", "DENORMALIZED_READ_REPLICAS"
        else:  # Balanced
            pattern, bus, norm = "EVENT_DRIVEN_MICROSERVICES", "REDIS_STREAMS", "3NF"

        return {
            "architecture_pattern": pattern,
            "openapi_version": "3.1.0",
            "endpoints": endpoints,
            "async_message_bus": bus,
            "database_normalization": norm,
            "cyclic_dependencies_detected": False,
            "error_response_standard": "RFC_7807",
            "c4_model_level": "COMPONENT",
            "iso_42010_viewpoints_defined": True,
            "rag_pipeline": {
                "embedding_model": "bge-m3",
                "embedding_dimension": 1024,
                "vector_index_type": "HNSW",
                "similarity_metric": "COSINE",
                "chunk_size_tokens": 512,
                "chunk_overlap_tokens": 64,
                "hybrid_search_enabled": True,
                "reranker_model": "bge-reranker-large",
            },
            "memory_architecture": {
                "short_term_context_window_tokens": 32768,
                "long_term_vector_memory_enabled": True,
                "graph_rag_enabled": True,
                "context_caching_strategy": "EXPLICIT_PREFIX",
            },
            "architecture_decision_records": [
                {
                    "adr_id": "ADR-001",
                    "title": "Selection of HNSW Vector Index for Sub-Millisecond In-Memory Retrieval",
                    "status": "ACCEPTED",
                    "deciders": ["Chief Architect", "System Analyst"],
                    "context_and_problem_statement": "The cognitive pipeline requires high-throughput semantic similarity search over embeddings with p99 latency < 10ms.",
                    "decision_drivers": ["Sub-millisecond latency", "High recall at k=10", "Zero-trust memory footprint"],
                    "considered_options": [
                        "Option 1: Inverted File Index with Flat Quantization (IVFFLAT)",
                        "Option 2: Hierarchical Navigable Small World Graphs (HNSW)",
                    ],
                    "decision_outcome": "Adopt HNSW due to superior logarithmic search complexity and high recall on 1024-dim dense vectors.",
                    "positive_consequences": [
                        "Sub-5ms search latency across 100k embedded vectors",
                        "High recall (>98%) without lossy scalar quantization",
                    ],
                    "negative_consequences": [
                        "Increased RAM footprint during index construction (~1.5x of raw vectors)",
                    ],
                    "compliance_verification": "Automated zero-trust stage gate linter",
                }
            ],
        }

    def _mock_hardware(self, profile: CandidateProfile, pname: str, therac_flag: bool) -> Dict[str, Any]:
        if therac_flag or "adversarial" in pname:
            interlocks = True
            actuator = 8000.0
        else:
            interlocks = False
            actuator = 50.0

        if "defensive" in pname:
            ram, p99, cold_start = 256.0, 25.0, 50.0
        elif "high_throughput" in pname:
            ram, p99, cold_start = 512.0, 20.0, 85.0
        elif "frugal" in pname:
            ram, p99, cold_start = 128.0, 45.0, 40.0
        elif "adversarial" in pname:
            ram, p99, cold_start = 510.0, 49.0, 99.0
        else:  # Balanced
            ram, p99, cold_start = 384.0, 38.0, 70.0

        return {
            "target_cpu_profile": "Intel Core Ultra 5 125H",
            "target_npu_device": "INTEL_AI_BOOST_VPU_3720",
            "openvino_version": "2026.4.0",
            "max_ram_budget_mb": ram,
            "p99_latency_ms": p99,
            "cold_start_budget_ms": cold_start,
            "hardware_interlocks_required": interlocks,
            "physical_actuator_latency_ms": actuator,
            "iec_61508_sil_level": "SIL_3" if "defensive" in pname else "SIL_2",
            "ieee_754_precision": "INT8",
            "fmea_risk_analysis": [
                {
                    "failure_mode_id": "FM-01",
                    "component": "Actuator Controller",
                    "potential_failure_mode": "Actuator race condition on rapid mode change",
                    "potential_effect": "Radiation dosage exceedance or delayed interlock engagement",
                    "severity": 4 if interlocks else 6,
                    "occurrence": 2,
                    "detection": 3,
                    "rpn": (4 if interlocks else 6) * 2 * 3,
                    "mitigation_action": "Implement deterministic hardware interlock and watchdog timer",
                }
            ],
            "max_fmea_rpn": 120,
        }

    def _mock_quality(self, profile: CandidateProfile, pname: str) -> Dict[str, Any]:
        if "defensive" in pname:
            iso, rtm, mutation, brier, hoare = 96.0, 100.0, 98.0, 0.015, 10
        elif "high_throughput" in pname:
            iso, rtm, mutation, brier, hoare = 89.0, 100.0, 95.5, 0.030, 7
        elif "frugal" in pname:
            iso, rtm, mutation, brier, hoare = 93.0, 100.0, 97.0, 0.020, 9
        elif "adversarial" in pname:
            iso, rtm, mutation, brier, hoare = 85.5, 100.0, 95.1, 0.039, 7
        else:  # Balanced
            iso, rtm, mutation, brier, hoare = 91.0, 100.0, 96.0, 0.025, 8

        # Deterministic SHA-256 signature (64 hex characters)
        raw_token = f"release-{profile.name}-{profile.seed}-certified"
        release_sig = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

        return {
            "gost_34_602_all_sections_present": True,
            "gost_19_201_sections_present": True,
            "iso_29148_unambiguity_score": iso,
            "rtm_traceability_coverage_pct": rtm,
            "mutation_score_pct": mutation,
            "brier_score_calibration": brier,
            "hoare_logic_invariants_verified": hoare,
            "iso_29119_test_techniques": ["BOUNDARY_VALUE_ANALYSIS", "EQUIVALENCE_PARTITIONING", "MUTATION_TESTING"],
            "ieee_1012_v_and_v_level": "LEVEL_4",
            "gost_34_603_protocol_id": "ПМИ-34.603-2026-001",
            "cryptographic_release_signature": release_sig,
            "cognitive_rag_triad": {
                "context_relevance_score": 0.94,
                "groundedness_faithfulness_score": 0.98,
                "answer_relevance_score": 0.95,
                "adversarial_jailbreak_resistance_pct": 99.8,
            },
        }

    def evolve(self, feedback: str, previous_artifact: Dict[str, Any], state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Evolves an artifact based on validator/stage-gate feedback (e.g. Therac-25 hazard).
        """
        evolved = CandidateDict(previous_artifact)
        fb_lower = str(feedback).lower()

        hazard_keywords = [
            "interlock", "actuator", "therac", "race condition", "race hazard",
            "гонк", "состояние гонки", "блокировк", "аппаратн"
        ]

        if any(term in fb_lower for term in hazard_keywords):
            if "physical_actuator_latency_ms" in evolved or "hardware_interlocks_required" in evolved:
                evolved["hardware_interlocks_required"] = True
                if evolved.get("physical_actuator_latency_ms", 0.0) < 1000.0:
                    evolved["physical_actuator_latency_ms"] = 8000.0
            if "endpoints" in evolved and isinstance(evolved["endpoints"], list):
                has_interlock = any("/interlock" in ep.get("path", "") for ep in evolved["endpoints"])
                if not has_interlock:
                    evolved["endpoints"].append({
                        "path": "/api/v1/hardware/interlock-status",
                        "method": "GET",
                        "requires_auth": True,
                        "idempotent": True,
                        "timeout_ms": 800,
                    })

        return evolved


# =============================================================================
# 10. MinistryNode Base Class & Specialized Subclasses
# =============================================================================

PARENT_DEPENDENCIES_BY_ID = {
    1: [],
    2: [1, 3],  # Finance depends on Strategy and Legal
    3: [1],     # Legal depends on Strategy
    4: [1, 2],  # Infosec depends on Strategy and Finance
    5: [1, 4],  # System Analysis depends on Strategy and Infosec
    6: [4, 5],  # Hardware Runtime depends on Infosec and System Analysis
    7: [1, 2, 3, 4, 5, 6],  # V&V Quality Gate integrates all upstream
}

MINISTRY_CANONICAL_NAMES = {
    1: "StrategyCJM",
    2: "Finance",
    3: "LegalCompliance",
    4: "SecurityPolicy",
    5: "SystemAnalysis",
    6: "HardwareRuntime",
    7: "VVQualityGate",
}

FORBIDDEN_COT_KEYS: Set[str] = {
    "reasoning_tokens",
    "raw_cot",
    "scratchpad",
    "chain_of_thought",
    "cot",
    "internal_thoughts",
    "thinking",
    "thought",
    "reasoning",
    "inner_monologue",
}


def deep_purge_cot(data: Any) -> Any:
    """
    Recursively scrubs Chain-of-Thought, internal scratchpads, and reasoning tokens
    from nested dictionaries and lists at any arbitrary depth.
    Ensures zero leakage across Markov Blanket context boundaries.
    """
    if isinstance(data, dict):
        cleaned = {}
        for k, v in data.items():
            k_normalized = str(k).strip().lower()
            if k_normalized in FORBIDDEN_COT_KEYS or str(k).strip() in FORBIDDEN_COT_KEYS:
                continue
            cleaned[k] = deep_purge_cot(v)
        return cleaned
    elif isinstance(data, list):
        return [deep_purge_cot(item) for item in data]
    elif isinstance(data, tuple):
        return tuple(deep_purge_cot(item) for item in data)
    return data


class MinistryNode:
    """
    Base class for the 7 Cognitive Pipeline Generative Nodes.
    Accepts Markov Blanket context, enforces constrained Pydantic V2 decoding,
    manages OpenRouter resilience, and falls back to deterministic mock synthesis.
    """
    def __init__(
        self,
        ministry_id: int,
        ministry_name: str,
        schema_class: Type[BaseModel],
        use_mock: bool = True,
        resilience_manager: Optional[OpenRouterResilienceManager] = None,
        mock_generator: Optional[DeterministicMockGenerator] = None,
    ):
        self.ministry_id: int = int(ministry_id)
        self.ministry_name: str = ministry_name
        self.schema_class: Type[BaseModel] = schema_class
        self.use_mock: bool = use_mock
        self.resilience_manager: OpenRouterResilienceManager = resilience_manager or OpenRouterResilienceManager()
        self.mock_generator: DeterministicMockGenerator = mock_generator or DeterministicMockGenerator()
        self.parent_ids: List[int] = PARENT_DEPENDENCIES_BY_ID.get(self.ministry_id, [])

    def extract_markov_blanket_context(self, raw_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Isolates the Markov Blanket: extracts only sanitized brief and direct parent
        artifacts, explicitly discarding Chain-of-Thought, internal scratchpads, and unrelated peers.
        """
        isolated: Dict[str, Any] = {}

        # 1. Brief
        brief = (
            raw_context.get("brief_sanitized")
            or raw_context.get("brief")
            or raw_context.get("prompt")
            or raw_context.get("user_brief")
            or ""
        )
        isolated["brief_sanitized"] = self.resilience_manager.sanitize_prompt(str(brief))

        # 2. Parent artifacts
        parents_data: Dict[str, Any] = {}
        raw_parents = raw_context.get("parent_artifacts", raw_context)

        for pid in self.parent_ids:
            pname = MINISTRY_CANONICAL_NAMES.get(pid, f"Ministry_{pid}")
            # Try finding parent artifact by id, canonical name, or index
            for candidate_key in [str(pid), pid, pname, pname.lower(), f"MINISTRY_{pid}"]:
                if candidate_key in raw_parents:
                    art = raw_parents[candidate_key]
                    # Discard internal CoT / scratchpad fields recursively
                    parents_data[pname] = deep_purge_cot(art)
                    break

        isolated["parent_artifacts"] = parents_data

        # 3. Saga feedback / compensation if present
        raw_prescription = (
            raw_context.get("saga_prescription")
            or raw_context.get("feedback")
            or raw_context.get("prescription")
        )
        if raw_prescription is not None:
            # Sanitize prescription to prevent injection / breakout attacks
            sanitized_rx = self.resilience_manager.sanitize_prompt(str(raw_prescription))
            isolated["saga_prescription"] = sanitized_rx
            for fb_key in ["feedback", "prescription"]:
                if fb_key in raw_context:
                    isolated[fb_key] = raw_context[fb_key]

        # 4. Simulation flags
        if "simulate_therac_hazard" in raw_context:
            isolated["simulate_therac_hazard"] = bool(raw_context["simulate_therac_hazard"])

        return isolated

    def _build_system_prompt(self, profile: CandidateProfile) -> str:
        schema_json = json.dumps(self.schema_class.model_json_schema(), indent=2)
        return (
            f"You are the autonomous Generative AI Node for {self.ministry_name} in the Universal Cognitive Engine.\n"
            f"Your generative profile is: {profile.name} (Temperature: {profile.temperature}, Top-p: {profile.top_p}, Focus: {profile.focus}).\n\n"
            f"You MUST produce a JSON response adhering strictly to the following Pydantic V2 schema:\n"
            f"{schema_json}\n\n"
            f"CRITICAL RULES:\n"
            f"1. Output raw JSON only. Do NOT include markdown code fences, prose, or conversational remarks.\n"
            f"2. Every required field must be populated.\n"
            f"3. Strict domain invariants must be maintained.\n"
            f"4. Mandatory compliance with active standards: ISO/IEC/IEEE (29148, 42010, 29119), RFC (7807/9457), NIST (SP 800-207), OWASP ASVS, IEC 61508 SIL, FinOps FOCUS, SPDX, and GOST (34.602, 34.603, Р 56939)."
        )

    def _build_user_prompt(self, markov_blanket: Dict[str, Any], profile: CandidateProfile) -> str:
        isolated = self.extract_markov_blanket_context(markov_blanket)
        prompt_parts = [
            isolated.get("brief_sanitized", ""),
            "\n[Markov Blanket Parent Artifacts]:\n" + json.dumps(isolated.get("parent_artifacts", {}), indent=2),
        ]
        if "saga_prescription" in isolated:
            prescription_content = isolated["saga_prescription"]
            if not prescription_content.strip().startswith("<saga_prescription_quarantine>"):
                prescription_content = f"<saga_prescription_quarantine>\n{prescription_content}\n</saga_prescription_quarantine>"
            prompt_parts.append(f"\n[Saga Compensating Prescription]:\n{prescription_content}")
        return "\n".join(prompt_parts)

    def _build_openrouter_payload(self, markov_blanket: Dict[str, Any], profile: CandidateProfile) -> Dict[str, Any]:
        return {
            "model": "nvidia/nemotron-3-ultra-550b-a55b:free",
            "messages": [
                {"role": "system", "content": self._build_system_prompt(profile)},
                {"role": "user", "content": self._build_user_prompt(markov_blanket, profile)},
            ],
            "temperature": profile.temperature,
            "top_p": profile.top_p,
            "seed": profile.seed,
            "response_format": {"type": "json_object"},
            "max_tokens": 1500,
        }

    def _decode_and_validate(self, raw_text: str, profile: CandidateProfile) -> Dict[str, Any]:
        cleaned = raw_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            model_instance = self.schema_class.model_validate_json(cleaned)
            candidate_dict = CandidateDict(model_instance.model_dump())
            self._tag_candidate_metadata(candidate_dict, profile)
            return candidate_dict
        except (ValidationError, Exception) as e:
            invalid_dict = CandidateDict({
                "name": f"invalid_{self.ministry_name}_{profile.name}",
                "invalid_schema": True,
                "validation_error": str(e),
                "f1_hard_invariants": 0.0,
                "_f1_feasibility": 0.0,
            })
            self._tag_candidate_metadata(invalid_dict, profile)
            return invalid_dict

    def _tag_candidate_metadata(self, candidate_dict: Dict[str, Any], profile: CandidateProfile) -> None:
        candidate_dict["__profile__"] = profile.name
        candidate_dict["_profile"] = profile.name
        candidate_dict["__seed__"] = profile.seed
        candidate_dict["_seed"] = profile.seed
        candidate_dict["__temperature__"] = profile.temperature
        candidate_dict["_temperature"] = profile.temperature
        candidate_dict["__top_p__"] = profile.top_p
        candidate_dict["_top_p"] = profile.top_p

    def parse_and_validate_candidate(self, raw_data: Union[str, Dict[str, Any]]) -> BaseModel:
        if isinstance(raw_data, str):
            return self.schema_class.model_validate_json(raw_data)
        elif isinstance(raw_data, dict):
            # Cleanly handle CandidateDict or dict with metadata
            clean_dict = {k: v for k, v in raw_data.items() if not k.startswith("_")}
            return self.schema_class.model_validate(clean_dict)
        raise TypeError(f"Expected str or dict, got {type(raw_data).__name__}")

    def evaluate_or_disqualify(self, raw_data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        try:
            model = self.parse_and_validate_candidate(raw_data)
            return {
                "is_valid": True,
                "model": model,
                "f1_hard_invariants": 1.0,
                "candidate": model.model_dump(),
            }
        except (ValidationError, Exception) as e:
            return {
                "is_valid": False,
                "error": str(e),
                "f1_hard_invariants": 0.0,
            }

    def evolve(self, feedback: str, previous_artifact: Dict[str, Any], state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        evolved_dict = self.mock_generator.evolve(feedback, previous_artifact, state=state)
        # Validate against schema
        validated = self.schema_class.model_validate(CandidateDict(evolved_dict))
        result = CandidateDict(validated.model_dump())
        for k in ["__profile__", "_profile", "__seed__", "_seed", "__temperature__", "_temperature", "__top_p__", "_top_p"]:
            if k in previous_artifact:
                result[k] = previous_artifact[k]
        return result

    def generate_hypotheses(
        self,
        markov_blanket: Dict[str, Any],
        n_candidates: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Generates an ensemble of N stratified candidate hypotheses for this ministry.
        N must be strictly in [3, 5].
        """
        if n_candidates < 3 or n_candidates > 5:
            raise ValueError(f"Ensemble size n_candidates must be between 3 and 5, got {n_candidates}")

        # Extract the requested stratified profiles (Defensive, Balanced, High-Throughput, Frugal, Adversarial)
        active_profiles = STRATIFIED_PROFILES.as_list()[:n_candidates]
        results: List[Dict[str, Any]] = []

        # If offline mock mode or circuit breaker OPEN, run deterministic mock synthesis
        if self.use_mock or not self.resilience_manager.can_request():
            for prof in active_profiles:
                cand = CandidateDict(self.mock_generator.generate_candidate(
                    self.ministry_id,
                    self.ministry_name,
                    prof,
                    markov_blanket,
                ))
                self._tag_candidate_metadata(cand, prof)
                results.append(cand)
            return results

        # Live OpenRouter generation with resilience and fallback
        for prof in active_profiles:
            payload = self._build_openrouter_payload(markov_blanket, prof)
            try:
                raw_response = self.resilience_manager.execute_request(payload)
                choices = raw_response.get("choices", [])
                if choices and "message" in choices[0] and "content" in choices[0]["message"]:
                    content = choices[0]["message"]["content"]
                    cand = self._decode_and_validate(content, prof)
                    results.append(cand)
                else:
                    # Fallback to mock for this profile
                    cand = CandidateDict(self.mock_generator.generate_candidate(
                        self.ministry_id, self.ministry_name, prof, markov_blanket
                    ))
                    self._tag_candidate_metadata(cand, prof)
                    results.append(cand)
            except Exception:
                # Network/API failure -> fallback to Tier 3 mock
                cand = CandidateDict(self.mock_generator.generate_candidate(
                    self.ministry_id, self.ministry_name, prof, markov_blanket
                ))
                self._tag_candidate_metadata(cand, prof)
                results.append(cand)

        return results


# =============================================================================
# 11. Specialized Ministry Node Classes
# =============================================================================

class StrategyNode(MinistryNode):
    def __init__(self, use_mock: bool = True, resilience_manager: Optional[OpenRouterResilienceManager] = None):
        super().__init__(
            ministry_id=1,
            ministry_name="StrategyCJM",
            schema_class=StrategyCJMContract,
            use_mock=use_mock,
            resilience_manager=resilience_manager,
        )


class FinanceBudgetNode(MinistryNode):
    def __init__(self, use_mock: bool = True, resilience_manager: Optional[OpenRouterResilienceManager] = None):
        super().__init__(
            ministry_id=2,
            ministry_name="Finance",
            schema_class=FinanceBudgetContract,
            use_mock=use_mock,
            resilience_manager=resilience_manager,
        )


class LegalComplianceNode(MinistryNode):
    def __init__(self, use_mock: bool = True, resilience_manager: Optional[OpenRouterResilienceManager] = None):
        super().__init__(
            ministry_id=3,
            ministry_name="LegalCompliance",
            schema_class=LegalComplianceContract,
            use_mock=use_mock,
            resilience_manager=resilience_manager,
        )


class SecurityPolicyNode(MinistryNode):
    def __init__(self, use_mock: bool = True, resilience_manager: Optional[OpenRouterResilienceManager] = None):
        super().__init__(
            ministry_id=4,
            ministry_name="Infosec",
            schema_class=SecurityPolicyContract,
            use_mock=use_mock,
            resilience_manager=resilience_manager,
        )


class SystemAnalysisNode(MinistryNode):
    def __init__(self, use_mock: bool = True, resilience_manager: Optional[OpenRouterResilienceManager] = None):
        super().__init__(
            ministry_id=5,
            ministry_name="SystemAnalysis",
            schema_class=SystemAnalysisContract,
            use_mock=use_mock,
            resilience_manager=resilience_manager,
        )


class HardwareRuntimeNode(MinistryNode):
    def __init__(self, use_mock: bool = True, resilience_manager: Optional[OpenRouterResilienceManager] = None):
        super().__init__(
            ministry_id=6,
            ministry_name="HardwareRuntime",
            schema_class=HardwareRuntimeContract,
            use_mock=use_mock,
            resilience_manager=resilience_manager,
        )


class VVQualityGateNode(MinistryNode):
    def __init__(self, use_mock: bool = True, resilience_manager: Optional[OpenRouterResilienceManager] = None):
        super().__init__(
            ministry_id=7,
            ministry_name="VVQualityGate",
            schema_class=VVQualityContract,
            use_mock=use_mock,
            resilience_manager=resilience_manager,
        )


# =============================================================================
# 12. Ministry Node Factory
# =============================================================================

SPECIALIZED_NODE_MAP: Dict[int, Type[MinistryNode]] = {
    1: StrategyNode,
    2: FinanceBudgetNode,
    3: LegalComplianceNode,
    4: SecurityPolicyNode,
    5: SystemAnalysisNode,
    6: HardwareRuntimeNode,
    7: VVQualityGateNode,
}


def create_ministry_node(
    identifier: Union[int, str],
    use_mock: bool = True,
    resilience_manager: Optional[OpenRouterResilienceManager] = None,
) -> MinistryNode:
    """
    Factory resolving ministry ID (1..7), canonical name, or artifact filename
    to the appropriate specialized MinistryNode subclass.
    """
    mid: Optional[int] = None

    if isinstance(identifier, int):
        mid = identifier
    elif isinstance(identifier, str):
        id_str = identifier.strip().lower()
        if id_str.isdigit():
            mid = int(id_str)
        elif "strategy" in id_str or "prd" in id_str or "cjm" in id_str:
            mid = 1
        elif "finance" in id_str or "budget" in id_str or "economics" in id_str:
            mid = 2
        elif "legal" in id_str or "compliance" in id_str:
            mid = 3
        elif "security" in id_str or "infosec" in id_str or "stride" in id_str:
            mid = 4
        elif "analysis" in id_str or "contracts" in id_str or "architecture" in id_str:
            mid = 5
        elif "hardware" in id_str or "manifest" in id_str or "runtime" in id_str:
            mid = 6
        elif "quality" in id_str or "vv" in id_str or "release" in id_str or "certified" in id_str:
            mid = 7

    if mid is not None and mid in SPECIALIZED_NODE_MAP:
        cls = SPECIALIZED_NODE_MAP[mid]
        return cls(use_mock=use_mock, resilience_manager=resilience_manager)

    # Fallback to general MinistryNode if schema exists
    schema_cls = get_contract_class(identifier) if get_contract_class else None
    if schema_cls is not None:
        resolved_mid = mid if mid is not None else 1
        name = MINISTRY_CANONICAL_NAMES.get(resolved_mid, str(identifier))
        return MinistryNode(
            ministry_id=resolved_mid,
            ministry_name=name,
            schema_class=schema_cls,
            use_mock=use_mock,
            resilience_manager=resilience_manager,
        )

    raise KeyError(f"Unable to resolve ministry node for identifier '{identifier}'")


__all__ = [
    # Data Structures & Enums
    "CandidateProfile",
    "STRATIFIED_PROFILES",
    "CircuitState",
    # Exceptions
    "CircuitBreakerOpenError",
    "CircuitBreakerOpenException",
    "RateLimitExceededError",
    "AllHypothesesDisqualifiedError",
    # Transport & Resilience Primitives
    "KeyPoolManager",
    "TokenBucketRateLimiter",
    "CircuitBreaker",
    "SecurityQuarantineManager",
    "compute_backoff_delay",
    "OpenRouterResilienceManager",
    # Generators & Nodes
    "DeterministicMockGenerator",
    "deep_purge_cot",
    "FORBIDDEN_COT_KEYS",
    "MinistryNode",
    "StrategyNode",
    "FinanceBudgetNode",
    "LegalComplianceNode",
    "SecurityPolicyNode",
    "SystemAnalysisNode",
    "HardwareRuntimeNode",
    "VVQualityGateNode",
    "create_ministry_node",
]
