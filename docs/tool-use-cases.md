# Rubrik MCP tools — use-case guide

Each tool wraps one tightly-scoped KQL question. Together they cover the four most common cyber-resilience conversations a Rubrik AE or SE has with a customer.

## 1. `Rubrik_Backup_Posture_Summary`

**Question:** "Across everything Rubrik protects, what's the posture right now?"

**Who asks:** Backup admin, CISO, IT director.

**Returns:** Asset count, Protected vs Unprotected, In/Out-of-Compliance, AwaitingFirstFull, total + missed snapshots, unique clusters and SLA domains, total local/archive storage, average data reduction, top object types.

**Why it matters:** Single-pane executive view of the backup estate. Replaces a sentence like "I think we're 90% protected" with hard numbers.

## 2. `Rubrik_Out_Of_Compliance_Assets`

**Question:** "Where exactly are we missing SLA?"

**Who asks:** Backup admin, compliance officer, auditor.

**Returns:** Per cluster × SLA domain × object type — how many assets are out of compliance for snapshot, archival, replication; aggregate missed-snapshot count; oldest/newest LastSnapshot; average archival and replication lag in days; example asset names.

**Why it matters:** Goes from "we have SLA failures" to "Gold-Tier1-Production SLA on `rubrik-prd-east-01` has 41 archival failures averaging 7-day lag — here are 10 of them" in one tool call.

## 3. `Rubrik_Unprotected_Asset_Hunt`

**Question:** "What's not protected at all?"

**Who asks:** Security lead, IT operations, backup admin.

**Returns:** Objects that are Unprotected, AwaitingFirstFull, or have TotalSnapshots == 0, grouped by ObjectType × ClusterName × OrgName. Includes provisioned/used bytes, example asset names, locations.

**Why it matters:** Unprotected production VMs and databases are the single biggest blind spot in any backup estate. This tool surfaces drift and onboarding lag in one query.

## 4. `Rubrik_Snapshot_Failure_Triage`

**Question:** "Which assets keep missing their snapshots and why?"

**Who asks:** Backup admin, on-call engineer.

**Returns:** Per cluster × SLA × object type — distinct assets with misses, total misses, max misses on a single asset, average archival/replication lag, oldest LastSnapshot, top offenders by name.

**Why it matters:** Drives the daily/weekly triage rhythm. Pairs cleanly with a follow-up call to `Rubrik_Out_Of_Compliance_Assets` for the full impact picture.

## 5. `Rubrik_Storage_Capacity_Risk`

**Question:** "Where is storage growth and reduction working against us?"

**Who asks:** Backup admin, capacity planning, infrastructure architect.

**Returns:** Per cluster — assets, local storage GB, logical/physical/used bytes, average data reduction, average logical data reduction, count of poor-reduction assets (<1.5x), archive and replica bytes.

**Why it matters:** Brings capacity planning into the same agent surface as compliance and protection. Identifies "cluster X has lots of logical data with poor reduction — investigate the workloads ingesting raw video or already-compressed payloads."
