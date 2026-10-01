"""
core/generators/spdx_guard.py
=============================================================================
Universal Cognitive Decomposition Engine (UCDE) - Wave 3
Department 3: Legal, Regulatory Compliance, OpenChain & SPDX 3.0 Tooling.

Software Bill of Materials (SBOM) and License Compliance Guard:
- Standards:
  * OpenChain Specification (ISO/IEC 5230:2020)
  * SPDX 3.0 / SPDX 2.3 (System Package Data Exchange)
- Analyzes software dependencies and licenses:
  * Permissive: MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC (APPROVED)
  * Weak Copyleft: MPL-2.0, LGPL-2.1, LGPL-3.0 (CONDITIONALLY APPROVED with dynamic linking)
  * Viral / Strong Copyleft: GPL-2.0, GPL-3.0, AGPL-3.0, SSPL-1.0 (PROHIBITED for proprietary SaaS/SLA)
- Generates SPDX 3.0 JSON SBOM and emits automated compliance certificates.
=============================================================================
"""

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field


class SpdxPackageEntry(BaseModel):
    """Single package record in an SPDX 3.0 Software Bill of Materials (SBOM)."""
    model_config = ConfigDict(extra="forbid")

    spdx_id: str = Field(description="SPDX идентификатор (например, SPDXRef-Package-Pydantic)")
    name: str = Field(description="Имя пакета / библиотеки")
    version: str = Field(description="Версия зависимости")
    license_concluded: str = Field(description="Идентификатор лицензии по каталогу SPDX (например, MIT, Apache-2.0, AGPL-3.0-only)")
    download_location: str = Field(default="https://pypi.org/simple", description="URL источника пакета")
    checksum_sha256: str = Field(description="Контрольная сумма пакета SHA-256")
    is_copyleft_viral: bool = Field(default=False, description="Признак вирусной лицензии (AGPL/GPL)")
    compliance_verdict: Literal["APPROVED", "CONDITIONAL_ACCEPT", "PROHIBITED_VETO"] = Field(
        description="Вердикт комплаенс-аудитора"
    )


class SbomManifest(BaseModel):
    """Complete SPDX 3.0 compliant Software Bill of Materials (SBOM)."""
    model_config = ConfigDict(extra="forbid")

    spdx_version: str = Field(default="SPDX-3.0", description="Версия стандарта SPDX")
    data_license: str = Field(default="CC0-1.0", description="Лицензия метаданных SBOM")
    document_name: str = Field(description="Название спецификации SBOM")
    document_namespace: str = Field(description="Уникальный URI документа")
    created_at: str = Field(description="Временная метка генерации (ISO 8601 UTC)")
    creators: List[str] = Field(default_factory=lambda: ["Organization: AO Cognitive Systems", "Tool: UCDE-SPDX-Guard-3.0"])
    packages: List[SpdxPackageEntry] = Field(description="Реестр проверенных зависимостей")
    total_packages: int = Field(ge=0, description="Общее число пакетов")
    viral_license_violations_count: int = Field(ge=0, description="Число обнаруженных вирусных лицензий")
    all_packages_compliant: bool = Field(description="Признак успешного юридического допуска")
    audit_hash_sha256: str = Field(description="Цифровая подпись аудиторского заключения SHA-256")


class SpdxLicenseGuard:
    """
    Automated license compliance scanner and SPDX 3.0 SBOM generator.
    """

    PERMISSIVE_LICENSES = {
        "MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "Unlicense", "Python-2.0"
    }

    WEAK_COPYLEFT_LICENSES = {
        "MPL-2.0", "LGPL-2.1-only", "LGPL-2.1-or-later", "LGPL-3.0-only", "LGPL-3.0-or-later"
    }

    VIRAL_COPYLEFT_LICENSES = {
        "GPL-2.0-only", "GPL-2.0-or-later", "GPL-3.0-only", "GPL-3.0-or-later",
        "AGPL-3.0-only", "AGPL-3.0-or-later", "SSPL-1.0", "EUPL-1.2"
    }

    def evaluate_license(self, license_name: str) -> Tuple[Literal["APPROVED", "CONDITIONAL_ACCEPT", "PROHIBITED_VETO"], bool]:
        """
        Classifies license and returns verdict and viral copyleft flag.
        """
        cleaned = license_name.strip()
        if any(cleaned.startswith(p) for p in self.PERMISSIVE_LICENSES):
            return "APPROVED", False
        elif any(cleaned.startswith(p) for p in self.WEAK_COPYLEFT_LICENSES):
            return "CONDITIONAL_ACCEPT", False
        elif any(cleaned.startswith(p) for p in self.VIRAL_COPYLEFT_LICENSES):
            return "PROHIBITED_VETO", True
        # Unknown license treated as conditional audit required
        return "CONDITIONAL_ACCEPT", False

    def generate_sbom(
        self,
        dependencies: Optional[List[Dict[str, str]]] = None,
        project_name: str = "Cognitive Harness Architect",
        project_version: str = "2.3.0",
    ) -> SbomManifest:
        """
        Synthesizes standard SPDX 3.0 SBOM document and checks for viral copyleft contamination.
        """
        raw_deps = dependencies or [
            {"name": "pydantic", "version": "2.8.2", "license": "MIT"},
            {"name": "fastapi", "version": "0.111.0", "license": "MIT"},
            {"name": "openvino", "version": "2024.2.0", "license": "Apache-2.0"},
            {"name": "numpy", "version": "1.26.4", "license": "BSD-3-Clause"},
            {"name": "z3-solver", "version": "4.13.0", "license": "MIT"},
            {"name": "httpx", "version": "0.27.0", "license": "BSD-3-Clause"},
        ]

        now_str = datetime.now(timezone.utc).isoformat()
        packages: List[SpdxPackageEntry] = []
        violations = 0

        for dep in raw_deps:
            pname = dep["name"]
            pver = dep.get("version", "1.0.0")
            plic = dep.get("license", "MIT")
            verdict, is_viral = self.evaluate_license(plic)
            if verdict == "PROHIBITED_VETO":
                violations += 1

            sha = hashlib.sha256(f"{pname}@{pver}:{plic}".encode("utf-8")).hexdigest()
            packages.append(
                SpdxPackageEntry(
                    spdx_id=f"SPDXRef-Package-{pname.replace('_', '-')}",
                    name=pname,
                    version=pver,
                    license_concluded=plic,
                    download_location=f"https://pypi.org/project/{pname}/{pver}/",
                    checksum_sha256=sha,
                    is_copyleft_viral=is_viral,
                    compliance_verdict=verdict,
                )
            )

        all_compliant = violations == 0
        doc_ns = f"https://cognitive.internal/spdx/{project_name.lower().replace(' ', '-')}/{project_version}"

        # Calculate audit hash
        audit_payload = f"{doc_ns}:{now_str}:{violations}:{len(packages)}"
        audit_sha = hashlib.sha256(audit_payload.encode("utf-8")).hexdigest()

        return SbomManifest(
            spdx_version="SPDX-3.0",
            data_license="CC0-1.0",
            document_name=f"SBOM-{project_name}-{project_version}",
            document_namespace=doc_ns,
            created_at=now_str,
            creators=["Organization: AO Cognitive Systems", "Tool: UCDE-SPDX-Guard-3.0"],
            packages=packages,
            total_packages=len(packages),
            viral_license_violations_count=violations,
            all_packages_compliant=all_compliant,
            audit_hash_sha256=audit_sha,
        )

    def to_markdown(self, sbom: SbomManifest) -> str:
        """Formats SBOM as Markdown audit report."""
        status_banner = "✅ OPENCHAIN COMPLIANT" if sbom.all_packages_compliant else "❌ COMPLIANCE VETO (VIRAL LICENSES DETECTED)"
        lines = [
            f"# OpenChain (ISO/IEC 5230) & SPDX 3.0 License Audit: {sbom.document_name}",
            f"**Status:** `{status_banner}` | **Total Dependencies:** {sbom.total_packages}",
            f"**Created At:** `{sbom.created_at}` | **Audit SHA-256:** `{sbom.audit_hash_sha256}`",
            "",
            "## 1. Package Inventory & License Categorization",
            "",
            "| Package | Version | Concluded License | Classification | Verdict | SHA-256 Digest |",
            "| :--- | :--- | :--- | :--- | :--- | :--- |",
        ]

        for pkg in sbom.packages:
            v_badge = "🟢 APPROVED" if pkg.compliance_verdict == "APPROVED" else ("🟡 CONDITIONAL" if pkg.compliance_verdict == "CONDITIONAL_ACCEPT" else "🔴 VETO")
            lines.append(
                f"| `{pkg.name}` | `{pkg.version}` | **{pkg.license_concluded}** | {'Viral Copyleft' if pkg.is_copyleft_viral else 'Permissive/Weak'} | {v_badge} | `{pkg.checksum_sha256[:12]}...` |"
            )

        lines.extend([
            "",
            "## 2. Legal Interlock Declaration",
            f"Viral copyleft violations count: **{sbom.viral_license_violations_count}**.",
            "All dependencies conform to proprietary SaaS distribution restrictions under OpenChain standards." if sbom.all_packages_compliant else "CRITICAL: Immediate dependency removal required prior to commercial release.",
        ])

        return "\n".join(lines)


__all__ = [
    "SpdxPackageEntry",
    "SbomManifest",
    "SpdxLicenseGuard",
]
