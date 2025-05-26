# AGENTS.md — MEV-OG Agent & Doctrine Guide (v1.2, May 2025+)

---

## 🧠 Doctrine & Mission Anchoring

**All agents (AI, Codex, LLM, human) must review and comply with `PROJECT_BIBLE.md` before any code, module, test, or process change.  
No change is valid unless doctrine-aligned or explicitly approved as a doctrine upgrade.  
If in doubt, pause and escalate to Founder.**

---

## 🛡️ Mission & Critical Standards

- This repo is the world’s most adversarial, adaptive, AI-driven MEV/quant crypto trading system.
- Grow $5K to $10M+ with extreme capital efficiency, survival, and risk controls (“1-in-a-billion” design).
- Every module must be modular, resilient, adversarially simulated, and ready for capital at scale.
- All code changes must be: production-grade, fully integrated, test-covered, and revertible in a single step.
- **Assume all code, infra, and process is audited by world-class red teams (Jump/Flashbots-level defense).**

---

## 🔒 Security, Capital Protection & Kill Switch Protocols

- **Kill Switch:** All core modules (trading, API, risk, notifier, dashboard) must integrate with `src/kill_switch.py`.  
  Any critical error, repeated failure, anomaly, or risk threshold breach must halt sensitive ops and alert Founder.
- **Tiered Risk:** Implement multi-stage response: pause, de-risk, liquidate, halt—no single-point-of-failure.
- **Secrets:** No secrets in code/config. Use `.env` (gitignored), rotate regularly, and provide automated secret scripts.
- **Config Validation:** All YAML/ENV configs must validate schema at load—fail fast, escalate errors.

---

## 🧑‍💻 Coding, Structure & AI Protocol

- **Orchestration:** `main.py` is the orchestrator—must gracefully propagate/handle all failures up to kill switch/notifier.
- **Core Logic:**  
  - `src/mev_bot.py` — all trading logic  
  - `src/risk_manager.py` — risk/capital logic  
  - `src/kill_switch.py` — halt logic  
- **AI/LLM/Codex:** All prompts, codegen, and changes must:  
  - Parse and cross-reference `PROJECT_BIBLE.md` at task start.  
  - For every codegen/refactor, explicitly answer: “Does this comply with doctrine?”  
  - Pause/escalate to Founder if unclear.
- **Infra/Ops:** All setup, test, run, and recovery scripts live in root or `scripts/`.
- **Notifier:** `src/notifier.py` must alert Founder for any halt, anomaly, or critical event.
- **Dashboard:** `src/dashboard.py` visualizes live risk, kill switch, and health metrics.
- **New Modules:** Fully documented, type-hinted, PEP8-compliant, with usage/tests.

---

## 🧪 Testing & Simulation (Pytest + Codespaces)

- All code must pass `pytest` in Codespaces root, covering kill switch, risk, notifier, edge modules.
- **Required Tests:**  
  - Normal operation  
  - Adversarial/chaos: gas wars, reorg, L1-L2 sandwich, node/API fail, mainnet fork, mempool attack  
  - Kill switch, health-check, rollback, DRP  
  - Capital gating, scaling, edge-case defense  
  - AI/LLM integration, mutation/decay logic (log outputs/mutation history)
- **CI/CD:** All PRs must pass all tests; coverage drops/blockers must fail merge.  
  No code with skipped tests or TODOs may merge.

---

## 🚨 Founder-First UX & Recovery

- All critical actions must be explicit, terminal-ready, and step-by-step.
- Every step/workflow/upgrade must include:  
  - Expected checkpoint/outcome  
  - Rollback/undo step  
  - Where to find logs/diagnostics if error/failure
- **Disaster Recovery:** All modules support Git-based snapshot/rollback.  
  DRP state recovery is documented and testable.

---

## 📊 Monitoring, Logging & Mutation

- All modules must log: key events, trades, failures, alerts, capital/PnL, mutation/auto-tune params.
- Logs must be parseable for AI/LLM research or automated strategy pruning.
- All mutations/AI-driven changes are timestamped and context-logged.

---

## 🧬 Overfitting & Alpha Decay Prevention (Mandatory)

- **Run at least one “dumb” (non-adaptive) baseline strategy at all times for control.**
- **All new strategies/param sets must show live out-of-sample/canary PnL before scaling.**
- **Use randomized/rotating backtest windows; stress-test all sims under volatility/chaos.**
- **Log and monitor alpha decay—flag and prune underperformers fast.**
- **Schedule regular contrarian review and “blind spot” search; AI/founder must check for edge crowding/overfitting monthly.**
- **Never hard-code params based on best backtest; sweep and validate on live.**
- **Avoid LLM/AI “feedback loops” (don’t just chase last week’s top PnL).**
- **Benchmark against public dashboards, escalate if lagging.**

---

## 📝 Documentation & Onboarding

- README always up-to-date (install, test, run, state restore).
- All modules must have docstrings/code comments for non-trivial logic.
- Mermaid diagrams/flowcharts required for new modules/refactors.
- State snapshot/recovery and DRP are documented/tested.

---

## ⚡️ Special Adversarial Tasks for Codex/AI/Agents

- **Always:**  
  - Scan for/fix integration gaps, unhandled exceptions, missing kill switch hooks.
  - Proactively adversarially test every module (simulate attack/failure before merge).
  - Propose chaos upgrades, edge-discovery, mutation improvements with major PRs.
- **Regularly:**  
  - Review all modules for alpha decay, perf drop, “rot.” Flag for prune/refactor.
  - Check all new chain/bridge/DEX/infra developments—propose relevant edge upgrades.

---

## 📂 File Structure Reference

- `main.py` — orchestrator  
- `src/` — core modules: `mev_bot.py`, `risk_manager.py`, `kill_switch.py`, `notifier.py`, `dashboard.py`, `utils.py`  
- `src/ai/` — all AI/LLM/mutation logic  
- `tests/` — full e2e, chaos, adversarial, rollback/state sim  
- `config.example.yaml`, `.env.example` — reference configs (**no secrets**)  
- `Dockerfile`, `run.sh` — infra/ops  
- `AGENTS.md`, `README.md` — onboarding and doctrine

---

## 🚦 PR/Merge Checklist (Codex/AI/Human)

- [ ] Code is production-ready, modular, integrated.
- [ ] All kill switch/risk logic is fully tested, including adversarial cases.
- [ ] All secrets/configs secure, validated, never leaked.
- [ ] Full pytest (including chaos/edge) passes in Codespaces.
- [ ] All actions explicit, rollback-able, checkpointed.
- [ ] Docs, onboarding, diagrams are updated.
- [ ] Any AI/mutation change is logged/documented.
- [ ] DRP and snapshot/restore up-to-date.
- [ ] Overfitting controls and baseline strategy coverage in place.
- [ ] All diffs reviewed for edge/attack surface.
- [ ] PR references compliance with `PROJECT_BIBLE.md` and this AGENTS.md.

---

## 🆘 Disaster Recovery Protocol (DRP)

- **State Snapshot:** Always commit before/after major change or config/secret update. Use `git tag` for checkpoints.
- **Restore:** Roll back via last good commit/tag, verify config/env, rerun `pytest`, redeploy.
- **Failure:** If halt, use logs to diagnose, apply kill/manual override, then restore workflow above.
- **Secrets:** Rotate immediately after any suspected leak/error.

---

## 📚 Key Doctrine Files

- [PROJECT_BIBLE.md](./PROJECT_BIBLE.md) — master doctrine (read first)

---

**TL;DR:**  
Every workflow, prompt, and code change begins by checking `PROJECT_BIBLE.md` and this `AGENTS.md`.  
If compliance is unclear, escalate to Founder.  
No ambiguity. No shortcuts. Founder-first. Capital-protective. Doctrine enforced.

---

*This AGENTS.md encodes the live doctrine and adversarial edge of MEV-OG. All Codex, AI, and human agents must comply. When in doubt, always favor capital protection, explicit recovery, and founder visibility above all else.*
