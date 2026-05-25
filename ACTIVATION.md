# Activation

This file is the under-30-minute path from prepared repository to public distribution and revenue switches. It assumes the repository will live at `huslayer826/bot-policy-guard`.

## 1. Publish the Repository

```bash
cd /Users/omar/cybermoney
./tools/export-project.sh bot-policy-guard
cd .release/bot-policy-guard
gh auth switch --user huslayer826 || gh auth login --hostname github.com
gh repo create huslayer826/bot-policy-guard --public --source . --remote origin --push --description "Audit Renovate, Dependabot, and GitHub Actions dependency automation policy."
git push origin v0.1.0
```

The export step creates a clean standalone git repository with its own `main` branch and `v0.1.0` tag.

## 2. Enable GitHub Pages

1. Open `https://github.com/huslayer826/bot-policy-guard/settings/pages`.
2. Under **Build and deployment**, set **Source** to **GitHub Actions**.
3. Open **Actions** and run the `Pages` workflow if it does not run automatically.
4. Public landing page: `https://huslayer826.github.io/bot-policy-guard/`.

## 3. Enable PyPI Trusted Publishing

1. Open `https://pypi.org/manage/account/publishing/`.
2. Choose **Add a new pending publisher**.
3. Enter:
   - PyPI project name: `bot-policy-guard`
   - Owner: `huslayer826`
   - Repository name: `bot-policy-guard`
   - Workflow filename: `release.yml`
   - Environment name: `pypi`
4. Save the pending publisher.
5. In GitHub, open `https://github.com/huslayer826/bot-policy-guard/releases/new`.
6. Choose tag `v0.1.0`, title `v0.1.0`, paste the `CHANGELOG.md` entry, and publish the release.

After the GitHub release is live and the PyPI pending publisher exists, open Actions > Release > Run workflow to publish to PyPI with GitHub OIDC. No PyPI API token is required.

## 4. Enable GitHub Sponsors

1. Open `https://github.com/sponsors/accounts`.
2. Select the `huslayer826` dashboard.
3. Open **Sponsor tiers**.
4. Create these monthly tiers:
   - `$5`: "Support safer dependency automation defaults for open source maintainers."
   - `$25`: "Policy supporter. Sponsors fund new Renovate, Dependabot, and GitHub Actions rules."
   - `$150`: "Platform team sponsor. Fund org-scale dependency-bot governance features and receive monthly rule notes."
5. Publish the tiers.
6. Add this to the top of `README.md` after Sponsors is live:

```markdown
[![Sponsor](https://img.shields.io/badge/Sponsor-GitHub%20Sponsors-ea4aaa)](https://github.com/sponsors/huslayer826)
```

## 5. Turn on the Pro Path

No payments are wired in this repo. The one-click switch later is an org dashboard:

- Product: GitHub App scans dependency-bot configs across repositories and tracks drift.
- First paid plan: `$99/month` for 25 repositories, SARIF export, policy history, and weekly email reports.
- Required infra later: GitHub App, queue, Postgres, SARIF/report storage, hosted docs.

Add a waitlist link to `docs/index.html` when a no-code form or hosted landing page is available.

## 6. Launch Copy

Use the drafts in:

- `content/social/linkedin.md`
- `content/social/x-bluesky.md`
- `content/social/reddit.md`

Suggested first post title:

```text
I built a dependency-bot policy linter for risky Renovate and Dependabot defaults
```

