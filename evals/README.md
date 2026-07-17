# Behavioral evaluation workflow

The default GitHub workflow performs static validation of evaluation definitions. It does not execute an AI agent and must not be interpreted as behavioral pass coverage.

## Prepare workspaces

Run the manual **LemonSlice behavioral evaluations** workflow in `prepare` mode, or run:

```bash
python evals/materialize_workspaces.py --output artifacts/eval-inputs
```

Each workspace contains the fixture, `_prompt.md`, and a small runner contract. An external agent executor should operate on a disposable copy of each workspace.

## Required result files

Each materialized result directory must contain:

- `_meta.json` with `selected_skill`;
- `_response.md`, or a `response` string in `_meta.json`;
- `_command-results.json` when the case declares commands.

Example command result:

```json
{
  "isolated": true,
  "results": [
    {
      "command": "npm test",
      "returncode": 0,
      "stderr": "",
      "stdout": "tests passed"
    }
  ]
}
```

The command executor—not `run_evals.py`—is responsible for isolation. It should use a disposable container or VM with no network, no inherited secrets, a non-root user, bounded CPU/memory/processes, a strict timeout, no Docker socket, and a writable temporary workspace only.

## Score results

```bash
python evals/run_evals.py --results-dir results
```

The manual workflow's `score` mode downloads an artifact named `agent-results` from a supplied workflow run ID and uploads the scoring output plus per-case result workspaces.
