from __future__ import annotations

"""Mock MCP client used when the terminal demo runs without Azure connectivity."""

import json
from typing import Any

from .client import MCPTool, MCPToolResult


class MockSentinelMCPClient:
    """Return deterministic MCP-like results for offline presenter practice."""

    def __init__(self) -> None:
        ws = {"type": "object", "properties": {"workspaceId": {"type": "string"}}}
        self.tools = [
            MCPTool(name="Rubrik_Backup_Posture_Summary",
                    description="Summarize Rubrik Security Cloud backup posture: protection, compliance, snapshot, and storage coverage.",
                    input_schema=ws),
            MCPTool(name="Rubrik_Out_Of_Compliance_Assets",
                    description="Find Rubrik-managed assets out of compliance for snapshot, archival, or replication SLAs.",
                    input_schema=ws),
            MCPTool(name="Rubrik_Unprotected_Asset_Hunt",
                    description="Hunt Rubrik-managed objects that are unprotected, awaiting first full, or have zero snapshots.",
                    input_schema=ws),
            MCPTool(name="Rubrik_Snapshot_Failure_Triage",
                    description="Triage Rubrik snapshot failures by cluster, SLA domain, and object type.",
                    input_schema=ws),
            MCPTool(name="Rubrik_Storage_Capacity_Risk",
                    description="Identify Rubrik cluster storage capacity and data-reduction risk.",
                    input_schema=ws),
        ]

    async def connect(self) -> None:
        return None

    async def close(self) -> None:
        return None

    async def list_tools(self) -> list[MCPTool]:
        return self.tools

    async def call_tool(self, tool_name: str, arguments: dict[str, Any] | None = None) -> MCPToolResult:
        args = arguments or {}
        workspace = args.get("workspaceId") or "mock-workspace"
        text = {
            "Rubrik_Backup_Posture_Summary": (
                f"Rubrik backup posture for {workspace}: 2,143 objects across 8 clusters.\n"
                "- Protected: 1,902 (88.7%)\n"
                "- Out of compliance: 187 (snapshot 92 | archival 64 | replication 31)\n"
                "- Awaiting first full: 24\n"
                "- Local storage: 142 TB | Archive: 89 TB | Replica: 47 TB\n"
                "- Avg data reduction: 3.4x\n"
                "- Recommended action: pivot into Out-of-Compliance and Snapshot-Failure tools"
            ),
            "Rubrik_Out_Of_Compliance_Assets": (
                f"Out-of-compliance for {workspace}: 187 objects miss SLA.\n"
                "- 'Gold-Tier1-Production' SLA on rubrik-prd-east-01 has 41 archival failures\n"
                "- 'PCI-Compliance-7yr' SLA has 12 replication failures (regulated workloads)\n"
                "- Oldest LastSnapshot: 14 days (rubrik-edge-phoenix-01)\n"
                "- Recommended action: open replication network + archive target tickets"
            ),
            "Rubrik_Unprotected_Asset_Hunt": (
                f"Unprotected hunt for {workspace}: 73 objects exposed.\n"
                "- 24 awaiting first full (newly registered VMs and MSSQL DBs)\n"
                "- 18 marked Unprotected by policy on production clusters\n"
                "- 31 with zero snapshots (likely DoNotProtect drift)\n"
                "- Top object types: VmwareVirtualMachine, MssqlDatabase\n"
                "- Recommended action: assign Gold-Tier1 SLA and trigger first full"
            ),
            "Rubrik_Snapshot_Failure_Triage": (
                f"Snapshot triage for {workspace}: 211 missed snapshots across 64 assets.\n"
                "- Worst offender: 'Gold-Tier1-Production' on rubrik-prd-west-01 (38 misses)\n"
                "- Max misses on one asset: 20\n"
                "- Avg archival lag: 4.2 days | replication lag: 2.7 days\n"
                "- Recommended action: investigate VSS quiescing on prod-sql-cluster-02"
            ),
            "Rubrik_Storage_Capacity_Risk": (
                f"Capacity risk for {workspace}: 142 TB local across 8 clusters.\n"
                "- rubrik-prd-east-01: 58 TB local, data reduction 2.9x, 12 poor-reduction assets\n"
                "- rubrik-edge-boston-01: 31 TB local, reduction 1.6x (review compression)\n"
                "- rubrik-rsc-cloud-01: 22 TB archive, replication healthy\n"
                "- Recommended action: rebalance high-logical/low-physical workloads"
            ),
        }.get(tool_name, f"Mock result for {tool_name}:\n{json.dumps(args, indent=2)}")

        return MCPToolResult(
            tool_name=tool_name,
            content=[{"type": "text", "text": text}],
            is_error=False,
        )
