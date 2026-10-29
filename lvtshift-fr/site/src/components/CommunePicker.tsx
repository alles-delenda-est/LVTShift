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

import { useState, useSyncExternalStore } from "react";
import type { Commune } from "@/lib/types";
import HeadlineCards from "@/components/charts/HeadlineCards";
import SensitivityBand from "@/components/charts/SensitivityBand";
import BaselineRange from "@/components/charts/BaselineRange";
import WinLoseSplit from "@/components/charts/WinLoseSplit";
import CategoryImpactBars from "@/components/charts/CategoryImpactBars";
import IncomeQuintileChart from "@/components/charts/IncomeQuintileChart";
import TerritoryMembers from "@/components/TerritoryMembers";
import { publishedCategories, withheldCategories } from "@/lib/disclosure";

/** Caption under charts that carry the ±10 pt land-share whiskers. */
function BandNote() {
  return (
    <p className="text-xs text-gris font-body italic mt-2 max-w-3xl leading-relaxed">
      Les traits fins indiquent la fourchette obtenue en faisant varier la part
      foncière de ±10&nbsp;points (hypothèses basse et haute) : la valeur du sol
      étant imputée, seule une conclusion qui tient sur toute la fourchette est
      robuste.
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
                centrale la recale sur le total national de la Cour des comptes ;
                l&apos;hypothèse plancher garde le chiffre brut. Les montants
                payés après la réforme sont identiques dans les deux colonnes :
                seul le point de départ change.
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

          {/* 4. Category impact (diverging median bars) */}
          <section aria-labelledby="section-categories">
            <h3
              id="section-categories"
              className="text-xs uppercase tracking-[0.18em] text-gris mb-3"
            >
              Impact médian par catégorie de bien
            </h3>
            <CategoryImpactBars
              byCategory={publishedCategories(commune.by_category)}
              band={{
                low: commune.headline_sensitivity?.low?.by_category,
                high: commune.headline_sensitivity?.high?.by_category,
              }}
            />
            <BandNote />
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
