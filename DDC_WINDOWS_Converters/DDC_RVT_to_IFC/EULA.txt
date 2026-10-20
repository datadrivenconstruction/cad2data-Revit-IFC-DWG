# DataDrivenConstruction End-User Licence Agreement (EULA)

Version 1.0, effective 2026-10-20. This English version is the binding version. Translations are
provided for convenience; if they differ, the English version prevails.

Applies to the DDC converter and tool binaries. It does not apply to `ddc-tools`, the n8n workflows,
notebooks, scripts, AI-agent instructions and documentation in this repository, which are open source
under the [MIT License](LICENSE).

## In short

- The DDC converters are **free for non-commercial use only**.
- **Commercial use requires a licence on request**: <info@datadrivenconstruction.io>.
- `ddc-tools` stays MIT (open source), including for commercial use. The converters it calls do not.

## 1. Licensor

Artem Boiko, sole proprietor (Einzelunternehmen), trading as DataDrivenConstruction,
Kraichgaustraße 3, 76676 Graben-Neudorf, Germany.
E-mail: info@datadrivenconstruction.io. Web: https://datadrivenconstruction.io
("Licensor", "we").

## 2. Scope and definitions

2.1 This EULA applies to the binary DDC converters and tools distributed through the GitHub Releases
of this repository, in the folders `DDC_WINDOWS_Converters/` and `DDC_LINUX_Converters/` and on
https://datadrivenconstruction.io, together with their updates, documentation and installers
(the "Software"). This includes DDC RVT Converter, DDC RVT to IFC, DDC IFC to Excel,
DDC CAD Drawing to Excel and the DDC Excel add-in. By installing or using the Software you
("you", the "User") accept this EULA. If you do not accept it, do not install or use the Software.

2.2 The DDC Data Viewer is licensed under the separate `LICENSE.txt` shipped with it.

2.3 **Commercial use** means any use of the Software
(a) by or on behalf of a business, company, self-employed professional, public authority or other
organisation, including use by its employees or contractors;
(b) in paid work or services, including processing files for clients;
(c) in a project that generates or is intended to generate revenue; or
(d) as part of, or to deliver, a product, service, pipeline or software-as-a-service offering made
available to others.

2.4 **Non-commercial use** means personal learning and hobby use, academic research, teaching and
study by students and instructors, and evaluation by non-profit organisations, in each case without
payment, revenue or business purpose. If a use fits 2.3, it is commercial use even if no fee is
charged for it. If you are unsure, write to us before you use the Software.

## 3. Licence grant

3.1 Non-commercial use. Subject to this EULA, we grant you a free of charge, non-exclusive,
non-transferable, non-sublicensable, worldwide licence to install and use the Software on your own
devices for non-commercial use.

3.2 Commercial use. Commercial use is not covered by 3.1. It requires a separate commercial licence
from us, which you can request at info@datadrivenconstruction.io. Scope, term and price are set in
the order or quote. A Paid licence (section 5) permits commercial use only to the extent its order
or quote says so.

3.3 Output files you create with the Software (spreadsheets, DXF, SVG, IFC and other results)
belong to you; we claim no rights in them. The restriction in 3.1 and 3.2 concerns the use of the
Software, not ownership of your output.

3.4 The Software is proprietary and closed source. All rights not expressly granted remain with the
Licensor. The Software is licensed, not sold.

## 4. Restrictions

Except where mandatory law expressly permits it (in particular Art. 5 and 6 of Directive
2009/24/EC and sections 69d and 69e of the German Copyright Act, UrhG), you must not:

a) reverse engineer, decompile, disassemble or otherwise attempt to derive the source code of the
Software;
b) modify, translate or create derivative works of the Software;
c) distribute, sell, rent, lend, sublicense, publish or otherwise make the Software available to
third parties (including as a download mirror, bundle or hosted service); point others to the
official download page instead;
d) remove or alter copyright notices, licence texts or third-party notices;
e) circumvent, disable or tamper with the licence check, the edition mechanism or the advertising
page;
f) use the Software to develop a competing product;
g) use the Software in violation of applicable law or third-party rights.

You may only process files you are entitled to use. You are responsible for having the right to
process the files you convert.

## 5. Editions: Community and Paid

5.1 Community (free, non-commercial): all conversion functions, fully functional, works offline,
no limits on files or rows, no watermarks and no changes to your data. After every third accepted
conversion the Software opens an information/advertising page of the Licensor in your browser.

5.2 Paid: the same functions; a valid Paid licence removes the advertising page. No other function
depends on the edition. Whether and how far a Paid licence covers commercial use is stated in its
order or quote (3.2).

5.3 If a Paid licence expires, is revoked or cannot be verified, the Software continues to work as
Community, and 3.1 and 3.2 apply. Prices, terms and payment of Paid and commercial licences are
governed by the separate order terms at the time of purchase.

## 6. Activation and device binding (Paid only)

6.1 A Paid licence is activated online with an activation code and bound to a device by a
pseudonymous key pair generated on that device (where available, protected by Windows). The
private key never leaves the device.

6.2 The licence is periodically verified online. There is no offline grace period: if verification
is not possible (for example without an internet connection), the Software runs as Community with
all functions until the next successful verification; only the advertising page is shown again.

6.3 Transfer of a licence to another device is possible within the limits of the order terms.

## 7. Data processing

The Software processes your files locally; we obtain no rights in your files. Community sends no
data; its conversion counter stays on your device. For Paid activation and renewal (and trusted-time
requests) the Software sends over HTTPS only: activation code or licence ID, product ID, the device
public key, a server challenge ID and nonce, the signature proving possession of the device key,
and for trusted time the protocol version, nonce and audience. The server receives your IP address
and the request time. Your drawings, models, file names, paths or contents, user or computer names
and hardware serial numbers are never sent. Details: privacy note (`PRIVACY.en.txt`).

## 8. Third-party components, trademarks, no affiliation

8.1 The Software contains third-party components licensed under their own licences (see
THIRD_PARTY_NOTICES and `licenses.json` in each package). Those licences apply to the respective
components; nothing in this EULA restricts rights granted by them.

8.2 Autodesk, AutoCAD, DWG and Revit are trademarks of Autodesk, Inc.; Bentley and MicroStation are
trademarks of Bentley Systems, Incorporated; IFC and buildingSMART are trademarks of buildingSMART
International. The Software is independent and is not affiliated with, endorsed or certified by
any of them. Other names belong to their owners. See [TRADEMARK.md](TRADEMARK.md).

## 9. Warranty

9.1 The Community edition is provided free of charge (gift-like). The Licensor is liable for defects
in title and quality only if it fraudulently conceals a defect (sections 523, 524 BGB, applied
analogously).

9.2 For Paid licences the statutory warranty rights apply; for consumers they cannot be excluded.

9.3 The Software decodes proprietary formats from independent observation. Results may be
incomplete; unread values are left empty and reported. Output fidelity versus the originating
application is not guaranteed. Verify converted quantities, geometry and parameters before relying
on them for design, cost, safety or legal purposes.

## 10. Liability

10.1 The Licensor is liable without limitation for intent and gross negligence, for injury to life,
body or health, under the German Product Liability Act (ProdHaftG), for fraudulently concealed
defects and under any guarantee given.

10.2 For the free Community edition, liability for slight negligence is excluded, except under 10.1
(sections 521, 523, 524 BGB, applied analogously).

10.3 For Paid and commercial licences, in case of slight negligence the Licensor is liable only for
breach of essential contractual obligations (obligations whose fulfilment makes proper performance
of the contract possible and on which you may regularly rely), and then limited to the damage
typical and foreseeable for this type of contract. Any further liability for slight negligence is
excluded.

10.4 The limits above also apply to the Licensor's vicarious agents. Mandatory statutory liability
remains unaffected.

10.5 You remain responsible for regular backups of your data.

## 11. Export control

You will comply with applicable export-control and sanctions laws. See
[EXPORT-COMPLIANCE.md](EXPORT-COMPLIANCE.md).

## 12. Term and termination

This EULA applies while you use the Software. Your rights end automatically if you materially
breach it (including by commercial use without a commercial licence); you must then stop using the
Software and delete it. Sections 3.3, 4, 8, 10 and 13 survive.

## 13. Governing law, consumers, miscellaneous

13.1 German law applies, excluding the UN Convention on Contracts for the International Sale of
Goods. If you are a consumer residing in the EU, the mandatory consumer-protection provisions of
your country of residence remain applicable.

13.2 If you are a merchant, a legal entity under public law or have no general place of
jurisdiction in Germany, the place of jurisdiction is the Licensor's place of business. Consumers
may be sued only at their place of residence.

13.3 EU online dispute resolution: https://ec.europa.eu/consumers/odr. The Licensor is not obliged
and not willing to participate in dispute resolution proceedings before a consumer arbitration
board.

13.4 Should any provision be invalid, the remaining provisions stay effective (the invalid provision
is replaced by a valid one closest in economic effect). Changes to this EULA apply to new versions
of the Software.

13.5 You may not assign this EULA without our written consent. We may assign it to a successor
entity of the Licensor.

13.6 Previously published releases that were distributed under an open-source licence remain under
that licence for their recipients; this EULA applies to versions published with it.

13.7 This EULA, together with [LICENSE-PROPRIETARY](LICENSE-PROPRIETARY), is the entire agreement
on the Software. In case of conflict, this EULA prevails.

## 14. Right of withdrawal for consumers (Paid licences)

If you are a consumer (section 13 BGB) and purchase a Paid licence at a distance, you have a
statutory right of withdrawal. The free Community edition involves no purchase. See Annex 1
(instructions on withdrawal) and Annex 2 (model withdrawal form).

## Annex 1: Instructions on withdrawal

**Right of withdrawal.** You have the right to withdraw from this contract within fourteen days
without giving any reason. The withdrawal period is fourteen days from the day of the conclusion of
the contract.

To exercise the right of withdrawal, you must inform us (Artem Boiko, DataDrivenConstruction,
Kraichgaustraße 3, 76676 Graben-Neudorf, Germany, e-mail info@datadrivenconstruction.io,
phone +49 (0) 15258901584) of your decision to withdraw from this contract by an unequivocal
statement (e.g. a letter sent by post or e-mail). You may use the attached model withdrawal form,
but it is not obligatory. To meet the withdrawal deadline, it is sufficient for you to send your
communication concerning your exercise of the right of withdrawal before the withdrawal period has
expired.

**Effects of withdrawal.** If you withdraw from this contract, we shall reimburse to you all
payments received from you without undue delay and in any event not later than fourteen days from
the day on which we are informed about your decision to withdraw from this contract. We will carry
out such reimbursement using the same means of payment as you used for the initial transaction,
unless you have expressly agreed otherwise; in any event, you will not incur any fees as a result
of such reimbursement.

**Early expiry of the right of withdrawal.** For a contract for the supply of digital content not
supplied on a tangible medium (such as the activation of a Paid licence), the right of withdrawal
expires once we have begun performance of the contract (activation) after you have (1) expressly
consented to our beginning performance before the end of the withdrawal period, (2) acknowledged
that you thereby lose your right of withdrawal, and (3) received a confirmation of the contract on
a durable medium (section 356(5) BGB).

## Annex 2: Model withdrawal form

(Complete and return this form only if you wish to withdraw from the contract.)

To: Artem Boiko, DataDrivenConstruction, Kraichgaustraße 3, 76676 Graben-Neudorf, Germany,
e-mail info@datadrivenconstruction.io, phone +49 (0) 15258901584

I/We (*) hereby give notice that I/We (*) withdraw from my/our (*) contract for the supply of the
following digital content / service (*):

Ordered on (*) / received on (*):
Name of consumer(s):
Address of consumer(s):
Signature of consumer(s) (only if this form is notified on paper):
Date:

(*) Delete as appropriate.

Copyright 2026 Artem Boiko, DataDrivenConstruction. All rights reserved.
