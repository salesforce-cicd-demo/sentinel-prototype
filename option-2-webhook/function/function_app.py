import azure.functions as func
import base64
import datetime
import hashlib
import hmac
import json
import logging
import os

import requests

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


# =============================================================================
# Log Analytics HTTP Data Collector API
# =============================================================================

def _build_signature(workspace_id: str, workspace_key: str, body: str, date: str) -> str:
    """Build the SharedKey authorization header for Log Analytics."""
    content_length = len(body.encode("utf-8"))
    string_to_hash = "\n".join([
        "POST",
        str(content_length),
        "application/json",
        f"x-ms-date:{date}",
        "/api/logs",
    ])
    decoded_key = base64.b64decode(workspace_key)
    signature = base64.b64encode(
        hmac.new(decoded_key, string_to_hash.encode("utf-8"), digestmod=hashlib.sha256).digest()
    ).decode("utf-8")
    return f"SharedKey {workspace_id}:{signature}"


def post_to_log_analytics(workspace_id: str, workspace_key: str, records: list, log_type: str) -> None:
    """POST a list of records to a Log Analytics custom table."""
    body = json.dumps(records)
    date = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    signature = _build_signature(workspace_id, workspace_key, body, date)

    url = f"https://{workspace_id}.ods.opinsights.azure.com/api/logs?api-version=2016-04-01"
    headers = {
        "Content-Type": "application/json",
        "Authorization": signature,
        "Log-Type": log_type,
        "x-ms-date": date,
        "time-generated-field": "created_at",
    }

    response = requests.post(url, data=body.encode("utf-8"), headers=headers)
    response.raise_for_status()


# =============================================================================
# GitHub webhook signature verification
# =============================================================================

def _verify_signature(payload: bytes, signature_header: str, secret: str) -> bool:
    """Verify GitHub's HMAC-SHA256 webhook signature."""
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(
        secret.encode("utf-8"), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature_header, expected)


# =============================================================================
# Azure Function handler
# =============================================================================

@app.route(route="github-webhook", methods=["POST"])
def github_webhook(req: func.HttpRequest) -> func.HttpResponse:
    event_type = req.headers.get("X-GitHub-Event", "unknown")
    delivery_id = req.headers.get("X-GitHub-Delivery", "")
    logging.info("Received GitHub event: %s (delivery: %s)", event_type, delivery_id)

    # Verify signature if a secret is configured. Reject if secret is set
    # but signature is missing or invalid; pass through if no secret is set
    # (useful for initial testing — set the secret before going to production).
    webhook_secret = os.environ.get("GITHUB_WEBHOOK_SECRET", "")
    if webhook_secret:
        signature = req.headers.get("X-Hub-Signature-256", "")
        if not _verify_signature(req.get_body(), signature, webhook_secret):
            logging.warning("Webhook signature verification failed for delivery %s", delivery_id)
            return func.HttpResponse("Unauthorized", status_code=401)

    try:
        payload = req.get_json()
    except ValueError:
        return func.HttpResponse("Invalid JSON body", status_code=400)

    # Flatten GitHub's event metadata into the record so it's queryable in KQL
    record = {
        **payload,
        "github_event_type": event_type,
        "github_delivery_id": delivery_id,
    }

    workspace_id = os.environ["LOG_ANALYTICS_WORKSPACE_ID"]
    workspace_key = os.environ["LOG_ANALYTICS_WORKSPACE_KEY"]

    try:
        post_to_log_analytics(workspace_id, workspace_key, [record], "GitHubEvents")
        logging.info("Forwarded %s event to Log Analytics", event_type)
        return func.HttpResponse("OK", status_code=200)
    except requests.HTTPError as exc:
        logging.error("Log Analytics rejected the payload: %s", exc)
        return func.HttpResponse("Failed to forward to Log Analytics", status_code=500)
