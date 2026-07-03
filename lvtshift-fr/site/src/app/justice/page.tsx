import PagerLayout from "@/components/PagerLayout";
import Content from "@/content/pagers/justice.mdx";

export const metadata = {
  title: "Justice — Pour une terre productive",
  description:
    "La valeur d'un terrain est créée par la collectivité ; il est juste qu'elle lui revienne. Le fondement de justice de la réforme.",
};

export default function JusticePage() {
  return (
    <PagerLayout
      eyebrow="Une question de justice"
      title="Récompenser le travail, décourager la rente"
      lede="La réforme n'est pas d'abord fiscale : c'est une réforme de justice, qui se trouve passer par l'impôt."
    >
      <Content />
    </PagerLayout>
  );
}
