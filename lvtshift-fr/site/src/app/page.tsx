import Link from "next/link";
import { loadIndex } from "@/lib/data";
import { pct } from "@/lib/format";

export default function Home() {
  const { communes } = loadIndex();

  const totalCommunes = communes.length;
  const totalParcels = communes.reduce((sum, c) => sum + c.parcels_modeled, 0);

  const landShares = communes
    .map((c) => c.land_share_pct)
    .filter((x): x is number => x !== null);
  const landShareMin = Math.min(...landShares);
  const landShareMax = Math.max(...landShares);

  return (
    <div>
      {/* ── Hero / lede ─────────────────────────────────────────────── */}
      <section className="border-b border-lisere">
        <div className="max-w-6xl mx-auto px-6 py-12 md:py-16">
          <p className="text-xs uppercase tracking-[0.18em] text-gris mb-4">
            L&apos;essentiel de la réforme
          </p>

          <h2 className="font-display text-[1.875rem] md:text-[2.5rem] font-medium text-marine leading-tight max-w-3xl mb-10">
            Déplacer l&apos;impôt du bâti vers le sol &mdash; sans alourdir la
            facture globale
          </h2>

          <div className="grid md:grid-cols-2 gap-x-12 gap-y-8 max-w-5xl">
            {/* Problem column */}
            <div>
              <h3 className="font-display text-[0.75rem] font-semibold text-rouge tracking-[0.15em] uppercase mb-3">
                Le problème
              </h3>
              <p className="font-body text-base text-encre leading-relaxed">
                Partout en France, du foncier bien situé reste improductif :
                terrains à bâtir gardés vides, friches, parkings de surface,
                logements vacants &mdash; pendant que les prix du logement
                grimpent et que les terrains se raréfient là où l&apos;on veut
                vivre. Notre fiscalité traite un terrain vide en cœur de ville à
                peu près comme un immeuble de logements :{" "}
                <strong>
                  construisez, et votre taxe foncière augmente ; laissez le
                  terrain s&apos;apprécier sans rien en faire, et elle reste
                  faible.
                </strong>{" "}
                Le code des impôts travaille contre l&apos;objectif que nos
                villes poursuivent.
              </p>
            </div>

            {/* Reform column */}
            <div className="md:border-l md:border-lisere md:pl-12">
              <h3 className="font-display text-[0.75rem] font-semibold text-rouge tracking-[0.15em] uppercase mb-3">
                La réforme
              </h3>
              <p className="font-body text-base text-encre leading-relaxed">
                Déplacer le poids de l&apos;impôt foncier :{" "}
                <strong>
                  moins sur ce qui est bâti, davantage sur le sol
                </strong>
                , à recettes totales inchangées. La France taxe{" "}
                <em>déjà</em> le bâti (taxe foncière sur les propriétés bâties)
                et le non-bâti (taxe foncière sur les propriétés non bâties)
                séparément, avec des taux votés séparément. Il s&apos;agit
                d&apos;actionner un{" "}
                <strong>levier qui existe déjà</strong> &mdash; alléger le
                bâti, relever le foncier &mdash; non de créer un impôt nouveau.
              </p>
            </div>
          </div>

          {/* Revenue-neutrality callout */}
          <div className="mt-8 border-l-4 border-rouge pl-5 max-w-2xl">
            <p className="font-body text-base text-encre leading-relaxed">
              <strong>À recettes constantes &mdash; ce n&apos;est pas une hausse déguisée.</strong>{" "}
              Le total perçu ne change pas : les taux sont recalculés
              mécaniquement pour produire{" "}
              <strong>les mêmes recettes</strong>, simplement réparties
              autrement entre les parcelles. Aucune collectivité ne perd de
              ressources. Ce qui change, c&apos;est{" "}
              <em>qui paie</em> &mdash; et le signal envoyé au foncier laissé
              oisif.
            </p>
          </div>
        </div>
      </section>

      {/* ── Teaser figures ───────────────────────────────────────────── */}
      <section className="bg-white border-b border-lisere">
        <div className="max-w-6xl mx-auto px-6 py-10">
          <p className="text-xs uppercase tracking-[0.18em] text-gris mb-6">
            Panel de modélisation &mdash; données ouvertes françaises
          </p>

          {/* Grid trick: gap-px on bg-lisere creates ruled dividers between white cells */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-px bg-lisere border border-lisere">
            <div className="bg-white p-6">
              <p className="font-display text-5xl font-medium text-marine leading-none">
                {totalCommunes}
              </p>
              <p className="text-sm text-gris mt-2 leading-snug">
                communes modélisées dans ce panel
              </p>
            </div>

            <div className="bg-white p-6">
              <p className="font-display text-5xl font-medium text-marine leading-none">
                {totalParcels.toLocaleString("fr-FR")}
              </p>
              <p className="text-sm text-gris mt-2 leading-snug">
                parcelles analysées au total
              </p>
            </div>

            <div className="bg-white p-6">
              <p className="font-display text-2xl font-medium text-marine leading-snug">
                {pct(landShareMin)} à {pct(landShareMax)}
              </p>
              <p className="text-sm text-gris mt-2 leading-snug">
                fourchette de la part du sol dans la base taxable, selon la
                commune
              </p>
            </div>
          </div>

          <p className="text-xs text-gris mt-3 leading-relaxed">
            Résultats issus de la modélisation LVTShiftFR à partir du cadastre,
            de DVF et des données DGCL/OFGL. Valeurs exprimées en ordres de
            grandeur agrégés &mdash; aucun résultat individuel ou par parcelle.
          </p>
        </div>
      </section>

      {/* ── Who pays ─────────────────────────────────────────────────── */}
      <section className="border-b border-lisere">
        <div className="max-w-6xl mx-auto px-6 py-10">
          <p className="text-xs uppercase tracking-[0.18em] text-gris mb-3">
            Qui paie davantage &mdash; qui paie moins
          </p>

          <h3 className="font-display text-xl md:text-2xl font-medium text-marine max-w-2xl mb-6 leading-snug">
            Des transferts ciblés : ils épargnent le logement occupé, ils
            pèsent sur le foncier oisif
          </h3>

          <div className="grid md:grid-cols-2 gap-4 max-w-3xl">
            {/* Owner-occupier — named FIRST per the honesty rule */}
            <div className="border border-lisere bg-creme p-5">
              <p className="text-[0.65rem] font-semibold uppercase tracking-[0.15em] text-gris mb-3">
                Le propriétaire qui occupe son logement
              </p>
              <p className="font-body text-base text-encre leading-relaxed">
                C&apos;est le cas le plus courant. L&apos;allègement sur le
                bâti lui bénéficie directement : l&apos;effet attendu est une{" "}
                <strong>baisse ou une quasi-neutralité</strong> de sa charge
                fiscale. Les résultats précis par commune et par catégorie
                figurent dans la modélisation.
              </p>
            </div>

            {/* Vacant-land owner */}
            <div className="border border-lisere bg-creme p-5">
              <p className="text-[0.65rem] font-semibold uppercase tracking-[0.15em] text-gris mb-3">
                Le détenteur d&apos;un terrain constructible gardé vide
              </p>
              <p className="font-body text-base text-encre leading-relaxed">
                Sa charge fiscale augmentera fortement. C&apos;est le{" "}
                <strong>cœur du dispositif, assumé</strong> : l&apos;impôt
                envoie le signal que la collectivité attend une mise en valeur
                du terrain.
              </p>
            </div>
          </div>

          <p className="text-xs text-gris mt-5 max-w-xl leading-relaxed">
            Les chiffres précis par catégorie de bien et par commune sont
            disponibles dans les résultats. Les imputations sont agrégées
            &mdash; aucune facture individuelle ou par parcelle n&apos;est
            publiée ni ne peut être inférée.
          </p>
        </div>
      </section>

      {/* ── Primary CTA ──────────────────────────────────────────────── */}
      <section>
        <div className="max-w-6xl mx-auto px-6 py-12 flex flex-col sm:flex-row sm:items-center gap-6 sm:gap-10">
          <div className="flex-1">
            <h3 className="font-display text-lg font-medium text-marine mb-1">
              Explorer les résultats commune par commune
            </h3>
            <p className="text-sm text-gris">
              {totalCommunes} communes &middot;{" "}
              {totalParcels.toLocaleString("fr-FR")} parcelles &middot;
              modélisation détaillée par catégorie de bien et par quintile de
              revenu.
            </p>
          </div>
          <Link
            href="/resultats"
            className="shrink-0 inline-block bg-rouge text-white px-7 py-3.5 font-body font-semibold text-sm tracking-wide hover:bg-marine transition-colors duration-200"
          >
            Voir les résultats &rarr;
          </Link>
        </div>
      </section>
    </div>
  );
}
