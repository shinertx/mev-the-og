# Disaster Recovery Process (DRP)

The DRP outlines how to capture snapshots before risky changes and how to restore the bot in case of failure.

## Snapshot workflow
1. Run `python scripts/snapshot.py` before any upgrade, config or secret change.
2. A timestamped folder will be created under `snapshots/` containing:
   - `commit.txt` – current git commit hash
   - `config.yaml` – current config
   - `env_hash.txt` – SHA256 hash of `.env` secrets
   - `logs.zip` – archived logs
   - `health.txt` – result of basic health check
3. Each snapshot is logged in `snapshots/snapshot.log` with UTC timestamp.

## Restore workflow
1. If the bot halts or upgrade fails, run `python scripts/restore.py`.
2. The script resets git to the last snapshot commit, restores `config.yaml`,
   checks the `.env` hash and prints a health status.
3. Restore events are also appended to `snapshots/snapshot.log`.
4. Once health is `healthy`, trading can resume.

Use these commands manually or incorporate them into CI/CD before deploying new versions.
