# LinkedIn Draft

Dependency bots reduce toil, but risky defaults can create a quiet supply-chain
path: broad automerge, missing update limits, unpinned GitHub Actions, and
workflow tokens with more write access than they need.

I built `bot-policy-guard`, an offline Python CLI that audits Renovate,
Dependabot, and GitHub Actions policy from repository files.

It reports rule IDs, severity, file locations, and remediation suggestions, with
text, JSON, Markdown, and SARIF output.

Example:

```bash
bot-policy-guard . --format sarif --output bot-policy-guard.sarif --fail-on medium
```

The first release focuses on practical checks:

- Automerge without release-age soak.
- Missing update limits and groups.
- Detectable disabled security update settings.
- GitHub Actions not pinned to full SHAs.
- Broad workflow token permissions around dependency bot automation.

Looking for maintainers and platform engineers to try it on real repositories
and share false positives.
