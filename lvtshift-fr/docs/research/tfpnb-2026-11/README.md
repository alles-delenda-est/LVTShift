# Replacing the TFPNB on non-agricultural unbuilt land, November 2026: audit trail

Research behind adding the unbuilt-land tax that the reform replaces to the
commune model (`ingest.fetch_rei_unbuilt_replaced`, `estimate.unbuilt_tax`,
METHODOLOGY §3.5, *Unbuilt land*; §6 item 15). Decision of the project lead on
11 November 2026: the reform replaces the TFPNB on unbuilt land other than
farmland, as the national scenarios already assumed
(`../yields-2026.md`, `../tfpnb_farm_split.py`).

| File | What it is |
|---|---|
| `01-brief.md` | The design brief sent to Gemini, with first measurements (vacant plots only, before the garden share) |
| `02-gemini-reply.md` | Gemini's critique, unedited |

Gemini's reply is not a source. What it claimed, and what the checks found:

- **Art. 1396 surcharge on building land (its "critical" issue): checked, not
  an issue here.** The legal point is right: the surcharge applies to the
  commune's share only (CGI art. 1396 II), so it raises the commune's TFPNB
  base (`B11`) but neither the EPCI's (`B31`) nor the TAFNB's, and the share
  method would count it as farmland. But on the REI 2025, none of the 66
  modelled communes that have both bases shows `B11` above `B31` (not by 1 %).
  For the 123 communes with no EPCI base (Paris and the inner ring), the most
  a surcharge could add is the part of the commune's TFPNB the method leaves
  unreplaced: €0.30 M in all, against €23.2 M replaced. Its statement that the
  surcharge explains the ×30 and ×48 in La Rochelle and Annemasse is wrong:
  both have equal bases. The fetch prints a warning if a commune ever shows
  the gap. OFGL's REI has no separate line for the surcharge.
- **Large gardens (its "high" issue): right, and adopted.** The five-are rule
  was verified in BOFiP (BOI-IF-TFB-10-10-40): a garden attached to a house is
  a dependence of the built property up to five ares; beyond, it is amenity
  land in cadastral group 11, under the TFPNB. On the current run, houses'
  ground beyond 500 m² (footprints not deducted, so an upper bound) is 34 % to
  68 % of that ground plus the vacant plots in the eleven panel communes. The
  same doctrine treats the courtyards, gardens and parks of collective
  buildings as dependences, so only houses take a garden share. Gemini's
  double weight for building plots against gardens had no source: one weight
  per m² is used.
- **Area or land value as the key: no practical difference.** On the current
  run both keys give the same percentage to within a point or two, because
  vacant building land is priced at one €/m² per commune almost everywhere.
  Area is used: the tax is assessed on tariffs per unit of area.
- **Presentation: adopted in part.** Rises of ×3 or more show as a multiple,
  with the euro median in the note; the bar is cut at the edge of the scale.
- **Not taken up here:** pricing vacant plots from the built parcels' land
  surface, and screening parks and roads with OpenStreetMap. Both are existing
  limitations (METHODOLOGY §6 item 10), outside this change.
- **Confirmed as designed:** the whole TAFNB is replaced; the chambers of
  agriculture tax, TSE, GEMAPI and syndicate shares stay out, as for the TFPB;
  the State's compensations stay out; collection fees are outside the REI
  amounts.

One observation of our own: the roll counts far fewer taxed accounts than the
model has building-less parcels (La Rochelle: 820 TFPNB accounts for all
unbuilt land, `B14`, against 3,822 building-less parcels inside the reform).
Many such parcels are slivers, private roads or yards that may pay nothing
today. This is stated as a limitation.

Working scripts and per-parcel files were kept outside the repository.
