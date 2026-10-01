"""
OpenRouter Multi-Model Adversarial Audit Engine
Cross-examines the Universal Cognitive Decomposition Engine, ГОСТ 34.602-89 specifications,
and Dual-Agent NPU mathematical foundations using independent external LLMs.
"""

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
sys.path.insert(0, str(PROJECT_ROOT.parent))

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

    def query_model(self, model_name: str, system_prompt: str, user_prompt: str, timeout: int = 25) -> Dict[str, Any]:
        """Queries a model on OpenRouter with key rotation and error handling."""
        url = "https://openrouter.ai/api/v1/chat/completions"
        
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 800
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
            if e.code in [429, 401]:
                self._rotate_key()
            return {"model": model_name, "success": False, "error": f"HTTP {e.code}: {err_msg}"}
        except Exception as e:
            return {"model": model_name, "success": False, "error": str(e)}

    def run_adversarial_audit(self) -> Dict[str, Any]:
        """
        Executes a 3-vector adversarial cross-examination of our architecture.
        """
        gost_md_path = PROJECT_ROOT / "TZ_GOST_34_602_89_SPECIFICATION.md"
        gost_excerpt = gost_md_path.read_text(encoding="utf-8")[:2500] if gost_md_path.exists() else "ТЗ отсутствует"

        # Task 1: Audit of ГОСТ 34.602-89 Compliance (Cohere North Mini Code)
        prompt_task1 = f"""
Вы — строгий, беспристрастный ведущий эксперт по сертификации ПО и стандартам ГОСТ 34.602-89 и ISO/IEC/IEEE 29148.
Вам на экспертизу передана выжимка сгенерированного ТЗ:
---
{gost_excerpt}
---
Ваша задача: провести жесткий аудит.
1. Соответствует ли структура документа разделам ГОСТ 34.602-89?
2. Есть ли в документе критические пробелы, размытые формулировки или уязвимости для отклонения госэкспертизой?
3. Достаточно ли требований для написания кода?
Ответьте кратко и по делу: оценка (1-10) и 2 главных замечания.
"""

        # Task 2: Audit of Mathematical and Physical Foundations (NVIDIA Nemotron 3 Ultra 550B)
        prompt_task2 = """
Вы — ученый в области Theoretical Computer Science и AI Hardware Architecture.
Оцените научную строгость архитектуры:
«Для устранения галлюцинаций и сикофантии в мультиагентных системах предлагается разделить вычисления:
1. System 2 (Генерация вариантов): Облачная LLM с открытым словарем V*.
2. System 1 (Тензорный арбитр с правом вето): Неавторегрессионный энкодер (Laya-421M / Jev / ModernBERT) на локальном физическом NPU (Intel AI Boost, 2W), выход которого строго ограничен вероятностным симплексом Delta^(K-1), что по неравенству Хоффдинга и теории PAC гарантирует конечность размерности Вапника-Червоненкиса d_VC <= log2(K) и исключает генеративные галлюцинации по построению.
3. Процесс выбора оптимизируется по принципу MDL Риссанена min [L(M) + L(X|M)] с 7 ортогональными Stage-Gates вместо ненадежного демократического голосования LLM (теорема Эрроу)».

Вопрос:
1. Математически и физически ли состоятелен этот подход?
2. Действительно ли неавторегрессионный арбитр на NPU защищает от поглощающих марковских цепей ошибок (Hallucination Snowball)?
Дайте жесткую, объективную рецензию (peer review).
"""

        # Task 3: Adversarial Red-Teaming (Poolside Laguna S 2.1)
        prompt_task3 = """
Вы — беспощадный Red Teamer и системный аудитор.
Найдите 3 самые слабые точки в архитектуре:
- 7 министерств (CJM, Финансы, Право, Безопасность, Архитектура, NPU, QA);
- Неавторегрессионный NPU арбитр (Laya-421M INT8 на Intel Core Ultra);
- Компилятор ТЗ по ГОСТ 34.602-89.
Где эта система может сломаться в жестком корпоративном продакшене под нагрузкой?
"""

        audit_results = []

        print("=" * 70)
        print("LAUNCHING INDEPENDENT MULTI-MODEL ADVERSARIAL AUDIT (OpenRouter)")
        print("=" * 70, flush=True)

        # Vector 1: Standards Audit (Cohere North Mini Code)
        print("\n[Audit Vector 1] ГОСТ 34.602-89 & ISO 29148 Compliance Audit...", flush=True)
        print("Querying: cohere/north-mini-code:free ...", flush=True)
        res_v1 = self.query_model(
            "cohere/north-mini-code:free",
            "You are a ruthless governmental and ISO compliance auditor.",
            prompt_task1
        )
        audit_results.append({"vector": "ГОСТ 34 & ISO 29148 Compliance", "data": res_v1})
        print(f"  -> Result: Success={res_v1['success']} ({res_v1.get('latency_ms', 0)} ms)", flush=True)

        # Vector 2: Mathematical & NPU Hardware Audit (NVIDIA Nemotron 3 Ultra 550B)
        print("\n[Audit Vector 2] Mathematical, PAC & NPU Foundations Audit...", flush=True)
        print("Querying: nvidia/nemotron-3-ultra-550b-a55b:free ...", flush=True)
        res_v2 = self.query_model(
            "nvidia/nemotron-3-ultra-550b-a55b:free",
            "You are a rigorous theoretical computer scientist and AI hardware architect.",
            prompt_task2
        )
        audit_results.append({"vector": "Mathematical & NPU Architecture", "data": res_v2})
        print(f"  -> Result: Success={res_v2['success']} ({res_v2.get('latency_ms', 0)} ms)", flush=True)

        # Vector 3: Red-Teaming & Failure Modes (Poolside Laguna S 2.1)
        print("\n[Audit Vector 3] Adversarial Red Teaming & Production Failure Modes...", flush=True)
        print("Querying: poolside/laguna-s-2.1:free ...", flush=True)
        res_v3 = self.query_model(
            "poolside/laguna-s-2.1:free",
            "You are a ruthless adversarial red-team auditor.",
            prompt_task3
        )
        audit_results.append({"vector": "Adversarial Red-Teaming & Bottlenecks", "data": res_v3})
        print(f"  -> Result: Success={res_v3['success']} ({res_v3.get('latency_ms', 0)} ms)", flush=True)

        # Save results
        report_file = PROJECT_ROOT / "AUDIT_CROSS_EXAMINATION_REPORT.md"
        report_json = PROJECT_ROOT / "AUDIT_CROSS_EXAMINATION_REPORT.json"

        report_json.write_text(json.dumps(audit_results, ensure_ascii=False, indent=2), encoding="utf-8")

        md_lines = [
            "# Официальный Отчет Независимого Мульти-Модельного Аудита (OpenRouter)",
            f"**Дата проведения экспертизы:** {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}",
            "**Привлеченные внешние независимые модели:**",
            "- `cohere/north-mini-code:free` (Экспертиза соответствия ГОСТ 34 и ISO 29148)",
            "- `nvidia/nemotron-3-ultra-550b-a55b:free` (Экспертиза математического базиса и физики NPU)",
            "- `poolside/laguna-s-2.1:free` (Red-Teaming стресс-тест слабых мест архитектуры)",
            "\n---\n"
        ]

        for item in audit_results:
            d = item["data"]
            md_lines.append(f"## Экспертиза: {item['vector']}")
            md_lines.append(f"**Аудитор (Модель):** `{d['model']}` | **Время ответа:** {d.get('latency_ms', 0)} мс")
            if d.get("success"):
                md_lines.append(f"\n### Дословный вердикт аудитора:\n{d['content']}\n")
            else:
                md_lines.append(f"\n*Ошибка опроса:* `{d.get('error')}`\n")
            md_lines.append("---\n")

        report_file.write_text("\n".join(md_lines), encoding="utf-8")
        print(f"\n[Audit Complete] Full report saved to: {report_file}", flush=True)
        return {"report_path": str(report_file), "results": audit_results}


if __name__ == "__main__":
    auditor = OpenRouterAuditor()
    auditor.run_adversarial_audit()
