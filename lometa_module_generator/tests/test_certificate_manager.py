import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from certificate_manager import CertificateManager


def test_certify_and_verify_round_trip(tmp_path):
    module_dir = tmp_path / "sample_module"
    module_dir.mkdir()

    (module_dir / "manifest.json").write_text(
        json.dumps({"name": "Sample Module", "version": "1.0.0"}),
        encoding="utf-8",
    )
    (module_dir / "main.py").write_text("print('hello')\n", encoding="utf-8")

    manager = CertificateManager(config_dir=tmp_path / ".lometa" / "certificates")
    cert = manager.certify_module(module_dir, "Test Certifier")

    assert cert is not None
    ok, message = manager.verify_module(module_dir)
    assert ok, message
