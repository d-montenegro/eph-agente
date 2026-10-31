import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "eph_1t2026_sqlite.ipynb"


class ColabNotebookTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
        cls.code = "\n\n".join(
            "".join(cell["source"])
            for cell in cls.document["cells"]
            if cell["cell_type"] == "code"
        )

    def test_is_a_valid_v4_notebook(self) -> None:
        self.assertEqual(self.document["nbformat"], 4)
        self.assertGreaterEqual(self.document["nbformat_minor"], 5)
        self.assertTrue(self.document["cells"])

    def test_python_cells_compile(self) -> None:
        compile(self.code, str(NOTEBOOK), "exec")

    def test_audit_and_scaling_contract_is_present(self) -> None:
        self.assertIn("www.indec.gob.ar/ftp/cuadros/menusuperior/eph/EPH_usu_1_Trim_2026_txt.zip", self.code)
        self.assertIn("chunksize=CHUNK_SIZE", self.code)
        self.assertIn("sha256_archivo", self.code)
        self.assertIn("EXPECTED_ZIP_SHA256", self.code)
        self.assertIn("mode=ro", self.code)
        self.assertIn("manifest", self.code)


if __name__ == "__main__":
    unittest.main()
