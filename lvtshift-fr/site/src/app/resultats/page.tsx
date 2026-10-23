import { loadIndex, loadCommune } from "@/lib/data";
import CommunePicker from "@/components/CommunePicker";

export const metadata = {
  title: "Résultats par commune — Pour une terre productive",
  description:
    "Explorez les résultats de la modélisation commune par commune : transferts fiscaux, impact sur les catégories de propriété et progressivité.",
};

export default function ResultatsPage() {
  const index = loadIndex();
  const communes = index.communes.map((c) => loadCommune(c.commune_key));

  return (
    <div className="max-w-6xl mx-auto px-6 py-10">
      <div className="mb-8 border-b border-lisere pb-6">
        <p className="text-xs uppercase tracking-[0.18em] text-gris mb-2">
          Résultats de modélisation
        </p>
        <h2 className="font-display text-2xl md:text-[1.75rem] font-medium text-marine leading-tight mb-3">
          Résultats par commune
        </h2>
        <p className="font-body text-base text-gris max-w-2xl leading-relaxed">
          Sélectionnez une commune pour explorer les effets simulés d&apos;une
          réforme de la taxe foncière vers une taxation de la valeur des
          terrains, à recettes constantes. Les résultats sont exprimés en
          variation médiane et en proportion de propriétaires concernés.
        </p>
      </div>
      <CommunePicker communes={communes} />
    </div>
  );
}
