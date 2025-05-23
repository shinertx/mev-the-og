# Monitoring and DRP Guide

This guide describes how to interpret the dashboard and respond to alerts.

## Dashboard Overview

The root endpoint `/` displays a JSON payload with:

- `risk` – current drawdown
- `capital_at_risk` – estimated capital in open positions
- `kill_switch_state` – `OK`, `TRIGGERED`, or `MANUAL_OVERRIDE`
- `alpha_performance` – per-strategy PnL metrics
- `notifier_health` – last known status of each notification channel
- `last_config_event` – last configuration or DRP event
- `heartbeat` – epoch timestamp of last update
- `panic` – `true` if a critical event occurred

The `/override` endpoint clears panic state and resets the kill switch.

## Panic Protocols

1. **Immediate alert** – Telegram, email and Slack will receive an alert. If none succeed, `PANIC.log` is written and a console message is printed.
2. **Check dashboard** – confirm kill switch status and reason in `last_config_event`.
3. **Mitigate** – fix the underlying issue (e.g., restore config, top up collateral).
4. **Manual reset** – once safe, POST to `/override` or use the dashboard button to resume trading.

## DRP Steps

Disaster recovery plans (DRP) should reference this guide:

- Backup `config.yaml` and `.env` regularly.
- Monitor `PANIC.log` for any failed notifications.
- Use the test suite (`pytest tests/test_critical_events.py`) to verify monitoring before resuming after downtime.

