# Universal Cognitive Task Decomposition Engine & Harness (UCDE)
### Dual-Agent Heterogeneous Cognitive Architecture: Cloud Reasoning (Gemini 3.1 Pro) + Local Physical NPU (Intel AI Boost VPU 3720)

---

## 1. Executive Summary & Purpose

**Universal Cognitive Task Decomposition Engine (UCDE)** — это программно-аппаратный комплекс нового поколения, предназначенный для **автономной многоуровневой декомпозиции и системного анализа любых сложных задач** (разработка enterprise-софта, финтех-платформ, автономной робототехники, распределенных сетей) в строгие, математически верифицированные спецификации до написания первой строчки целевого программного кода.

Система устраняет «детские болезни» чисто генеративных нейросетей (галлюцинации, сикофантический консенсус, размытие контекста, обман тестов `assert True`) за счет **строгого разделения обязанностей**:
- **System 2 (Генератор гипотез / Медленное мышление)**: Облачная reasoning-модель **Google Gemini 3.1 Pro** — креативный поиск вариантов, синтез архитектурных паттернов, мутации и кроссовер.
- **System 1 (Тензорный арбитр / Быстрое мышление)**: Локальный физический нейропроцессор **Intel AI Boost NPU (Meteor Lake VPU 3720)**, исполняющий неавторегрессионные модели (Laya-421M / ModernBERT / Jev-примитивы) через OpenVINO 2026.0 с субмиллисекундным откликом (0.7–22 мс) при энергопотреблении всего 1.5–2.5 Вт.

---

## 2. Научный Базис и Теоретические Основы

Архитектура UCDE опирается на строгие математические и физические законы:

1. **Принцип минимальной длины описания Риссанена (MDL)**:  
   $$\min_{M \in \mathcal{M}} \left[ L(M) + \sum_{v \in V} L(X_v \mid \text{Pa}(v)) \right]$$  
   Фиксация топологии из 7 ортогональных макро-нод гарантирует минимизацию длины описания связей $\mathcal{O}(|V|)$, предотвращая как «микросервисный взрыв» комбинаторных связей ($\mathcal{O}(|V|^2)$), так и потерю контекста в «монолитном коме».
2. **Конечная размерность Вапника-Червоненкиса ($d_{\text{VC}}$) и PAC-обучение**:  
   Неавторегрессионный NPU-арбитр оценивает конечное подпространство гипотез $|\mathcal{H}| = K$, гарантируя экспоненциальную сходимость калибровки доверительных интервалов по неравенству Хоффдинга (Brier Score $< 0.04$).
3. **Теорема Эрроу и защита от сикофантии (Arrow & Gibbard-Satterthwaite)**:  
   Отказ от многоагентного голосования однородных LLM. Замена на **лексикографический Парето-отбор (L-MOPA)**:
   $$\text{Safety} \succ \text{Legal} \succ \text{Contracts/Types} \succ \text{Performance} \succ \text{Cost}$$
4. **Принцип Ландауэра и термодинамика вычислений ($\Delta Q \ge k_B T \ln 2$)**:  
   Устранение энергозатратных рекурсивных авторегрессионных диалогов самопроверки за счет однопроходного тензорного прямого хода (Single-Pass Feedforward) на бортовом кремнии NPU.
5. **Теорема Райса и проекция на разрешимые пространства**:  
   Семантическая верификация через строгие компиляторы схем (Pydantic v2, OpenAPI 3.1) и SMT-солверы инвариантов.

---

## 3. Иерархическая Топология: 7 Министерств $\times$ 4 Специалиста (28 Нод)

```
[MINISTRY_1_STRATEGY_CJM]         -> PRD_Specification.json
   ├── 1.1. User Persona & JTBD Analyst
   ├── 1.2. Conversion Funnel & CJM Architect
   ├── 1.3. Value Proposition Evaluator
   └── 1.4. Feature Prioritization & Scope Guard

[MINISTRY_2_FINANCE]              -> Unit_Economics_Budget.json
   ├── 2.1. CAC/LTV & Unit-Economics Modeler
   ├── 2.2. Cloud & Serverless Infra Cost Estimator
   ├── 2.3. Payment Gateway Fee & P&L Auditor
   └── 2.4. Break-Even & Cash Flow Forecaster

[MINISTRY_3_LEGAL_COMPLIANCE]     -> Compliance_Attestation.json
   ├── 3.1. Personal Data (152-ФЗ / GDPR) Officer
   ├── 3.2. Financial Regulations & KYC/AML Auditor
   ├── 3.3. Licensing & Third-party Terms Inspector
   └── 3.4. Consumer Rights & Terms of Service Formalizer

[MINISTRY_4_INFOSEC]              -> Security_Policy.agentpolicy
   ├── 4.1. Threat Modeler (STRIDE / Attack Trees)
   ├── 4.2. Auth, RBAC & Token Lifecycle Engineer
   ├── 4.3. Anti-Fraud & Rate-Limiting Policy Designer
   └── 4.4. Data Encryption & Secret Zero-Trust Officer

[MINISTRY_5_SYSTEM_ARCHITECTURE]  -> System_Contracts.json / openapi.yaml
   ├── 5.1. Database Schema & Normalization Specialist
   ├── 5.2. API Contract & Protocol Designer
   ├── 5.3. Event-Driven & Async Message Queue Architect
   └── 5.4. Domain State Machine & Invariant Formalizer

[MINISTRY_6_HARDWARE_RUNTIME]     -> Hardware_Runtime_Manifest.json
   ├── 6.1. Memory Footprint & Leaks Auditor (Лимит 16GB RAM)
   ├── 6.2. Intel AI Boost NPU Offloader (OpenVINO INT8)
   ├── 6.3. Concurrency, Thread Pool & Asyncio Profiler
   └── 6.4. Cold-Start & Latency Minimizer

[MINISTRY_7_VV_QUALITY_GATE]      -> Release_Certified_Artifacts.json
   ├── 7.1. Mutation Testing & Test Suite Auditor (Защита от assert True)
   ├── 7.2. End-to-End Acceptance Scenario Synthesizer
   ├── 7.3. Brier Calibration & Conformal Prediction Verifier
   └── 7.4. Simplex Fail-Safe & Deployment Release Gatekeeper
```

---

## 4. Конкурентный Ландшафт: Что делают гиганты и в чем наша разница

| Игрок / Технология | Что они создали | В чем их ограничение | Наше архитектурное отличие |
| :--- | :--- | :--- | :--- |
| **TypeSafe AI (Jev)**<br/>*Диого Алмейда (ex-OpenAI)* | System 1 неавторегрессионная модель (70–200 мс, \$0.042/1M токенов). | Это «голый кирпич» (API функции `is_valid`), не знающий бизнес-логики и права. | Мы используем этот класс примитивов как мотор внутри 7-ведомственного конвейера декомпозиции. |
| **Figure AI (Helix)**<br/>*Гуманоид Figure 02* | Дуальная архитектура для автономного тела: VLA System 2 + Action Policy 50Hz. | Заточена под сервоприводы и физический мир заводов BMW. | Мы применили доказанный кибернетический дуализм роботов к миру проектирования комплексного ПО. |
| **Physical Intelligence (pi)**<br/>*Модель $\pi_0$* | 3B PaliGemma VLM + 300M Action Expert на Flow Matching. | Физические манипуляторы, складские и домашние роботы. | Мы используем Gemini 3.1 Pro + 421M Laya/BERT на локальном NPU для символической декомпозиции. |
| **OpenAI (PRM / o1)** | Process Reward Models для математических рассуждений. | Облачные монолитные LLM с высокой стоимостью и задержкой. | Гибридный контур: тяжелый поиск в облаке, дешевое судейство на кристалле NPU ноутбука. |
| **NVIDIA (NeMo Guardrails)** | Colang-прослойка для фильтрации токсичности и джейлбрейков. | Файрвол для чат-ботов, не занимающийся архитектурой. | Полный цикл системного проектирования (CJM $\to$ Деньги $\to$ Право $\to$ Схемы $\to$ NPU). |
| **MetaGPT / Devin** | Агенты в терминале, сразу пишущие код на Python/JS. | Галлюцинации, сикофантия, пропуск юристов и финансов, фейк-тесты. | Строгий мораторий на кодинг до 100% верификации 7 Stage-Gates. |

---

## 5. Запуск и Эксплуатация Системы

### Требования к оборудованию:
- **Процессор**: Intel Core Ultra 5 125H (Meteor Lake) или аналогичный с поддержкой NPU.
- **Нейропроцессор**: Intel AI Boost (VPU 3720).
- **Память**: 16 ГБ RAM (модель NPU занимает $<450$ МБ в INT8).
- **Среда**: Python 3.11+, OpenVINO 2026.0.

### Команды CLI:
```bash
# 1. Анализ и декомпозиция любой задачи через 28 специалистов и NPU:
python cli.py analyze "Universal Autonomous Robotics & SMM Cognitive Platform with Intel NPU"

# 2. Дарвиновский эволюционный поиск оптимальной архитектуры (GAS):
python cli.py evolve "High-load Fintech Payment Core" --population 1000 --generations 3

# 3. Синтез полного каркаса проекта с генерацией недостающих скиллов:
python cli.py scaffold --name "my-autonomous-project" --brief "..."
```

### Единый шлюз импорта в коде:
```python
from design_arbiter import arbitrate, validate_proposition, score_candidate, evolve

# Субмиллисекундный выбор System 1 на Intel AI Boost NPU:
decision = arbitrate(context="High-load API", candidates=["Fastify", "Django", "Flask"])

# Проверка логического инварианта с правом вето (noul):
is_safe = validate_proposition(context="Payment Pipeline", proposition="Can user bypass KYC?")
```
