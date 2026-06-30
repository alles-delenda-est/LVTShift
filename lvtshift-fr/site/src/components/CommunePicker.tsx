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

import { useState } from "react";
import type { Commune } from "@/lib/types";
import HeadlineCards from "@/components/charts/HeadlineCards";
import SensitivityBand from "@/components/charts/SensitivityBand";
import WinLoseSplit from "@/components/charts/WinLoseSplit";
import CategoryImpactBars from "@/components/charts/CategoryImpactBars";
import IncomeQuintileChart from "@/components/charts/IncomeQuintileChart";

export interface CommunePickerProps {
  communes: Commune[];
}

export default function CommunePicker({ communes }: CommunePickerProps) {
  const defaultKey =
    communes.find((c) => c.commune_key === "montreuil")?.commune_key ??
    communes[0]?.commune_key ??
    "";

  const [selectedKey, setSelectedKey] = useState<string>(defaultKey);

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
        <div className="relative inline-block">
          <select
            id="commune-select"
            value={selectedKey}
            onChange={(e) => setSelectedKey(e.target.value)}
            className="
              border border-lisere bg-creme text-encre
              font-body text-base
              px-4 py-2.5
              pr-10
              appearance-none
              cursor-pointer
              focus:outline-none focus:ring-2 focus:ring-marine/40
              min-w-[18rem]
            "
          >
            {communes.map((c) => (
              <option key={c.commune_key} value={c.commune_key}>
                {c.name}
                {c.departement ? ` (${c.departement})` : ""}
              </option>
            ))}
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
            Code INSEE&nbsp;: {commune.insee}
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

          {/* 3. Win/lose split by category */}
          <section aria-labelledby="section-gagnants">
            <h3
              id="section-gagnants"
              className="text-xs uppercase tracking-[0.18em] text-gris mb-3"
            >
              Gagnants et perdants par catégorie
            </h3>
            <WinLoseSplit byCategory={commune.by_category} />
          </section>

          {/* 4. Category impact (diverging median bars) */}
          <section aria-labelledby="section-categories">
            <h3
              id="section-categories"
              className="text-xs uppercase tracking-[0.18em] text-gris mb-3"
            >
              Impact médian par catégorie de bien
            </h3>
            <CategoryImpactBars byCategory={commune.by_category} />
          </section>

          {/* 5. Income quintile chart (or explanatory note if unavailable) */}
          <section aria-labelledby="section-quintiles">
            <h3
              id="section-quintiles"
              className="text-xs uppercase tracking-[0.18em] text-gris mb-3"
            >
              Impact par quintile de revenu
            </h3>
            <IncomeQuintileChart quintiles={commune.by_income_quintile} />
          </section>
        </div>
      </div>
    </div>
  );
}
