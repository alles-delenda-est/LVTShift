import Link from "next/link";
import { loadCommune, loadIndex } from "@/lib/data";
import { pct, signedPct } from "@/lib/format";
import { countRange, impactSummary } from "@/lib/impactSummary";
import { panelLandShares } from "@/lib/panel";

/** One decimal, French comma ("9,8"); "n. d." when missing. */
function fmt1(n: number | null): string {
  return n == null
    ? "n. d."
    : n.toLocaleString("fr-FR", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
}

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

          {/* Key redistribution results, computed from the payloads
              (lib/impactSummary), so the banner cannot drift from the model. */}
          <aside
            aria-labelledby="resultats-cles"
            className="mt-10 bg-marine text-creme max-w-5xl"
          >
            <div className="px-6 pt-5 pb-1 flex flex-wrap items-baseline justify-between gap-x-6 gap-y-1">
              <h3
                id="resultats-cles"
                className="text-xs uppercase tracking-[0.18em] text-creme/80"
              >
                Ce que la réforme change &mdash; principaux résultats
              </h3>
              <p className="text-xs text-creme/70">
                {impact.territories} territoires
                {impact.alt ? ", deux hypothèses sur la taxe actuelle" : ", cas central"}
              </p>
            </div>
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-px bg-creme/15">
              {[
                {
                  value: `${fmt1(impact.shiftMin)} à ${fmt1(impact.shiftMax)} %`,
                  label: "de la taxe foncière change de payeur, selon le territoire",
                },
                {
                  value: `${impact.poorestBelowRichestBoth} sur ${impact.poorestAnalysable}`,
                  label: impact.alt
                    ? "territoires où les 20 % de ménages les plus modestes s’en sortent mieux que les 20 % les plus aisés, dans les deux hypothèses"
                    : "territoires où les 20 % de ménages les plus modestes s’en sortent mieux que les 20 % les plus aisés",
                },
                {
                  value: countRange(impact.blocksPayLess, impact.alt?.blocksPayLess, impact.territories),
                  label: "territoires où l’immeuble collectif type (5 logements ou plus) paie moins",
                },
                {
                  value: countRange(impact.housesPayMore, impact.alt?.housesPayMore, impact.territories),
                  label: "territoires où la maison type paie davantage",
                },
              ].map(({ value, label }) => (
                <div key={label} className="bg-marine px-6 py-5">
                  <p className="font-display text-3xl md:text-4xl font-medium leading-none text-creme">
                    {value}
                  </p>
                  <p className="text-sm text-creme/80 mt-2 leading-snug">{label}</p>
                </div>
              ))}
            </div>
            <p className="px-6 py-4 text-xs text-creme/70 leading-relaxed">
              Taxe foncière déplacée du bâti vers le sol, à recettes égales dans
              chaque commune. «&nbsp;Type&nbsp;» : variation médiane de la
              catégorie.{" "}
              {impact.alt && (
                <>
                  Deux nombres : l&apos;un pour le cas central, l&apos;autre
                  pour la variante locale, deux estimations de la part des
                  locaux professionnels dans la taxe actuelle. Part qui change
                  de payeur : cas central.{" "}
                </>
              )}
              <Link href="/resultats" className="underline underline-offset-2 text-creme hover:text-white">
                Détail par commune
              </Link>
            </p>
          </aside>

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
                {impact.territories} territoires présentés
                {impact.alt && impact.alt.housesPayMore !== impact.housesPayMore && (
                  <> ({impact.alt.housesPayMore} dans la variante locale)</>
                )}{" "}
                (variation médiane de {signedPct(impact.houseMedianMin)} à{" "}
                {signedPct(impact.houseMedianMax)} selon le territoire, cas
                central). Le sol étant évalué comme s&apos;il était nu, à la
                densité habituelle de son quartier, c&apos;est la maison basse
                au milieu d&apos;immeubles qui paie le plus.
              </p>
            </div>

            <div className="border border-lisere bg-creme p-5">
              <p className="text-[0.65rem] font-semibold uppercase tracking-[0.15em] text-gris mb-3">
                L&apos;immeuble collectif et les ménages modestes
              </p>
              <p className="font-body text-base text-encre leading-relaxed">
                Le cinquième des ménages le plus modeste, pris dans son
                ensemble, s&apos;en sort <strong>mieux</strong> que le cinquième
                le plus aisé dans {impact.poorestBelowRichestBoth} des{" "}
                {impact.poorestAnalysable} territoires où le découpage par revenu
                est possible
                {impact.alt ? (
                  <>
                    , dans les deux hypothèses. Il paie moins dans{" "}
                    {impact.poorestPayLess} d&apos;entre eux dans le cas central,{" "}
                    {impact.alt.poorestPayLess} dans la variante locale. Dans
                    l&apos;immeuble collectif, où vivent la plupart des ménages, le
                    sol est partagé entre de nombreux logements : il paie moins
                    dans {impact.blocksPayLess} territoires sur{" "}
                    {impact.territories} dans le cas central,{" "}
                    {impact.alt.blocksPayLess} dans la variante locale. Le petit
                    immeuble de 2 à 4 logements, souvent moins dense que ses
                    voisins, paie moins dans {impact.smallBuildingsPayLess}{" "}
                    territoires seulement dans le cas central.
                  </>
                ) : (
                  <>
                    , et paie moins dans {impact.poorestPayLess} d&apos;entre eux.
                    Dans l&apos;immeuble collectif, où vivent la plupart des
                    ménages, le sol est partagé : il paie moins dans{" "}
                    {impact.blocksPayLess} territoires sur {impact.territories}.
                  </>
                )}
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
            taxe foncière d&apos;une commune ; nous l&apos;estimons. Une variante
            locale, tirée de la taxe d&apos;habitation de 2017, la place plus
            haut que notre estimation centrale dans presque toutes les villes
            modélisées : les ménages paieraient alors aujourd&apos;hui moins, et
            la réforme leur serait moins favorable. Le classement, lui, ne
            change pas : les plus modestes s&apos;en sortent mieux que les plus
            aisés dans les deux cas. Les résultats présentent les deux
            hypothèses côte à côte.
          </p>

          <p className="text-sm text-encre mt-3 max-w-3xl leading-relaxed">
            <strong>Seconde incertitude : la valeur du sol bâti.</strong> Le sol
            sous un bâtiment est évalué comme s&apos;il était nu, à la densité
            habituelle de sa zone d&apos;urbanisme, ce qu&apos;un impôt sur la
            valeur du sol doit taxer. Cette valeur ne se vérifie pas sur les
            ventes de biens bâtis : seules les rares ventes de terrains nus et
            de biens destinés à la démolition en donnent une mesure directe.{" "}
            <Link href="/methodologie" className="underline underline-offset-2">
              Méthode et limites
            </Link>
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
