# Social housing and the TFPB, November 2026: audit trail

Research behind modelling social housing's exemptions today and ending them in
the reform (`social_housing.py`, METHODOLOGY §3.5, *Social housing*; §6 item 14).

| File | What it is |
|---|---|
| `01-brief.md` | The legal brief sent to Gemini (3 November 2026) |
| `02-gemini-reply.md` | Gemini's reply to the brief, unedited |
| `03-legal-report.md` | Current law (CGI 1384 A, 1384 C, 1388 bis), compensation, magnitudes and the policy debate, from primary sources (Légifrance, BOFiP, REI 2024, Cour des comptes, CPO). §7 is the decision table. States which sources were opened and which were seen only in snippets |
| `04-sources-report.md` | Live check of the data: RPLS (SDES DiDo), QPV 2024 contours (ANCT), DGFiP personnes morales; three parcel joins tested on Montreuil and Villeurbanne. Aggregates only |
| `05-gemini-code-review.md` | Gemini's review of the first implementation, unedited except for [redacted] passages: it repeated first-run figures for a commune whose social housing category is not published, and guessed at a landlord's share there |
| `06-gemini-followup.md` | Gemini's answer to four follow-up questions (the convention-date transfer rule, PLA codes 10–12, the disclosure rule), unedited |

Gemini's replies are not sources. What the model adopted from them was checked
against `03`, `04` or the RPLS data:

- **Adopted:** a company counts as HLM by its groupe code only if most of its
  rows carry it; estates are grouped by landlord, never across two; the QPV
  abatement needs a convention or pre-1977 HLM financing; for 2005–06 starts the
  convention must date from 2005; the dominance rule (no landlord above 85 % of
  the category's tax); filtering the Paris register before building unit keys;
  and, for the site text, the 2021–26 full compensation (10 of 25 years), the
  QPV abatement's 40 % compensation, the transition for the existing exempt
  stock and the VEFA channel.
- **Found on the data, after Gemini's first review:** RPLS's first-letting year
  (`LOCAT`) is reported inconsistently, so it cannot mark transfers between
  landlords; the convention date does (METHODOLOGY §3.5). Gemini agreed in `06`.
  PLA ordinaire (code 12) can no longer be exempt in 2025.
- **Rejected:** that acquisitions without works are never exempt (art. 1384 C
  covers dwellings « acquis en vue de leur location avec le concours financier
  de l'État », `03` §2.4); that the exemption of an acquisition with works runs
  from the end of the works (the statute counts from the year after
  acquisition); that code 15 is ANRU financing (it is PAP locatif, `04`'s
  dictionary); that code 10 is a closed 1990s loan (95 % of code-10 dwellings in
  Montreuil and 89 % in Villeurbanne entered the stock from 2010: landlords use
  it for today's PLAI); a tighter transfer threshold (conventions often precede
  the entry into the stock by one or two years after works); and Gemini's claim
  that the open RPLS file names landlords (it does not, `04` §1).

The RPLS diffusion rules (`04` §1) bind every published figure: no statistic
identifying a landlord, no figure on fewer than 11 dwellings below commune
level, no redistribution of the rows. The per-dwelling and per-parcel working
files were kept outside the repository and are not published.
