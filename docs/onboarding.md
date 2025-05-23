# Onboarding Guide

This document outlines the basic steps for a founder to bring up **MEV The OG** and verify that monitoring works.

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Configure environment**:
   - Copy `config.example.yaml` to `config.yaml` and fill in API keys.
   - Set `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `EMAIL_TO`, and `SLACK_WEBHOOK` in your environment or `.env`.

3. **Run the bot in test mode**:
   ```bash
   python main.py --mode test
   ```
   Logs appear in `logs/mev_og.log`.

4. **Launch the dashboard**:
   ```bash
   python main.py --dashboard
   ```
   Open `http://localhost:8501` to view live metrics.

5. **Verify alerts**:
   - Trigger a sample risk event by running the test suite:
     ```bash
     pytest tests/test_critical_events.py::test_notifier_escalation_fail
     ```
   - Check that Telegram, email and Slack/Webhook notifications arrive. If all fail, `PANIC.log` will contain the alert and the console prints a panic message.

6. **Resetting the kill switch**:
   - The dashboard exposes a `POST /override` endpoint. Click the manual override button or issue:
     ```bash
     curl -X POST http://localhost:8501/override
     ```
   - This clears the panic state and re-enables trading if you have resolved the issue.

