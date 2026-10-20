# Temporary reviewer access

The public frontend requires a provisioned, short-lived identity for prediction, history and audit operations. Public Signup and external organizational OIDC are deferred. Do not create a permanent public administrator account or place tokens in a ticket, README, screenshot, shell history or repository.

An authorized operator should first confirm the intended reviewer role and existing database entitlement. A reviewer role has review permissions and is not interchangeable with the engineer role used for the full prediction walkthrough. For a temporary full-workflow demonstration, use the least privileged existing engineer entitlement that can create and read its own analyses. The local cloud-identity helper generates a signed access token for an existing entitlement; it does not create a database user or role.

On the trusted operator workstation, with the existing ignored signing material already present, run:

```powershell
.\.venv\Scripts\python.exe deployment/azure/cloud-identity.py token --role engineer
```

The helper writes the short-lived token to the ignored `artifacts/azure-preflight/cloud-private/` directory and prints only a status message. It expires after 840 seconds (14 minutes). Deliver it through a secure, temporary channel to the intended person, direct them to the public **Provisioned identity** screen, and allow it to expire after the session. The browser keeps the connected token in memory and requires reconnection after refresh. If the existing signing material or entitlement is unavailable, stop and ask the project owner to provision access; do not initialize new cloud signing material or change Azure configuration as part of this guide.

The [public walkthrough](assets/demo/walkthrough.webm) lets interviewers inspect the product without any credential. It hides identifiers and does not include the token entry.
