# GitHub Actions Updates Need Pinning and Grouping

GitHub Actions are dependencies. They run code inside CI, often with repository
tokens, package credentials, or deployment permissions nearby. Treating
`uses: actions/checkout@v4` as harmless because it is common misses the policy
point: a tag can move, and a workflow dependency can change outside the normal
lockfile review loop.

There are two controls that work well together:

- Pin actions to full commit SHAs.
- Use Dependabot or Renovate to open grouped update pull requests.

Pinning gives reviewers a fixed artifact to inspect. Grouping keeps the review
stream manageable, especially when multiple workflow actions update in the same
week. Without grouping, teams tend to ignore the noise. Without pinning, teams
may not know exactly what code ran.

`bot-policy-guard` scans workflow YAML for action references that are not pinned
to full SHAs. It also checks whether GitHub Actions dependency updates are
grouped through Dependabot or Renovate configuration.

Example finding:

```text
[MEDIUM] BPG-GHA-ACTION-NOT-PINNED - GitHub Action is not pinned to a full commit SHA
Remediation: Pin third-party and first-party actions to full commit SHAs; let Dependabot or Renovate open grouped updates.
```

This is a practical control. It does not require a new service, and it does not
ask teams to stop using marketplace actions. It just moves workflow dependencies
into a reviewable update path.
