import PagerLayout from "@/components/PagerLayout";
import Content from "@/content/pagers/logement-abordable.mdx";

export const metadata = {
  title: "Logement abordable — Pour une terre productive",
  description:
    "Le logement abordable ne bute pas d'abord sur les normes, mais sur le prix du sol. Pourquoi un impôt foncier fait partie de la solution.",
};

export default function LogementAbordablePage() {
  return (
    <PagerLayout
      eyebrow="Logement abordable"
      title="Pourquoi le logement abordable a besoin d'un impôt foncier"
      lede="Assouplir l'urbanisme, subventionner, accélérer les permis : tout cela aide un peu. Rien de tout cela ne touche au coût qui commande les autres — le prix du sol."
    >
      <Content />
    </PagerLayout>
  );
}
