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

## Configuration & Secret Management

All secrets must live in `.env` only. Copy `.env.example` to `.env` and fill values.
`config.yaml` holds non-secret parameters and is strictly validated at startup.

To rotate secrets:
1. Run `scripts/rotate_secrets.py` to back up the current `.env`.
2. Edit the `.env` with new values.
3. Restart the bot.

If the bot halts due to config or secret issues:
1. Check logs for `ConfigMonitor` messages.
2. Restore the last known-good `.env` or `config.yaml` from backups.
3. Fix any validation errors and restart.

The `ConfigMonitor` halts trading if `.env` or `config.yaml` change while running.
Notifications are sent via all configured channels when this occurs.

### Troubleshooting
- Ensure `.env` syntax is `KEY=value` per line with no quotes.
- Missing required fields will raise a `RuntimeError` during startup.
- After resolving issues, restart the bot to resume operation.
