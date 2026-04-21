# Security Policy

## Reporting a Vulnerability

**Please DO NOT open public GitHub issues for security
vulnerabilities.** Public disclosure before a fix is available
puts users at risk.

Report vulnerabilities privately to:

- **GitHub Security Advisories** (preferred):
  [Create a new advisory](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN/security/advisories/new)
- **Email:** `info@datadrivenconstruction.io`

Please include in your report:

- Product name and version
  (e.g. `RvtExporter.exe` from `DDC_CONVERTER_REVIT`, git commit
  hash or release tag)
- Affected platform (Windows version, Linux distribution, CPU
  architecture, relevant dependencies)
- Steps to reproduce
- Proof-of-concept (if available)
- Impact assessment
- Your preferred credit attribution (or request for anonymity)

## Response Timeline

We follow coordinated disclosure:

| Stage               | Target time                                  |
|---------------------|----------------------------------------------|
| Acknowledgement     | 3 business days                              |
| Initial assessment  | 14 calendar days                             |
| Fix or mitigation   | 90 calendar days where technically feasible  |
| Public disclosure   | After a fix is available; at the latest 120 days from the report |

For actively exploited vulnerabilities, we shorten all stages and
publish a mitigation advisory as soon as one is available.

## Supported Versions

| Version track                     | Security updates                         |
|-----------------------------------|------------------------------------------|
| Latest stable release             | Yes                                      |
| Previous minor version            | 6 months after a newer minor release     |
| Older versions                    | No                                       |

## Scope

**In scope:**

- Binary converters distributed through this repository and via
  `https://datadrivenconstruction.io`
  (RvtExporter, RVT2IFCconverter, IfcExporter, DwgExporter,
  DgnExporter, and related CLI/worker binaries under
  `DDC_LINUX_Converters/`).
- n8n workflow templates in this repository.
- AI agent instruction files under `AI_AGENTS_INSTRUCTIONS/`.
- Official Docker images or OS packages published by
  DataDrivenConstruction, where available.

**Out of scope:**

- Third-party tools invoked by our converters
  (report directly to the upstream vendor).
- Social engineering of Licensor or customers.
- Issues that require an already-compromised user system or the
  user deliberately bypassing security controls.
- Self-XSS, DoS via resource exhaustion on free / community use.

## Regulatory Reporting

Where required by EU Regulation 2024/2847 (Cyber Resilience Act,
vulnerability-reporting obligations effective 11 September 2026)
we report actively exploited vulnerabilities through the ENISA
Single Reporting Platform and cooperate with the German Federal
Office for Information Security (BSI) / CERT-Bund.

## No Bug Bounty

DataDrivenConstruction currently does not operate a paid
bug-bounty programme. We gratefully acknowledge responsible
researchers in the associated GitHub Security Advisories unless
anonymity is requested.

## Contact

All security communication: `info@datadrivenconstruction.io`

For general enquiries, commercial licensing, and privacy requests,
the same address applies.
