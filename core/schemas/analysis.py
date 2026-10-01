"""
Ministry 5: System Analysis & Architecture Schema Contract
Artifact: System_Contracts.json
Stage-Gate: Gate 5: OpenAPI 3.1 Strict Typing & Zero Cyclic Graph
"""

from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ApiEndpoint(BaseModel):
    """Specification of an API REST Endpoint under OpenAPI 3.1."""
    model_config = ConfigDict(extra="forbid")

    path: str = Field(min_length=1, description="Путь URI эндпоинта")
    method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"] = Field(description="HTTP-метод")
    requires_auth: bool = Field(default=True, description="Требование аутентификации (Zero-Trust)")
    idempotent: bool = Field(description="Флаг идемпотентности операции")
    timeout_ms: int = Field(gt=0, le=5000, description="Максимальный таймаут ответа в миллисекундах <= 5000")


class RagPipelineConfig(BaseModel):
    """Configuration for AI-Native RAG (Retrieval-Augmented Generation) Pipeline."""
    model_config = ConfigDict(extra="forbid")

    embedding_model: str = Field(default="bge-m3", description="Модель генерации плотных векторных эмбеддингов")
    embedding_dimension: int = Field(default=1024, gt=0, le=4096, description="Размерность векторного пространства эмбеддингов")
    vector_index_type: Literal["HNSW", "IVFFLAT", "FLAT"] = Field(default="HNSW", description="Тип векторного индекса")
    similarity_metric: Literal["COSINE", "DOT_PRODUCT", "EUCLIDEAN"] = Field(default="COSINE", description="Метрика сходства векторов")
    chunk_size_tokens: int = Field(default=512, gt=0, le=2048, description="Размер чанка в токенах")
    chunk_overlap_tokens: int = Field(default=64, ge=0, le=256, description="Перекрытие между соседними чанками")
    hybrid_search_enabled: bool = Field(default=True, description="Гибридный поиск: BM25 + Dense Vectors с RRF")
    reranker_model: Optional[str] = Field(default="bge-reranker-large", description="Модель кросс-энкодера для реранкинга")


class MemoryArchitectureConfig(BaseModel):
    """4-Tier Cognitive Memory Architecture Configuration."""
    model_config = ConfigDict(extra="forbid")

    short_term_context_window_tokens: int = Field(default=32768, gt=0, description="Размер контекстного окна LLM")
    long_term_vector_memory_enabled: bool = Field(default=True, description="Векторная семантическая память")
    graph_rag_enabled: bool = Field(default=True, description="Ассоциативная память графа знаний (GraphRAG)")
    context_caching_strategy: Literal["EXPLICIT_PREFIX", "EPISODIC_LRU", "NONE"] = Field(
        default="EXPLICIT_PREFIX", description="Стратегия кэширования неизменяемого контекста"
    )


class ArchitectureDecisionRecord(BaseModel):
    """Architecture Decision Record (ADR) conforming to MADR 3.0 specification."""
    model_config = ConfigDict(extra="forbid")

    adr_id: str = Field(min_length=1, pattern=r"^ADR-\d+$", description="Идентификатор ADR, например ADR-001")
    title: str = Field(min_length=5, description="Краткое название архитектурного решения")
    status: Literal["PROPOSED", "ACCEPTED", "REJECTED", "DEPRECATED", "SUPERSEDED"] = Field(
        default="ACCEPTED", description="Статус архитектурного решения"
    )
    deciders: List[str] = Field(min_length=1, default_factory=lambda: ["Chief Architect", "System Analyst"], description="Лица, принимающие решение")
    context_and_problem_statement: str = Field(min_length=10, description="Контекст и постановка проблемы")
    decision_drivers: List[str] = Field(min_length=1, description="Ключевые архитектурные драйверы (требования)")
    considered_options: List[str] = Field(min_length=2, description="Минимум 2 рассмотренных архитектурных варианта")
    decision_outcome: str = Field(min_length=10, description="Выбранный вариант с обоснованием")
    positive_consequences: List[str] = Field(min_length=1, description="Позитивные последствия и преимущества")
    negative_consequences: List[str] = Field(min_length=1, description="Компромиссы, ограничения и плата за решение")
    compliance_verification: str = Field(default="Automated zero-trust stage gate linter", description="Механизм верификации соблюдения")


class AsyncMessageTopic(BaseModel):
    """AsyncAPI 3.0 Message Topic Specification with CloudEvents 1.0 support."""
    model_config = ConfigDict(extra="forbid")

    topic_name: str = Field(min_length=1, pattern=r"^[a-zA-Z0-9_\-\.]+$", description="Имя топика сообщений брокера")
    event_type: str = Field(min_length=1, description="Тип события по CloudEvents 1.0, например com.cognitive.artifact.committed")
    schema_format: Literal["AVRO", "JSON_SCHEMA", "PROTOBUF"] = Field(default="JSON_SCHEMA", description="Формат схемы полезной нагрузки")
    retention_hours: int = Field(default=24, gt=0, description="Период удержания сообщений в топике в часах")


class SelfRagConfig(BaseModel):
    """Self-RAG (Self-Reflective Retrieval-Augmented Generation) Architecture Configuration."""
    model_config = ConfigDict(extra="forbid")

    retrieve_reflection_token: bool = Field(default=True, description="Флаг активации токена рефлексии потребности извлечения [Retrieve]")
    is_rel_reflection_token: bool = Field(default=True, description="Флаг активации токена оценки релевантности фрагмента [IsRel]")
    is_sup_reflection_token: bool = Field(default=True, description="Флаг активации токена обоснованности ответа источником [IsSup]")
    is_use_reflection_token: bool = Field(default=True, description="Флаг активации токена полезности и полноты ответа [IsUse]")
    critique_threshold: float = Field(default=0.85, ge=0.5, le=1.0, description="Порог самокритики для фиксации ответа >= 0.85")


class SystemAnalysisContract(BaseModel):
    """Contract for Ministry 5 (System Analysis & Architecture)."""
    model_config = ConfigDict(extra="forbid")

    architecture_pattern: Literal["EVENT_DRIVEN_MICROSERVICES", "MODULAR_MONOLITH", "SERVERLESS_ISOLATES"] = Field(
        description="Архитектурный шаблон системы"
    )
    openapi_version: str = Field(default="3.1.0", description="Версия спецификации OpenAPI 3.1.0")
    endpoints: List[ApiEndpoint] = Field(min_length=1, description="Спецификация API-эндпоинтов")
    async_message_bus: Optional[Literal["KAFKA", "RABBITMQ", "REDIS_STREAMS", "NATS"]] = Field(
        default=None, description="Брокер асинхронных сообщений"
    )
    asyncapi_version: str = Field(default="3.0.0", description="Версия спецификации AsyncAPI 3.0.0")
    async_topics: List[AsyncMessageTopic] = Field(
        default_factory=list, description="Реестр топиков асинхронных сообщений AsyncAPI 3.0"
    )
    database_normalization: Literal["3NF", "BCNF", "DENORMALIZED_READ_REPLICAS"] = Field(
        default="3NF", description="Степень нормализации базы данных"
    )
    cyclic_dependencies_detected: bool = Field(
        default=False, description="Признак наличия циклических зависимостей"
    )
    error_response_standard: Literal["RFC_7807", "RFC_9457"] = Field(
        default="RFC_7807", description="Стандарт форматирования ошибок API (RFC 7807 Problem Details for HTTP APIs)"
    )
    c4_model_level: Literal["CONTEXT", "CONTAINER", "COMPONENT", "CODE"] = Field(
        default="COMPONENT", description="Уровень архитектурной детализации модели C4"
    )
    iso_42010_viewpoints_defined: bool = Field(
        default=True, description="Определение архитектурных представлений по стандарту ISO/IEC/IEEE 42010"
    )
    rag_pipeline: RagPipelineConfig = Field(
        default_factory=RagPipelineConfig, description="Спецификация RAG-пайплайна и векторной памяти"
    )
    self_rag: SelfRagConfig = Field(
        default_factory=SelfRagConfig, description="Конфигурация Self-RAG адаптивного извлечения и самокритики"
    )
    memory_architecture: MemoryArchitectureConfig = Field(
        default_factory=MemoryArchitectureConfig, description="4-уровневая архитектура когнитивной памяти"
    )
    architecture_decision_records: List[ArchitectureDecisionRecord] = Field(
        default_factory=list, description="Реестр архитектурных решений ADR по стандарту MADR 3.0"
    )

    @field_validator("cyclic_dependencies_detected")
    @classmethod
    def assert_no_cycles(cls, v: bool) -> bool:
        """Architectural veto if cyclic dependencies are detected in subsystem interaction graph."""
        if v:
            raise ValueError("Architecture Veto: Cyclic dependencies found in subsystem interaction graph!")
        return v


__all__ = [
    "ApiEndpoint",
    "AsyncMessageTopic",
    "RagPipelineConfig",
    "SelfRagConfig",
    "MemoryArchitectureConfig",
    "ArchitectureDecisionRecord",
    "SystemAnalysisContract",
]
