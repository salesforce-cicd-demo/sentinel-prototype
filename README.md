# GitHub Enterprise → Microsoft Sentinel Prototype

Two options for getting GitHub events into Sentinel, both backed by the same Log Analytics workspace. The goal is to evaluate them side-by-side before committing to an approach for WWCT's production setup.

## The Two Options

### Option 1: Native Sentinel GitHub Connector

Sentinel's built-in GitHub data connector polls the GitHub Audit Log API every ~5 minutes. No infrastructure beyond the Log Analytics workspace. Covers org-level admin events (member changes, settings changes, branch protection changes). Does not cover repo-level activity like pushes, PRs, or Actions runs.

**Best if:** the SIEM team's primary requirement is governance/admin audit trail.

→ See [option-1-native/README.md](option-1-native/README.md)

### Option 2: GitHub Webhooks → Azure Function → Log Analytics

GitHub fires webhook events in real time to an Azure Function. The function validates the HMAC signature and forwards the payload to Log Analytics. Covers every event type GitHub can emit — pushes, PRs, Actions runs, secret scanning alerts, deployments.

**Best if:** the SIEM team needs real-time visibility into code activity and CI/CD pipeline events, not just admin changes.

→ See [option-2-webhook/README.md](option-2-webhook/README.md)

## Shared Infrastructure

Both options need a Log Analytics workspace with Sentinel enabled. Apply the shared Terraform first.

### Prerequisites

- Azure CLI authenticated: `az login`
- Terraform installed

### Apply

```bash
cd terraform
terraform init
terraform apply -var "azure_subscription_id=<your-sub-id>"
```

### terraform.tfvars

```hcl
azure_subscription_id = "<your-subscription-id>"
```

## What You'll Be Able to Show

After setting up both options against your personal GitHub org, you'll have:

- **Option 1**: Org audit events visible in `GitHubAuditLogs_CL` — trigger some org changes to populate it
- **Option 2**: Real-time events in `GitHubEvents_CL` — push a commit or open a PR and watch it appear in seconds
- **KQL queries** ready to run in Sentinel showing both tables (see [option-2-webhook/kql-queries.md](option-2-webhook/kql-queries.md))
- **Sentinel analytics rule examples** that could fire incidents on specific conditions

This gives a concrete basis for the conversation with the SIEM team: you can show them both tables, explain the trade-offs, and ask them which events they actually care about rather than debating architecture in the abstract.

## Comparison

|                           | Option 1 (native connector)                                                                        | Option 2 (webhook function)                                                       |
|---------------------------|----------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| Setup complexity          | Low — UI only                                                                                      | Medium — Terraform + function deploy                                              |
| Setup time                | ~10 min                                                                                            | ~30 min                                                                           |
| Infrastructure            | Log Analytics only                                                                                 | + Storage account, Function App                                                   |
| Latency                   | ~5 minutes (polling)                                                                               | Seconds (real-time)                                                               |
| What it captures          | Org settings changes, team changes, member add/remove, repo visibility changes, PAT policy changes | Pushes, PRs, Actions runs, secret scanning alerts, deployments, plus audit events |
| Audit log (admin actions) | ✓                                                                                                  | ✓                                                                                 |
| Push / PR / branch events | ✗                                                                                                  | ✓                                                                                 |
| Actions workflow runs     | ✗                                                                                                  | ✓                                                                                 |
| Secret scanning alerts    | ✗                                                                                                  | ✓                                                                                 |
| Deployments               | ✗                                                                                                  | ✓                                                                                 |
| Ongoing maintenance       | None                                                                                               | Function app                                                                      |

If the SIEM team's primary interest is "who changed what in the GitHub admin settings," Option 1 covers that with no infrastructure to own. If they need code push activity, pipeline run status, or security alerts, they need Option 2.
foo
foo
