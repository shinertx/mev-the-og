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

## Capital & Risk Configuration

`config.yaml` now exposes advanced risk controls:

- `risk.max_drawdown_pct` – global drawdown cap
- `risk.max_loss_usd` – max loss before pausing
- `risk.max_trade_size_usd` – base trade cap (auto-scaled)
- `risk.rolling_window_hours` – window for PnL tracking
- `risk.per_alpha.{name}.max_loss_usd` – per-strategy loss threshold
- `risk.per_alpha.{name}.max_trade_size_usd` – per-strategy trade cap

When a threshold is hit the kill switch pauses trading and sends alerts via the configured notifier channels.
