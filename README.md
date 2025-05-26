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

## Kill Switch

All trading flows route through a centralised kill switch with four tiers:

1. **Pause** – temporarily stop new trades while monitoring continues.
2. **Reduce Risk** – trade sizes are automatically cut in half.
3. **Liquidate** – existing positions should be unwound.
4. **Halt** – trading stops entirely and the founder is alerted immediately.

Configure `founder_chat_id` and `kill_switch_max_errors` in `config.yaml` to
control alerting and sensitivity.

### Expected behaviour

* Every trade updates PnL and drawdown via the global kill switch.
* On RPC outages or repeated errors the bot escalates through pause → halt.
* Invalid or missing config halts the system on startup and notifies the founder.
* If Telegram alerts fail, an email fallback is triggered.

### Restore & DRP

1. Inspect `logs/mev_og.log` for the halt reason.
2. Fix the root cause and update `config.yaml` if needed.
3. Verify notifier channels with `tests/test_notifier.py`.
4. Reset kill switch state via `manual_override(PAUSE, confirm=True)`.
5. Start the bot and monitor for at least one full cycle.

If all notifiers fail, consult the logs and manually reach out to the founder.
