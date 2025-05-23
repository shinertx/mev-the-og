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

## AI Mutation & Pruning

The `src/ai/` folder contains automation helpers:

- **parameter_mutator.py** – live parameter mutation based on the `ai.mutation_frequency` setting.
- **strategy_scorer.py** – calculates edge scores using weights from `ai.scoring`.
- **edge_pruner.py** – disables strategies when their score drops below `ai.decay_threshold`.

All AI events are logged with UTC timestamps and the active config hash. Review
`logs/mev_og.log` or `logs/ai_demo.log` to audit mutations and prunes.

### Recovering from a prune
1. Inspect the log entry to identify which module was disabled.
2. Re-add the module to `alpha.enabled` in `config.yaml` and reset its entry in
   `logs/module_performance.json`.

### Tuning mutation logic
Edit the values under `ai:` in `config.yaml`:

- `mutation_frequency` – how often parameter mutation runs.
- `decay_threshold` – minimum score before pruning.
- `scoring` – weights for `winrate`, `avg_pnl` and `fail_count`.

### Reviewing logs
Logs are plaintext with UTC timestamps and config hash prefixes. They can be
parsed by other tools or LLMs for optimization.

Run the demonstration script:

```bash
python examples/ai_flow_demo.py
```

