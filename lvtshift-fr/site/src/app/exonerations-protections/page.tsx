import PagerLayout from "@/components/PagerLayout";
import Content from "@/content/pagers/exonerations-protections.mdx";

export const metadata = {
  title: "Exonérations et protections — Pour une terre productive",
  description:
    "Aucune protection des ménages n'est supprimée. La réforme allège l'impôt sur le logement occupé, ajoute un report de paiement pour les propriétaires fragiles et met fin à l'exonération des bailleurs sociaux, une aide cachée qui appauvrit les communes les moins fortunées.",
};

export default function ExonerationsProtectionsPage() {
  return (
    <PagerLayout
      eyebrow="Exonérations et protections"
      title="Aucune protection des ménages n'est retirée — une est même ajoutée"
      lede="Les protections des ménages restent toutes en place, et la réforme en ajoute une pour le propriétaire riche en foncier mais pauvre en revenu. Seule disparaît l'exonération des bailleurs sociaux : une aide qui gagnerait à être visible, plutôt que imposée sur les communes par le gouvernement."
    >
      <Content />
    </PagerLayout>
  );
}
