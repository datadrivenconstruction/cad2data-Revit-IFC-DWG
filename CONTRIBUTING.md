# Contributing to cad2data

Thank you for your interest in improving the cad2data toolkit.
Before opening a pull request, please read this short guide.

## Scope of contributions

**In scope (MIT-licensed):**

- n8n workflow JSON files
- AI agent instruction files under `AI_AGENTS_INSTRUCTIONS/`
- Python utility scripts
- Sample project files under `Sample_Projects/`
- Additional assets under `DDC_in_additon/`
- Documentation (README files in any language, other `*.md`)

**Out of scope (proprietary binaries):**

- Files under `DDC_WINDOWS_Converters/` and
  `DDC_LINUX_Converters/` are proprietary and are not accepted
  as community contributions. Bug reports against the binaries
  are welcome via GitHub Issues or Security Advisories.

See [LICENSE](./LICENSE), [LICENSE-PROPRIETARY](./LICENSE-PROPRIETARY),
and [NOTICE](./NOTICE) for the full dual-licensing scheme.

## How to contribute

1. Fork the repository.
2. Create a feature branch from `main`:
   `git checkout -b feat/<short-description>`.
3. Make your changes. Keep the change focused and atomic.
4. **Sign every commit** (Developer Certificate of Origin):
   `git commit -s -m "..."`. The `dco.yml` workflow fails any
   PR with unsigned commits.
5. Open a pull request against `main` with a clear description
   of what changed and why.
6. Address review feedback and rebase as needed.

## Developer Certificate of Origin (DCO)

By signing off on a commit you attest to the
**Developer Certificate of Origin** at
<https://developercertificate.org/>. In short: you confirm that
you have the right to submit the contribution under the
project's open-source licence.

Sign with `git commit -s`. To fix already-unsigned commits in a
branch:

```bash
git rebase --signoff main
```

## Code of Conduct

Contributors agree to follow the [Code of Conduct](./CODE_OF_CONDUCT.md)
(Contributor Covenant 2.1) in all project spaces.

## Reporting bugs and feature requests

- **Bug or feature:** open a GitHub issue using the appropriate
  template.
- **Security vulnerability:** do not open a public issue. See
  [SECURITY.md](./SECURITY.md) for the private reporting
  channel.
- **Trademark concern:** see [TRADEMARK.md](./TRADEMARK.md) and
  contact `info@datadrivenconstruction.io`.

## Attribution

Merged contributions are acknowledged in release notes.

Contact: `info@datadrivenconstruction.io`
