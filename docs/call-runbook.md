# Rubrik Sentinel MCP demo — call runbook

## Pre-call (T-30 min)

1. `az login` and pick the subscription that hosts the Sentinel workspace.
2. `cd ~/rubrik-sentinel-mcp-demo && source .venv/bin/activate`.
3. Confirm `.env` has `MCP_DEFAULT_ARGUMENTS={"workspaceId":"..."}` and `MCP_DEMO_MODE=real`.
4. Smoke test:
   ```bash
   python3 terminal_demo.py --prompt "Summarize Rubrik backup posture"
   ```
5. Open VS Code with this repo + the Defender portal (https://security.microsoft.com) side-by-side.

## On-call story (10–12 minutes)

| Step | Say | Show |
| :-: | --- | --- |
| 1 | "You already stream Rubrik into Sentinel via the Security Store solution. MCP turns that data into agent-callable tools." | README architecture diagram |
| 2 | "Here's the live executive backup posture." | `Summarize Rubrik backup posture` |
| 3 | "Drill into SLA violations." | `Show out-of-compliance Rubrik assets` |
| 4 | "Now the scariest question — what's NOT protected?" | `Hunt unprotected Rubrik objects` |
| 5 | "Daily triage rhythm — missed snapshots." | `Triage Rubrik snapshot failures` |
| 6 | "And capacity planning in the same surface." | `Show Rubrik storage capacity risk` |
| 7 | "Same tool collection runs in VS Code, Copilot Studio, Foundry, Claude, ChatGPT." | Defender portal MCP collection page |
| 8 | "Production path: swap LogSeeder for the CCP connector; point the tools at the real `RubrikProtectionStatus_CL` table." | README "How to adapt for production" |

## Q&A cheat sheet

- **"How is auth handled?"** Azure CLI / DefaultAzureCredential token to Sentinel Platform Services (resource id `4500ebfb-89b6-4b14-a480-7f749797bfcd`).
- **"How do customers get these tools?"** Either publish via the management API (this repo's `scripts/publish-mcp-tools.py`) or via the Defender portal "Save as tool" UI flow.
- **"Can we add tools without code?"** Yes — paste KQL into Advanced Hunting and click *Save as tool*.
- **"Does it support multi-workspace?"** Tools take `workspaceId` as input — agent can pass a customer-specific value.
- **"Latency?"** First MCP call signs in to Sentinel (~1s) and then runs the underlying KQL query (~hundreds of ms for these aggregations).

## Backup plan

If live calls fail, set `MCP_DEMO_MODE=mock` and rerun the same prompts — the mock client returns realistic narrative output for the same five tools.
