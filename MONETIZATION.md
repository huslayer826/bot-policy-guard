# Monetization

`bot-policy-guard` remains useful as a free open source CLI. Revenue paths should monetize policy depth, hosted visibility, and support, not basic local scans.

## GitHub Sponsors Tiers

Use these as the first GitHub Sponsors monthly tiers:

- `$5 - Maintainer supporter`: "Support safer dependency automation defaults for open source maintainers."
- `$25 - Rule supporter`: "Fund new Renovate, Dependabot, and GitHub Actions policy checks."
- `$150 - Platform team sponsor`: "Fund org-scale dependency-bot governance features and receive monthly rule notes."

README badge after activation:

```markdown
[![Sponsor](https://img.shields.io/badge/Sponsor-GitHub%20Sponsors-ea4aaa)](https://github.com/sponsors/huslayer826)
```

## Pro Feature

First paid feature: **Policy Pack for Dependency Automation**.

- Presets for strict, balanced, and OSS-maintainer profiles.
- CI snippets for SARIF upload and pull-request comments.
- Organization-specific exceptions documented as code.

Suggested price: `$29/month` individual, `$149/month` team.

## Hosted Version Pitch

Hosted product: **Dependency Bot Posture Dashboard**.

- GitHub App scans Renovate, Dependabot, and workflow files across repositories.
- Shows risky automerge, missing update limits, unpinned actions, and broad permissions.
- Tracks drift over time and opens remediation PRs later.

Initial infra later:

- GitHub App.
- Queue worker.
- Postgres.
- SARIF/report storage.
- Static dashboard.

Pricing hypothesis:

- `$99/month` for up to 25 repositories.
- `$299/month` for up to 100 repositories.
- Consulting upsell for dependency-automation policy rollout.

TAM read:

The early market is public maintainers and small platform teams already using Renovate or Dependabot. The wedge is strong because syntax validators exist, but posture review is not the default workflow.

## Content Plan

Drafts are ready in `content/`:

- `blog-post-1-risky-automerge.md`
- `blog-post-2-github-actions-pinning.md`
- `blog-post-3-workflow-token-permissions.md`

Social launch drafts are ready in `content/social/`.

## Activation

Follow `ACTIVATION.md` to publish the repository, enable GitHub Pages, configure PyPI trusted publishing, and add GitHub Sponsors tiers.

