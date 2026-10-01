"""
Project Vector Decomposer
Breaks down multifaceted, ambiguous project briefs into granular, narrow technical vectors.
Identifies required harnesses, runtime stacks, and missing specialized skills.
"""

from typing import List, Dict, Any
from pathlib import Path
import re
from core.npu_engine import IntelNpuDecisionEngine
from config import GLOBAL_SKILLS_DIR


class ProjectVectorDecomposer:
    """
    Universal Hierarchical Vector Decomposer
    Implements the 7 Orthogonal Ministries x 4 Sub-specialists (28 Specialist Nodes) topology.
    Uses Intel AI Boost NPU System 1 primitives for non-autoregressive contract verification.
    """
    def __init__(self, npu_engine: IntelNpuDecisionEngine = None):
        self.npu = npu_engine or IntelNpuDecisionEngine()
        self.installed_skills = self._scan_installed_skills()
        self.ministries_registry = self._init_ministries_registry()

    def _init_ministries_registry(self) -> Dict[str, Dict[str, Any]]:
        return {
            "MINISTRY_1_STRATEGY_CJM": {
                "name": "Дирекция стратегии, маркетинга и CJM",
                "contract_out": "PRD_Specification.json",
                "stage_gate": "Gate 1: Business Value & Step Invariant",
                "specialists": [
                    {"id": "1.1", "role": "User Persona & JTBD Analyst", "focus": "Выявление глубинных потребностей целевой аудитории и сегментация."},
                    {"id": "1.2", "role": "Conversion Funnel & CJM Architect", "focus": "Пошаговый пользовательский путь с точками оттока и конверсиями."},
                    {"id": "1.3", "role": "Value Proposition Evaluator", "focus": "Формулирование ключевого ценностного предложения и дифференциации."},
                    {"id": "1.4", "role": "Feature Prioritization & Scope Guard", "focus": "RICE-скоринг и безжалостное отсечение скоупа MVP."}
                ]
            },
            "MINISTRY_2_FINANCE": {
                "name": "Департамент финансов и юнит-экономики",
                "contract_out": "Unit_Economics_Budget.json",
                "stage_gate": "Gate 2: LTV/CAC >= 3.0 & Infra OPEX Cap",
                "specialists": [
                    {"id": "2.1", "role": "CAC/LTV & Unit-Economics Modeler", "focus": "Маржинальность одной транзакции и период окупаемости."},
                    {"id": "2.2", "role": "Cloud & Serverless Infra Cost Estimator", "focus": "Прогноз расходов на серверы, egress-трафик, базы и NPU."},
                    {"id": "2.3", "role": "Payment Gateway Fee & P&L Auditor", "focus": "Комиссии эквайринга, возвраты (chargeback) и налогообложение."},
                    {"id": "2.4", "role": "Break-Even & Cash Flow Forecaster", "focus": "Точка безубыточности и защита от кассовых разрывов."}
                ]
            },
            "MINISTRY_3_LEGAL_COMPLIANCE": {
                "name": "Юридический отдел и регуляторный комплаенс",
                "contract_out": "Compliance_Attestation.json",
                "stage_gate": "Gate 3: Data Sovereignty & License Immunity",
                "specialists": [
                    {"id": "3.1", "role": "Personal Data (152-ФЗ / GDPR) Officer", "focus": "Локализация баз, согласия на обработку, право на забвение."},
                    {"id": "3.2", "role": "Financial Regulations & KYC/AML Auditor", "focus": "Соответствие платежному законодательству и антиотмывочным нормам."},
                    {"id": "3.3", "role": "Licensing & Third-party Terms Inspector", "focus": "Аудит открытых лицензий (GPL/MIT/Apache) и рисков патентных исков."},
                    {"id": "3.4", "role": "Consumer Rights & Terms of Service Formalizer", "focus": "Публичная оферта, политика конфиденциальности и SLA."}
                ]
            },
            "MINISTRY_4_INFOSEC": {
                "name": "Департамент информационной безопасности и угроз",
                "contract_out": "Security_Policy.agentpolicy",
                "stage_gate": "Gate 4: Zero Trust & Zero Unauthenticated Endpoints",
                "specialists": [
                    {"id": "4.1", "role": "Threat Modeler (STRIDE / Attack Trees)", "focus": "Моделирование векторов атак и поверхностей проникновения."},
                    {"id": "4.2", "role": "Auth, RBAC & Token Lifecycle Engineer", "focus": "Криптографическая авторизация, ротации ключей, OAuth/JWT."},
                    {"id": "4.3", "role": "Anti-Fraud & Rate-Limiting Policy Designer", "focus": "Защита от DDoS, парсинга, спама и атак методом перебора."},
                    {"id": "4.4", "role": "Data Encryption & Secret Zero-Trust Officer", "focus": "Шифрование at-rest и in-transit, управление секретами в Vault."}
                ]
            },
            "MINISTRY_5_SYSTEM_ARCHITECTURE": {
                "name": "Департамент системного анализа и архитектуры",
                "contract_out": "System_Contracts.json",
                "stage_gate": "Gate 5: OpenAPI 3.1 Strict Typing & Zero Cyclic Graph",
                "specialists": [
                    {"id": "5.1", "role": "Database Schema & Normalization Specialist", "focus": "Проектирование схемы данных, индексы, минимизация блокировок."},
                    {"id": "5.2", "role": "API Contract & Protocol Designer", "focus": "OpenAPI 3.1, gRPC-протоколы, идемпотентность эндпоинтов."},
                    {"id": "5.3", "role": "Event-Driven & Async Message Queue Architect", "focus": "Асинхронные очереди (Kafka/RabbitMQ/Redis Streams) и Outbox."},
                    {"id": "5.4", "role": "Domain State Machine & Invariant Formalizer", "focus": "Машины состояний, исключающие недопустимые переходы заказов."}
                ]
            },
            "MINISTRY_6_HARDWARE_RUNTIME": {
                "name": "Департамент аппаратной оптимизации и рантайма",
                "contract_out": "Hardware_Runtime_Manifest.json",
                "stage_gate": "Gate 6: RAM Budget <= 16GB & NPU Latency <= 50ms",
                "specialists": [
                    {"id": "6.1", "role": "Memory Footprint & Leaks Auditor", "focus": "Профилирование RAM, предотвращение утечек, лимит 550 МБ NPU."},
                    {"id": "6.2", "role": "Intel AI Boost NPU Offloader", "focus": "Квантование INT8, компиляция графов в OpenVINO для VPU 3720."},
                    {"id": "6.3", "role": "Concurrency, Thread Pool & Asyncio Profiler", "focus": "Оптимизация параллелизма под 14 ядер / 18 потоков Core Ultra 5."},
                    {"id": "6.4", "role": "Cold-Start & Latency Minimizer", "focus": "Устранение пауз инициализации и ускорение прогрева кэша."}
                ]
            },
            "MINISTRY_7_VV_QUALITY_GATE": {
                "name": "Департамент контроля качества, V&V и сертификации",
                "contract_out": "Release_Certified_Artifacts.json",
                "stage_gate": "Gate 7: Mutation Score >= 0.95 & Brier Score <= 0.04",
                "specialists": [
                    {"id": "7.1", "role": "Mutation Testing & Test Suite Auditor", "focus": "Убийца фиктивных assert True: внедрение мутаций в код тестов."},
                    {"id": "7.2", "role": "End-to-End Acceptance Scenario Synthesizer", "focus": "Сквозные BDD-сценарии от лица пользователя и интеграторов."},
                    {"id": "7.3", "role": "Brier Calibration & Conformal Prediction Verifier", "focus": "Математическая калибровка доверительных интервалов NPU."},
                    {"id": "7.4", "role": "Simplex Fail-Safe & Deployment Release Gatekeeper", "focus": "Аварийный контур остановки и выдача цифровой подписи релиза."}
                ]
            }
        }

    def _scan_installed_skills(self) -> Dict[str, str]:
        """Scans local global and workspace skills to identify pre-existing capabilities."""
        skills = {}
        if GLOBAL_SKILLS_DIR.exists():
            for skill_dir in GLOBAL_SKILLS_DIR.iterdir():
                if skill_dir.is_dir():
                    skill_md = skill_dir / "SKILL.md"
                    if skill_md.exists():
                        try:
                            content = skill_md.read_text(encoding="utf-8")
                            desc_match = re.search(r"description:\s*(.+)", content)
                            desc = desc_match.group(1).strip() if desc_match else "Custom skill"
                            skills[skill_dir.name] = desc
                        except Exception:
                            skills[skill_dir.name] = "Installed skill"
        return skills

    def decompose(self, project_brief: str) -> Dict[str, Any]:
        """
        Decomposes the project across the 7 Orthogonal Ministries and their 28 specialists.
        Evaluates risk profiles and stage-gate readiness on physical Intel AI Boost NPU.
        """
        decomposition_report = []
        total_specialists = 0

        for ministry_key, ministry_data in self.ministries_registry.items():
            specialist_tasks = []
            for spec in ministry_data["specialists"]:
                total_specialists += 1
                # NPU System 1 evaluation of risk & necessity for this specialist
                npu_audit = self.npu.score(
                    f"{project_brief} :: {spec['role']}",
                    f"Significance score of {spec['focus']} for project success"
                )
                specialist_tasks.append({
                    "id": spec["id"],
                    "role": spec["role"],
                    "focus": spec["focus"],
                    "npu_priority_rating": npu_audit["rating"],
                    "device": npu_audit["device"],
                    "latency_ms": npu_audit["latency_ms"]
                })

            # Check stage-gate readiness
            gate_check = self.npu.noul(
                project_brief,
                f"Does the project definition have enough information to pass {ministry_data['stage_gate']}?"
            )

            decomposition_report.append({
                "ministry_key": ministry_key,
                "ministry_name": ministry_data["name"],
                "contract_out": ministry_data["contract_out"],
                "stage_gate": ministry_data["stage_gate"],
                "gate_ready_preliminary": gate_check["value"],
                "gate_confidence": gate_check["probability"],
                "specialists": specialist_tasks
            })

        # Calculate architectural technical vectors
        pb_lower = project_brief.lower()
        vectors = []

        # Vector 1: Cloud & Edge Runtime
        candidates_edge = [
            "Cloudflare Workers & D1 (Wrangler v3, Edge V8 isolate, 0ms cold start)",
            "Fastify Node.js (High-throughput HTTP server, native TypeScript)",
            "Supabase Edge Functions (Deno runtime, PostgreSQL integration)",
            "Vercel Serverless (Next.js server actions, Node runtime)"
        ]
        choice_edge = self.npu.choice(project_brief, candidates_edge)
        vectors.append({
            "category": "Cloud & Edge Infrastructure",
            "recommended_tech": choice_edge["choice"],
            "confidence": choice_edge["confidence"],
            "required_skill": "cloudflare-workers" if "Cloudflare" in choice_edge["choice"] else "fastify-backend",
            "rationale": "Zero cold start, edge isolation, native SQL bindings."
        })

        # Vector 2: VCS & CI/CD
        candidates_ci = [
            "GitHub Actions & gh CLI (Automated pipelines, secrets, status checks)",
            "GitLab CI/CD (Pipeline Yaml, runner fleet)",
            "Local Git Hooks (Husky, lint-staged, pre-commit)"
        ]
        choice_ci = self.npu.choice(project_brief, candidates_ci)
        vectors.append({
            "category": "VCS & CI/CD Automation",
            "recommended_tech": choice_ci["choice"],
            "confidence": choice_ci["confidence"],
            "required_skill": "github-actions-automation",
            "rationale": "Automated regression testing, multi-OS builds, automated release drafts."
        })

        # Vector 3: Local Hardware Acceleration
        candidates_hw = [
            "Intel OpenVINO NPU Native (Intel AI Boost, zero-GPU battery friendly)",
            "DirectML (Windows DirectX 12 hardware acceleration)",
            "ONNX Runtime CPU (Deterministic CPU inference fallback)"
        ]
        choice_hw = self.npu.choice(project_brief, candidates_hw)
        vectors.append({
            "category": "Local Hardware & AI Coprocessor",
            "recommended_tech": choice_hw["choice"],
            "confidence": choice_hw["confidence"],
            "required_skill": "intel-npu-coprocessor",
            "rationale": "Runs sub-millisecond System 1 primitives on Meteor Lake NPU with 0.0W idle power."
        })

        # Vector 4: Testing & V&V
        candidates_test = [
            "Vitest (Ultra-fast ESM runner with native TypeScript and mocking)",
            "Node.js Native Test Runner (node:test, zero-dependency, built-in)",
            "Playwright (End-to-end browser automation & UI regression)"
        ]
        choice_test = self.npu.choice(project_brief, candidates_test)
        vectors.append({
            "category": "Testing Harness & V&V Certification",
            "recommended_tech": choice_test["choice"],
            "confidence": choice_test["confidence"],
            "required_skill": "vitest-esm-harness",
            "rationale": "High-velocity test execution, mutation testing support, zero transpilation lag."
        })

        # Skills Audit
        skills_audit = []
        for vec in vectors:
            skill_name = vec["required_skill"]
            is_installed = skill_name in self.installed_skills
            skills_audit.append({
                "skill_name": skill_name,
                "category": vec["category"],
                "is_installed": is_installed,
                "action": "USE_EXISTING" if is_installed else "SYNTHESIZE_FROM_OFFICIAL_DOCS"
            })

        return {
            "project_brief": project_brief,
            "total_ministries": len(self.ministries_registry),
            "total_specialists": total_specialists,
            "hierarchy": decomposition_report,
            "vectors": vectors,
            "skills_audit": skills_audit,
            "missing_skills_count": sum(1 for s in skills_audit if not s["is_installed"]),
            "npu_telemetry": {
                "device": self.npu.device_name,
                "npu_active": self.npu.npu_active,
                "model": "Laya-421M / ModernBERT Intel AI Boost"
            }
        }
