# KQL Queries — GitHub Events in Sentinel

## Option 1 (Native Connector) — GitHubAuditLogs_CL

```kql
// All audit events, newest first
GitHubAuditLogs_CL
| project TimeGenerated, action_s, actor_s, org_s
| order by TimeGenerated desc

// Events by action type
GitHubAuditLogs_CL
| summarize count() by action_s
| order by count_ desc

// Member additions and removals
GitHubAuditLogs_CL
| where action_s startswith "org.add_member" or action_s startswith "org.remove_member"
| project TimeGenerated, action_s, actor_s, user_s

// Repository visibility or settings changes
GitHubAuditLogs_CL
| where action_s startswith "repo."
| project TimeGenerated, action_s, actor_s, repo_s

// Branch protection changes
GitHubAuditLogs_CL
| where action_s startswith "protected_branch."
| project TimeGenerated, action_s, actor_s, repo_s
```

---

## Option 2 (Webhook Function) — GitHubEvents_CL

```kql
// All events, newest first
GitHubEvents_CL
| project TimeGenerated, github_event_type_s, repository_full_name_s
| order by TimeGenerated desc

// Volume by event type — useful for understanding what's flowing in
GitHubEvents_CL
| summarize count() by github_event_type_s
| order by count_ desc

// All push events with branch and actor
GitHubEvents_CL
| where github_event_type_s == "push"
| project TimeGenerated, actor_login_s, repository_full_name_s, ref_s

// Pull request activity
GitHubEvents_CL
| where github_event_type_s == "pull_request"
| project TimeGenerated, action_s, actor_login_s, repository_full_name_s,
          pull_request_title_s = tostring(parse_json(tostring(pull_request_s)).title)

// GitHub Actions workflow run results
GitHubEvents_CL
| where github_event_type_s == "workflow_run"
| project TimeGenerated, repository_full_name_s,
          workflow_name = tostring(parse_json(tostring(workflow_run_s)).name),
          conclusion = tostring(parse_json(tostring(workflow_run_s)).conclusion),
          head_branch = tostring(parse_json(tostring(workflow_run_s)).head_branch)
| where conclusion in ("failure", "cancelled")

// Secret scanning alerts
GitHubEvents_CL
| where github_event_type_s == "secret_scanning_alert"
| project TimeGenerated, repository_full_name_s, action_s,
          secret_type = tostring(parse_json(tostring(alert_s)).secret_type)

// Deployments
GitHubEvents_CL
| where github_event_type_s == "deployment_status"
| project TimeGenerated, repository_full_name_s,
          environment = tostring(parse_json(tostring(deployment_s)).environment),
          state = tostring(parse_json(tostring(deployment_status_s)).state)
```

---

## Sentinel Analytics Rule Examples

These can be saved as Sentinel analytics rules to generate incidents.

```kql
// Alert: push directly to main branch (bypass PR)
// Requires Option 2
GitHubEvents_CL
| where github_event_type_s == "push"
| where ref_s == "refs/heads/main"
| where sender_login_s != "github-actions[bot]"
| project TimeGenerated, actor_login_s, repository_full_name_s, ref_s

// Alert: failed production deployment
GitHubEvents_CL
| where github_event_type_s == "deployment_status"
| where tostring(parse_json(tostring(deployment_s)).environment) == "production"
| where tostring(parse_json(tostring(deployment_status_s)).state) == "failure"

// Alert: new org member added outside business hours
GitHubAuditLogs_CL
| where action_s == "org.add_member"
| where hourofday(TimeGenerated) < 8 or hourofday(TimeGenerated) > 18
```
