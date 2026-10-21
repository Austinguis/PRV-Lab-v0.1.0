import csv
import json

from prv_lab.cli import main


def test_gaussian_curve_cli_writes_reproducible_outputs(tmp_path):
    code = main(
        [
            "gaussian-curve",
            "--noise-std", "2.0",
            "--steps", "4",
            "--eps-max", "2.0",
            "--points", "11",
            "--output-dir", str(tmp_path),
        ]
    )
    assert code == 0
    csv_path = tmp_path / "gaussian_curve.csv"
    plot_path = tmp_path / "gaussian_curve.png"
    metadata_path = tmp_path / "run_metadata.json"
    assert csv_path.exists() and plot_path.exists() and metadata_path.exists()
    with csv_path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 11
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata["command"] == "gaussian-curve"
    assert metadata["parameters"]["steps"] == 4
