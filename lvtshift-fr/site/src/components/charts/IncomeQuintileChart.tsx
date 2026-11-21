"use client";

/**
 * IncomeQuintileChart — tax change across income quintiles Q1→Q5.
 *
 * Offers a 2-mode toggle when household-weighted metrics are present:
 *   - "total" (default): bars show the whole group's total change on its
 *     residential parcels (with ±20 % whiskers), and outlined diamonds (◇)
 *     overlay the typical household's change.
 *   - "household": bars show the typical household's change (parcel change
 *     weighted by dwellings) with its own ±20 % whiskers.
 *
 * Older payloads without those figures fall back to the residential parcel
 * median, and the caption says so.
 *
 * When quintiles === null (IRIS income too homogeneous to slice), renders
 * an explanatory note instead of a chart.
 */

import { ReactElement, useState } from "react";
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
import { euros, pct, signedPct, signedPctAxis } from "@/lib/format";
import { quintileBars, type QuintileBar, type QuintileMode } from "@/lib/quintile";
import { symmetricAxis } from "@/lib/axis";
import { ROUGE, GREEN, CREME, ENCRE, GRIS, GRIS_PALE, LISERE, TICK } from "./theme";

const QUINTILE_MODES: { id: QuintileMode; label: string }[] = [
  { id: "total", label: "Ensemble du groupe (total)" },
  { id: "household", label: "Ménage type (par logement)" },
];

/* ── tooltip ──────────────────────────────────────────────────────── */

function makeTooltip(isTotal: boolean, mode: QuintileMode) {
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
        {row.household != null && (
          <p style={mode === "household" ? { fontWeight: 600 } : undefined}>
            Ménage type (par logement)&nbsp;: {signedPct(row.household)}
          </p>
        )}
        {row.share_dwellings_paying_more_pct != null && (
          <p>
            Logements payant davantage&nbsp;:{" "}
            {pct(row.share_dwellings_paying_more_pct)}
          </p>
        )}
        {(isTotal || row.total_change_pct != null) && (
          <p style={mode === "total" && isTotal ? { fontWeight: 600 } : undefined}>
            Ensemble du groupe (total)&nbsp;: {signedPct(row.total_change_pct ?? row.bar)}
          </p>
        )}
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
            Fourchette (coût du bâti ±20&nbsp;%)&nbsp;: {signedPct(row.bandLo)}{" "}
            à {signedPct(row.bandHi)}
          </p>
        )}
      </div>
    );
  };
}

/* ── values under each quintile ───────────────────────────────────── */

function makeQuintileTick(data: QuintileBar[], showDiamond: boolean) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return function QuintileTick(props: any): ReactElement<SVGElement> {
    const row = data.find((r) => r.quintile === props.payload?.value);
    const x: number = props.x ?? 0;
    const y: number = props.y ?? 0;
    const font = { fontFamily: "var(--font-body)", textAnchor: "middle" as const };
    return (
      <g>
        <text x={x} y={y + 12} fontSize={11} fill={GRIS} {...font}>
          Q{props.payload?.value}
        </text>
        {row?.bar != null && (
          <text
            x={x}
            y={y + 28}
            fontSize={11}
            fontWeight={600}
            fill={row.bar >= 0 ? ROUGE : GREEN}
            {...font}
          >
            {signedPct(row.bar)}
          </text>
        )}
        {showDiamond && row?.household != null && (
          <text x={x} y={y + 43} fontSize={10} fill={ENCRE} {...font}>
            ◇&#8239;{signedPct(row.household)}
          </text>
        )}
      </g>
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

function QuintileCaption({
  mode,
  isTotal,
  hasHousehold,
}: {
  mode: QuintileMode;
  isTotal: boolean;
  hasHousehold: boolean;
}) {
  const style = {
    fontFamily: "var(--font-body)",
    fontSize: "0.8125rem",
    color: ENCRE,
    lineHeight: 1.6,
    marginTop: "0.5rem",
    maxWidth: "48rem",
  } as const;
  if (mode === "household") {
    return (
      <p style={style}>
        <strong>Barres</strong> (chiffre en couleur sous chaque quintile)&nbsp;:
        variation médiane pour le ménage type du groupe — chaque parcelle
        résidentielle compte autant de fois qu&apos;elle a de logements.
      </p>
    );
  }
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
      <strong>Barres</strong> (chiffre en couleur sous chaque quintile)&nbsp;:
      variation de l&apos;impôt payé par
      l&apos;ensemble des logements du groupe (total des nouvelles cotisations
      rapporté au total actuel, parcelles résidentielles).
      {hasHousehold && (
        <>
          {" "}<strong>Losanges</strong> (◇)&nbsp;: variation pour le ménage type du
          groupe — chaque parcelle compte autant de fois qu&apos;elle a de
          logements.
        </>
      )}
    </p>
  );
}

/* ── component ────────────────────────────────────────────────────── */

export interface IncomeQuintileChartProps {
  quintiles: QuintileRow[] | null;
  /** Low / high legs of the sensitivity band (optional). */
  band?: {
    low?: BandQuintileRow[] | null;
    high?: BandQuintileRow[] | null;
  };
}

export default function IncomeQuintileChart({
  quintiles,
  band,
}: IncomeQuintileChartProps) {
  const [requestedMode, setRequestedMode] = useState<QuintileMode>("total");
  if (!quintiles) return <NullQuintileNote />;

  const {
    rows: data,
    isTotal,
    hasHousehold,
    mode,
  } = quintileBars(quintiles, band?.low, band?.high, requestedMode);

  const showDiamond = mode === "total" && hasHousehold;

  const vals = data.flatMap((r) =>
    [r.bar, r.bandLo, r.bandHi, showDiamond ? r.household : null].filter(
      (v): v is number => v != null,
    ),
  );
  // symmetric axis on round ticks (values are printed under the axis)
  const absMax = Math.max(...vals.map(Math.abs), 5);
  const { lim, ticks } = symmetricAxis(absMax, { headroom: 1.1 });
  const domain: [number, number] = [-lim, lim];

  const incomes = data.map((r) => r.median_income_eur);
  const incomeRange =
    incomes.length >= 2
      ? `De ${euros(Math.min(...incomes))} (Q1) à ${euros(Math.max(...incomes))} (Q5) de revenu médian IRIS`
      : null;

  return (
    <figure aria-label="Variation de l'impôt par quintile de revenu">
      {hasHousehold && (
        <div
          role="group"
          aria-label="Mode d'affichage du graphique par quintile"
          className="flex flex-wrap gap-1.5 mb-3"
        >
          {QUINTILE_MODES.map((opt) => {
            const active = opt.id === mode;
            return (
              <button
                key={opt.id}
                type="button"
                aria-pressed={active}
                onClick={() => setRequestedMode(opt.id)}
                className={`px-3 py-1.5 text-xs font-body border transition-colors cursor-pointer ${
                  active
                    ? "bg-marine text-creme border-marine font-medium"
                    : "bg-creme text-encre border-lisere hover:border-marine/50"
                }`}
              >
                {opt.label}
              </button>
            );
          })}
        </div>
      )}

      <ResponsiveContainer width="100%" height={showDiamond ? 330 : 315}>
        <ComposedChart
          data={data}
          margin={{ top: 12, right: 8, bottom: 8, left: 0 }}
          barCategoryGap="35%"
        >
          <XAxis
            dataKey="quintile"
            tick={makeQuintileTick(data, showDiamond)}
            height={showDiamond ? 52 : 36}
            interval={0}
            axisLine={{ stroke: LISERE }}
            tickLine={{ stroke: LISERE }}
          />
          <YAxis
            domain={domain}
            ticks={ticks}
            tickFormatter={signedPctAxis}
            interval={0}
            tick={TICK}
            axisLine={false}
            tickLine={false}
            width={52}
          />
          <Tooltip content={makeTooltip(isTotal, mode)} cursor={{ fill: "rgba(0,0,0,0.04)" }} />
          <ReferenceLine y={0} stroke={ENCRE} strokeWidth={1.5} />
          <Bar
            dataKey="bar"
            maxBarSize={40}
            isAnimationActive={false}
          >
            {data.map((entry, idx) => (
              <Cell key={`q-cell-${idx}`} fill={(entry.bar ?? 0) >= 0 ? ROUGE : GREEN} />
            ))}
            <ErrorBar dataKey="err" direction="y" width={8} stroke={ENCRE} strokeWidth={1} />
          </Bar>
          {showDiamond && (
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
      <QuintileCaption mode={mode} isTotal={isTotal} hasHousehold={hasHousehold} />
      <figcaption className="sr-only">
        {data
          .map(
            (r) =>
              `Q${r.quintile} : ${signedPct(r.bar)}` +
              (showDiamond && r.household != null ? `, ménage type ${signedPct(r.household)}` : ""),
          )
          .join(" ; ")}
      </figcaption>
    </figure>
  );
}
