# Option 1: Native Sentinel GitHub Connector

Microsoft Sentinel has a built-in GitHub data connector. It polls the GitHub Audit Log API on a schedule and writes events to a `GitHubAuditLogs_CL` custom table in Log Analytics. No Azure Functions, no Event Hub, no code.

---

## Prerequisites

- Log Analytics workspace with Sentinel enabled (from shared Terraform)
- GitHub organization admin access
- Classic GitHub PAT with `read:org` and `admin:org` scopes

## Steps

### 1. Create a GitHub PAT

1. Go to your GitHub org → `Settings → Developer settings → Personal access tokens → Tokens (classic)`
2. Generate a new token with scopes: `read:org`, `admin:org`
3. Copy the token — you won't see it again

### 2. Open the Sentinel GitHub Connector

1. In the Azure Portal, navigate to your Log Analytics workspace
2. Open **Microsoft Sentinel** from the left nav
3. Go to **Content hub** and search for **GitHub**
4. Install the **GitHub** solution
5. After installation, go to **Data connectors** and open **GitHub (using Audit Log API)**
6. Click **Open connector page**

### 3. Configure the Connector

1. On the connector page, enter:
   - **Organization**: your GitHub org name
   - **GitHub PAT**: the token from Step 1
2. Click **Connect**
3. Status should change to **Connected** within a few minutes

### 4. Verify Data is Flowing

Run this KQL query in Log Analytics (**Logs** in the Azure portal):

```kql
GitHubAuditLogs_CL
| take 10
| project TimeGenerated, action_s, actor_s, org_s
```

It may take 5–10 minutes for the first events to appear. Trigger some activity in your GitHub org (create a team, change a setting, invite a member) to generate audit events.

---

## Notes

- The connector polls every 5 minutes; there is no push/webhook option for this connector
- It captures the org-level audit log — the same events visible at `https://github.com/organizations/{org}/audit-log`
- Repository-level events (pushes, PRs, Actions runs) are **not** captured by this connector — those require Option 2
