# Option 2: GitHub Webhooks → Azure Function → Log Analytics

GitHub fires webhook events in real time to an HTTPS endpoint. This option uses an Azure Function as that endpoint — it validates the webhook signature, adds event metadata, and POSTs the payload to Log Analytics via the HTTP Data Collector API. Events land in a `GitHubEvents_CL` custom table in Sentinel within seconds.

## Architecture

```
GitHub org
  │  webhook (HTTPS POST, signed with HMAC-SHA256)
  ▼
Azure Function (github-webhook endpoint)
  │  validates signature
  │  adds event metadata (event type, delivery ID)
  │  POST to Log Analytics HTTP Data Collector API
  ▼
Log Analytics workspace (GitHubEvents_CL table)
  ▼
Microsoft Sentinel
```

## Prerequisites

- Log Analytics workspace + Sentinel (from shared Terraform)
- Function App deployed (from shared Terraform)
- Azure Functions Core Tools: `brew install azure-functions-core-tools@4`
- Azure CLI authenticated: `az login`

## Setup

### 1. Apply shared Terraform

```bash
cd ../terraform
terraform init
terraform apply
```

### 2. Generate a webhook secret

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Run function locally

```sh
pip install -r requirements.txt

# Set the environment variables the function expects in your ./function/local.settings.json
```json
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "LOG_ANALYTICS_WORKSPACE_ID": "<redacted>",
    "LOG_ANALYTICS_WORKSPACE_KEY": "<redacted>",
    "GITHUB_WEBHOOK_SECRET": "<redacted>",
    "AzureWebJobsStorage": "UseDevelopmentStorage=true"
  }
}
```

# Start the function locally
func start
```

### 4. Start ngrok

```sh
# Expose port 7071 (Azure Functions default) to the internet
ngrok http 7071
```

### 6. Configure the GitHub webhook

1. Go to your GitHub org → **Settings → Webhooks → Add webhook**
2. Fill in:
   - **Payload URL**: `https://<your ngrok hostname>`
   - **Content type**: `application/json`
   - **Secret**: the secret from Step 4
   - **Which events**: start with **Send me everything** for the prototype, narrow later
3. Click **Add webhook**

GitHub will send a ping event immediately. Check the terminal output to confirm it returned HTTP 200.

### 7. Verify data in Log Analytics

```kql
GitHubEvents_CL
| take 10
| project TimeGenerated, github_event_type_s, repository_full_name_s
```

Trigger some activity (push a commit, open a PR) and events should appear within seconds.

---

## Extending

To capture specific event types differently (e.g., route secret scanning alerts to a separate table), add logic to `function_app.py` before the `post_to_log_analytics` call:

```python
log_type = "GitHubSecurityAlerts" if event_type == "secret_scanning_alert" else "GitHubEvents"
post_to_log_analytics(workspace_id, workspace_key, [record], log_type)
```

Each `log_type` value creates a separate `<log_type>_CL` table in Log Analytics.
