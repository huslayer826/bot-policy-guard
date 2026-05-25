# Submission Plan

This file is a draft plan for submitting `bot-policy-guard` to relevant lists.
It is not a real pull request and does not create any external submissions.

## Candidate Lists

- Awesome Supply Chain Security
- Awesome GitHub Actions
- Awesome DevSecOps
- Awesome Python CLI tools

## Checklist Before Submitting

- Confirm package is published or installable from a tagged release.
- Confirm `huslayer826` GitHub URLs match the published repository URL.
- Make sure the README has a short, accurate install command.
- Keep the description under each list's preferred length.
- Follow each list's alphabetical ordering and contribution rules.

## Draft PR Entry

```markdown
- [bot-policy-guard](https://github.com/huslayer826/bot-policy-guard) - Offline CLI
  that audits Renovate, Dependabot, and GitHub Actions dependency automation
  policy for risky automerge, missing limits, ungrouped updates, unpinned
  actions, and broad workflow token permissions.
```

## Draft PR Description

```markdown
Adds bot-policy-guard, a dependency-light Python CLI for auditing dependency bot
configuration risk in Renovate, Dependabot, and GitHub Actions workflows.

It runs offline, emits text/JSON/Markdown/SARIF, and includes remediation
guidance for each rule.
```
