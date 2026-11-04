import Link from "next/link";
import type { Commune } from "@/lib/types";
import { socialNote } from "@/lib/socialHousing";

/** Under the category chart: what the social landlord category is, why it
 *  stays out of the household figures, and today's exemptions. */
export default function SocialHousingNote({ commune }: { commune: Pick<Commune, "provenance"> }) {
  const note = socialNote(commune);
  if (!note) return null;
  return (
    <p className="text-xs text-gris font-body mt-2 max-w-3xl leading-relaxed">
      {note.kind === "category" ? (
        <>
          <strong className="font-medium text-encre">Logement social (bailleurs)</strong>
          &nbsp;: parcelles détenues principalement par des organismes HLM ou des
          SEM. Aujourd&apos;hui, une partie de leurs logements est exonérée de taxe
          foncière (construction ou achat récents) ou bénéficie d&apos;un
          abattement en quartier prioritaire, et l&apos;impôt actuel modélisé en
          tient compte. {note.counts ? `${note.counts} ` : ""}La réforme met fin à
          ces exonérations, d&apos;où de fortes hausses pour les logements qui en
          bénéficient.
        </>
      ) : (
        <>
          Les parcelles des bailleurs sociaux sont comptées dans «&nbsp;Autre
          bâtiment&nbsp;» : les montrer à part, ici, permettrait de reconnaître un
          bailleur ou un bien. Leur impôt actuel tient compte des exonérations du
          logement social, auxquelles la réforme met fin.
        </>
      )}{" "}
      Cette taxe n&apos;étant pas récupérable sur les locataires et les loyers
      sociaux étant plafonnés, la variation pèse sur le bailleur : elle
      n&apos;entre dans aucun graphique par revenu des ménages. Voir{" "}
      <Link href="/exonerations-protections" className="underline">
        Exonérations et protections
      </Link>
      .
    </p>
  );
}
