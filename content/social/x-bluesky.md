# X / Bluesky Drafts

## Short

Dependency bots are useful until broad automerge, missing limits, unpinned
Actions, and write-all workflow tokens turn them into policy risk.

`bot-policy-guard` audits Renovate, Dependabot, and GitHub Actions configs
offline.

`bot-policy-guard . --fail-on medium`

## Thread

1. Dependency bot risk is usually not "the bot is bad." It is broad policy:
   automerge everywhere, no release-age soak, no update limits, unpinned workflow
   actions, and wide GitHub token permissions.

2. I built `bot-policy-guard`: a small Python CLI that scans Renovate,
   Dependabot, and GitHub Actions files offline.

3. It emits text, JSON, Markdown, or SARIF and includes rule IDs plus remediation
   suggestions.

4. First checks cover risky automerge, missing limits/groups, disabled security
   settings where detectable, unpinned Actions, and dependency bot workflow
   permissions.

5. Try:
   `bot-policy-guard . --format markdown --output bot-policy-audit.md`
