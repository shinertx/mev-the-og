# MEV The OG

## Mission
Build and operate the world’s most aggressive, adaptive, AI/quant-driven crypto trading system—targeting $5K starting capital to $10M+ with 1-in-a-billion capital efficiency, survival, and risk controls.

## Quickstart

1. Install dependencies:  
   `pip install -r requirements.txt`

2. Fill in `config.yaml` (see `.env.example` for env vars).

3. Run any alpha module:  
   - `python main.py --mode test --alpha cross_chain`
   - `python main.py --mode test --alpha mev_share`
   - (or try any in `src/alpha/`)

4. Logs are in `logs/mev_og.log`.

5. See the dashboard:  
   `python main.py --dashboard`

## Structure

- `src/alpha/` – All advanced MEV modules
- `src/` – Core bot, risk, kill switch, utils, dashboard, notifier
- `tests/` – Full test suite
- `logs/` – Log output
- `Dockerfile` – Run anywhere
- `run.sh` – Example launch script

## Disaster Recovery
Refer to `docs/DRP.md` for the full snapshot and restore process. Before any
upgrade or secret change, run:
```
python scripts/snapshot.py
```
To rollback to the last known good state run:
```
python scripts/restore.py
```
Snapshots and restores are logged in `snapshots/snapshot.log`.
