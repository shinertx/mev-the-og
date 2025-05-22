# AGENTS.md — MEV-OG Project Agent Guide (v1.0, May 2025+)

## 🛡️ Mission & Critical Standards
- This repo is for the world’s most adversarial, adaptive, AI-driven MEV/quant crypto trading system.
- Target: grow $5K to $10M+ with extreme capital efficiency, survival, and risk controls.
- Every module must be resilient, modular, and adversarially tested.
- All code changes must be: production-grade, fully integrated, test-covered, and revertible in a single step.
- **Assume every task is being audited by world-class red teams and must defend against Jump/Flashbots-level adversaries.**

## 🔒 Security, Capital Protection & Kill Switch Protocols
- **Kill switch**: All trading, API, risk, notifier, and dashboard modules must integrate with `src/kill_switch.py`. Any error, repeated fail, anomaly, or risk threshold breach MUST halt all sensitive operations and escalate to Founder.
- **Tiered risk**: Implement multi-level responses: pause, de-risk, liquidate, halt.
- **Secrets**: No secrets in code or config. Use `.env` (gitignored) and rotate regularly. Provide/patch secret handling scripts if needed.
- **Config validation**: All YAML/ENV configs must schema-validate at load. Fail fast and escalate any config or secret error.

## 🧑‍💻 Coding, Structure & Placement
- **Orchestration**: Main entry is `main.py`, which must gracefully handle and propagate all failures up to kill switch/notifier.
- **Trading/risk logic**: `src/mev_bot.py` (all trading), `src/risk_manager.py` (all capital/risk), `src/kill_switch.py` (all halt logic).
- **AI/LLM/Adaptation**: `src/ai/` (orchestrator, alpha scraper, param mutation, meta-strategy logic).
- **Infra/ops**: All setup, test, run, and recovery scripts must live in repo root or `scripts/`.
- **Notifier**: `src/notifier.py` must send Founder alerts for any halt, anomaly, or critical event.
- **Dashboard**: `src/dashboard.py` must visualize live risk/kill switch/health metrics.
- **New modules**: Must be fully documented, type-hinted, PEP8 compliant, and include usage/tests.

## 🧪 Testing & Simulation (Pytest + Codespaces)
- **All code must pass**: `pytest` in Codespaces root; include coverage for all kill switch, risk, notifier, and edge modules.
- **Required tests**:
  - Normal operation, chaos/adversarial (gas war, reorg, L1-L2 sandwich, node disconnect, API fail, mainnet fork, mempool attack)
  - Kill switch, health-check, state snapshot/rollback, disaster recovery
  - Capital gating, scaling, and edge-case defense (e.g. repeated failed trades, API lag, invalid config)
  - AI/LLM integration and mutation/decay logic (log outputs and mutation history)
- **CI/CD**: All PRs must run and pass all tests. Failures or coverage drops must block merge.
- **No code with skipped tests or TODOs may be merged.**

## 🚨 Founder-First UX & Recovery
- **All critical actions must be explicit, terminal-ready, and step-by-step.**
- Each step in any workflow or upgrade must include:
  - Expected outcome/checkpoint
  - Rollback or “undo” step
  - Where to find logs or diagnostics if error/failure
- **Disaster Recovery**: All modules must support Git-based snapshot/rollback. Document state recovery in DRP section below.

## 📊 Monitoring, Logging & Mutation
- **All modules must log key events, trades, failures, alerts, capital/PnL, and mutation/auto-tune params.**
- Logs must be parseable for AI/LLM research or automated strategy pruning.
- All mutations/AI-driven parameter changes must be logged with timestamp and triggering context.

## 📝 Documentation & Onboarding
- README must always be up-to-date with install, test, run, and state restore steps.
- All modules must have docstrings and code comments for any non-trivial logic.
- Mermaid diagrams or text flowcharts required for new modules/major refactors.
- State snapshot/recovery and DRP must be explicitly documented and tested.

## ⚡️ Special Adversarial Tasks for Codex/Agents
- Always:
  - Scan for and fix any integration gaps, unhandled exceptions, or missing kill switch hooks.
  - Proactively adversarially test every module (simulate attack/edge/fail before merge).
  - Propose chaos upgrades, edge discovery, and edge-mutation improvements with each major PR.
- Regularly:
  - Review all modules for alpha decay, performance drop, or “rot.” Flag for prune/refactor.
  - Check all new chain/bridge/DEX/infra developments; propose relevant edge upgrades.

---

## 📂 File Structure Reference

- `main.py` – orchestrator
- `src/` – core modules: `mev_bot.py`, `risk_manager.py`, `kill_switch.py`, `notifier.py`, `dashboard.py`, `utils.py`
- `src/ai/` – all AI/LLM/mutation logic
- `tests/` – must include full e2e, chaos, adversarial, rollback/state sim
- `config.example.yaml`, `.env.example` – reference configs, **no secrets**
- `Dockerfile`, `run.sh` – infra/ops
- `AGENTS.md`, `README.md` – onboarding and doctrine

---

## 🚦 PR/Merge Checklist (for Codex/AI/humans)
- [ ] Code is production-ready, modular, and integrated.
- [ ] All kill switch/risk logic is fully tested in normal and adversarial mode.
- [ ] All secrets/configs are secure, validated, and never leaked in code.
- [ ] Full pytest suite (including chaos/edge) passes in Codespaces.
- [ ] All actions are explicit, rollback-able, and checkpointed.
- [ ] Documentation, onboarding, and diagrams are updated.
- [ ] Any mutation/AI-driven change is logged and documented.
- [ ] DRP and snapshot/restore procedures are up-to-date.
- [ ] All code and test diffs are reviewed for edge/attack surface.

---

## 🆘 Disaster Recovery Protocol (DRP)

- **State Snapshot:** Always commit before and after major change or config/secret update. Use `git tag` for checkpointing.
- **Restore:** To rollback, checkout last good commit/tag, verify config/env, rerun `pytest`, and redeploy.
- **Failure:** If bot halts, use logs to identify cause, apply kill switch/manual override, then run restore workflow above.
- **Secrets:** Rotate secrets immediately after any suspected leak or error.

---

*This AGENTS.md encodes MEV-OG’s doctrine and adversarial edge. All Codex, AI, and human agents must comply fully. When in doubt, favor capital protection, resilience, and explicit Founder UX above all else.*
