# Dependency Bot Workflows Should Not Get Broad Tokens by Accident

Dependency bot pull requests often trigger CI workflows, metadata checks, label
automation, and sometimes merge automation. Those workflows can be useful, but
they deserve explicit token permissions. A workflow that references Dependabot
or Renovate and leaves `permissions` implicit is harder to reason about than one
that states exactly what it needs.

The riskiest pattern is `permissions: write-all`. It grants broad write access
even when a workflow only needs to read contents or update a pull request. A
better pattern is least privilege at the workflow or job level:

```yaml
permissions:
  contents: read
  pull-requests: write
```

Some merge jobs do need write permissions. The point is to isolate that need and
document it in configuration, not inherit broad access everywhere.

`bot-policy-guard` flags dependency bot workflows with implicit permissions,
`write-all`, or broad write scopes such as `contents`, `actions`, `packages`, or
`security-events`. The remediation text points maintainers toward explicit,
narrow permissions.

Run it locally:

```bash
bot-policy-guard . --format markdown --output bot-policy-audit.md
```

The resulting report is designed to be copied into a pull request, security
review, or platform baseline issue.
