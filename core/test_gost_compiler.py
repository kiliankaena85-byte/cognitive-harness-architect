"""
core/test_gost_compiler.py
=============================================================================
Unit Test Suite for GostStandardsCompiler:
Validates compilation to ГОСТ 34.602-89, ISO/IEC/IEEE 29148 Traceability Matrix,
Formal Data Dictionary (Приложение Б), and Acceptance Criteria / PMI (Приложение В).
=============================================================================
"""

import sys
import tempfile
import unittest
from pathlib import Path

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
CORE_DIR = PROJECT_ROOT / "core"
if str(CORE_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_DIR))

from core.gost_compiler import GostStandardsCompiler


class TestGostStandardsCompiler(unittest.TestCase):
    """Tests the ГОСТ 34.602-89 and ISO 29148 specification compiler."""

    def setUp(self):
        self.compiler = GostStandardsCompiler()
        self.sample_brief = {
            "project_title": "Умная высоконагруженная SMM-платформа с NPU-арбитражем",
            "core_actors": [
                {"role": "Guest", "jtbd": "Быстрый заказ за 10 секунд без паролей"},
                {"role": "Wholesale_Client", "jtbd": "Массовые заказы через API и личный баланс"},
                {"role": "Administrator", "jtbd": "Управление провайдерами и наценкой маржи"},
                {"role": "Support_Agent", "jtbd": "Обработка тикетов по заказам с SLA 4 часа"}
            ]
        }

    def test_gost_compiler_structure_and_artifacts(self):
        """Verifies compiler produces valid markdown with all sections, data dictionary, and PMI."""
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir)
            result = self.compiler.compile(self.sample_brief, output_dir=out_dir)

            self.assertEqual(result["sections_count"], 8)
            self.assertGreaterEqual(result["traceability_matrix_items"], 8)
            self.assertGreaterEqual(result["data_dictionary_items"], 8)
            self.assertGreaterEqual(result["pmi_items"], 5)

            md_path = Path(result["markdown_path"])
            self.assertTrue(md_path.exists())
            content = md_path.read_text(encoding="utf-8")

            # Check core sections
            self.assertIn("ГОСТ 34.602-89", content)
            self.assertIn("1. ОБЩИЕ СВЕДЕНИЯ", content)
            self.assertIn("4. ТРЕБОВАНИЯ К СИСТЕМЕ", content)
            self.assertIn("8. ПРИЛОЖЕНИЕ А: МАТРИЦА ТРАССИРУЕМОСТИ ТРЕБОВАНИЙ", content)

            # Check Phase 4 additions: Data Dictionary and PMI
            self.assertIn("9. ПРИЛОЖЕНИЕ Б: ФОРМАЛЬНЫЙ СЛОВАРЬ ДАННЫХ И СУЩНОСТЕЙ", content)
            self.assertIn("Customer Journey Map", content)
            self.assertIn("L-MOPA Pareto Arbiter", content)
            self.assertIn("Saga Distributed Transaction", content)

            self.assertIn("10. ПРИЛОЖЕНИЕ В: ПРОГРАММА И МЕТОДИКА ИСПЫТАНИЙ", content)
            self.assertIn("ПМИ-01", content)
            self.assertIn("ПМИ-02", content)
            self.assertIn("ПМИ-05", content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
