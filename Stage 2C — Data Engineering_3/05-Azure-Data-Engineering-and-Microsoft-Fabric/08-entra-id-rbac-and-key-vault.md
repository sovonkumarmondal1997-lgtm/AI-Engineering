# 08 — Microsoft Entra ID, Azure RBAC, and Key Vault

## 1. Purpose, prerequisites, and learning objectives

Identity is a primary security boundary for Azure data platforms. A secure pipeline must prove **who** is calling, **what** that identity can do, **where** the permission applies, and **which network path** is allowed. Authentication proves identity; authorization decides whether an operation is permitted; network controls determine whether the endpoint can be reached. All three can fail independently.

**Prerequisites:** Azure subscription and resource-group basics; ADLS Gen2 containers, ADF pipelines, Synapse SQL, VNets and private endpoints; basic Azure CLI/Bicep; Python virtual environments and environment variables. Read the Stage 2C lessons on ADLS Gen2, ADF, Synapse and Azure Databricks first.

By the end, you should be able to:
- distinguish Entra identities, authentication methods, Azure RBAC role definitions, assignments, scopes and data-plane permissions;
- choose and grant a managed identity least-privilege access for a data flow;
- configure Key Vault access, recovery protection and safe Python retrieval;
- explain private endpoint/DNS/firewall interactions, encryption options, policy guardrails and audit trails;
- diagnose authorization versus networking errors without exposing secrets.

**Security boundary:** examples use placeholders. Do not put passwords, tokens, keys, connection strings, client secrets or credential-bearing URLs in source control, screenshots, logs or tickets. Cloud actions in this lesson are instructions, not claims of deployment or verification.

## 2. Entra ID identities and authentication fundamentals

Microsoft Entra ID is the identity provider for Azure resource identities and many application sign-ins. It issues tokens after authentication and policy evaluation; Azure services then authorize the token against their own role, ACL, database or application permissions.

| Identity object | What it represents | Typical use | Security note |
|---|---|---|---|
| User | A human account | Engineer, analyst, administrator | Use MFA and Conditional Access; avoid direct resource assignments where groups work |
| Group | A collection of users/service principals where supported | Team-based access | Assign resource roles to well-managed groups; review membership and group ownership |
| App registration | Application definition in a tenant | Configure app identity, redirect URIs, credentials, API permissions | Not itself the runtime credential; creates/relates to a service principal |
| Service principal | Tenant-local instance/security principal for an application | Automation using workload identity federation, certificate or secret | Prefer federation/certificates over long-lived client secrets when managed identity is not possible |
| Managed identity | Azure-managed service principal with credential lifecycle handled by Azure | ADF, Functions, VMs, supported Synapse/Databricks patterns | No application-managed password; still needs explicit permissions on each target |

**Authentication versus authorization:** a valid token does not imply data access. For example, a managed identity can successfully obtain an Entra token for Storage and still receive `403 AuthorizationPermissionMismatch` because it lacks the required data role or ADLS ACL. Conversely, correct RBAC does not fix DNS resolution or a blocked endpoint.

Use human identities for interactive administration and workload identities for applications. Avoid shared user accounts and embedding service-principal secrets in pipeline JSON. When a service supports managed identity directly, prefer it; when it does not, evaluate workload identity federation or a certificate-backed service principal and rotate/revoke credentials deliberately.

## 3. Azure RBAC: role definitions, assignments, scope and inheritance

A **role definition** describes permissions (for example `Actions`, `NotActions`, `DataActions`, `NotDataActions`). A **role assignment** binds a security principal to a role definition at a scope. These are different objects: creating a custom role does not grant it to anyone; assigning a role does not change the role's permission set.

A role assignment conceptually contains:
1. **Security principal** — user, group, service principal or managed identity.
2. **Role definition** — built-in or custom set of allowed operations.
3. **Scope** — the resource hierarchy level where the grant applies.

Scope hierarchy, broadest to narrowest:

```text
Management group
  └── Subscription
       └── Resource group
            └── Resource (e.g., storage account or Key Vault)
```

Assignments at a parent scope generally inherit to child scopes. A subscription-level `Contributor` can therefore manage many more resources than one resource-group assignment. Azure RBAC is additive: a narrower assignment does not cancel a broader grant. `NotActions`/`NotDataActions` are exclusions from that role definition, not global deny rules. Azure Policy can deny certain resource operations, but it is not a substitute for data authorization design.

**Built-in versus custom:** use built-in roles when their permission set matches the job. Create a custom role only when built-ins cannot meet a real least-privilege requirement, and maintain it as code with owner, rationale, review date and tests. Do not create a custom role just to avoid understanding a built-in role's scope.

Useful examples:
- `Reader`: read Azure resource configuration; not a general grant to read data inside Storage or SQL.
- `Contributor`: manage most resource configuration at its scope but cannot grant Azure RBAC access by itself. It is not equivalent to every data-plane role.
- `Storage Blob Data Reader`: read blob data at the assigned scope.
- `Storage Blob Data Contributor`: read, write and delete blob data at the assigned scope.
- `Key Vault Secrets User`: read secret values in a vault configured for Azure RBAC.
- `Key Vault Secrets Officer`: manage secrets, but not administer role assignments.
- `Key Vault Administrator`: broad Key Vault data-plane authority; not a routine application role.

Confirm the current built-in role permissions before assigning. Role names can be similar while control/data-plane permissions differ.

## 4. Control plane versus data plane

The **control plane** manages the Azure resource itself through Azure Resource Manager: create/update a storage account, change networking settings, configure tags, or assign roles (with a suitable role). The **data plane** operates on data inside the service: list/read/write blobs, retrieve a secret, execute a SQL query or use a key.

| Scenario | Likely permission layer | Example |
|---|---|---|
| View a storage account's properties | Control plane | `Reader` on the account |
| Create/update storage-account settings | Control plane | `Contributor` on the account/resource group, if justified |
| Download a blob using Entra authorization | Data plane | `Storage Blob Data Reader` plus any required ADLS ACLs |
| Upload/delete blobs | Data plane | `Storage Blob Data Contributor` plus any required ADLS ACLs |
| Retrieve a Key Vault secret value | Data plane | `Key Vault Secrets User` on the vault or narrower supported scope |
| Create a role assignment | Authorization administration | A role such as `Owner`, `User Access Administrator` or `Role Based Access Control Administrator`, subject to its permissions |

A control-plane `Contributor` assignment alone does not generally grant data-plane access to Storage when Entra authorization is used. Important exception: Storage account keys/SAS and other alternate authentication paths can bypass the intended Entra data-role model if enabled and exposed. Restrict shared-key access where feasible and govern SAS issuance.

**ADLS Gen2 ACL interaction:** RBAC data roles and POSIX-style ACLs both matter. A broad data role can grant access without needing a path ACL; when access is not covered by a broad data role, ACL traversal and read/write/execute permissions matter. To rely on directory ACLs, avoid accidentally granting a broad data role that supersedes the intended path boundary. Test with the exact workload identity and authentication method.

## 5. System-assigned versus user-assigned managed identity

| Property | System-assigned | User-assigned |
|---|---|---|
| Lifecycle | Created with a supported Azure resource; deleted when that resource/identity is removed | Independent Azure resource; can be attached to supported resources and managed separately |
| Sharing | Tied to one resource | Can be reused across multiple supported resources (only when sharing is intentional) |
| Replacement | Recreating the resource generally means a new identity and new grants | Can survive resource replacement; grants remain until explicitly removed |
| Best fit | Simple one-resource workload identity | Stable identity across deployments, pre-provisioned permissions, or multiple workloads that genuinely share a trust boundary |
| Main risk | Resource recreation can change the principal | Over-sharing expands blast radius; detached identity can retain permissions unnecessarily |

Both identities require explicit authorization on every target. Attaching a user-assigned identity does not grant it access to Storage or Key Vault automatically. Assign only the identity the job is expected to use, and remove unused role assignments when the workload is retired.

**Service-specific note:** ADF supports system-assigned identity and user-assigned identity in supported linked-service scenarios. Azure Functions commonly supports both. Synapse workspace identity can access supported resources after grants are made. Azure Databricks identity patterns depend on the feature and deployment design (for example Unity Catalog storage credentials using an access connector/managed identity); do not assume a generic identity can be attached to every Databricks compute mode. Check the service-specific documentation and supported authentication path.

## 6. Least-privilege identity map: ADF reads ADLS and writes to Synapse

Example flow: a Data Factory pipeline reads source files from an ADLS Gen2 landing container and copies rows to a Synapse dedicated SQL pool. The exact roles depend on linked-service authentication, sink type, SQL permission model, and whether the pipeline reads, writes, deletes or stages files.

| Principal | Target | Minimum access pattern (verify for chosen connector) | Scope |
|---|---|---|---|
| Human platform admins | Azure resources | Time-bound elevated resource administration through PIM; avoid standing Owner | Smallest management scope required |
| Data engineers group | ADF authoring resources | Data Factory Contributor or a narrower custom role if feasible; separate deployment permissions | ADF resource/resource group |
| ADF managed identity (source reader) | ADLS source container/files | `Storage Blob Data Reader`; for hierarchical namespace paths, verify required ACLs and connector behavior | Source container or storage account if narrower scope unsupported |
| ADF managed identity (sink writer) | Synapse SQL pool | Create contained database user for the Entra identity and grant only required database/schema/table permissions; use supported Synapse connector auth | Target database/schema/table permissions, not broad Azure Contributor |
| ADF managed identity (only if it retrieves a secret) | Key Vault | `Key Vault Secrets User` for secret retrieval under RBAC model | Specific vault; consider a dedicated vault for workload boundaries |
| Deployment identity | Resource provisioning and role assignment | Separate infrastructure deployment from runtime identity; role assignment permissions only where needed | Scoped deployment target; tightly controlled |
| Monitoring identity/operator | Logs and diagnostics | Read relevant monitoring data; no application data access unless required | Log Analytics workspace/monitoring scope |

The two ADF rows normally refer to the **same Data Factory managed identity** using different permissions on different targets—not two identities unless the design deliberately selects different supported credentials per linked service. Record the actual identity selected by each linked service.

The ADF identity does **not** automatically need `Contributor` on the storage account, subscription or Synapse workspace just to read files and write SQL rows. SQL data access is not granted by Azure resource RBAC alone: configure Entra authentication in Synapse and grant SQL database permissions to the intended principal. For example, after an Entra administrator and database owner have prepared the target database, the grant pattern is conceptually `CREATE USER [<data-factory-identity-name>] FROM EXTERNAL PROVIDER;` followed by narrowly scoped `GRANT INSERT`/`SELECT` (and only the operations required) on the target schema/table. Validate the exact SQL syntax, principal resolution and permissions for the chosen Synapse pool and connector before production use. The pipeline may also need access to intermediate staging storage or a managed private endpoint; add only if the selected connector requires it.

**Design review questions:** Which identity actually obtains the Storage token? Which identity connects to SQL? Is staging involved? Does a copy activity need list/read/write/delete? Is there an ACL boundary? Is the identity used by another workload? What is the narrowest scope supported by the service?

## 7. Key Vault configuration, retrieval, rotation and recovery

Key Vault stores **secrets** (passwords, tokens, connection strings), **keys** (cryptographic operations and encryption integration), and **certificates** (certificate lifecycle and associated keys). A secret is not an encryption key just because it is stored in Key Vault.

### Authorization model

Azure Key Vault supports two authorization models for data-plane operations:
- **Azure RBAC (recommended for most new designs):** role assignments are managed through Azure RBAC; the model cleanly separates vault management from data access. Example: `Key Vault Secrets User` for an application that only reads secret values.
- **Vault access policies (legacy model):** explicit secret/key/certificate permissions are stored on the vault. Under this model, principals with certain vault write permissions can potentially modify access policies, creating privilege-escalation risk. Avoid mixing assumptions between the two models; the active model determines how data-plane access is evaluated.

Vault `Contributor` or `Key Vault Contributor` is not the same as permission to read secret values. Conversely, a secrets-read role does not grant the ability to manage the vault resource or role assignments. Grant separate administration and secret-consumption roles.

For Azure RBAC vaults, choose the data role by object type and operation; these examples are not interchangeable:

| Need | Typical least-privilege built-in role | Boundary to remember |
|---|---|---|
| Read secret values | `Key Vault Secrets User` | Does not grant secret creation or update |
| Create/update/delete secrets | `Key Vault Secrets Officer` | Broader than a runtime that only consumes a secret |
| Read key metadata without key operations | `Key Vault Reader` | Does not expose secret values or key material |
| Perform cryptographic operations with keys | A suitable crypto role, such as `Key Vault Crypto User`, where supported | Does not grant general secret access |
| Manage certificates | A suitable certificate role, such as `Key Vault Certificates Officer` | Certificate management is distinct from secret retrieval |
| Manage the vault resource | `Key Vault Contributor` for control-plane operations | Does not grant access to secret values, keys, or certificates |

Role names and supported scope can evolve; check the current built-in-role definition before assignment. The active vault authorization model matters: Azure RBAC role assignments do not grant data access to a vault configured to use legacy access policies, and access-policy permissions are not evaluated as Azure RBAC data roles. Microsoft recommends RBAC for new designs. Microsoft Learn documents Azure RBAC as the default for new vaults using API version `2026-02-01` and later; deployments that pin an API version or use older templates must explicitly verify the effective model.

### Secure baseline

- Use a dedicated vault per application/environment or security boundary; separate production from development.
- Enable soft delete (enabled by default for new vaults) and purge protection according to retention requirements. Purge protection is effectively irreversible after enabling and prevents permanent purge during the retention period.
- Prefer RBAC authorization, private endpoints where required, public network access disabled where the network design supports it, and diagnostic logging.
- Use a managed identity for the workload and grant only required secret access. Don't put secret values in pipeline parameters, notebooks, logs, source files or exception messages.
- Use separate secrets for separate applications and environments; set owner, purpose, expiry and rotation process. Do not assume every secret type can rotate automatically.

### Rotation and revocation

Rotation is an operational workflow: issue a new credential in the downstream system, update the Key Vault secret version, verify consumers use the new version, then revoke the old credential after a controlled overlap. Coordinate caches, connection pools, scheduled jobs and rollback. For customer-managed encryption keys, rotation has service-specific behavior and timing; don't disable an old key version until the service has safely switched. Secret versioning alone does not rotate a database password at the database.

Audit access and administrative changes. Key Vault diagnostic settings can route relevant logs to Log Analytics, Storage or Event Hubs. Enabling diagnostics is not retroactive; define retention and alerting before an incident.

## 8. Safe Python access with DefaultAzureCredential

Install dependencies in a virtual environment:

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install azure-identity azure-keyvault-secrets
```

`DefaultAzureCredential` tries a chain of supported credential sources. For local development, sign in with an approved developer identity (for example Azure CLI) and ensure that identity has the required Key Vault data role. In Azure, use a supported managed identity and grant that identity access. Avoid accidentally using a developer's cached identity in a deployed environment; configure and test the intended credential path, and use explicit credential configuration when ambiguity is a risk.

```python
import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

vault_url = os.environ["KEY_VAULT_URL"]  # e.g. https://<vault-name>.vault.azure.net/
secret_name = os.environ.get("DB_PASSWORD_SECRET_NAME", "<secret-name>")

credential = DefaultAzureCredential()
client = SecretClient(vault_url=vault_url, credential=credential)

try:
    secret = client.get_secret(secret_name)
    database_password = secret.value  # Keep in memory only as long as needed.
    # Pass database_password directly to the database driver's secure API.
    # Never print it, interpolate it into SQL/log messages, or persist it to disk.
finally:
    client.close()
    credential.close()
```

The code is a minimal SDK example, not a complete database connection or proof of deployment. Supply `KEY_VAULT_URL` through deployment configuration (not a secret), install packages through the normal build process, and ensure network/DNS reachability. Catch exceptions at the application boundary and log only sanitized metadata (error category, operation, correlation ID if available)—never the secret value or credential object.

**Local development:** `az login` with an approved account, select the correct subscription when needed, and grant that user a narrowly scoped Key Vault role in a development vault. **Deployed environment:** enable/attach the chosen managed identity and grant it the Key Vault role. The local user and deployed managed identity are different principals and need separate authorization. If a private endpoint is enabled, the local machine must have a route and DNS resolution to that private endpoint; an RBAC grant cannot bypass network restrictions.

When using a **user-assigned** managed identity with `DefaultAzureCredential`, configure the credential selection for the runtime. For supported managed-identity environments, set `AZURE_CLIENT_ID` to the UAMI client ID when needed to disambiguate the identity; do not set it to the principal/object ID or resource ID. Validate the identity actually selected from the target runtime rather than inferring it from configuration alone.

## 9. Conditional Access, MFA, PIM and group design

Conditional Access evaluates signals and applies access controls to supported sign-ins. Common policies require MFA for administrators, block legacy authentication, require compliant devices for sensitive access, and apply risk-based controls where licensing supports them. Roll out policies using report-only mode and staged testing where available; maintain emergency access accounts according to the organization's documented break-glass standard and monitor them closely. Do not create an untested policy that could lock out all administrators.

Use groups aligned to job function and environment, such as `data-platform-dev`, `data-platform-prod-readonly`, and `security-operators`. Define group owners, approval requirements, access reviews and joiner/mover/leaver workflows. Avoid assigning resource access directly to individuals except for controlled exceptions.

Privileged Identity Management (PIM) supports eligible, time-bound role activation with controls such as MFA, justification, approval, and notifications where configured/licensed. Keep routine access non-privileged; make Owner and role-assignment administration eligible rather than permanently active where operationally feasible. PIM does not replace least privilege: activating an unnecessarily broad role is still broad access.

Human identities and workload identities are not interchangeable. Conditional Access/MFA policies generally govern human sign-ins; workloads should use managed identities or supported federation rather than interactive MFA or stored human credentials. Apply workload-specific protections, restrict where identity can be used, and audit its permissions.

## 10. Private endpoints, DNS, firewalls, NSGs and service endpoints

A private endpoint is a network interface with a private IP in a VNet that privately connects to a supported Azure service over Private Link. It is not an authorization grant. Access still requires valid identity and data permissions.

A typical private Storage path:

```text
Workload subnet / private runtime
        │
        ├── DNS query for <account>.blob.core.windows.net
        │       └── Private DNS zone privatelink.blob.core.windows.net
        │               └── private endpoint IP in VNet
        │
        └── HTTPS to Storage private endpoint ──► Entra token + data RBAC/ACL
```

For ADLS Gen2, clients may need both Blob (`blob`) and Data Lake (`dfs`) endpoints depending on operations and client behavior. Configure the relevant private endpoints and DNS zones/records for the service subresources you use. Link private DNS zones to the VNets that need resolution, or configure approved custom DNS forwarding. Validate from the actual workload subnet using DNS lookup and connectivity tests.

- **Private endpoint:** private IP and Private Link path; typically preferred for private access to PaaS services.
- **Service endpoint:** extends a subnet identity to a supported Azure service firewall; traffic still reaches the service's public endpoint, not a private IP. It is a different design from Private Link.
- **Storage firewall:** controls public-endpoint access from selected networks; setting default action to `Deny` matters for firewall rules. Disabling public network access blocks the public endpoint and requires a working private path for clients that must connect.
- **NSG:** filters network traffic at subnet/NIC boundaries where supported; it does not grant service-level authorization and cannot be used as a replacement for PaaS firewall configuration.
- **Private DNS:** maps the normal service name to the private endpoint IP in the private network context. Incorrect DNS can cause a private endpoint client to resolve a public IP and fail.

Private endpoint approval state, subnet routing, DNS, firewall settings, TLS and identity permissions must all align. For Storage, test public access from a genuinely external network after disabling public network access; testing only from an allowed VNet does not prove the public endpoint is blocked. Do not disable public access until a validated private path and recovery/admin route exist.

## 11. Encryption, Azure Policy, Defender for Cloud and IaC guardrails

### Encryption choices

- **Microsoft-managed keys (MMK):** Azure manages the service encryption keys and rotation. Azure Storage encrypts data at rest by default; encryption is not an optional substitute for network and identity controls.
- **Customer-managed keys (CMK):** the customer controls a key in Key Vault or Managed HSM and its lifecycle/permissions. This supports key-control and compliance requirements but introduces dependencies: key availability, identity permissions, soft delete/purge protection, rotation timing and recovery must be designed. Revoking or deleting the key can make data unavailable.
- **Infrastructure encryption / double encryption:** an additional service-managed infrastructure encryption layer for supported resources. For Azure Storage, infrastructure encryption must be enabled at account creation and cannot later be toggled on for that account. It is a compliance/defense-in-depth option, not automatically necessary for every workload.
- **Encryption in transit:** require secure transfer and current TLS settings; use HTTPS endpoints and do not disable certificate validation.

Do not confuse customer-managed keys with customer-provided per-request keys or with storing a database password in Key Vault.

### Azure Policy

Azure Policy evaluates resource properties and can audit, deny or deploy configurations depending on the definition/effect. A role definition grants actions; a policy definition expresses resource-compliance rules. A policy assignment attaches that rule at a scope with parameters/exclusions. `deny` blocks matching create/update requests; existing resources may be reported non-compliant but are not automatically repaired by a deny policy.

The lab includes a **custom illustrative policy** that denies Storage account create/update requests when `publicNetworkAccess` is not explicitly `Disabled`. Its rule uses the Storage resource type and the `Microsoft.Storage/storageAccounts/publicNetworkAccess` alias; validate the alias against current Azure Policy tooling before assignment. Because the condition is strict, an omitted property may also match and be denied. The policy does not create a private endpoint or prove that private connectivity works.

This policy may block deployments that rely on public endpoints, service endpoint firewall rules, trusted-service exceptions, or deployment-time access. Use a dedicated non-production subscription/resource group, test with `Audit` first or an unassigned definition, validate exemptions, then assign `Deny` only after a change review. Prefer the Microsoft built-in policy **Storage accounts should disable public network access** when it meets the requirement; inspect its current parameters/effects and assignment scope before use. Do not assign an untested deny policy broadly to production. A deny policy blocks matching create/update requests; it does not repair existing resources.

### Defender for Cloud and infrastructure-as-code review

Defender for Cloud provides security posture recommendations and, depending on plan, workload protection capabilities. It is not a firewall or an RBAC role. Review recommendations, regulatory compliance views and alerts; route actionable findings to an owner and track remediation. Capabilities and cost depend on enabled plans.

For Bicep/Terraform/ARM pull requests, review:
- public network access, firewall defaults, private endpoints and DNS links;
- TLS/secure transfer, encryption/CMK requirements and recovery protection;
- identity type, scope and role assignment principal IDs;
- Key Vault permission model, soft delete, purge protection and diagnostics;
- secrets in parameters, outputs, state files, pipeline variables and logs;
- broad `Owner`/`Contributor` roles, wildcard custom roles, and role assignment permissions;
- policy exemptions, scope, effect and impact on existing deployments.

Use secret references and managed identities rather than passing secret values through IaC parameters. Protect Terraform state and pipeline logs as sensitive data. Run static analysis and policy validation in CI, then deploy into a test scope before production.

## 12. Diagnostic logging and incident investigation

Use multiple evidence sources because they answer different questions:

- **Azure Activity Log:** subscription-level control-plane operations, such as resource updates and role assignment changes. Configure diagnostic settings to export it to Log Analytics/Storage/Event Hubs for retention and correlation.
- **Resource diagnostic logs:** service-specific data-plane/audit logs when supported and configured, including Key Vault audit events and relevant Storage logs. Diagnostic settings are configured per resource; not all categories are enabled by default.
- **Microsoft Entra sign-in logs:** human and workload sign-in events where available, including Conditional Access results and authentication failures. Workload identity logs can be a distinct log type; check tenant licensing and retention.
- **Azure Monitor / Log Analytics:** centralize supported logs, query across resources, define retention and alerts. Avoid logging credentials or sensitive payloads in application telemetry.

### Triage sequence for an access failure

1. Record UTC timestamp, operation, resource URI (without secret query parameters), correlation/request ID and sanitized error code.
2. Identify the **actual caller** (object/principal ID and tenant), not just the resource owner or pipeline author.
3. Verify token audience and authentication method; confirm the expected managed identity is enabled/attached.
4. Check role assignment at the right scope and correct data-plane role. Check group membership, ADLS ACLs, SQL grants and Key Vault's active authorization model.
5. Check private endpoint approval, DNS result, route/NSG, service firewall and public network access.
6. Allow for propagation delay after role changes, then retry with a bounded backoff. Do not keep broadening permissions until the error disappears.
7. Correlate Activity Log, Entra sign-in logs and service diagnostic logs. Capture evidence without secret values.
8. If compromise is suspected, contain the principal, remove unnecessary assignments/credentials, preserve logs, rotate affected secrets, and follow the organization's incident-response process.

An HTTP `403` alone does not prove an RBAC problem; it may indicate network policy, ACL, service configuration or data authorization. A DNS/connection timeout is more likely a network path issue but should still be verified.

## 13. Hands-on lab — `experiments/08_identity_keyvault/`

**Goal:** create a user-assigned managed identity, give it minimal ADLS data access, retrieve a Key Vault secret through `DefaultAzureCredential`, intentionally remove and restore a role assignment, validate a private endpoint path, and test an Azure Policy guardrail safely.

### Before you begin

Use a dedicated non-production subscription/resource group and a region supporting the selected services. Confirm permissions to create managed identities, role assignments, Key Vault, Storage, private endpoints, VNet/DNS resources and policy definitions/assignments. These are different permissions; do not assume a Contributor grant permits role assignment or policy assignment. Estimate costs, especially private endpoints and log ingestion. Define a cleanup plan.

The lab contains `README.md`, a Python sample, a policy JSON definition and a deployment checklist. Resource names and IDs are placeholders. No resources are created by reading this lesson.

### Lab sequence

1. **Create a user-assigned managed identity (UAMI).** Record its client ID, principal/object ID and resource ID separately. Attach it only to the supported workload that should use it.
2. **Grant the minimum ADLS data role.** For read-only listing/reading, assign `Storage Blob Data Reader` at the source container if the required scope is supported. If the workload must write, select the appropriate data role at the narrowest supported scope. Verify ACL behavior for hierarchical namespace paths. Do not grant `Contributor` at subscription scope.
3. **Configure Key Vault.** Prefer the Azure RBAC model. Enable soft delete and purge protection, configure diagnostics, and grant `Key Vault Secrets User` to the principal that will retrieve the secret. Store a dummy/non-production database password; never print it.
4. **Test Python locally.** Sign in as an approved developer identity and grant that human identity a development-only Key Vault data role. `DefaultAzureCredential` locally uses a developer credential from its chain; it does not impersonate the UAMI merely because the UAMI exists in Azure.
5. **Test in a deployed environment, where available.** Enable/attach the UAMI to a supported workload, configure the intended credential selection, ensure network/DNS reachability, and grant the UAMI its own role assignment. Verify that local and deployed identities are distinct and authorized separately.
6. **Break and restore authorization.** Remove only the lab identity's Storage role assignment. After propagation, attempt a benign read and record the sanitized error. Restore the exact role/scope and retest. Do not remove a shared production role or use broad permissions as a shortcut.
7. **Private endpoint.** Create a Storage private endpoint for required subresources, approve it, configure Private DNS zone(s), link the zone to the workload VNet, and test name resolution from the workload network. Only after a successful private-path test, disable Storage public network access in this disposable lab. Verify from an external network that the public path fails and from the VNet that private access still works.
8. **Azure Policy.** First inspect the provided policy definition and validate its field against the current Storage resource schema. Create the definition without assigning it broadly. Test `audit` or a non-production scoped `deny` assignment, attempt a new test storage account with public network access enabled, and confirm the deployment is denied by policy. Then test a compliant configuration. Remove the test assignment/resources when finished.
9. **Evidence and cleanup.** Record principal ID, role name/scope, policy assignment scope, sanitized errors, DNS results and Activity Log/diagnostic events. Never capture secret values, access tokens, passwords or credential-bearing screenshots. Remove test resources and review remaining role assignments.

### Role assignment and policy concepts to explain

- **Role definition:** the reusable permission set.
- **Role assignment:** binds a principal + role definition + scope.
- **Scope:** where the grant applies; parent assignments can inherit to children.
- **Identity permissions:** the caller needs the correct data-plane role/ACL/SQL grant on the target; the resource's own identity is not automatically the caller.
- **Propagation delay:** role changes may not be immediately effective; allow a short interval and retry safely before diagnosing other causes.
- **Private network/DNS:** a private endpoint needs an approved connection, correct service subresource, private DNS zone/record, VNet link/resolution and route; network reachability still does not grant data access.

## 14. Practice questions

1. Why can a principal with `Contributor` on a storage account still be unable to read a blob?
2. What are the three parts of a role assignment? How does scope inheritance affect blast radius?
3. When is a UAMI preferable to a system-assigned identity, and what risk does sharing introduce?
4. Which principal reads the Key Vault secret in local development versus a deployed workload?
5. Why is `Key Vault Contributor` not the right role for an application that needs to read a password?
6. Explain the difference between a private endpoint and a service endpoint. What role does Private DNS play?
7. Why can a deny policy break an otherwise valid deployment? How would you test it safely?
8. What is the operational risk of revoking a customer-managed key's access?
9. Which logs help determine who changed a role assignment, whether sign-in was blocked, and whether a Key Vault secret was accessed?
10. ADF can read ADLS but cannot insert into Synapse. List the identity, SQL permission and network checks you would perform.

## 15. Troubleshooting reference

| Symptom | Likely causes | Checks |
|---|---|---|
| Storage `403` | Missing data role, wrong principal, ACL, wrong auth mode | Caller object ID; role/scope; ACL traversal; whether shared key/SAS is being used |
| Key Vault `403` | Missing Key Vault data role, wrong authorization model, wrong principal | RBAC vs access policies; principal ID; role scope; audit event |
| Key Vault timeout/name resolution failure | Private endpoint/DNS/routing/firewall | DNS from runtime subnet; zone link/forwarding; endpoint approval; route and NSG |
| Local Python works, deployed code fails | Local user has access but workload identity does not; different network | Identify credential selected; grant deployed principal; check runtime DNS/network |
| Private endpoint resolves public IP | Missing/wrong private DNS record, zone not linked, custom DNS forwarding | Resolve service FQDN from actual VNet/runtime; check correct subresource and zone |
| Role added but access still denied | Propagation delay, token/cache, wrong scope or identity | Wait/retry with fresh process/token; inspect effective assignment and principal ID |
| Policy blocks deployment | Deny effect or assignment scope/parameters | Read deployment error and policy assignment ID; validate compliant properties and exemptions |
| ADF SQL write fails | SQL user/grant missing, wrong identity, private connectivity or staging issue | Linked-service auth type; contained user and schema/table grants; SQL firewall/private endpoint; staging prerequisites |

## 16. Checkpoint

- [ ] Explain Entra users, groups, service principals, app registrations and managed identities.
- [ ] Distinguish role definition from assignment, and control plane from data plane.
- [ ] Explain scope inheritance and why broad Owner/Contributor grants are dangerous.
- [ ] Draw a least-privilege ADF → ADLS → Synapse identity map.
- [ ] Retrieve a Key Vault secret with `DefaultAzureCredential` without logging it.
- [ ] Explain Conditional Access/MFA for humans and PIM for eligible privileged roles.
- [ ] Explain private endpoints, service endpoints, DNS, NSGs and firewall controls.
- [ ] Compare MMK, CMK and infrastructure/double encryption.
- [ ] Explain safe Azure Policy rollout and distinguish Activity Log, sign-in logs and resource diagnostics.

**Common mistakes:** Owner/Contributor everywhere; assigning roles directly to individuals instead of governed groups; assuming control-plane roles grant data access; confusing role definitions with assignments; leaving secrets in pipeline JSON; assuming a managed identity has permissions automatically; forgetting Private DNS; disabling public access before private connectivity works; treating a private endpoint as authorization; enabling a deny policy directly at a broad production scope; logging secrets; revoking CMK access without understanding data availability impact.

## 17. Official references

Use these Microsoft Learn references as the authoritative source for current service behavior and role requirements:

- [Azure role definitions](https://learn.microsoft.com/en-us/azure/role-based-access-control/role-definitions)
- [Azure built-in roles](https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles)
- [Managed identity for Azure Data Factory](https://learn.microsoft.com/en-us/azure/data-factory/data-factory-service-identity)
- [Azure RBAC versus Key Vault access policies](https://learn.microsoft.com/en-us/azure/key-vault/general/rbac-access-policy)
- [Key Vault RBAC guide and built-in data-plane roles](https://learn.microsoft.com/en-us/azure/key-vault/general/rbac-guide)
- [Azure Key Vault Python secrets quickstart](https://learn.microsoft.com/en-us/azure/key-vault/secrets/quick-create-python)
- [Azure Identity library for Python](https://learn.microsoft.com/en-us/python/api/overview/azure/identity-readme)
- [Conditional Access documentation](https://learn.microsoft.com/en-us/entra/identity/conditional-access/)
- [Privileged Identity Management](https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-configure)
- [Secure Azure Storage](https://learn.microsoft.com/en-us/azure/storage/common/secure-storage)
- [Storage network security](https://learn.microsoft.com/en-us/azure/storage/common/storage-network-security-overview)
- [Azure Storage private endpoints](https://learn.microsoft.com/en-us/azure/storage/common/storage-private-endpoints)
- [Azure Storage service encryption and key management](https://learn.microsoft.com/en-us/azure/storage/common/storage-service-encryption)
- [Enable infrastructure encryption](https://learn.microsoft.com/en-us/azure/storage/common/infrastructure-encryption-enable)
- [Azure Policy deny effect](https://learn.microsoft.com/en-us/azure/governance/policy/concepts/effect-deny)
- [Storage built-in policy reference](https://learn.microsoft.com/en-us/azure/storage/common/policy-reference)
- [Azure Policy aliases](https://learn.microsoft.com/en-us/azure/governance/policy/concepts/definition-structure-alias)
- [Grant permissions to a Synapse workspace managed identity](https://learn.microsoft.com/en-us/azure/synapse-analytics/security/how-to-grant-workspace-managed-identity-permissions)
- [Azure Monitor Activity Log](https://learn.microsoft.com/en-us/azure/azure-monitor/essentials/activity-log)
- [Create diagnostic settings](https://learn.microsoft.com/en-us/azure/azure-monitor/essentials/diagnostic-settings)
- [Microsoft Entra sign-in logs](https://learn.microsoft.com/en-us/entra/identity/monitoring-health/concept-sign-ins)

Service capabilities, licensing, supported identity options and role requirements can change. Verify the current documentation for the exact connector, SKU, region and authentication mode before production rollout.
