from __future__ import annotations

"""Interactive terminal demo for the Rubrik Sentinel MCP tools."""

import argparse
import asyncio
import json
import os
from typing import Any

from dotenv import load_dotenv

from sentinel_mcp_demo.client import MCPToolResult, SentinelMCPClient
from sentinel_mcp_demo.mock import MockSentinelMCPClient


RUBRIK_TOOLS = {
    "posture": "Rubrik_Backup_Posture_Summary",
    "compliance": "Rubrik_Out_Of_Compliance_Assets",
    "unprotected": "Rubrik_Unprotected_Asset_Hunt",
    "failure": "Rubrik_Snapshot_Failure_Triage",
    "storage": "Rubrik_Storage_Capacity_Risk",
}

TOOL_ROUTES = [
    (("compliance", "out of compliance", "sla", "archival", "replication"), RUBRIK_TOOLS["compliance"]),
    (("unprotected", "awaiting", "no snapshot", "no backup", "missing backup", "first full"), RUBRIK_TOOLS["unprotected"]),
    (("failure", "missed", "miss", "failed snapshot", "snapshot failure", "triage", "skipped"), RUBRIK_TOOLS["failure"]),
    (("storage", "capacity", "data reduction", "growth", "usage", "tb", "gb"), RUBRIK_TOOLS["storage"]),
]

EXAMPLE_PROMPTS = [
    "Summarize Rubrik backup posture",
    "Show out-of-compliance Rubrik assets",
    "Hunt unprotected Rubrik objects",
    "Triage Rubrik snapshot failures",
    "Show Rubrik storage capacity risk",
]


def parse_json_env(name: str, default: dict[str, Any]) -> dict[str, Any]:
    raw = os.getenv(name)
    if not raw:
        return default
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{name} must be valid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be a JSON object.")
    return value


def render_arguments(message: str, template: str, defaults: dict[str, Any]) -> dict[str, Any]:
    rendered = template.replace("{message}", message)
    try:
        args = json.loads(rendered)
    except json.JSONDecodeError as exc:
        raise ValueError(f"MCP_TOOL_ARGUMENT_TEMPLATE rendered invalid JSON: {exc}") from exc
    if not isinstance(args, dict):
        raise ValueError("MCP_TOOL_ARGUMENT_TEMPLATE must render to a JSON object.")
    return {**args, **defaults}


def select_tool(prompt: str) -> str:
    configured = os.getenv("SENTINEL_MCP_TOOL", "").strip()
    prompt_lower = prompt.lower()
    for keywords, tool_name in TOOL_ROUTES:
        if any(keyword in prompt_lower for keyword in keywords):
            return tool_name
    return configured or RUBRIK_TOOLS["posture"]


def create_mcp_client() -> SentinelMCPClient | MockSentinelMCPClient:
    mode = os.getenv("MCP_DEMO_MODE", "mock").strip().lower()
    if mode == "real":
        return SentinelMCPClient(
            collection=os.getenv("SENTINEL_MCP_COLLECTION"),
            server_url=os.getenv("SENTINEL_MCP_SERVER_URL"),
        )
    if mode == "mock":
        return MockSentinelMCPClient()
    raise ValueError("MCP_DEMO_MODE must be 'mock' or 'real'.")


def dataset_rows(result: MCPToolResult) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in result.content:
        if item.get("type") != "text":
            continue
        text = str(item.get("text", ""))
        try:
            frames = json.loads(text)
        except json.JSONDecodeError:
            continue
        if not isinstance(frames, list):
            continue
        primary = next(
            (
                frame for frame in frames
                if isinstance(frame, dict)
                and frame.get("FrameType") == "DataTable"
                and frame.get("TableKind") == "PrimaryResult"
            ),
            None,
        )
        if not primary:
            continue
        columns = [column.get("ColumnName", "") for column in primary.get("Columns", [])]
        for row in primary.get("Rows", []):
            rows.append({columns[index]: value for index, value in enumerate(row) if index < len(columns)})
    return rows


def summarize(prompt: str, tool_name: str, rows: list[dict[str, Any]], raw_text: str) -> str:
    if not rows:
        return raw_text or f"{tool_name} completed for: {prompt}"

    row = rows[0]
    if tool_name == RUBRIK_TOOLS["compliance"]:
        return (
            f"Out-of-compliance: SLA {row.get('SlaDomainName')} on cluster {row.get('ClusterName')} "
            f"({row.get('ObjectType')}) -> {row.get('OutOfComplianceAssets')} assets failing "
            f"(archival {row.get('ArchivalGap')} | replication {row.get('ReplicationGap')} | snapshot {row.get('SnapshotGap')}). "
            f"Missed snapshots: {row.get('MissedSnapshots')}; oldest LastSnapshot: {row.get('OldestLastSnapshot')}."
        )
    if tool_name == RUBRIK_TOOLS["unprotected"]:
        return (
            f"Unprotected hunt: {row.get('UnprotectedAssets')} {row.get('ObjectType')} objects on "
            f"{row.get('ClusterName')} ({row.get('OrgName')}) — {row.get('AwaitingFirstFullCount')} awaiting first full, "
            f"{row.get('NoSnapshotsCount')} with zero snapshots."
        )
    if tool_name == RUBRIK_TOOLS["failure"]:
        return (
            f"Snapshot triage: {row.get('AssetsWithMisses')} assets on {row.get('ClusterName')} / "
            f"{row.get('SlaDomainName')} ({row.get('ObjectType')}) racked up {row.get('TotalMisses')} misses "
            f"(max {row.get('MaxMissesOnOneAsset')} on one asset). "
            f"Avg lag — archival: {row.get('AvgArchivalLagDays')}d, replication: {row.get('AvgReplicationLagDays')}d."
        )
    if tool_name == RUBRIK_TOOLS["storage"]:
        return (
            f"Storage risk: {row.get('ClusterName')} -> {row.get('Assets')} assets / {row.get('StorageGB')} GB local, "
            f"avg data reduction {row.get('AvgDataReduction')}x ({row.get('PoorReductionAssets')} poor-reduction assets)."
        )

    return (
        f"Rubrik backup posture: {row.get('Assets')} objects, {row.get('Protected')} protected, "
        f"{row.get('OutOfCompliance')} out of compliance, {row.get('AwaitingFirstFull')} awaiting first full, "
        f"{row.get('TotalMissedSnapshots')} missed snapshots, {row.get('UniqueClusters')} clusters, "
        f"avg data reduction {row.get('AvgDataReduction')}x. Object types: {row.get('ObjectTypes')}."
    )


async def run_prompt(prompt: str, *, show_raw: bool) -> None:
    tool_name = select_tool(prompt)
    template = os.getenv("MCP_TOOL_ARGUMENT_TEMPLATE", '{"query":"{message}"}')
    defaults = parse_json_env("MCP_DEFAULT_ARGUMENTS", {})
    arguments = render_arguments(prompt, template, defaults)

    print(f"\nPrompt: {prompt}")
    print(f"Tool:   {tool_name}")
    print(f"Args:   {json.dumps(arguments, sort_keys=True)}")
    print("Status: calling Sentinel MCP...\n")

    client = create_mcp_client()
    await client.connect()
    try:
        result = await client.call_tool(tool_name, arguments)
    finally:
        await client.close()

    rows = dataset_rows(result)
    raw_text = result.text or json.dumps(result.content, indent=2)
    print("Summary")
    print("-------")
    print(summarize(prompt, tool_name, rows, raw_text))

    if show_raw:
        print("\nRaw MCP result")
        print("--------------")
        print(raw_text)


async def interactive_loop(show_raw: bool) -> None:
    print("Rubrik Sentinel MCP Terminal Demo")
    print("Type a prompt and press Enter. Type 'examples' to list prompts or 'quit' to exit.\n")
    print("Examples:")
    for prompt in EXAMPLE_PROMPTS:
        print(f"  - {prompt}")

    while True:
        try:
            prompt = input("\nrubrik-mcp> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return

        if not prompt:
            continue
        if prompt.lower() in {"quit", "exit", "q"}:
            return
        if prompt.lower() == "examples":
            for example in EXAMPLE_PROMPTS:
                print(f"  - {example}")
            continue

        try:
            await run_prompt(prompt, show_raw=show_raw)
        except Exception as exc:
            print(f"Error: {exc}")


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Run the Rubrik Sentinel MCP terminal demo.")
    parser.add_argument("--prompt", help="Run one prompt and exit instead of starting the interactive loop.")
    parser.add_argument("--show-raw", action="store_true", help="Print the formatted raw MCP/Kusto result.")
    args = parser.parse_args()

    if args.prompt:
        asyncio.run(run_prompt(args.prompt, show_raw=args.show_raw))
    else:
        asyncio.run(interactive_loop(show_raw=args.show_raw))


if __name__ == "__main__":
    main()
