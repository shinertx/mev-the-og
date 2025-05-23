import os
import shutil
import subprocess
from glob import glob

SNAP_DIR = "snapshots"
LOG_FILE = os.path.join(SNAP_DIR, "snapshot.log")


def latest_snapshot():
    snaps = sorted([d for d in glob(os.path.join(SNAP_DIR, "*")) if os.path.isdir(d)])
    return snaps[-1] if snaps else None


def restore_snapshot(folder):
    commit_file = os.path.join(folder, "commit.txt")
    cfg_file = os.path.join(folder, "config.yaml")
    env_hash_file = os.path.join(folder, "env_hash.txt")

    if os.path.exists(commit_file):
        commit = open(commit_file).read().strip()
        try:
            subprocess.check_call(["git", "reset", "--hard", commit])
        except Exception:
            print("Failed to reset git commit")

    if os.path.exists(cfg_file):
        shutil.copy(cfg_file, "config.yaml")

    if os.path.exists(env_hash_file) and os.path.exists(".env"):
        with open(env_hash_file) as f:
            expected = f.read().strip()
        import hashlib
        with open(".env", "rb") as f:
            current = hashlib.sha256(f.read()).hexdigest()
        if current != expected:
            print("[WARN] .env hash mismatch during restore")

    # post-restore health check
    health = "unknown"
    try:
        subprocess.check_call(["python", "-m", "py_compile", "main.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        health = "healthy"
    except Exception:
        health = "unhealthy"

    ts = os.path.basename(folder)
    with open(LOG_FILE, "a") as log:
        log.write(f"{ts} RESTORE {folder}\n")
    print(f"Restored snapshot {folder} - health: {health}")


def main():
    folder = latest_snapshot()
    if not folder:
        print("No snapshots found")
        return
    restore_snapshot(folder)


if __name__ == "__main__":
    main()
