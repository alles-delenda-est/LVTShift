import PagerLayout from "@/components/PagerLayout";
import Content from "@/content/pagers/exonerations-protections.mdx";

export const metadata = {
  title: "Exonérations et protections — Pour une terre productive",
  description:
    "Aucune protection existante n'est supprimée. La réforme allège l'impôt sur le logement occupé et ajoute un report de paiement pour les propriétaires fragiles.",
};

export default function ExonerationsProtectionsPage() {
  return (
    <PagerLayout
      eyebrow="Exonérations et protections"
      title="Rien n'est retiré — une protection est même ajoutée"
      lede="Aucune protection existante n'est supprimée ; la réforme en ajoute une nouvelle pour le propriétaire riche en foncier mais pauvre en revenu."
    >
      <Content />
    </PagerLayout>
  );
}
