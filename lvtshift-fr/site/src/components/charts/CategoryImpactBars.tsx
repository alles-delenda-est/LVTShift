"use client";

/**
 * CategoryImpactBars — horizontal diverging bars showing median_change_pct
 * per property category, sorted descending (most positive first, null last).
 *
 * Colour convention:
 *   positive (pays more)  → rouge  (#b5281e)
 *   negative (pays less)  → green  (#2a6244)
 *   null (no median)      → gris pâle — bar at 0, labelled "n. d."
 *
 * Null categories (e.g. Terrain nu / non bâti — 100 % pay more but the
 * median is undefined) are kept visible: zero-width bar at the reference
 * line, "n. d." label, and median_change_eur shown in the tooltip.
 */

import { ReactElement } from "react";
import {
  BarChart,
  Bar,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
} from "recharts";
import type { TooltipProps } from "recharts";
import type { CategoryRow } from "@/lib/types";
import { pct, signedPct, eurosExact } from "@/lib/format";

const MARINE    = "#1a2744";
const ROUGE     = "#b5281e";
const GREEN     = "#2a6244";
const CREME     = "#f6f4f0";
const ENCRE     = "#1c1917";
const GRIS      = "#6b6560";
const GRIS_PALE = "#b0a89f";
const LISERE    = "#d6d1ca";

void MARINE; // imported but colour only used via GREEN/ROUGE/GRIS_PALE per-cell

const TICK = {
  fontFamily: "var(--font-body)",
  fontSize: 11,
  fill: GRIS,
} as const;

/* ── extended row ─────────────────────────────────────────────────── */

interface ProcessedRow extends CategoryRow {
  barValue: number;   // median_change_pct ?? 0
  isNull: boolean;
}

/* ── tooltip ──────────────────────────────────────────────────────── */

function CatTooltip({ active, payload }: TooltipProps<number, string>) {
  if (!active || !payload?.length) return null;
  const row = payload[0]?.payload as ProcessedRow;
  const sign = row.median_change_eur >= 0 ? "+" : "−";
  const absEur = eurosExact(Math.abs(row.median_change_eur));
  return (
    <div
      style={{
        background: ENCRE,
        color: CREME,
        padding: "0.75rem 1rem",
        fontSize: 12,
        fontFamily: "var(--font-body)",
        border: `1px solid ${GRIS}`,
        maxWidth: 270,
        lineHeight: 1.65,
      }}
    >
      <p style={{ fontWeight: 600, marginBottom: "0.25rem" }}>{row.label_fr}</p>
      <p>
        Variation médiane&nbsp;:{" "}
        {row.isNull ? "n. d." : signedPct(row.median_change_pct)}
      </p>
      <p>
        En montant&nbsp;: {sign}
        {absEur}
      </p>
      <p>Paie davantage&nbsp;: {pct(row.share_paying_more_pct)}</p>
    </div>
  );
}

/* ── custom label renderer ─────────────────────────────────────────
   Recharts passes label-function props at runtime as
   { x, y, width, height, value, index, ... }.
   We capture `data` via closure to look up the original row by index.
────────────────────────────────────────────────────────────────────── */

function makeLabelRenderer(data: ProcessedRow[]) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return function BarLabel(props: any): ReactElement | null {
    const x: number     = props.x     ?? 0;
    const y: number     = props.y     ?? 0;
    const width: number = props.width ?? 0;
    const height: number = props.height ?? 0;
    const val: number   = props.value ?? 0;
    const idx: number   = props.index ?? 0;

    const entry = data[idx];
    if (!entry) return null;

    const label = entry.isNull ? "n. d." : signedPct(entry.median_change_pct);

    // For layout="vertical" (horizontal bars):
    //   positive bar: x = zero-line pixel, x+width = value pixel (right)
    //   negative bar: x = value pixel (left),  x+width = zero-line pixel
    const PADDING = 5;
    const textX =
      val > 0
        ? x + width + PADDING
        : val < 0
        ? x - PADDING
        : x + width + PADDING;
    const anchor = val < 0 ? "end" : "start";

    return (
      <text
        x={textX}
        y={y + height / 2}
        textAnchor={anchor}
        dominantBaseline="central"
        fontSize={10}
        fill={ENCRE}
        fontFamily="var(--font-body)"
      >
        {label}
      </text>
    );
  };
}

/* ── component ────────────────────────────────────────────────────── */

export interface CategoryImpactBarsProps {
  byCategory: CategoryRow[];
}

export default function CategoryImpactBars({
  byCategory,
}: CategoryImpactBarsProps) {
  /* Sort: most positive → least positive → negative; null rows last */
  const sortedData: ProcessedRow[] = [...byCategory]
    .map((row) => ({
      ...row,
      barValue: row.median_change_pct ?? 0,
      isNull: row.median_change_pct === null,
    }))
    .sort((a, b) => {
      if (a.isNull && !b.isNull) return 1;
      if (!a.isNull && b.isNull) return -1;
      return b.barValue - a.barValue;
    });

  /* Symmetric domain with 10 % headroom for labels */
  const nonNull = sortedData.filter((r) => !r.isNull).map((r) => r.barValue);
  const minVal = nonNull.length ? Math.min(...nonNull) : -10;
  const maxVal = nonNull.length ? Math.max(...nonNull) : 10;
  const absMax = Math.max(Math.abs(minVal), Math.abs(maxVal), 5);
  const domainPad = absMax * 1.35; // extra headroom for outside labels
  const domain: [number, number] = [-domainPad, domainPad];

  const cellFill = (entry: ProcessedRow): string => {
    if (entry.isNull) return GRIS_PALE;
    return entry.barValue >= 0 ? ROUGE : GREEN;
  };

  const BAR_HEIGHT = 38;
  const chartHeight = sortedData.length * BAR_HEIGHT + 64;

  const renderLabel = makeLabelRenderer(sortedData);

  return (
    <ResponsiveContainer width="100%" height={chartHeight}>
      <BarChart
        layout="vertical"
        data={sortedData}
        margin={{ top: 8, right: 80, bottom: 28, left: 8 }}
        barSize={22}
        barCategoryGap="30%"
      >
        <XAxis
          type="number"
          domain={domain}
          tickFormatter={(v: number) =>
            v === 0 ? "0" : `${v > 0 ? "+" : ""}${v} %`
          }
          tick={TICK}
          axisLine={{ stroke: LISERE }}
          tickLine={{ stroke: LISERE }}
        />
        <YAxis
          type="category"
          dataKey="label_fr"
          width={200}
          tick={TICK}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip
          content={<CatTooltip />}
          cursor={{ fill: "rgba(0,0,0,0.04)" }}
        />
        <ReferenceLine x={0} stroke={ENCRE} strokeWidth={1.5} />
        <Bar
          dataKey="barValue"
          isAnimationActive={false}
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          label={renderLabel as any}
        >
          {sortedData.map((entry, idx) => (
            <Cell key={`cat-cell-${idx}`} fill={cellFill(entry)} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
