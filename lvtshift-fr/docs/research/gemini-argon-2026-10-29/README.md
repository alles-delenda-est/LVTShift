# Gemini review of the farmland exclusion, 29 October 2026

`gemini-4-argon` was asked to critique D6 as revised on 29 October: unbuilt A/N
land outside the reform, the TAFNB method that splits the TFPNB, and the
`MIN_IRIS_INCOMES` guard. The prompt is in `01-prompt.md`, the reply in
`02-gemini-reply.md`. As with every Gemini review, no figure changed on its
word alone. Each point was checked first:

| # | Gemini's point | Check | Outcome |
|---|---|---|---|
| 1 | Excluding by PLU zone, not by cadastral group, suits an LVT (development rights) | Agrees with the design | Kept |
| 2 | Micro/macro mismatch: the commune model excludes by PLU zone, the national split by cadastral group, so a field (groups 1–6) in a U zone pays the LVT and its TFPNB stays; amenity land in an N zone is dropped from both | Correct. No source gives the TFPNB by PLU zone (it would need the Fichiers fonciers) | **Stated as a caveat** in `yields-2026.md`. Direction mixed, size unknown, bounded by the ≈ 266 M€ non-agricultural TFPNB |
| 3 | "Unzoned = taxable" breaks the model in RNU communes | Panel: 10 of ≈ 1,1 million parcels have no zoning (Jonage 6, Valenton 3, Villiers-sur-Marne 1); every panel commune has GPU coverage | Not material now. **Rule for new communes:** a commune without GPU zoning needs a cadastral-nature fallback before it is modelled |
| 4 | Corsica: farmland wholly exempt (CGI 1394 B), so the TAFNB/B11 ratio should be near 1 there | The script caps the ratio at 1; Corsica's few M€ do not move the national share | No change |
| 5 | The CGI 1396 surcharge on building land is in the TFPNB base but not the TAFNB base, overstating the agricultural share | Not verified against BOFiP. Bounded by the independent D21 cross-check, which agrees within 0,6 % | Stated as an unverified caveat |
| 6 | Use D21 (the 1394 B bis exemption base) directly instead | D21 is empty for 2025 in the REI extract (the script returns 0), and it misses Corsica and the DOM | Kept TAFNB, D21 as cross-check for 2024 |
| 7 | Group numbering (water as group 9, sols as group 10, golf as group 12) | Wrong: the 1908 instruction has 8 eaux, 9 jardins, 10 terrains à bâtir, 11 agrément, 12 chemins de fer, 13 sols (BOI-IF-AUT-80, BOI-IF-TFNB-10-40-50) | Ignored |
| 8 | The rate rises because farmland was ~3,5 % of the base but its TFPNB only ~1,5 % of the yield | Correct; that is the arithmetic (1,06 → 1,09 %) | No change |
| 9 | Unbuilt U/AU land should be in the national denominator | Fair, but it predates this change: INSEE's built land (AN.2111) has always been the base. Small against 6 091 Md€ | Open point, not this PR |
| 10 | 10 IRIS is weak; ask for ≥ 20 IRIS or use the Filosofi 200 m grid | A judgment call. 20 would also drop Annemasse (10) and Sète (17). The guard here only restores the rule the methodology page already stated | **For Patrick to decide** in a separate PR |
