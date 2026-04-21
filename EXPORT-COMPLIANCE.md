# Export Compliance

**Version 1.0 — Effective April 2026**

This document describes how DataDrivenConstruction handles
export-control obligations for the binary converters
distributed under this repository. It complements the export-
control notice in [NOTICE](./NOTICE) and the pass-through
obligations in [LICENSE-PROPRIETARY](./LICENSE-PROPRIETARY).

## 1. Classification

| Regime                                                              | Classification    |
|---------------------------------------------------------------------|-------------------|
| U.S. Export Administration Regulations (EAR, 15 CFR Parts 730-774)  | **EAR99**         |
| EU Regulation 2021/821 (dual-use items)                             | Out of Annex I    |
| German Außenwirtschaftsgesetz (AWG) / -verordnung (AWV)             | No AWV Annex AL entry |

EAR99 covers items that are subject to the EAR but are not
listed on the Commerce Control List (CCL). EAR99 items may
still not be exported to, or re-exported from, destinations
subject to comprehensive U.S. sanctions without a licence or
licence exception (TSU under § 740.13, encryption open-source
exemption under § 740.17(b)(2), or a specific licence).

Cryptographic functionality used in the binaries (TLS, PKCS,
OpenSSL runtime components that ship inside the installers) is
covered by **EAR § 740.17(b)(2)** (mass-market encryption,
publicly available) and by **EU Reg. 2021/821** Annex I Cat.
5 Part 2 Note 3 (publicly-available mass-market software).
No export licence is required for distribution from Germany to
countries outside embargoed regions.

## 2. Prohibited destinations and persons

Downloading, installing, or re-exporting the binaries is
prohibited to:

- **Jurisdictions under comprehensive U.S. sanctions** (OFAC):
  Cuba, Iran, North Korea, Syria, and the Crimea / Donetsk /
  Luhansk regions of Ukraine.
- **Jurisdictions under comprehensive EU restrictive measures**
  administered by Council Regulations - currently Russia,
  Belarus, Iran, North Korea, Syria, and the non-government-
  controlled regions of Ukraine (the scope evolves; see
  <https://finance.ec.europa.eu/eu-sanctions-map>).
- **Sanctioned persons and entities** on the OFAC Specially
  Designated Nationals (SDN) List, on the EU Consolidated List,
  on the UK OFSI Consolidated List, or on the UN Security
  Council Consolidated List.
- **Military end-uses and military end-users** where prohibited
  by EAR § 744.21 or by EU Council Regulation 2021/821
  Art. 4(1)(b).

## 3. Exporter-of-record and screening

DataDrivenConstruction is the exporter of record when the
binaries are downloaded from GitHub Releases, from
`pkg.datadrivenconstruction.io`, or from any other distribution
channel operated by Licensor.

Licensor's export-compliance measures include:

- **Public notice** of the classification and prohibited
  destinations in this document, in
  [LICENSE-PROPRIETARY](./LICENSE-PROPRIETARY) Section 4.1(c),
  and in [NOTICE](./NOTICE).
- **Download-time click-wrap** accepting the terms of the
  DataDrivenConstruction End-User License Agreement
  (<https://datadrivenconstruction.io/term-of-use-and-eula/>),
  which includes an export-compliance representation by the
  downloader.
- **Geo-restriction** of download endpoints on
  `pkg.datadrivenconstruction.io` and commercial-distribution
  URLs, implemented at the CDN layer, to block IP ranges
  allocated to OFAC-sanctioned jurisdictions.
- **SDN screening** of named commercial-licence counterparties
  using publicly available consolidated-list sources (OFAC
  SDN, EU Consolidated List, UK OFSI) before any commercial
  order is fulfilled.
- **Record retention** of commercial transactions for at least
  five (5) years, as required by EAR § 762.

## 4. Downstream obligations

Downstream redistributors (resellers, OEM integrators, VARs)
who ship the binaries as part of their own product must:

(a) pass through the prohibited-destinations / prohibited-
    persons restrictions in Section 2 of this document to
    their own end-users;
(b) not contractually undermine the pass-through obligations
    in Section 4.1 of
    [LICENSE-PROPRIETARY](./LICENSE-PROPRIETARY);
(c) maintain their own screening and record-retention
    measures appropriate to their jurisdiction and business
    volume.

## 5. Military and dual-use concerns

The binaries are general-purpose CAD/BIM data-conversion
utilities. They are not designed for, and are not specifically
intended for, military end-uses. Customers who plan to use the
Software in connection with a military end-use or with a
military end-user in a restricted destination must obtain a
specific licence from the competent authority (BAFA in Germany,
BIS in the United States) before importing the Software, and
must notify Licensor at `info@datadrivenconstruction.io`.

## 6. Encryption notification (one-time)

For U.S. EAR § 740.17(b)(1) / § 742.15 open-source-encryption
notification, the public URL of the source archive is:

<https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN>

The encryption content is limited to standard TLS and PKCS
routines in runtime components bundled with the installers; no
originally authored cryptographic algorithm is distributed.

## 7. Contact

Export-compliance queries, licence requests, screening
challenges: `info@datadrivenconstruction.io`.
