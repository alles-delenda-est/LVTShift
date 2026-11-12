import Link from "next/link";
import type { Commune } from "@/lib/types";
import { poorestNote } from "@/lib/poorestNote";
import { eurosExact, pct } from "@/lib/format";

/** "3,4 % de plus" / "2,2 % de moins" */
const moreLess = (v: number) => `${pct(Math.abs(v))} de ${v >= 0 ? "plus" : "moins"}`;
const hundred = (v: number) => eurosExact(Math.round(v / 100) * 100);

/** Under the income chart, where the poorest fifth pays more (lib/poorestNote). */
export default function PoorestNote({
  commune,
}: {
  commune: Pick<Commune, "commune_key" | "name" | "by_income_quintile" | "by_category">;
}) {
  const n = poorestNote(commune);
  if (!n) return null;
  return (
    <div className="border-l-4 border-lisere pl-4 mt-3 max-w-3xl">
      <p className="text-sm text-encre font-body leading-relaxed">
        <strong className="font-medium">
          Pourquoi le cinquième le plus modeste paie-t-il davantage à {commune.name}&nbsp;?
        </strong>{" "}
        Ici, les quartiers aisés ne reposent pas sur un sol plus cher : l&apos;écart
        de revenu entre quartiers est faible (revenu médian de{" "}
        {hundred(n.q1Income)} à {hundred(n.q5Income)}), et les ménages les plus
        aisés vivent presque tous en immeuble, qui paie moins. Les quartiers plus
        modestes comptent encore beaucoup de maisons, sur des terrains où le PLU
        permet de construire dense : évalué à l&apos;usage permis, leur sol pèse
        lourd
        {n.housesTotal != null && (
          <>, et l&apos;ensemble des maisons de la commune paie {moreLess(n.housesTotal)}</>
        )}
        . Le cinquième le plus modeste paie ainsi {moreLess(n.q1Total)} au total, le
        plus aisé {moreLess(n.q5Total)}
        {n.q1Household != null && n.q1Household < 0 && (
          <>
            {" "}; mais le ménage type du cinquième le plus modeste, qui vit le plus
            souvent en immeuble, paie{" "}
            {moreLess(n.q1Household)}
          </>
        )}
        .
      </p>
      <p className="text-xs text-gris font-body mt-2 leading-relaxed">
        Deux précisions. Les logements sociaux ne sont pas comptés ici (leur impôt
        pèse sur les bailleurs), alors que beaucoup des ménages les plus modestes y
        vivent. Et le revenu est celui du quartier, non du ménage : le propriétaire
        d&apos;une maison dans un quartier modeste n&apos;est pas forcément modeste.
        Pour les propriétaires riches en terrain mais pauvres en revenu, la réforme
        prévoit le report de paiement et le plafonnement selon le revenu (voir{" "}
        <Link href="/exonerations-protections" className="underline underline-offset-2">
          Exonérations et protections
        </Link>
        ).
      </p>
    </div>
  );
}
