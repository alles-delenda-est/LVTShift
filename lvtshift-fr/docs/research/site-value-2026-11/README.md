# Site value of built land, November 2026: audit trail

Research behind the switch from current-use land value (the residual at the
existing density) to site value for built parcels (`estimate.site_value_land`,
METHODOLOGY §3.4) and the house classification fix (§3.1, *Property
categories*).

| File | What it is |
|---|---|
| `01-brief.md` | The research brief sent to two agents and Gemini (2 November 2026) |
| `02-gemini-reply.md` | Gemini's reply to the brief, unedited |
| `03-literature.md` | Literature and practice review (Germany, Baden-Württemberg, Denmark, NSW, Wales; IAAO; EPTB; Insee). States which sources were opened and which were seen only in snippets |
| `04-dvf-tests.md` | Tests on the model's own data: DVF plot-size gradients for 8,591 house and 190,000 flat sales in 9 communes, designs re-solved through the upstream solver, out-of-sample validation. Aggregates only |
| `05-synthesis-for-review.md` | The combined findings and proposed plan, as sent to Gemini |
| `06-gemini-reply.md` | Gemini's critique of that plan, unedited |
| `07-implementation-for-review.md` | The implementation (code diff) and first results, as sent to Gemini |
| `08-gemini-reply.md` | Gemini's review of the implementation, unedited |

Gemini's replies are not sources. They cite statutes and studies that were not
all checked; what the model adopted from them is checked in `03` and `04` or in
the data, and is listed in METHODOLOGY §3.4. In particular, Gemini's warning
that large plots were absorbing the pool (`08`, risk 1) was confirmed on the
data and led to the surplus-land rule. Its claim (`06`) that buildings with
zero recorded dwellings were being counted as houses was right: 817 Paris
"house" parcels had a recorded 0 (the households sidecar hid them by imputing
one dwelling to every house).

The per-parcel and per-sale working files behind `04` were kept outside the
repository and are not published.

The house misclassification and the plot-area problem were first found in an
earlier review of the revaluation decomposition (not kept here).
