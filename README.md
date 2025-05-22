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

## Adversarial Testing

The `tests/adversarial` directory exercises the full bot under hostile
conditions.  Integration tests launch `MEVBot`, trigger chaos events and
verify that the kill switch disables trading and all notifiers alert the
founder.

Covered scenarios include:

- Mainnet fork/reorg using **anvil** or the in-memory chain
- Gas wars and mempool flooding
- RPC disconnects and reconnect attempts
- L1–L2 sandwich or cross-domain replay exploits

Run the entire suite with:

```bash
pytest -v
```

If `anvil` is missing, the fork test skips automatically.  CI will fail if
any adversarial test fails.  When the kill switch triggers, review the logs
and Telegram/email alerts to confirm the bot halted as expected before
re-enabling live trading.
