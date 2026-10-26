"use client";

/**
 * HeadlineCards — four key-figure stat tiles.
 *
 * Honesty rule: "Proportion qui paie davantage" gets the same visual
 * weight as every other headline — a rouge accent border, rouge numerals.
 * Never buried.
 */

import type { Headline } from "@/lib/types";
import { euros, pct } from "@/lib/format";
import { MARINE, ROUGE, CREME, GRIS, LISERE } from "./theme";

export interface HeadlineCardsProps {
  headline: Headline;
  /** Pass commune.headline_sensitivity.base.share_paying_more_pct */
  sharePayingMorePct: number | null;
}

interface StatDef {
  id: string;
  label: string;
  value: string;
  note: string;
  accent: boolean;
}

export default function HeadlineCards({
  headline,
  sharePayingMorePct,
}: HeadlineCardsProps) {
  // When most built parcels sit at the 85 % clip, the land share is set by the
  // bound, not measured: label it as such rather than present it as a finding.
  const capPct = headline.built_at_cap_pct ?? null;
  const capped = capPct !== null && capPct >= 50;
  const stats: StatDef[] = [
    {
      id: "parcels",
      label: "Parcelles modélisées",
      value: headline.parcels_modeled.toLocaleString("fr-FR"),
      note: "unités foncières",
      accent: false,
    },
    {
      id: "levy",
      label: "Prélèvement neutre",
      value: euros(headline.neutral_levy_eur),
      note: "à recettes constantes",
      accent: false,
    },
    {
      id: "land",
      label: "Part foncière estimée",
      value: pct(headline.land_share_pct),
      note: capped
        ? `plafonnée : ${pct(capPct)} des parcelles bâties à la borne de 85 % — chiffre fixé par l'hypothèse, non mesuré`
        : "de la base taxable",
      accent: false,
    },
    {
      id: "paysmore",
      label: "Proportion qui paie davantage",
      value: pct(sharePayingMorePct),
      // It counts parcels, not owners or households: one parcel can hold a
      // house or a 200-flat building (see the quintile chart's caption).
      note: "des parcelles (une copropriété compte pour une)",
      accent: true,
    },
  ];

  return (
    <div
      role="list"
      aria-label="Indicateurs clés"
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(2, 1fr)",
        gap: "1px",
        backgroundColor: LISERE,
        border: `1px solid ${LISERE}`,
      }}
    >
      {stats.map((s) => (
        <article
          key={s.id}
          role="listitem"
          style={{
            backgroundColor: CREME,
            borderTop: `3px solid ${s.accent ? ROUGE : "transparent"}`,
            padding: "1.5rem",
            display: "flex",
            flexDirection: "column",
            gap: "0.5rem",
          }}
        >
          <span
            style={{
              fontFamily: "var(--font-body)",
              fontSize: "0.6875rem",
              letterSpacing: "0.1em",
              textTransform: "uppercase",
              color: GRIS,
            }}
          >
            {s.label}
          </span>
          <span
            style={{
              fontFamily: "var(--font-display)",
              fontSize: "clamp(1.5rem, 3.5vw, 2.25rem)",
              lineHeight: 1,
              color: s.accent ? ROUGE : MARINE,
            }}
          >
            {s.value}
          </span>
          <span
            style={{
              fontFamily: "var(--font-body)",
              fontSize: "0.6875rem",
              fontStyle: "italic",
              color: GRIS,
            }}
          >
            {s.note}
          </span>
        </article>
      ))}
    </div>
  );
}
