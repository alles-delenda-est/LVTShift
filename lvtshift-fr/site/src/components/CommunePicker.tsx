"use client";

/**
 * CommunePicker — client-side commune selector for the /resultats page.
 *
 * All commune data is loaded at build time by the server page and passed
 * as plain-object props, so no network round-trip occurs on switch.
 *
 * Honesty rules:
 *  - The commune heading shows the reference year when known
 *    ("Montreuil — exercice 2024"); omits it when null rather than inventing one.
 *  - The "Proportion qui paie davantage" figure is never buried — HeadlineCards
 *    already enforces this with its rouge accent treatment.
 */

import Link from "next/link";
import { useState, useSyncExternalStore } from "react";
import type { Commune } from "@/lib/types";
import HeadlineCards from "@/components/charts/HeadlineCards";
import SensitivityBand from "@/components/charts/SensitivityBand";
import BaselineRange from "@/components/charts/BaselineRange";
import WinLoseSplit from "@/components/charts/WinLoseSplit";
import CategoryImpactBars from "@/components/charts/CategoryImpactBars";
import IncomeQuintileChart from "@/components/charts/IncomeQuintileChart";
import StepsTable from "@/components/charts/StepsTable";
import TerritoryMembers from "@/components/TerritoryMembers";
import SocialHousingNote from "@/components/SocialHousingNote";
import PoorestNote from "@/components/PoorestNote";
import { publishedCategories, withheldCategories } from "@/lib/disclosure";
import { computePrivateHouseholdWinners } from "@/lib/householdWinners";
import { categoryNotes, hasCategoryNotes } from "@/lib/categoryNotes";
import { pct } from "@/lib/format";
import { ROUGE, GREEN } from "@/components/charts/theme";

/** Caption under charts that carry the building-cost whiskers. */
function BandNote() {
  return (
    <p className="text-xs text-gris font-body italic mt-2 max-w-3xl leading-relaxed">
      Les traits fins indiquent la fourchette obtenue en faisant varier le coût
      du bâti de ±20&nbsp;% (hypothèses basse et haute), ce qui déplace la
      valeur du sol des parcelles bâties d&apos;un quartier à l&apos;autre : la
      valeur du sol étant imputée, seule une conclusion qui tient sur toute la
      fourchette est robuste.
    </p>
  );
}

/** The query string never changes behind our back (we only replaceState). */
const subscribeNever = () => () => {};

export interface CommunePickerProps {
  communes: Commune[];
}

export default function CommunePicker({ communes }: CommunePickerProps) {
  const defaultKey =
    communes.find((c) => c.commune_key === "montreuil")?.commune_key ??
    communes[0]?.commune_key ??
    "";

  // Shareable links: /resultats?commune=paris opens on Paris. The page is
  // statically exported, so the query is read on the client (the server
  // snapshot is null, which keeps hydration consistent) and written back with
  // replaceState, so picking a commune adds no history entry.
  const urlKey = useSyncExternalStore(
    subscribeNever,
    () => new URLSearchParams(window.location.search).get("commune"),
    () => null,
  );
  const [pickedKey, setPickedKey] = useState<string | null>(null);
  const isKnown = (k: string | null): k is string =>
    k !== null && communes.some((c) => c.commune_key === k);
  const selectedKey = pickedKey ?? (isKnown(urlKey) ? urlKey : defaultKey);

  const selectCommune = (key: string) => {
    setPickedKey(key);
    const url = new URL(window.location.href);
    url.searchParams.set("commune", key);
    window.history.replaceState(null, "", url);
  };

  const commune =
    communes.find((c) => c.commune_key === selectedKey) ?? communes[0] ?? null;

  if (communes.length === 0 || !commune) {
    return (
      <p className="text-gris italic font-body">
        Aucune commune disponible.
      </p>
    );
  }

  /* Reference-year label — never fabricate a year */
  const communeHeading =
    commune.reference_year != null
      ? `${commune.name} — exercice ${commune.reference_year}`
      : commune.name;

  const householdWinners = computePrivateHouseholdWinners(commune.by_category);
  const notes = categoryNotes(publishedCategories(commune.by_category));

  return (
    <div>
      {/* ── Commune selector ─────────────────────────────────────── */}
      <div className="mb-8">
        <label
          htmlFor="commune-select"
          className="block text-xs uppercase tracking-[0.18em] text-gris mb-2"
        >
          Choisir une commune
        </label>
        {/* Explicit width: a select sized by its longest option overflowed
            phone screens on some platforms. */}
        <div className="relative w-full sm:w-[26rem] max-w-full">
          <select
            id="commune-select"
            value={selectedKey}
            onChange={(e) => selectCommune(e.target.value)}
            className="
              w-full
              border border-lisere bg-creme text-encre
              font-body text-base
              px-4 py-2.5
              pr-10
              appearance-none
              cursor-pointer
              truncate
              focus:outline-none focus:ring-2 focus:ring-marine/40
            "
          >
            <optgroup label="Communes">
              {communes
                .filter((c) => c.kind !== "territory")
                .map((c) => (
                  <option key={c.commune_key} value={c.commune_key}>
                    {c.name}
                    {c.departement ? ` (${c.departement})` : ""}
                  </option>
                ))}
            </optgroup>
            {communes.some((c) => c.kind === "territory") && (
              <optgroup label="Couronnes (agrégats de communes)">
                {communes
                  .filter((c) => c.kind === "territory")
                  .map((c) => (
                    <option key={c.commune_key} value={c.commune_key}>
                      {c.name}
                    </option>
                  ))}
              </optgroup>
            )}
          </select>
          {/* Custom dropdown arrow */}
          <span
            aria-hidden="true"
            className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-gris"
          >
            <svg
              width="12"
              height="8"
              viewBox="0 0 12 8"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M1 1L6 7L11 1"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </span>
        </div>
      </div>

      {/* ── Selected commune results ──────────────────────────────── */}
      <div>
        {/* Commune identification heading */}
        <div className="border-l-4 border-marine pl-4 mb-8">
          <h3 className="font-display text-xl md:text-2xl font-medium text-marine leading-tight">
            {communeHeading}
          </h3>
          <p className="text-xs text-gris mt-1 italic font-body">
            {commune.kind === "territory" && commune.coverage
              ? `Territoire de ${commune.coverage.members_total} communes (${commune.coverage.members_modeled} modélisées)`
              : <>Code INSEE&nbsp;: {commune.insee ?? "n. d."}</>}
            {commune.departement ? ` · Département : ${commune.departement}` : ""}
          </p>
        </div>

        {/* Charts in logical order */}
        <div className="space-y-10">
          {/* 1. Key figures */}
          <section aria-labelledby="section-indicateurs">
            <h3
              id="section-indicateurs"
              className="text-xs uppercase tracking-[0.18em] text-gris mb-3"
            >
              Indicateurs clés
            </h3>
            <HeadlineCards
              headline={commune.headline}
              sharePayingMorePct={
                commune.headline_sensitivity.base.share_paying_more_pct
              }
            />
            {/* Per-dwelling view, after the parcel figures and showing both
                sides: it complements the headline, it does not replace it. */}
            {householdWinners && (
              <div className="mt-4 border border-lisere bg-creme px-5 py-4">
                <p className="text-[0.6875rem] uppercase tracking-[0.12em] text-gris font-body mb-1">
                  Par logement (parc privé)
                </p>
                <p className="font-display text-base md:text-lg font-medium text-marine leading-snug">
                  Logements privés dont la taxe foncière augmente&nbsp;:{" "}
                  <span className="font-semibold" style={{ color: ROUGE }}>
                    {pct(householdWinners.pctPayingMore)}
                  </span>
                  <span className="text-gris font-normal"> · </span>
                  baisse ou reste stable&nbsp;:{" "}
                  <span className="font-semibold" style={{ color: GREEN }}>
                    {pct(householdWinners.pctPayingLess)}
                  </span>
                </p>
                <p className="text-xs text-gris font-body italic mt-1 leading-relaxed">
                  Sur {householdWinners.totalDwellings.toLocaleString("fr-FR")} logements
                  privés modélisés (maisons, petits immeubles de 2 à 4 logements et
                  immeubles collectifs de 5 logements et plus), chacun affecté de la
                  variation de sa parcelle. Ce chiffre compte des logements, occupés ou
                  non, et non des ménages&nbsp;: la taxe foncière est due par le
                  propriétaire, qu&apos;il occupe son logement ou le loue. Le logement
                  social, détenu par des bailleurs institutionnels et présenté à part
                  plus bas, n&apos;est pas inclus. La proportion de parcelles payant
                  davantage, ci-dessus, compte un immeuble collectif comme une seule
                  parcelle&nbsp;; ici, chaque logement compte.
                </p>
              </div>
            )}
          </section>

          {/* 2. Sensitivity band */}
          <section aria-labelledby="section-sensibilite">
            <h3
              id="section-sensibilite"
              className="text-xs uppercase tracking-[0.18em] text-gris mb-3"
            >
              Analyse de sensibilité
            </h3>
            <SensitivityBand sensitivity={commune.headline_sensitivity} />
          </section>

          {/* 2b. Uncertainty about today's tax on professional premises */}
          {commune.baseline_sensitivity && (
            <section aria-labelledby="section-taxe-actuelle">
              <h3
                id="section-taxe-actuelle"
                className="text-xs uppercase tracking-[0.18em] text-gris mb-3"
              >
                Incertitude sur la taxe actuelle des locaux professionnels
              </h3>
              <p className="text-sm text-encre font-body mb-3 max-w-3xl leading-relaxed">
                Les données ouvertes sous-estiment la part des bureaux et
                commerces dans la taxe foncière d&apos;aujourd&apos;hui (locaux
                vacants, locaux loués par des organismes publics). L&apos;estimation
                centrale la recale sur le total national de la Cour des comptes ;{" "}
                {commune.baseline_sensitivity.low_source === "cfe_raw" ||
                !commune.baseline_sensitivity.low_source
                  ? "l'hypothèse plancher garde le chiffre brut."
                  : "la variante locale l'estime commune par commune à partir de la taxe d'habitation de 2017, qui portait sur tous les logements occupés."}{" "}
                Les montants payés après la réforme sont identiques dans les
                deux colonnes : seul le point de départ change.
              </p>
              <BaselineRange
                baseline={commune.baseline_sensitivity}
                withinCommune={commune.kind === "territory"}
              />
            </section>
          )}

          {/* 3. Win/lose split by category */}
          <section aria-labelledby="section-gagnants">
            <h3
              id="section-gagnants"
              className="text-xs uppercase tracking-[0.18em] text-gris mb-3"
            >
              Gagnants et perdants par catégorie
            </h3>
            <WinLoseSplit byCategory={publishedCategories(commune.by_category)} />
            {withheldCategories(commune.by_category) > 0 && (
              <p className="text-xs text-gris mt-2">
                Les catégories de moins de 11 parcelles ne sont pas détaillées,
                pour qu&apos;aucun bien ne soit reconnaissable.
              </p>
            )}
          </section>

          {/* 4. Category impact (diverging bars: household / parcel / total) */}
          <section aria-labelledby="section-categories">
            <h3
              id="section-categories"
              className="text-xs uppercase tracking-[0.18em] text-gris mb-3"
            >
              Impact par catégorie de bien
            </h3>
            <CategoryImpactBars
              byCategory={publishedCategories(commune.by_category)}
              unbuiltReplaced={commune.provenance.unbuilt_tax?.replaced ?? false}
              band={{
                low: commune.headline_sensitivity?.low?.by_category,
                high: commune.headline_sensitivity?.high?.by_category,
              }}
            />
            <BandNote />
            <SocialHousingNote commune={commune} />
            {hasCategoryNotes(notes) && (
              <div className="mt-4 border border-lisere bg-creme px-4 py-3.5 max-w-3xl">
                <p className="text-xs uppercase tracking-[0.14em] text-gris font-body mb-2">
                  Notes de lecture par catégorie
                </p>
                <ul className="font-body text-xs text-encre leading-relaxed space-y-2 list-disc pl-4">
                  {notes.collective && (
                    <li>
                      <strong className="font-semibold">{notes.collective.label}</strong>&nbsp;:
                      regroupe les immeubles d&apos;au moins 5 logements, en copropriété
                      ou détenus par un seul propriétaire. Le terrain y est partagé entre
                      de nombreux logements&nbsp;: c&apos;est là que la baisse par logement
                      est en général la plus marquée. Les petits immeubles de 2 à 4
                      logements forment une catégorie à part.
                    </li>
                  )}
                  {notes.social && (
                    <li>
                      <strong className="font-semibold">{notes.social.label}</strong>&nbsp;:
                      {notes.social.totalSentence ? ` ${notes.social.totalSentence}` : ""}{" "}
                      La variation médiane par parcelle intègre la fin modélisée des
                      exonérations temporaires de 15 à 25&nbsp;ans (art. 1384&nbsp;A et
                      1384&nbsp;C du CGI) sur les opérations récentes. Le traitement des
                      exonérations en cours reste à arrêter (compensation budgétaire sur
                      leur durée restante, ou maintien jusqu&apos;à leur terme)&nbsp;: voir{" "}
                      <Link href="/exonerations-protections" className="underline underline-offset-2">
                        Exonérations et protections
                      </Link>
                      .
                    </li>
                  )}
                  {notes.industrial && (
                    <li>
                      <strong className="font-semibold">{notes.industrial.label}</strong>&nbsp;:
                      {notes.industrial.median
                        ? ` ici, ${notes.industrial.median} en médiane par parcelle.`
                        : ""}{" "}
                      L&apos;impôt actuel des établissements industriels (méthode comptable
                      de l&apos;art. 1499 du CGI, même après la réduction de moitié de 2021)
                      pèse lourdement sur les bâtiments et installations fixes, alors que le
                      foncier des zones d&apos;activités vaut souvent peu au m². La TVTN,
                      qui n&apos;impose que le sol, allège donc l&apos;impôt là où ce
                      foncier est bon marché, et l&apos;alourdit là où les sites industriels
                      occupent un foncier cher (voir{" "}
                      <Link href="/methodologie" className="underline underline-offset-2">
                        la méthodologie
                      </Link>
                      ).
                    </li>
                  )}
                </ul>
              </div>
            )}
          </section>

          {/* 5. Income quintile chart (or explanatory note if unavailable) */}
          <section aria-labelledby="section-quintiles">
            <h3
              id="section-quintiles"
              className="text-xs uppercase tracking-[0.18em] text-gris mb-3"
            >
              Impact par quintile de revenu
            </h3>
            {commune.kind === "territory" && (
              <p className="text-sm text-encre font-body mb-3 max-w-3xl leading-relaxed">
                Classement des revenus sur l&apos;ensemble de la couronne. Comme
                chaque commune garde son propre produit fiscal, ce classement
                mêle l&apos;effet de la réforme et les écarts entre communes
                riches et pauvres — à lire avec le graphique suivant.
              </p>
            )}
            <IncomeQuintileChart
              quintiles={commune.by_income_quintile}
              band={{
                low: commune.headline_sensitivity?.low?.by_income_quintile,
                high: commune.headline_sensitivity?.high?.by_income_quintile,
              }}
            />
            <BandNote />
            <p className="text-xs text-gris font-body mt-2 max-w-3xl leading-relaxed">
              Ces résultats ne portent que sur les logements. La variation de
              l&apos;impôt des commerces, bureaux et locaux industriels n&apos;est
              attribuée à aucun ménage : savoir qui la supporterait au bout du
              compte (clients, salariés, locataires ou propriétaires) est
              difficile à estimer, même à comportements inchangés, et
              indissociable des effets dynamiques de la réforme. Ce point pourra
              être traité dans une seconde phase. La variation de l&apos;impôt des
              bailleurs sociaux n&apos;est pas non plus attribuée aux ménages qui
              y habitent : elle n&apos;est pas récupérable sur leurs loyers.
            </p>
            <PoorestNote commune={commune} />
          </section>

          {/* 5a. Where the change comes from: revaluation vs the TVTN */}
          <section aria-labelledby="section-etapes">
            <h3
              id="section-etapes"
              className="text-xs uppercase tracking-[0.18em] text-gris mb-3"
            >
              D&apos;où viennent les écarts ?
            </h3>
            <p className="text-sm text-encre font-body mb-3 max-w-3xl leading-relaxed">
              Une partie des écarts ne tient pas à la TVTN : elle vient de ce que
              la taxe foncière des logements repose encore sur des valeurs
              locatives de 1970. Le tableau sépare deux étapes, chacune à
              recettes constantes : <strong>1.</strong> l&apos;impôt d&apos;aujourd&apos;hui,
              réparti entre les logements selon leur valeur de marché actuelle,
              sans rien changer d&apos;autre (ce qu&apos;apporterait, en ordre de
              grandeur, la révision des valeurs locatives des logements, repoussée à 2031) ;{" "}
              <strong>2.</strong> le passage à la TVTN, qui met aussi fin aux
              exonérations des logements sociaux. Chaque case est en % de
              l&apos;impôt actuel du groupe ; les deux étapes s&apos;additionnent
              au total.
            </p>
            <StepsTable
              byCategory={publishedCategories(commune.by_category)}
              byQuintile={commune.by_income_quintile}
            />
            <p className="text-xs text-gris font-body mt-2 max-w-3xl leading-relaxed">
              L&apos;impôt d&apos;aujourd&apos;hui est lui-même une estimation : faute
              d&apos;accès aux valeurs locatives réelles, il est réparti selon la
              surface, par groupe de locaux. La première étape mesure donc le
              passage d&apos;une répartition selon la surface à une répartition
              selon la valeur, non l&apos;effet exact de la révision. Les loyers
              variant moins que les prix d&apos;un quartier à l&apos;autre, la
              valeur y est atténuée (voir la méthodologie). Les surfaces de
              commerces, de bureaux et d&apos;industrie gardent leur part à cette
              étape, leurs valeurs ayant été révisées en 2017 : une catégorie de
              bien ne bouge que par les logements qu&apos;elle compte.
            </p>
          </section>

          {/* 5b. Territory only: quintiles ranked within each commune */}
          {commune.kind === "territory" && (
            <section aria-labelledby="section-quintiles-intra">
              <h3
                id="section-quintiles-intra"
                className="text-xs uppercase tracking-[0.18em] text-gris mb-3"
              >
                Impact par quintile de revenu — classement au sein de chaque commune
              </h3>
              <p className="text-sm text-encre font-body mb-3 max-w-3xl leading-relaxed">
                Les revenus sont classés à l&apos;intérieur de chaque commune,
                là où la réforme s&apos;applique réellement, puis regroupés. Les
                communes trop petites pour former cinq groupes de revenu sont
                exclues
                {commune.by_income_quintile_within_coverage_pct != null
                  ? ` (couverture : ${commune.by_income_quintile_within_coverage_pct.toLocaleString("fr-FR")} % des parcelles).`
                  : "."}
              </p>
              <IncomeQuintileChart
                quintiles={commune.by_income_quintile_within ?? null}
                band={{
                  low: commune.headline_sensitivity?.low?.by_income_quintile_within,
                  high: commune.headline_sensitivity?.high?.by_income_quintile_within,
                }}
              />
              <BandNote />
            </section>
          )}

          {/* 6. Territory only: the per-commune spread behind the aggregate */}
          {commune.kind === "territory" && commune.members && (
            <section aria-labelledby="section-membres">
              <h3
                id="section-membres"
                className="text-xs uppercase tracking-[0.18em] text-gris mb-3"
              >
                Détail par commune membre
              </h3>
              <TerritoryMembers members={commune.members} coverage={commune.coverage} />
            </section>
          )}
        </div>
      </div>
    </div>
  );
}
