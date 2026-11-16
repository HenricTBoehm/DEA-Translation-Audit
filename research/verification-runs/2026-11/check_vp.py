"""Smoke-test the versioned extraction and strict semantic comparator."""
import importlib.util
import json
import subprocess
import tempfile
import zipfile
from pathlib import Path

VP = Path(__file__).resolve().parents[3] / "VP-1.0"


def check(condition, reason):
    if not condition:
        raise AssertionError(reason)


def main():
    subprocess.run(["bash", str(VP / "verification-v1.0.1/run.sh"), "--help"],
                   check=True, capture_output=True, text=True)
    with tempfile.TemporaryDirectory() as scratch:
        root = Path(scratch)
        module_path = root / "verify.py"
        subprocess.run(["patch", "--silent", "--output", str(module_path),
                        str(VP / "verify.py"), str(VP / "verification-v1.0.1/verify.patch")],
                       check=True)
        spec = importlib.util.spec_from_file_location("corrected", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        archive = root / "sample.zip"
        dest = root / "extracted"
        for prefix in ("", "dea-v0343-remediation/"):
            with zipfile.ZipFile(archive, "w") as package:
                package.writestr(prefix + "SHA256SUMS", "test manifest")
                package.writestr(prefix + "harness/run_audit.py", "# fixture")
            check(Path(module.extract(archive, dest)) == dest / prefix, prefix)
        with zipfile.ZipFile(archive, "w") as package:
            package.writestr("unrelated", "fixture")
        try:
            module.extract(archive, dest)
        except ValueError:
            pass
        else:
            raise AssertionError("missing archive root accepted")

        expected, actual = root / "expected", root / "actual"
        for directory in (expected, actual):
            directory.mkdir()
            (directory / "countermodels.json").write_text("[]")
        archived = {"meta": {"python": "3.14.4", "seed": 7}, "data": [1]}
        current = {"meta": {"python": "3.12.14", "seed": 7}, "data": [1]}
        (expected / "remediation-results.json").write_text(json.dumps(archived))
        result_path = actual / "remediation-results.json"
        result_path.write_text(json.dumps(current))
        result = module.compare_rp(actual, expected, 0)
        check(result["semantic_equal"] and not result[result_path.name]["byte_equal"], result)
        check(not module.compare_rp(actual, expected, 2)["semantic_equal"], "nonzero exit accepted")
        current["data"] = [True]
        result_path.write_text(json.dumps(current))
        check(not module.compare_rp(actual, expected, 0)["semantic_equal"], "JSON type change accepted")
        current["data"] = [1]
        current["meta"]["seed"] = 8
        result_path.write_text(json.dumps(current))
        check(not module.compare_rp(actual, expected, 0)["semantic_equal"], "non-runtime metadata change accepted")
        result_path.write_text(json.dumps(archived))
        (actual / "countermodels.json").write_text("[{}]")
        check(not module.compare_rp(actual, expected, 0)["semantic_equal"], "countermodel change accepted")
    print("PASS: VP archive layouts and semantic/byte comparator")


if __name__ == "__main__":
    main()
