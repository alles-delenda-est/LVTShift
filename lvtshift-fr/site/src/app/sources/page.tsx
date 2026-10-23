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
    role: "Emprise, niveaux, hauteur, nombre de logements, usage et nature des bâtiments (typage des locaux d'activité) ; appariement avec les Fichiers Fonciers",
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
    name: "REI 2025 — répartition de la base",
    source: "DGFiP, via OFGL (jeux rei et base-fiscale-simplifiee)",
    role: "Base TFPB (E11), compensation de l'abattement industriel (WC75), bases brutes de CFE (T29, T29_1, X503) et taux de TFPB 2020 : parts industrielle, professionnelle et logement de la taxe actuelle, commune par commune",
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
          Des références de prix publiées complètent la configuration :{" "}
          <strong>SAFER « Le prix des terres »</strong> (barème départemental
          2024, agricole&nbsp;/&nbsp;naturel) pour le foncier non
          constructible ; l&apos;enquête{" "}
          <strong>EPTB du SDES</strong> (prix des terrains et du bâti des
          maisons individuelles), pour le repli national 2023
          (99&nbsp;€/m²) des terrains à bâtir sans comparables locaux DVF
          suffisants et, dans son édition 2024 (Île-de-France, Rhône), pour
          le coût de reconstruction des maisons à Paris, à Lyon et dans
          leurs couronnes ; le <strong>bilan des logements aidés
          DHUP/SISAL</strong> pour le coût des autres bâtiments sur ces
          mêmes territoires. Ces valeurs sont des paramètres de
          configuration explicites, documentés dans{" "}
          <code className="font-mono bg-lisere px-1">config.py</code> et
          modifiables par commune.
        </p>

        <div className="mt-8 max-w-3xl">
          <h4 className="font-body text-sm font-semibold text-encre uppercase tracking-[0.1em] mb-2">
            Valorisation des locaux d&apos;activité
          </h4>
          <p className="font-body text-sm text-gris leading-relaxed mb-3">
            Les types de bâtiments, leurs coûts de construction et le prix du
            foncier d&apos;activité reposent sur les sources suivantes,
            consultées en octobre 2026. Les ratios qui en sont tirés sont des
            paramètres de configuration, documentés dans la note de recherche{" "}
            <code className="text-xs font-mono bg-lisere px-1">
              docs/research/nonres-valuation-2025.md
            </code>
            .
          </p>
          <ul className="font-body text-sm text-encre leading-relaxed space-y-2 list-disc pl-5">
            <li>
              <strong>IGN, <em>BD TOPO v3.5 — Descriptif de contenu</em></strong>{" "}
              (juillet 2026) : définitions des natures et usages des bâtiments
              et du nombre d&apos;étages.{" "}
              <a
                href="https://data.geopf.fr/annexes/ressources/documentation/DC_BDTOPO_3-5.pdf"
                className="underline text-marine break-all"
              >
                data.geopf.fr
              </a>
            </li>
            <li>
              <strong>Etalab, DVF géolocalisé 2023–2024</strong>{" "}
              (départements 93, 94 et 69) : ventes de terrains nus, classées
              en foncier d&apos;activité ou résidentiel par le{" "}
              <strong>MOS 2021 de l&apos;Institut Paris Région</strong> en
              Île-de-France et par les{" "}
              <strong>zones d&apos;activités de la Métropole de Lyon</strong>{" "}
              ; elles fondent le ratio du foncier d&apos;activité (0,45 et
              0,35).{" "}
              <a
                href="https://files.data.gouv.fr/geo-dvf/latest/csv/"
                className="underline text-marine break-all"
              >
                files.data.gouv.fr
              </a>
              {" · "}
              <a
                href="https://data.iledefrance.fr/explore/dataset/mos-occupation-du-sol-2025-and-2021-en-79-postes-de-la-region-ile-de-france/"
                className="underline text-marine break-all"
              >
                data.iledefrance.fr
              </a>
              {" · "}
              <a
                href="https://data.grandlyon.com/geoserver/metropole-de-lyon/ows"
                className="underline text-marine break-all"
              >
                data.grandlyon.com
              </a>
            </li>
            <li>
              <strong>
                RICS, <em>Depreciated replacement cost method of valuation for
                financial reporting</em>
              </strong>{" "}
              (Royaume-Uni, 1<sup>re</sup> édition, avril 2026) : méthode du
              coût de remplacement déprécié (« sol + construction ») pour les
              biens qui se vendent rarement, valorisation du terrain à son
              usage dominant, TVA comptée seulement si elle est
              irrécupérable.{" "}
              <a
                href="https://www.rics.org/content/dam/ricsglobal/documents/standards/drc_method_of_valuation_for_financial_reporting_1st_edition_rics.pdf"
                className="underline text-marine break-all"
              >
                rics.org
              </a>
            </li>
            <li>
              <strong>Quostra, guide des coûts de construction au m² en France</strong>{" "}
              (€ de janvier 2026, hors taxes) : coûts des entrepôts, ateliers,
              grandes surfaces, bureaux, équipements sportifs et logements
              collectifs sur une même base, ramenés en ratio du coût du
              logement. Guide commercial unique : les ratios sont à
              ±&thinsp;25&nbsp;%.{" "}
              <a
                href="https://quostra.com/fr-fr/blog/cout-construction-m2-france/"
                className="underline text-marine break-all"
              >
                quostra.com
              </a>
            </li>
          </ul>
        </div>

        <div className="mt-8 max-w-3xl">
          <h4 className="font-body text-sm font-semibold text-encre uppercase tracking-[0.1em] mb-2">
            Répartition de la taxe actuelle
          </h4>
          <p className="font-body text-sm text-gris leading-relaxed mb-3">
            Les parts de la taxe foncière payées aujourd&apos;hui par les
            établissements industriels, les locaux professionnels et les
            logements sont reconstituées commune par commune à partir des
            sources suivantes, consultées en octobre 2026. La méthode est
            documentée dans la note de recherche{" "}
            <code className="text-xs font-mono bg-lisere px-1">
              docs/research/tfpb-baseline-calibration.md
            </code>
            .
          </p>
          <ul className="font-body text-sm text-encre leading-relaxed space-y-2 list-disc pl-5">
            <li>
              <strong>
                DGFiP, recensement des éléments d&apos;imposition à la
                fiscalité directe locale (REI) 2025
              </strong>
              , diffusé par l&apos;OFGL : base nette de TFPB (E11),
              allocation compensatrice de l&apos;abattement de 50&nbsp;% des
              valeurs locatives des établissements industriels (WC75), bases
              brutes de CFE totales et des locaux professionnels (T29,
              T29_1), abattement industriel de CFE (X503) ; taux de TFPB 2020
              tirés de la base fiscale simplifiée.{" "}
              <a
                href="https://data.ofgl.fr/explore/dataset/rei/"
                className="underline text-marine break-all"
              >
                data.ofgl.fr
              </a>
              {" · "}
              <a
                href="https://www.data.gouv.fr/datasets/impots-locaux-fichier-de-recensement-des-elements-dimposition-a-la-fiscalite-directe-locale-rei-4"
                className="underline text-marine break-all"
              >
                data.gouv.fr
              </a>
            </li>
            <li>
              <strong>Loi n° 2020-1721 de finances pour 2021, art. 29</strong>{" "}
              : division par deux des valeurs locatives industrielles et
              compensation égale à la base perdue × le taux de TFPB de 2020
              (taux 2014 du Rhône pour les communes de la Métropole de Lyon).{" "}
              <a
                href="https://www.legifrance.gouv.fr/jorf/article_jo/JORFARTI000042753620"
                className="underline text-marine break-all"
              >
                legifrance.gouv.fr
              </a>
            </li>
            <li>
              <strong>Code général des impôts, art. 1388</strong> : la TFPB est
              établie sur la valeur locative cadastrale, sous déduction de
              50&nbsp;%, pour toutes les propriétés bâties (d&apos;où le
              facteur 0,5 appliqué à la base de CFE).{" "}
              <a
                href="https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006311555"
                className="underline text-marine break-all"
              >
                legifrance.gouv.fr
              </a>
            </li>
            <li>
              <strong>
                Cour des comptes, <em>Les taxes foncières</em>
              </strong>{" "}
              (observations définitives, 27 février 2023) : établissements
              industriels 5,7&nbsp;% et locaux professionnels 22&nbsp;% du
              produit de la taxe foncière en 2021, repères nationaux du
              calage.{" "}
              <a
                href="https://www.ccomptes.fr/sites/default/files/2023-10/20230227-S2023-0028-Taxes-foncieres.pdf"
                className="underline text-marine break-all"
              >
                ccomptes.fr
              </a>
            </li>
          </ul>
        </div>
      </section>
    </div>
  );
}
