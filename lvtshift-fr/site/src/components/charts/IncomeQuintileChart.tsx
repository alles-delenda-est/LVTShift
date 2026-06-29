"use client";

/**
 * IncomeQuintileChart — bar chart of median_change_pct_residential
 * across income quintiles Q1→Q5.
 *
 * When quintiles === null (IRIS income too homogeneous to slice), renders
 * an explanatory note instead of a chart.
 *
 * Bar colours: rouge when positive (pays more), institutional green when
 * negative (pays less).  A reference line at y=0 makes the sign clear.
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
import type { QuintileRow } from "@/lib/types";
import { euros, signedPct } from "@/lib/format";

const ROUGE   = "#b5281e";
const GREEN   = "#2a6244";
const CREME   = "#f6f4f0";
const ENCRE   = "#1c1917";
const GRIS    = "#6b6560";
const LISERE  = "#d6d1ca";

const TICK = {
  fontFamily: "var(--font-body)",
  fontSize: 11,
  fill: GRIS,
} as const;

/* ── tooltip ──────────────────────────────────────────────────────── */

function QuintileTooltip({ active, payload, label }: TooltipProps<number, string>) {
  if (!active || !payload?.length) return null;
  const row = payload[0]?.payload as QuintileRow;
  return (
    <div
      style={{
        background: ENCRE,
        color: CREME,
        padding: "0.75rem 1rem",
        fontSize: 12,
        fontFamily: "var(--font-body)",
        border: `1px solid ${GRIS}`,
        lineHeight: 1.65,
      }}
    >
      <p style={{ fontWeight: 600, marginBottom: "0.25rem" }}>
        Quintile {label}
      </p>
      <p>Revenu médian IRIS&nbsp;: {euros(row.median_income_eur)}</p>
      <p>
        Variation résidentielle&nbsp;:{" "}
        {signedPct(row.median_change_pct_residential)}
      </p>
      <p>Parcelles&nbsp;: {row.parcels.toLocaleString("fr-FR")}</p>
    </div>
  );
}

/* ── label rendered above/below each bar ─────────────────────────── */

function makeBarLabel(data: QuintileRow[]) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return function QuintileBarLabel(props: any): ReactElement | null {
    const x: number      = props.x      ?? 0;
    const y: number      = props.y      ?? 0;
    const width: number  = props.width  ?? 0;
    const val: number    = props.value  ?? 0;
    const idx: number    = props.index  ?? 0;

    const entry = data[idx];
    if (!entry) return null;

    const label = signedPct(entry.median_change_pct_residential);
    const PADDING = 4;
    // For a standard vertical bar chart (default layout):
    //   positive bar: y is top of bar, label goes above  (y - PADDING)
    //   negative bar: y + height is bottom, but Bar provides y = top, height < 0?
    // Actually Recharts gives y = top of bar, height = bar pixel height (positive).
    // For negative values the bar extends downward from the zero line.
    // props.y for a negative bar = zero-line y, bar goes down.
    // Simpler: just place label above the bar rect using props.y - PADDING.
    const textY = val >= 0 ? y - PADDING : y + (props.height ?? 0) + PADDING + 10;
    const textAnchor = "middle";

    return (
      <text
        x={x + width / 2}
        y={textY}
        textAnchor={textAnchor}
        dominantBaseline={val < 0 ? "hanging" : "auto"}
        fontSize={10}
        fill={val >= 0 ? ROUGE : GREEN}
        fontFamily="var(--font-body)"
        fontWeight={600}
      >
        {label}
      </text>
    );
  };
}

/* ── null-case message ────────────────────────────────────────────── */

function NullQuintileNote() {
  return (
    <div
      style={{
        padding: "2rem 1.5rem",
        border: `1px solid ${LISERE}`,
        background: CREME,
        fontFamily: "var(--font-body)",
        fontSize: "0.9375rem",
        color: GRIS,
        fontStyle: "italic",
        textAlign: "center",
        lineHeight: 1.6,
      }}
    >
      Revenu IRIS trop peu varié dans cette commune pour un découpage en quintiles.
    </div>
  );
}

/* ── component ────────────────────────────────────────────────────── */

export interface IncomeQuintileChartProps {
  quintiles: QuintileRow[] | null;
}

export default function IncomeQuintileChart({
  quintiles,
}: IncomeQuintileChartProps) {
  if (!quintiles) return <NullQuintileNote />;

  /* Sort by quintile ascending (should already be, but guard) */
  const data = [...quintiles].sort((a, b) => a.quintile - b.quintile);

  const vals = data.map((r) => r.median_change_pct_residential ?? 0);
  const absMax = Math.max(...vals.map(Math.abs), 5);
  const domain: [number, number] = [-absMax * 1.35, absMax * 1.35];

  /* Subtitle: income range */
  const incomes = data.map((r) => r.median_income_eur);
  const incomeRange =
    incomes.length >= 2
      ? `De ${euros(Math.min(...incomes))} (Q1) à ${euros(Math.max(...incomes))} (Q5) de revenu médian IRIS`
      : null;

  const cellFill = (val: number | null) =>
    (val ?? 0) >= 0 ? ROUGE : GREEN;

  const renderLabel = makeBarLabel(data);

  return (
    <div>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart
          data={data}
          margin={{ top: 28, right: 24, bottom: 32, left: 16 }}
          barSize={40}
          barCategoryGap="35%"
        >
          <XAxis
            dataKey="quintile"
            tickFormatter={(v: number) => `Q${v}`}
            tick={TICK}
            axisLine={{ stroke: LISERE }}
            tickLine={{ stroke: LISERE }}
          />
          <YAxis
            domain={domain}
            tickFormatter={(v: number) =>
              v === 0 ? "0 %" : `${v > 0 ? "+" : ""}${v} %`
            }
            tick={TICK}
            axisLine={false}
            tickLine={false}
            width={48}
          />
          <Tooltip
            content={<QuintileTooltip />}
            cursor={{ fill: "rgba(0,0,0,0.04)" }}
          />
          <ReferenceLine y={0} stroke={ENCRE} strokeWidth={1.5} />
          <Bar
            dataKey="median_change_pct_residential"
            isAnimationActive={false}
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            label={renderLabel as any}
          >
            {data.map((entry, idx) => (
              <Cell
                key={`q-cell-${idx}`}
                fill={cellFill(entry.median_change_pct_residential)}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {incomeRange && (
        <p
          style={{
            fontFamily: "var(--font-body)",
            fontSize: "0.75rem",
            color: GRIS,
            fontStyle: "italic",
            textAlign: "center",
            marginTop: "0.25rem",
          }}
        >
          {incomeRange}
        </p>
      )}
    </div>
  );
}

