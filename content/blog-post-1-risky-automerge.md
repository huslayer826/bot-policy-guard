# Risky Dependency Bot Automerge Is Usually a Policy Bug

Dependency bots are often treated as operational plumbing: configure them once,
let them open pull requests, and move on. The risky part is not the bot. The
risky part is a policy that allows fresh upstream releases to move through a
repository faster than maintainers can review them.

The pattern to watch for is broad automerge without a release-age soak. A new
package version can be published, compromised, yanked, or found broken within
hours. If Renovate or workflow automation merges it immediately, branch
protection may still pass while the organization loses the review window that
would have caught the issue.

Safer dependency automation usually has three properties:

- Narrow automerge scope, ideally dev-only or patch-only.
- Explicit update limits that match reviewer capacity.
- A release-age soak, such as Renovate `minimumReleaseAge` or Dependabot
  `cooldown`, before merge automation is allowed.

`bot-policy-guard` checks repository files for these policy mistakes. It runs
offline and reports rule IDs with remediation text, so the finding can become a
small configuration change instead of a vague security concern.

Example:

```bash
bot-policy-guard . --fail-on high
```

The goal is not to ban automerge. The goal is to make automerge boring,
constrained, and easy to explain during an incident review.
