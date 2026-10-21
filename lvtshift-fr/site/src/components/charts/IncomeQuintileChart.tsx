"use client";

/**
 * IncomeQuintileChart — tax change across income quintiles Q1→Q5.
 *
 * Bar: the whole group's total change on its residential parcels.
 * Diamond: the typical household's change (parcel change weighted by
 * dwellings). See lib/quintile.ts for why a plain parcel median misleads.
 * Older payloads without those figures fall back to the residential parcel
 * median, and the caption says so.
 *
 * When quintiles === null (IRIS income too homogeneous to slice), renders
 * an explanatory note instead of a chart.
 *
 * Bar colours: rouge when positive (pays more), institutional green when
 * negative (pays less). A reference line at y=0 makes the sign clear.
 */

import { ReactElement } from "react";
import {
  ComposedChart,
  Bar,
  Scatter,
  Cell,
  ErrorBar,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
} from "recharts";
import type { TooltipProps } from "recharts";
import type { BandQuintileRow, QuintileRow } from "@/lib/types";
import { euros, signedPct } from "@/lib/format";
import { quintileBars, type QuintileBar } from "@/lib/quintile";
import { ROUGE, GREEN, CREME, ENCRE, GRIS, GRIS_PALE, LISERE, TICK } from "./theme";

/* ── tooltip ──────────────────────────────────────────────────────── */

function makeTooltip(isTotal: boolean) {
  return function QuintileTooltip({ active, payload, label }: TooltipProps<number, string>) {
    if (!active || !payload?.length) return null;
    const row = payload[0]?.payload as QuintileBar;
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
        <p style={{ fontWeight: 600, marginBottom: "0.25rem" }}>Quintile {label}</p>
        <p>Revenu médian IRIS&nbsp;: {euros(row.median_income_eur)}</p>
        {isTotal && <p>Ensemble du groupe&nbsp;: {signedPct(row.bar)}</p>}
        {row.household != null && <p>Ménage type&nbsp;: {signedPct(row.household)}</p>}
        <p>
          Parcelle résidentielle médiane&nbsp;:{" "}
          {signedPct(row.median_change_pct_residential)}
        </p>
        <p>
          Parcelles&nbsp;: {row.parcels.toLocaleString("fr-FR")}
          {row.dwellings != null && <> · logements&nbsp;: {row.dwellings.toLocaleString("fr-FR")}</>}
        </p>
        {row.bandLo !== null && row.bandHi !== null && (
          <p style={{ color: GRIS_PALE }}>
            Fourchette (±10&nbsp;pt de part foncière)&nbsp;: {signedPct(row.bandLo)}{" "}
            à {signedPct(row.bandHi)}
          </p>
        )}
      </div>
    );
  };
}

/* ── value label outside the end of each bar ─────────────────────── */

function makeBarLabel(data: QuintileBar[]) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return function QuintileBarLabel(props: any): ReactElement | null {
    const entry = data[props.index ?? 0];
    if (!entry || entry.bar == null) return null;
    const x: number = props.x ?? 0;
    const width: number = props.width ?? 0;
    const y: number = props.y ?? 0;
    const height: number = props.height ?? 0;
    // Recharts may report a negative bar with a negative height, so take the
    // rectangle's true top and bottom rather than trusting the sign.
    const top = Math.min(y, y + height);
    const bottom = Math.max(y, y + height);
    const neg = entry.bar < 0;
    // Clear the whisker and the household diamond when they reach past the
    // bar's end: convert their overshoot to pixels with the bar's own scale.
    const reach = [entry.bar, entry.bandLo, entry.bandHi, entry.household]
      .filter((v): v is number => v != null);
    const extreme = neg ? Math.min(...reach) : Math.max(...reach);
    const pxPerUnit = entry.bar !== 0 ? Math.abs(height) / Math.abs(entry.bar) : 0;
    const overshoot = Math.abs(extreme - entry.bar) * pxPerUnit;
    const markerPad = entry.household != null ? 7 : 0;
    return (
      <text
        x={x + width / 2}
        y={neg ? bottom + overshoot + markerPad + 12 : top - overshoot - markerPad - 6}
        textAnchor="middle"
        fontSize={10}
        fill={neg ? GREEN : ROUGE}
        fontFamily="var(--font-body)"
        fontWeight={600}
      >
        {signedPct(entry.bar)}
      </text>
    );
  };
}

/* ── household marker: an outlined diamond ───────────────────────── */

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function Diamond(props: any): ReactElement | null {
  const { cx, cy } = props;
  if (!Number.isFinite(cx) || !Number.isFinite(cy)) return null;
  const r = 6;
  return (
    <path
      d={`M${cx},${cy - r} L${cx + r},${cy} L${cx},${cy + r} L${cx - r},${cy} Z`}
      fill={CREME}
      stroke={ENCRE}
      strokeWidth={1.5}
    />
  );
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
      Revenu IRIS trop peu varié dans cette commune pour un découpage en quintiles
    </div>
  );
}

/* ── caption: what the bar and the diamond measure ───────────────── */

function QuintileCaption({ isTotal, hasHousehold }: { isTotal: boolean; hasHousehold: boolean }) {
  const style = {
    fontFamily: "var(--font-body)",
    fontSize: "0.8125rem",
    color: ENCRE,
    lineHeight: 1.6,
    marginTop: "0.5rem",
    maxWidth: "48rem",
  } as const;
  if (!isTotal) {
    return (
      <p style={style}>
        Barres&nbsp;: variation médiane par parcelle résidentielle. Une parcelle
        compte une fois, qu&apos;elle porte une maison ou un immeuble de 200
        logements.
      </p>
    );
  }
  return (
    <p style={style}>
      <strong>Barres</strong>&nbsp;: variation de l&apos;impôt payé par
      l&apos;ensemble des logements du groupe (total des nouvelles cotisations
      rapporté au total actuel, parcelles résidentielles).
      {hasHousehold && (
        <>
          {" "}<strong>Losanges</strong>&nbsp;: variation pour le ménage type du
          groupe — chaque parcelle compte autant de fois qu&apos;elle a de
          logements.
        </>
      )}{" "}
      Une simple médiane par parcelle compterait un immeuble de 200 logements
      une seule fois, comme une maison&nbsp;: elle peut montrer la plupart des
      parcelles en hausse alors que le groupe, dans son ensemble, paie moins.
    </p>
  );
}

/* ── component ────────────────────────────────────────────────────── */

export interface IncomeQuintileChartProps {
  quintiles: QuintileRow[] | null;
  /** Low / high legs of the ±10 pt land-share band (optional). */
  band?: {
    low?: BandQuintileRow[] | null;
    high?: BandQuintileRow[] | null;
  };
}

export default function IncomeQuintileChart({
  quintiles,
  band,
}: IncomeQuintileChartProps) {
  if (!quintiles) return <NullQuintileNote />;

  const { rows: data, isTotal, hasHousehold } = quintileBars(quintiles, band?.low, band?.high);

  const vals = data.flatMap((r) =>
    [r.bar, r.bandLo, r.bandHi, r.household].filter((v): v is number => v != null),
  );
  // symmetric axis on a round 5-point step, with headroom for the labels
  const absMax = Math.max(...vals.map(Math.abs), 5);
  const lim = Math.ceil((absMax * 1.3) / 5) * 5;
  const domain: [number, number] = [-lim, lim];
  const ticks = [-lim, -lim / 2, 0, lim / 2, lim];

  const incomes = data.map((r) => r.median_income_eur);
  const incomeRange =
    incomes.length >= 2
      ? `De ${euros(Math.min(...incomes))} (Q1) à ${euros(Math.max(...incomes))} (Q5) de revenu médian IRIS`
      : null;

  return (
    <div>
      <ResponsiveContainer width="100%" height={300}>
        <ComposedChart
          data={data}
          margin={{ top: 28, right: 24, bottom: 32, left: 16 }}
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
            ticks={ticks}
            tickFormatter={(v: number) => signedPct(v)}
            tick={TICK}
            axisLine={false}
            tickLine={false}
            width={48}
          />
          <Tooltip content={makeTooltip(isTotal)} cursor={{ fill: "rgba(0,0,0,0.04)" }} />
          <ReferenceLine y={0} stroke={ENCRE} strokeWidth={1.5} />
          <Bar
            dataKey="bar"
            barSize={40}
            isAnimationActive={false}
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            label={makeBarLabel(data) as any}
          >
            {data.map((entry, idx) => (
              <Cell key={`q-cell-${idx}`} fill={(entry.bar ?? 0) >= 0 ? ROUGE : GREEN} />
            ))}
            <ErrorBar dataKey="err" direction="y" width={8} stroke={ENCRE} strokeWidth={1} />
          </Bar>
          {hasHousehold && (
            <Scatter dataKey="household" shape={<Diamond />} isAnimationActive={false} />
          )}
        </ComposedChart>
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
      <QuintileCaption isTotal={isTotal} hasHousehold={hasHousehold} />
    </div>
  );
}
