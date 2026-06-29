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

export interface HeadlineCardsProps {
  headline: Headline;
  /** Pass commune.headline_sensitivity.base.share_paying_more_pct */
  sharePayingMorePct: number | null;
}

const MARINE = "#1a2744";
const ROUGE  = "#b5281e";
const CREME  = "#f6f4f0";
const GRIS   = "#6b6560";
const LISERE = "#d6d1ca";

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
      note: "de la base taxable",
      accent: false,
    },
    {
      id: "paysmore",
      label: "Proportion qui paie davantage",
      value: pct(sharePayingMorePct),
      note: "des propriétaires concernés",
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
