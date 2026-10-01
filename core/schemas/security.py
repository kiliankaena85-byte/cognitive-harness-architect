"""
Ministry 4: Information Security & Threat Modeling Schema Contract
Artifact: Security_Policy.agentpolicy
Stage-Gate: Gate 4: Zero Trust & Zero Unauthenticated Endpoints
"""

import re
from typing import Any, Dict, List, Literal, Set
from pydantic import BaseModel, ConfigDict, Field, field_validator

REQUIRED_STRIDE_CATEGORIES: Set[str] = {
    "SPOOFING",
    "TAMPERING",
    "REPUDIATION",
    "INFO_DISCLOSURE",
    "DENIAL_OF_SERVICE",
    "ELEVATION_OF_PRIVILEGE",
}

# Банк данных угроз безопасности информации (БДУ) ФСТЭК России
DEFAULT_STRIDE_TO_UBI: dict[str, str] = {
    "SPOOFING": "УБИ.012",             # Угроза подмены субъекта доступа
    "TAMPERING": "УБИ.045",            # Угроза несанкционированной модификации информации
    "REPUDIATION": "УБИ.089",          # Угроза отказа от авторства или факта совершенных действий
    "INFO_DISCLOSURE": "УБИ.123",      # Угроза утечки/раскрытия конфиденциальной информации
    "DENIAL_OF_SERVICE": "УБИ.031",    # Угроза нарушения доступности (отказ в обслуживании)
    "ELEVATION_OF_PRIVILEGE": "УБИ.067"# Угроза несанкционированного повышения привилегий
}


class StrideThreat(BaseModel):
    """STRIDE Threat Model Component with FSTEC BDU Threat Database mapping."""
    model_config = ConfigDict(extra="forbid")

    category: Literal[
        "SPOOFING",
        "TAMPERING",
        "REPUDIATION",
        "INFO_DISCLOSURE",
        "DENIAL_OF_SERVICE",
        "ELEVATION_OF_PRIVILEGE",
    ] = Field(description="Категория угрозы STRIDE")
    target_component: str = Field(min_length=1, description="Целевой компонент системы")
    mitigation_strategy: str = Field(min_length=10, description="Конкретная стратегия нейтрализации угрозы")
    fstec_ubi_code: str = Field(
        default="",
        description="Идентификатор угрозы из Банка данных угроз ФСТЭК России (БДУ ФСТЭК), например УБИ.012"
    )

    def model_post_init(self, __context: Any) -> None:
        """Auto-populates fstec_ubi_code from DEFAULT_STRIDE_TO_UBI if left empty."""
        super().model_post_init(__context)
        if not self.fstec_ubi_code:
            self.fstec_ubi_code = DEFAULT_STRIDE_TO_UBI.get(self.category, "УБИ.001")
        elif not re.match(r"^УБИ\.\d{3}$", self.fstec_ubi_code):
            raise ValueError(f"Invalid FSTEC BDU code '{self.fstec_ubi_code}': must match '^УБИ\\.\\d{{3}}$'")


class OwaspLlmSecurityConfig(BaseModel):
    """OWASP Top 10 for LLM Applications and Cognitive Guardrails Configuration."""
    model_config = ConfigDict(extra="forbid")

    covered_llm_vulnerabilities: List[str] = Field(
        default_factory=lambda: [
            "LLM01_PROMPT_INJECTION",
            "LLM02_INSECURE_OUTPUT_HANDLING",
            "LLM04_MODEL_DENIAL_OF_SERVICE",
            "LLM06_SENSITIVE_INFO_DISCLOSURE",
            "LLM08_EXCESSIVE_AGENCY",
        ],
        description="Перечень нейтрализованных уязвимостей по каталогу OWASP Top 10 for LLM Applications"
    )
    prompt_quarantine_enforced: bool = Field(
        default=True, description="Изоляция пользовательского ввода через XML-карантин и дезинфекцию спецтокенов"
    )
    model_context_protocol_auth: Literal["BEARER_TOKEN", "MTLS", "LOCAL_SOCKET"] = Field(
        default="BEARER_TOKEN", description="Аутентификация вызовов инструментов по Model Context Protocol (MCP)"
    )



MITRE_ATLAS_TACTICS = Literal[
    "RECONNAISSANCE",
    "RESOURCE_DEVELOPMENT",
    "INITIAL_ACCESS",
    "ML_MODEL_ACCESS",
    "EXECUTION",
    "PERSISTENCE",
    "DEFENSE_EVASION",
    "CREDENTIAL_ACCESS",
    "DISCOVERY",
    "COLLECTION",
    "ML_ATTACK_STAGING",
    "EXFILTRATION",
    "IMPACT",
]


class MitreAtlasThreat(BaseModel):
    """Threat Model Component conforming to MITRE ATLAS (Adversarial Threat Landscape for AI Systems)."""
    model_config = ConfigDict(extra="forbid")

    tactic: MITRE_ATLAS_TACTICS = Field(description="Тактика матрицы MITRE ATLAS")
    technique_id: str = Field(
        pattern=r"^AML\.T\d{4}(\.\d{3})?$",
        description="Идентификатор техники MITRE ATLAS (например AML.T0043, AML.T0054)"
    )
    technique_name: str = Field(min_length=3, description="Название техники атаки на ИИ")
    mitigation: str = Field(min_length=10, description="Конкретная мера противодействия / нейтрализации")


class SecurityPolicyContract(BaseModel):
    """Contract for Ministry 4 (Information Security)."""
    model_config = ConfigDict(extra="forbid")

    zero_trust_enforced: bool = Field(default=True, description="Обязательная Zero-Trust архитектура")
    auth_mechanisms: List[Literal["JWT_ED25519", "MTLS", "OIDC_PKCE"]] = Field(
        min_length=1, description="Криптографически стойкие механизмы аутентификации"
    )
    stride_matrix: List[StrideThreat] = Field(
        min_length=6, description="Минимум по 1 угрозе на каждую из 6 категорий STRIDE"
    )
    mitre_atlas_matrix: List[MitreAtlasThreat] = Field(
        default_factory=list, description="Матрица угроз безопасности систем искусственного интеллекта по MITRE ATLAS"
    )
    rate_limiting_rps_per_ip: int = Field(gt=0, le=1000, description="Ограничение частоты запросов RPS на IP")
    data_encryption_at_rest: Literal["AES_256_GCM", "GOST_KUZNYECHIK"] = Field(
        default="AES_256_GCM", description="Алгоритм шифрования хранящихся данных"
    )
    data_encryption_in_transit: Literal["TLS_1_3"] = Field(
        default="TLS_1_3", description="Шифрование данных при передаче"
    )
    fstec_gost_56939_certified: bool = Field(
        default=True, description="Сертификация процессов разработки по ГОСТ Р 56939 (ФСТЭК)"
    )
    owasp_asvs_level: Literal["L1", "L2", "L3"] = Field(
        default="L2", description="Уровень соответствия OWASP ASVS 4.0 (Application Security Verification Standard)"
    )
    nist_800_207_zero_trust: bool = Field(
        default=True, description="Соответствие архитектуре NIST SP 800-207 Zero Trust"
    )
    iso_42001_security_controls_active: bool = Field(
        default=True, description="Активация контролей безопасности ИИ по стандарту ISO/IEC 42001:2023"
    )
    ai_security: OwaspLlmSecurityConfig = Field(
        default_factory=OwaspLlmSecurityConfig, description="Конфигурация безопасности ИИ и защиты от инъекций"
    )
    fstec_orders_classification: Dict[str, str] = Field(
        default_factory=lambda: {
            "order_17_gis": "К2",
            "order_21_ispdn": "УЗ-2",
            "order_239_kii": "КАТЕГОРИЯ_2",
        },
        description="Классификация мер защиты по Приказам ФСТЭК № 17, 21, 239"
    )

    @field_validator("stride_matrix")
    @classmethod
    def verify_all_stride_categories(cls, v: List[StrideThreat]) -> List[StrideThreat]:
        """Ensures at least 1 mitigation exists for EACH of the 6 STRIDE categories."""
        present_categories = {threat.category for threat in v}
        missing = REQUIRED_STRIDE_CATEGORIES - present_categories
        if missing:
            raise ValueError(f"Incomplete STRIDE matrix: missing categories {sorted(missing)}")
        return v


__all__ = [
    "StrideThreat",
    "MitreAtlasThreat",
    "OwaspLlmSecurityConfig",
    "SecurityPolicyContract",
    "REQUIRED_STRIDE_CATEGORIES",
    "DEFAULT_STRIDE_TO_UBI",
]
