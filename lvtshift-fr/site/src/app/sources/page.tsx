export const metadata = {
  title: "Sources — Pour une terre productive",
  description:
    "Références institutionnelles et académiques, et lignée complète des données ouvertes utilisées dans la modélisation.",
};

// ── Open-data lineage (faithful to METHODOLOGIE.md §2) ────────────────────

const DATA_SOURCES: {
  name: string;
  source: string;
  role: string;
  licence: string;
}[] = [
  {
    name: "DVF géolocalisé",
    source: "Etalab (DGFiP)",
    role: "Valeurs de marché hédoniques (régressions log-linéaires) et prix des terrains à bâtir",
    licence: "Licence Ouverte / Etalab",
  },
  {
    name: "Cadastre — parcellaire",
    source: "Etalab (DGFiP)",
    role: "Géométrie des parcelles, surface officielle (contenance)",
    licence: "Licence Ouverte / Etalab",
  },
  {
    name: "BD TOPO V3",
    source: "IGN",
    role: "Emprise, niveaux, hauteur, nombre de logements et usage des bâtiments ; appariement avec les Fichiers Fonciers",
    licence: "Licence Ouverte / Etalab",
  },
  {
    name: "GPU — zone_urba",
    source: "IGN (Géoportail de l'Urbanisme)",
    role: "Zonage PLU / PLUi : constructibilité des parcelles non bâties (U, AU, A, N)",
    licence: "Licence Ouverte / Etalab",
  },
  {
    name: "DPE logements existants",
    source: "ADEME",
    role: "Tranche de construction par bâtiment (ancrage de la dépréciation)",
    licence: "Licence Ouverte / Etalab",
  },
  {
    name: "REI foncier bâti",
    source: "OFGL / DGCL",
    role: "Produit de taxe foncière sur propriétés bâties par commune (cible de neutralité budgétaire)",
    licence: "Licence Ouverte / Etalab",
  },
  {
    name: "Contours IRIS",
    source: "IGN",
    role: "Géométrie des IRIS pour l'attribution parcelle → zone de revenu",
    licence: "Licence Ouverte / Etalab",
  },
  {
    name: "Filosofi — revenus IRIS",
    source: "INSEE",
    role: "Revenu médian disponible par IRIS (analyse distributive par quintile de revenu)",
    licence: "Licence Ouverte / Etalab",
  },
];

// ── Page ──────────────────────────────────────────────────────────────────

export default function SourcesPage() {
  return (
    <div className="max-w-6xl mx-auto px-6 py-10">
      {/* ── Page header ──────────────────────────────────────────────── */}
      <div className="mb-10 border-b border-lisere pb-6">
        <p className="text-xs uppercase tracking-[0.18em] text-gris mb-2">
          Références et données
        </p>
        <h2 className="font-display text-2xl md:text-[1.75rem] font-medium text-marine leading-tight mb-3">
          Sources
        </h2>
        <p className="font-body text-base text-gris max-w-2xl leading-relaxed">
          Références institutionnelles et académiques ayant encadré la
          conception du modèle, et lignée complète des données ouvertes
          utilisées dans le calcul parcelle par parcelle.
        </p>
      </div>

      {/* ── Section 1 : Literature ────────────────────────────────────── */}
      <section className="mb-12">
        <h3 className="font-display text-xl font-medium text-marine mb-4">
          Littérature et cadrage institutionnel
        </h3>

        <div className="space-y-7 max-w-3xl">
          {/* CPO 2023 */}
          <div className="border-l-2 border-lisere pl-5">
            <p className="font-display text-base font-medium text-encre mb-1">
              Conseil des prélèvements obligatoires (CPO), décembre 2023
            </p>
            <p className="font-body text-sm text-gris leading-relaxed">
              Le CPO recommande dans ce rapport de rebaser la taxe foncière
              sur les valeurs de marché et de déplacer une partie de la charge
              fiscale des droits de mutation à titre onéreux (DMTO) vers
              l&apos;impôt récurrent sur la propriété. Il constitue le point
              d&apos;appui institutionnel principal pour le cadrage de la
              réforme proposée ici.
            </p>
            <p className="font-body text-xs text-gris mt-1.5 italic">
              Note : le titre précis du rapport n&apos;a pas pu être vérifié
              de façon indépendante dans les sources disponibles ; la citation
              est donc conservatrice (corps + mois + année) conformément à
              notre politique de précision bibliographique.
            </p>
          </div>

          {/* Trannoy & Wasmer 2022 */}
          <div className="border-l-2 border-lisere pl-5">
            <p className="font-display text-base font-medium text-encre mb-1">
              Trannoy, A. &amp; Wasmer, E. (2022)
            </p>
            <p className="font-body text-sm text-gris leading-relaxed">
              Travaux académiques présentant le cas en faveur d&apos;une
              taxation de la valeur foncière en France, avec une estimation de
              la richesse foncière française à environ 7&thinsp;000 milliards
              d&apos;euros — soit environ six années de revenu national.
              Régulièrement cités dans les débats du CPO, du CAE et de France
              Stratégie comme le travail de référence francophone sur
              l&apos;assiette foncière.
            </p>
            <p className="font-body text-xs text-gris mt-1.5 italic">
              Note : le titre précis n&apos;a pas pu être vérifié de façon
              indépendante dans les sources disponibles ; citation
              conservatrice (auteurs + année).
            </p>
          </div>

          {/* Supporting framing */}
          <div className="border-l-2 border-lisere pl-5">
            <p className="font-display text-base font-medium text-encre mb-1">
              Bonnet, O., Bono, P.-H., Chapelle, G. &amp; Wasmer, E.
            </p>
            <p className="font-body text-sm text-gris leading-relaxed">
              Travaux de l&apos;équipe de Sciences Po montrant que la
              divergence entre rendement du capital et croissance (
              <em>r &gt; g</em> au sens de Piketty) provient massivement de
              l&apos;appréciation des <strong>terrains</strong> et non du
              capital productif. Cités dans les pagers de campagne pour
              ancrer la réforme dans la littérature sur les inégalités
              patrimoniales.
            </p>
          </div>
        </div>
      </section>

      {/* ── Section 2 : Open-data lineage ────────────────────────────── */}
      <section className="mb-10 border-t border-lisere pt-10">
        <h3 className="font-display text-xl font-medium text-marine mb-2">
          Lignée des données ouvertes
        </h3>
        <p className="font-body text-sm text-gris max-w-2xl leading-relaxed mb-6">
          Toutes les données utilisées dans la modélisation sont sous{" "}
          <strong>Licence Ouverte&nbsp;/ Etalab</strong>. Les URL et millésimes
          exacts sont configurés dans le code source (
          <code className="text-xs font-mono bg-lisere px-1">
            config.DATA_SOURCES
          </code>
          ) et reproductibles par toute partie. Les jeux de données
          individuels ne sont jamais publiés ; seuls des agrégats par
          catégorie de bien et par quintile de revenu sont diffusés.
        </p>

        <div className="overflow-x-auto">
          <table className="w-full text-sm border-collapse">
            <caption className="sr-only">
              Lignée des données ouvertes par source et producteur
            </caption>
            <thead>
              <tr className="border-b-2 border-lisere">
                <th
                  scope="col"
                  className="text-left text-xs font-semibold uppercase tracking-[0.12em] text-gris pb-2 pr-6 w-44"
                >
                  Donnée&nbsp;/&nbsp;jeu de données
                </th>
                <th
                  scope="col"
                  className="text-left text-xs font-semibold uppercase tracking-[0.12em] text-gris pb-2 pr-6 w-40"
                >
                  Source&nbsp;/&nbsp;producteur
                </th>
                <th
                  scope="col"
                  className="text-left text-xs font-semibold uppercase tracking-[0.12em] text-gris pb-2 pr-6"
                >
                  Rôle dans le modèle
                </th>
                <th
                  scope="col"
                  className="text-left text-xs font-semibold uppercase tracking-[0.12em] text-gris pb-2 w-40"
                >
                  Licence
                </th>
              </tr>
            </thead>
            <tbody>
              {DATA_SOURCES.map((row) => (
                <tr key={row.name} className="border-b border-lisere last:border-0">
                  <td className="py-2.5 pr-6 font-medium text-encre align-top leading-snug">
                    {row.name}
                  </td>
                  <td className="py-2.5 pr-6 text-gris align-top leading-snug">
                    {row.source}
                  </td>
                  <td className="py-2.5 pr-6 text-encre align-top leading-snug">
                    {row.role}
                  </td>
                  <td className="py-2.5 text-gris align-top text-xs leading-snug">
                    {row.licence}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <p className="text-xs text-gris mt-4 leading-relaxed max-w-2xl">
          Deux références de prix non-ouverts complètent la configuration :{" "}
          <strong>SAFER « Le prix des terres »</strong> (barème départemental
          2024, agricole&nbsp;/&nbsp;naturel) pour le foncier non
          constructible, et le <strong>repli national EPTB (SDES)</strong>{" "}
          2023 (99&nbsp;€/m²) pour les terrains à bâtir sans comparables
          locaux DVF suffisants. Ces valeurs sont des paramètres de
          configuration explicites, documentés dans{" "}
          <code className="font-mono bg-lisere px-1">config.py</code> et
          modifiables par commune.
        </p>
      </section>
    </div>
  );
}
