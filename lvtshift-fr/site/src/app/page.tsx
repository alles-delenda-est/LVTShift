import Link from "next/link";
import { loadCommune, loadIndex } from "@/lib/data";
import { pct, signedPct } from "@/lib/format";
import { impactSummary } from "@/lib/impactSummary";
import { panelLandShares } from "@/lib/panel";

export default function Home() {
  const { communes } = loadIndex();

  // Territories aggregate many communes, two of which (Montreuil,
  // Villeurbanne) are also published on their own: sum the de-duplicated
  // counts so no commune or parcel is counted twice.
  const totalCommunes = communes.reduce((sum, c) => sum + (c.n_communes_unique ?? 1), 0);
  const totalParcels = communes.reduce(
    (sum, c) => sum + (c.parcels_unique ?? c.parcels_modeled), 0);

  // Over every modelled commune, territory members included (not just the
  // selector entries).
  const landShares = [...panelLandShares(communes, loadCommune).values()];
  const landShareMin = Math.min(...landShares);
  const landShareMax = Math.max(...landShares);
  // What the results page actually lets you open one by one.
  const singles = communes.filter((c) => c.kind !== "territory").length;
  const rings = communes.length - singles;

  // "Who pays" figures, computed from the payloads (central case).
  const impact = impactSummary(communes.map((c) => loadCommune(c.commune_key)));

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
                vivre et travailler. Notre fiscalité pèse sur le bâtiment et
                le commerce bien plus que sur le terrain :{" "}
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
                <em>déjà</em> séparément le bâti (TFPB) et le non-bâti (TFPNB),
                avec des taux votés séparément : un premier pas peut être,
                dans les limites fixées par la loi actuelle, de baisser le taux
                de la TFPB et d&apos;augmenter celui de la TFPNB, mais ce sera
                imparfait et incomplet. La réforme modélisée ici va
                plus loin : elle assoit la taxe foncière de chaque parcelle sur
                la <strong>valeur de son sol</strong>, ce qui suppose de
                construire une base foncière par une loi de finances (voir{" "}
                <Link href="/voie-juridique" className="underline underline-offset-2 hover:text-rouge">
                  la voie juridique
                </Link>
                ).
              </p>
            </div>
          </div>

          {/* Revenue-neutrality callout */}
          <div className="mt-8 border-l-4 border-rouge pl-5 max-w-2xl">
            <p className="font-body text-base text-encre leading-relaxed">
              <strong>
                La réforme proposée est à recettes constantes &mdash; ce
                n&apos;est pas une hausse déguisée.
              </strong>{" "}
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
                fourchette de la part du sol dans la base taxable, sur
                les {landShares.length} communes
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
            Le transfert suit la part du sol dans chaque bien
          </h3>

          {/* Figures computed from the published payloads (lib/impactSummary):
              the card used to promise owner-occupiers "une baisse ou une
              quasi-neutralité", which the model contradicts for houses. */}
          <div className="grid md:grid-cols-3 gap-4 max-w-5xl">
            <div className="border border-lisere bg-creme p-5">
              <p className="text-[0.65rem] font-semibold uppercase tracking-[0.15em] text-gris mb-3">
                La maison individuelle
              </p>
              <p className="font-body text-base text-encre leading-relaxed">
                Souvent assise sur un terrain de valeur, elle paie{" "}
                <strong>davantage</strong> dans {impact.housesPayMore} des{" "}
                {impact.territories} territoires présentés (variation médiane de{" "}
                {signedPct(impact.houseMedianMin)} à{" "}
                {signedPct(impact.houseMedianMax)} selon le territoire).
              </p>
            </div>

            <div className="border border-lisere bg-creme p-5">
              <p className="text-[0.65rem] font-semibold uppercase tracking-[0.15em] text-gris mb-3">
                L&apos;appartement et les ménages modestes
              </p>
              <p className="font-body text-base text-encre leading-relaxed">
                En copropriété, le sol est partagé : l&apos;appartement paie{" "}
                <strong>moins</strong> dans {impact.flatsPayLess} territoires sur{" "}
                {impact.territories}. Le cinquième des ménages le plus modeste,
                pris dans son ensemble, paie moins dans {impact.poorestPayLess}{" "}
                des {impact.poorestAnalysable} territoires où le découpage par
                revenu est possible.
              </p>
            </div>

            <div className="border border-lisere bg-creme p-5">
              <p className="text-[0.65rem] font-semibold uppercase tracking-[0.15em] text-gris mb-3">
                Le terrain constructible gardé vide
              </p>
              <p className="font-body text-base text-encre leading-relaxed">
                Sa charge augmente fortement : c&apos;est le{" "}
                <strong>cœur du dispositif</strong>, qui envoie le signal que la
                collectivité attend une mise en valeur du terrain.
              </p>
            </div>
          </div>

          <p className="text-sm text-encre mt-5 max-w-3xl leading-relaxed">
            <strong>Incertitude principale.</strong> Pour savoir qui gagne, il
            faut connaître ce que chaque type de bien paie aujourd&apos;hui. Aucune
            donnée publique ne donne la part des bureaux et commerces dans la
            taxe foncière d&apos;une commune ; nous l&apos;estimons. Si elle est
            plus faible que notre estimation, les ménages paient aujourd&apos;hui
            davantage, et la réforme leur est nettement plus favorable. Les
            chiffres ci-dessus correspondent à notre estimation centrale ; les
            résultats présentent les deux hypothèses côte à côte.
          </p>

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
              Explorer les résultats
            </h3>
            <p className="text-sm text-gris">
              {singles} communes et {rings} couronnes détaillées par catégorie
              de bien et par quintile de revenu &middot; {totalCommunes}{" "}
              communes et {totalParcels.toLocaleString("fr-FR")} parcelles
              modélisées au total.
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
