import PagerLayout from "@/components/PagerLayout";
import Content from "@/content/pagers/voie-juridique.mdx";

export const metadata = {
  title: "La voie juridique — Pour une terre productive",
  description:
    "En France, la difficulté n'est pas la légalité : deux impôts fonciers existent déjà. Les vraies questions sont le calibrage et la base foncière.",
};

export default function VoieJuridiquePage() {
  return (
    <PagerLayout
      eyebrow="La voie juridique"
      title="La difficulté n'est pas la légalité — la voie est déjà ouverte"
      lede="La France taxe déjà le sol et le bâti séparément. Le débat n'est pas constitutionnel : il porte sur le calibrage et la construction d'une base foncière."
    >
      <Content />
    </PagerLayout>
  );
}
