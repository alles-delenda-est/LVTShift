import PagerLayout from "@/components/PagerLayout";
import Content from "@/content/pagers/exonerations-protections.mdx";
import { loadCommune, loadIndex } from "@/lib/data";
import { socialSummary, socialSummarySentence } from "@/lib/socialHousing";

export const metadata = {
  title: "Exonérations et protections — Pour une terre productive",
  description:
    "Aucune protection des ménages n'est supprimée. La réforme allège l'impôt sur le logement occupé, ajoute un report de paiement pour les propriétaires fragiles et met fin à l'exonération des bailleurs sociaux, une aide cachée payée par les communes.",
};

export default function ExonerationsProtectionsPage() {
  // computed from the published payloads, so the sentence follows the model
  const landlords = socialSummarySentence(
    socialSummary(loadIndex().communes.map((c) => loadCommune(c.commune_key))),
  );
  return (
    <PagerLayout
      eyebrow="Exonérations et protections"
      title="Aucune protection des ménages n'est retirée — une est même ajoutée"
      lede="Les protections des ménages restent toutes en place, et la réforme en ajoute une pour le propriétaire riche en foncier mais pauvre en revenu. Seule disparaît l'exonération des bailleurs sociaux : une aide qui gagnerait à être visible, plutôt que payée par les communes."
    >
      <Content landlords={landlords} />
    </PagerLayout>
  );
}
