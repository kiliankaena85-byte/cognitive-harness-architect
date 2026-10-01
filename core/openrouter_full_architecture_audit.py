import sys
import os
import json
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import List, Dict, Any

# Force UTF-8 stdout unbuffered
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
CONFIG_FILE = PROJECT_ROOT / "openrouter_config.json"

class OpenRouterAuditor:
    def __init__(self, config_path: Path = None):
        cfg_path = config_path or CONFIG_FILE
        with open(cfg_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)
        
        self.api_keys = self.config.get("api_keys", [])
        self.current_key_idx = 0

    def _get_active_key(self) -> str:
        return self.api_keys[self.current_key_idx % len(self.api_keys)]

    def _rotate_key(self):
        self.current_key_idx = (self.current_key_idx + 1) % len(self.api_keys)

    def query_model(self, model_name: str, system_prompt: str, user_prompt: str, timeout: int = 40) -> Dict[str, Any]:
        """Queries a model on OpenRouter with key rotation and error handling."""
        url = "https://openrouter.ai/api/v1/chat/completions"
        
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 1200
        }

        key = self._get_active_key()
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.config.get("site_url", "https://antigravity.internal"),
            "X-Title": self.config.get("site_name", "Cognitive Engine Audit")
        }

        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        t0 = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                latency_ms = round((time.perf_counter() - t0) * 1000, 2)
                content = data["choices"][0]["message"]["content"]
                return {
                    "model": model_name,
                    "success": True,
                    "content": content,
                    "latency_ms": latency_ms,
                    "key_used": key[:15] + "..."
                }
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8") if e.fp else str(e)
            if e.code in [429, 401, 403]:
                self._rotate_key()
            return {"model": model_name, "success": False, "error": f"HTTP {e.code}: {err_msg}"}
        except Exception as e:
            return {"model": model_name, "success": False, "error": str(e)}

    def run_full_architecture_audit(self):
        print("=" * 70)
        print("LAUNCHING FULL ARCHITECTURE MULTI-MODEL ADVERSARIAL AUDIT")
        print("=" * 70, flush=True)

        architecture_summary = """
Внимание, эксперты! На аудит передается архитектура Универсального Модуля Декомпозиции Задач.
Стэк:
1. Генеративный контур (System 2): LLM (Gemini 3.1 Pro) генерирует гипотезы ТЗ, кода, архитектуры.
2. 7 изолированных министерств-нод (DAG): 1) Стратегия/CJM, 2) Финансы/Юнит-экономика, 3) Право/Комплаенс, 4) Безопасность/ФСТЭК, 5) Системный анализ, 6) Hardware NPU, 7) QA & V&V.
3. Локальный тензорный фильтр (System 1): На локальном Intel AI Boost NPU (16GB RAM) работает неавторегрессионный энкодер (напр. ModernBERT), который отсеивает сгенерированные LLM артефакты, не проходящие "механический" барьер (Stage Gate).
4. Zero-Trust детерминированная обвязка: Все артефакты после LLM проходят через Python-скрипты `gost_verifier.py` (жесткий парсинг ГОСТ 34.602-89, отсутствие "fuzzy" слов, ISO 29148) и `cdd_tdd_engine.py` (Contract-Driven Development, проверка математических инвариантов по логике Хоара, генерация 1000+ синтетических кейсов Hypothesis PBT). Ни один пункт не принимается на веру LLM.
"""

        prompt_task1 = f"""
{architecture_summary}
ЗАДАЧА 1: Оценить целостность 7 министерств и Zero-Trust подхода. 
Выступая как строгий системный архитектор уровня Staff/Principal.
1. Насколько надежна предложенная концепция 7 изолированных нод + детерминированного CDD-TDD барьера в качестве защиты от галлюцинаций LLM?
2. Какие потенциальные bottleneck (узкие горлышки) вы видите при передаче контекста между 7 министерствами?
"""

        prompt_task2 = f"""
{architecture_summary}
ЗАДАЧА 2: Оценить интеграцию ГОСТов и детерминированных скриптов.
Выступая как строгий аудитор гос. стандартов (ГОСТ 34, ФСТЭК).
1. Использование python-скрипта (gost_verifier.py), который ищет качественные прилагательные ("высоконагруженный", "быстрый") и жестко требует их замены на SLA/RPS — это рабочий подход для автоматизации?
2. Какие еще проверки вы бы добавили в этот детерминированный барьер, чтобы исключить человеческий (и LLM) фактор при сертификации?
"""

        prompt_task3 = f"""
{architecture_summary}
ЗАДАЧА 3: Краш-тест (Red-Teaming).
Выступая как безжалостный тестировщик и Red-Teamer.
Найдите 3 самых неочевидных способа, как эта система может "сломаться" (зависнуть, выдать неверный результат, уйти в бесконечный цикл) на этапе генерации ТЗ, несмотря на NPU-оценщик и детерминированные барьеры. Предложите защиту.
"""

        audit_results = []
        
        # We will try several models since some might fail with 429/403.
        models_to_try = [
            "nvidia/nemotron-3-ultra-550b-a55b:free",
            "cohere/north-mini-code:free",
            "inception/mercury-decide:free",
            "nvidia/llama-nemotron-rerank-vl-1b-v2:free",
            "poolside/laguna-s-2.1:free"
        ]

        def try_models(prompt, role):
            for model in models_to_try:
                print(f"Querying: {model} ...", flush=True)
                res = self.query_model(model, role, prompt)
                if res["success"]:
                    return res
                else:
                    print(f"  -> Failed: {res.get('error')}. Retrying next model...", flush=True)
            return {"model": "None", "success": False, "error": "All models failed"}

        print("\n[Audit Vector 1] System Architecture & DAG Integrity...", flush=True)
        res_v1 = try_models(prompt_task1, "You are a Principal Systems Architect. Speak concisely but scientifically.")
        audit_results.append({"vector": "Architecture & DAG Integrity", "data": res_v1})
        print(f"  -> Result: Success={res_v1['success']} ({res_v1.get('latency_ms', 0)} ms)\n", flush=True)

        print("[Audit Vector 2] GOST Compliance & Python Deterministic Verification...", flush=True)
        res_v2 = try_models(prompt_task2, "You are a State Compliance Auditor for GOST and ISO. Speak strictly and formally.")
        audit_results.append({"vector": "GOST & Deterministic Verification", "data": res_v2})
        print(f"  -> Result: Success={res_v2['success']} ({res_v2.get('latency_ms', 0)} ms)\n", flush=True)

        print("[Audit Vector 3] Red-Teaming Stress Test...", flush=True)
        res_v3 = try_models(prompt_task3, "You are a ruthless Red Teamer looking for deadlocks and logical loopholes in AI pipelines.")
        audit_results.append({"vector": "Red-Teaming Crash Test", "data": res_v3})
        print(f"  -> Result: Success={res_v3['success']} ({res_v3.get('latency_ms', 0)} ms)\n", flush=True)

        report_file = PROJECT_ROOT / "FULL_ARCHITECTURE_AUDIT_REPORT.md"
        
        md_lines = [
            "# Отчет полного аудита архитектуры 7-уровневого Модуля Декомпозиции (OpenRouter)",
            f"**Дата:** {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}",
            "\n---\n"
        ]

        for item in audit_results:
            d = item["data"]
            md_lines.append(f"## {item['vector']}")
            md_lines.append(f"**Аудитор:** `{d.get('model')}` | **Время:** {d.get('latency_ms', 0)} мс")
            if d.get("success"):
                md_lines.append(f"\n### Вердикт:\n{d['content']}\n")
            else:
                md_lines.append(f"\n*Ошибка:* `{d.get('error')}`\n")
            md_lines.append("---\n")

        report_file.write_text("\n".join(md_lines), encoding="utf-8")
        print(f"\n[Audit Complete] Full report saved to: {report_file}", flush=True)

if __name__ == "__main__":
    auditor = OpenRouterAuditor()
    auditor.run_full_architecture_audit()
