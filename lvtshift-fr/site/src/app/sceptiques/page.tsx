import PagerLayout from "@/components/PagerLayout";
import Content from "@/content/pagers/sceptiques.mdx";

export const metadata = {
  title: "Pour les sceptiques — Pour une terre productive",
  description:
    "Les objections les plus fréquentes, et les réponses que le modèle permet — y compris qui paie vraiment davantage, sans enjoliver.",
};

export default function SceptiquesPage() {
  return (
    <PagerLayout
      eyebrow="Pour les sceptiques"
      title="Les objections, et nos réponses"
      lede="Toute réforme sérieuse doit affronter ses objections de face — y compris là où le modèle contredit les slogans les plus commodes."
    >
      <Content />
    </PagerLayout>
  );
}
