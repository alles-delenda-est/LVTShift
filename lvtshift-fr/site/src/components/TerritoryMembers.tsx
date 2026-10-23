/**
 * TerritoryMembers — per-commune breakdown of an inner-ring territory.
 *
 * Honesty rules:
 *  - Each member was modelled on its OWN levy (revenue-neutral commune by
 *    commune), so the table shows the spread the territory headline averages over.
 *  - Members that could not be modelled are named, never silently dropped.
 *  - Rows are per-commune aggregates; nothing here is per-parcel.
 */

import type { Coverage, MemberRow } from "@/lib/types";
import { euros, pct } from "@/lib/format";

export interface TerritoryMembersProps {
  members: MemberRow[];
  coverage?: Coverage;
}

export default function TerritoryMembers({ members, coverage }: TerritoryMembersProps) {
  return (
    <div>
      <p className="text-sm text-encre font-body mb-4 max-w-3xl leading-relaxed">
        Chaque commune est modélisée sur son propre produit de taxe foncière et
        reste à recettes constantes : il n&apos;y a pas de taux unique
        métropolitain. Les chiffres du territoire agrègent ces résultats
        commune par commune.
        {coverage && coverage.members_missing.length > 0 && (
          <>
            {" "}
            <strong>
              {coverage.members_missing.length} commune
              {coverage.members_missing.length > 1 ? "s" : ""} sur{" "}
              {coverage.members_total} n&apos;ont pas pu être modélisées
            </strong>{" "}
            ({coverage.members_missing.join(", ")}) et sont absentes des
            agrégats.
          </>
        )}
      </p>
      <div className="overflow-x-auto max-h-[28rem] overflow-y-auto border border-lisere">
        <table className="w-full text-sm font-body">
          <caption className="sr-only">
            Résultats par commune membre, triés par produit de taxe foncière
          </caption>
          <thead className="sticky top-0 bg-creme">
            <tr className="text-left text-xs uppercase tracking-[0.1em] text-gris">
              <th scope="col" className="px-3 py-2">Commune</th>
              <th scope="col" className="px-3 py-2 text-right">Produit TFPB</th>
              <th scope="col" className="px-3 py-2 text-right">Part foncière</th>
              <th scope="col" className="px-3 py-2 text-right">Montant déplacé</th>
              <th scope="col" className="px-3 py-2 text-right">Paient davantage</th>
            </tr>
          </thead>
          <tbody>
            {members.map((m) => (
              <tr key={m.commune_key} className="border-t border-lisere">
                <th scope="row" className="px-3 py-1.5 text-left font-normal text-encre">
                  {m.name}
                </th>
                <td className="px-3 py-1.5 text-right tabular-nums">{euros(m.neutral_levy_eur)}</td>
                <td className="px-3 py-1.5 text-right tabular-nums">{pct(m.land_share_pct)}</td>
                <td className="px-3 py-1.5 text-right tabular-nums">{pct(m.gross_pct_of_levy)}</td>
                <td className="px-3 py-1.5 text-right tabular-nums">{pct(m.share_paying_more_pct)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="text-xs text-gris italic mt-2 font-body">
        « Montant déplacé » : somme des hausses et des baisses, en % du produit
        de la commune. « Paient davantage » : part des parcelles dont la
        cotisation augmenterait.
      </p>
    </div>
  );
}
