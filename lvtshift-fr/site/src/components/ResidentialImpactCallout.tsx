import { loadCommune } from "@/lib/data";
import { pct, signedPct } from "@/lib/format";
import type { CategoryRow } from "@/lib/types";

// Honest, data-grounded callout for the pagers: the effect on an owner-occupier
// is NOT uniform. It depends on the land share of the property and on the
// commune. Apartment owners (land split across the copropriété) generally pay
// less; individual-house owners on valuable plots often pay MORE, especially in
// dense high-land-value communes. This component reads the real model figures
// so the prose can never drift from what the model actually shows.

const CONTRASTS: { key: string; label: string; note: string }[] = [
  { key: "villeurbanne", label: "Villeurbanne (69)", note: "cœur dense, foncier cher" },
  { key: "montreuil", label: "Montreuil (93)", note: "petite couronne parisienne" },
  { key: "roubaix", label: "Roubaix (59)", note: "foncier peu valorisé" },
];

function cat(rows: CategoryRow[], category: string): CategoryRow | undefined {
  return rows.find((r) => r.category === category);
}

export default function ResidentialImpactCallout() {
  const rows = CONTRASTS.map(({ key, label, note }) => {
    const c = loadCommune(key);
    return {
      label,
      note,
      house: cat(c.by_category, "Single Family Residential"),
      flat: cat(c.by_category, "Condominium"),
    };
  });

  return (
    <div className="my-6 border border-lisere bg-creme">
      <div className="px-4 py-3 border-b border-lisere">
        <p className="text-xs uppercase tracking-[0.15em] text-gris">
          Ce que dit vraiment le modèle
        </p>
        <p className="font-body text-sm text-encre mt-1 leading-relaxed">
          L&apos;effet sur un propriétaire occupant dépend de la part du sol dans
          la valeur de son bien — et de la commune. Il n&apos;est pas uniforme.
        </p>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <caption className="sr-only">
            Part des propriétaires occupants payant davantage, par type de bien
            et commune
          </caption>
          <thead>
            <tr className="border-b border-lisere">
              <th scope="col" className="text-left text-xs font-semibold uppercase tracking-[0.1em] text-gris px-4 py-2">
                Commune
              </th>
              <th scope="col" className="text-left text-xs font-semibold uppercase tracking-[0.1em] text-gris px-4 py-2">
                Maison individuelle
              </th>
              <th scope="col" className="text-left text-xs font-semibold uppercase tracking-[0.1em] text-gris px-4 py-2">
                Appartement (copropriété)
              </th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.label} className="border-b border-lisere last:border-0 align-top">
                <th scope="row" className="text-left px-4 py-3 font-display font-medium text-marine whitespace-nowrap">
                  {r.label}
                  <span className="block text-xs text-gris font-body font-normal italic mt-0.5">
                    {r.note}
                  </span>
                </th>
                <td className="px-4 py-3 text-encre">
                  {r.house ? (
                    <>
                      <strong className="font-semibold">
                        {pct(r.house.share_paying_more_pct)}
                      </strong>{" "}
                      paient davantage
                      <span className="block text-xs text-gris mt-0.5">
                        variation médiane {signedPct(r.house.median_change_pct)}
                      </span>
                    </>
                  ) : (
                    "—"
                  )}
                </td>
                <td className="px-4 py-3 text-encre">
                  {r.flat ? (
                    <>
                      <strong className="font-semibold">
                        {pct(r.flat.share_paying_more_pct)}
                      </strong>{" "}
                      paient davantage
                      <span className="block text-xs text-gris mt-0.5">
                        variation médiane {signedPct(r.flat.median_change_pct)}
                      </span>
                    </>
                  ) : (
                    "—"
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="px-4 py-3 text-xs text-gris leading-relaxed border-t border-lisere">
        Toutes les variations médianes sont encadrées par la bande de
        sensibilité ±&thinsp;10&nbsp;points sur la part foncière. L&apos;appartement
        en copropriété, dont le sol est partagé, paie généralement moins ; la
        maison individuelle sur un terrain de valeur paie souvent davantage,
        surtout là où le foncier est cher.{" "}
        <a href="/resultats" className="text-rouge underline underline-offset-2 hover:text-marine">
          Voir chaque commune en détail →
        </a>
      </p>
    </div>
  );
}
