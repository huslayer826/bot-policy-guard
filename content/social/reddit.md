# Reddit Draft

Title: I built an offline CLI to audit risky Renovate, Dependabot, and GitHub Actions policy

I have been looking at dependency bot configs and noticed the same risky
patterns show up a lot:

- Broad Renovate automerge without a release-age soak.
- Missing Dependabot or Renovate update limits.
- No grouping, so maintainers get noisy one-package PR streams.
- GitHub Actions referenced by tags instead of full SHAs.
- Dependency bot workflows with implicit or broad token permissions.

I built `bot-policy-guard` as a small Python CLI that checks those files
offline. It does not call GitHub or any package registry. It emits text, JSON,
Markdown, or SARIF.

Example:

```bash
bot-policy-guard . --fail-on high
```

The goal is to make these findings easy to fix in config rather than turn them
into a big security program. I would appreciate feedback from maintainers using
Renovate or Dependabot, especially false positives from real repositories.
