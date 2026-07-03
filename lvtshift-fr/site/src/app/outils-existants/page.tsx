import PagerLayout from "@/components/PagerLayout";
import Content from "@/content/pagers/outils-existants.mdx";

export const metadata = {
  title: "Outils existants — Pour une terre productive",
  description:
    "Pourquoi une réforme du foncier plutôt que muscler les outils existants ? Parce qu'ils sont étroits, optionnels et faciles à contourner — et l'ont prouvé.",
};

export default function OutilsExistantsPage() {
  return (
    <PagerLayout
      eyebrow="Outils existants"
      title="Pourquoi pas seulement muscler les outils existants ?"
      lede="Les dispositifs actuels contre la rétention foncière existent — mais ils sont étroits, optionnels et faciles à contourner. Un impôt foncier en est la version systémique."
    >
      <Content />
    </PagerLayout>
  );
}
