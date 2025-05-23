import os
import subprocess

from scripts import snapshot as snapshot_mod
from scripts import restore as restore_mod


def init_repo(path):
    os.chdir(path)
    subprocess.run(["git", "init"], check=True, stdout=subprocess.DEVNULL)
    (path / "config.yaml").write_text("val: 1")
    subprocess.run(["git", "add", "config.yaml"], check=True)
    subprocess.run(["git", "commit", "-m", "init"], check=True, stdout=subprocess.DEVNULL)
    os.makedirs(path / "logs")
    (path / "logs" / "mev_og.log").write_text("log")


def test_snapshot_and_restore(tmp_path, monkeypatch):
    init_repo(tmp_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(snapshot_mod, "SNAP_DIR", str(tmp_path / "snaps"))
    monkeypatch.setattr(restore_mod, "SNAP_DIR", str(tmp_path / "snaps"))

    snapshot_mod.create_snapshot()
    snap = restore_mod.latest_snapshot()
    assert snap is not None
    # modify config
    (tmp_path / "config.yaml").write_text("val: 2")
    restore_mod.restore_snapshot(snap)
    assert (tmp_path / "config.yaml").read_text() == "val: 1"
