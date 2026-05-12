# Sample tool runs

The terminal demo, in mock mode, produces this kind of output for each tool. Once LogSeeder populates `RubrikProtectionStatusDemo_CL` and the publish script lands the collection, the same prompts will return live KQL results in the same shape.

## Rubrik_Backup_Posture_Summary

```text
Rubrik backup posture for 77429a58-...-cdfe3cb73: 2,143 objects across 8 clusters.
- Protected: 1,902 (88.7%)
- Out of compliance: 187 (snapshot 92 | archival 64 | replication 31)
- Awaiting first full: 24
- Local storage: 142 TB | Archive: 89 TB | Replica: 47 TB
- Avg data reduction: 3.4x
```

## Rubrik_Out_Of_Compliance_Assets

```text
Out-of-compliance: 187 objects miss SLA.
- 'Gold-Tier1-Production' SLA on rubrik-prd-east-01 has 41 archival failures
- 'PCI-Compliance-7yr' SLA has 12 replication failures (regulated workloads)
- Oldest LastSnapshot: 14 days (rubrik-edge-phoenix-01)
```

## Rubrik_Unprotected_Asset_Hunt

```text
Unprotected hunt: 73 objects exposed.
- 24 awaiting first full (newly registered VMs and MSSQL DBs)
- 18 marked Unprotected by policy on production clusters
- 31 with zero snapshots (likely DoNotProtect drift)
- Top object types: VmwareVirtualMachine, MssqlDatabase
```

## Rubrik_Snapshot_Failure_Triage

```text
Snapshot triage: 211 missed snapshots across 64 assets.
- Worst offender: 'Gold-Tier1-Production' on rubrik-prd-west-01 (38 misses)
- Max misses on one asset: 20
- Avg archival lag: 4.2 days | replication lag: 2.7 days
```

## Rubrik_Storage_Capacity_Risk

```text
Capacity risk: 142 TB local across 8 clusters.
- rubrik-prd-east-01: 58 TB local, data reduction 2.9x, 12 poor-reduction assets
- rubrik-edge-boston-01: 31 TB local, reduction 1.6x (review compression)
- rubrik-rsc-cloud-01: 22 TB archive, replication healthy
```
