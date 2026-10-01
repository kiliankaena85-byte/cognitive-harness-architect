"""
Dual-Agent Scientific & Hardware Validation of Standards-Compliant Specification Engine
Evaluates GOST 34.602-89 / ISO/IEC/IEEE 29148 compilation feasibility on Intel AI Boost NPU.
"""

import sys
import time
from pathlib import Path

# Force UTF-8 stdout
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT.parent))

from design_arbiter import validate_proposition, score_candidate, arbitrate


def run_standards_validation():
    print("=" * 70)
    print("DUAL-AGENT VALIDATION: GOST 34.602 / ISO 29148 STANDARDS ENGINE")
    print("=" * 70)

    # 1. Проверка логических инвариантов на физическом чипе NPU (noul)
    p1 = validate_proposition(
        "Контекст: Госзакупки 44-ФЗ, Enterprise B2B, ISO 29148, ГОСТ 34.602",
        "Устраняет ли строгая структурная разметка ТЗ по ГОСТ/ISO двусмысленность и галлюцинации при последующей кодогенерации?"
    )
    print(f"[NPU-Gate 1] Снижение двусмысленности требований: {p1['value']} (Уверенность: {p1['probability']*100:.1f}%) | {p1['latency_ms']} мс")

    p2 = validate_proposition(
        "Контекст: Сопоставление JSON контрактов 7 Министерств с разделами ГОСТ 34",
        "Возможно ли детерминированное преобразование верифицированных схем OpenAPI и PRD в официальные разделы ГОСТ 34.602 без потери смысла?"
    )
    print(f"[NPU-Gate 2] Детерминированная трансляция в ГОСТ: {p2['value']} (Уверенность: {p2['probability']*100:.1f}%) | {p2['latency_ms']} мс")

    # 2. Многокритериальный скоринг вариантов на NPU
    cand_free = "Свободный текстовый Markdown бриф без стандартов"
    cand_gost = "Автоматически скомпилированное ТЗ по ГОСТ 34.602-89 и ISO/IEC/IEEE 29148 с матрицей трассируемости RTM"

    score_free = score_candidate(cand_free, "Пригодность для Enterprise-закупок и строгого аудита качества")
    score_gost = score_candidate(cand_gost, "Пригодность для Enterprise-закупок и строгого аудита качества")

    print(f"\n[NPU-Score 1] Свободный Markdown : {score_free['rating']} / 10")
    print(f"[NPU-Score 2] ТЗ по ГОСТ 34 / ISO : {score_gost['rating']} / 10")

    # 3. Выбор движка сборщика документов на NPU
    decision = arbitrate(
        "Генерация юридически значимых документов ГОСТ 34 на ноутбуке 16GB RAM без MS Office",
        [
            "Pure OpenXML / docx-templates (Автономный легковесный компилятор без Office)",
            "Тяжелый запуск LibreOffice/MS Word в headless-режиме через COM/Docker",
            "Простая конвертация Markdown в PDF через Pandoc"
        ]
    )
    print(f"\n[NPU-Choice] Оптимальный движок генерации документов:")
    print(f"             Выбор: {decision['choice']}")
    print(f"             Уверенность: {decision['confidence']*100:.1f}% | Чип: {decision['device']} | Время: {decision['latency_ms']} мс")
    print("=" * 70)


if __name__ == "__main__":
    run_standards_validation()
