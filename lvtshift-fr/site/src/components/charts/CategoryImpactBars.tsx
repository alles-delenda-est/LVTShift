"use client";

/**
 * CategoryImpactBars — horizontal diverging bars showing median_change_pct
 * per property category, sorted descending (most positive first, null last).
 *
 * Colour convention:
 *   positive (pays more)  → rouge  (#b5281e)
 *   negative (pays less)  → green  (#2a6244)
 *   null (no median %)    → gris pâle — bar at 0, value shown in euros
 *
 * Null categories (e.g. Terrain nu / non bâti — 100 % pay more, but today's
 * modelled tax is 0 € so the % change is undefined) are kept visible:
 * zero-width bar at the reference line, the median change in euros in the
 * value column, and a footnote saying why.
 */

import { ReactElement } from "react";
import {
  BarChart,
  Bar,
  Cell,
  ErrorBar,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
} from "recharts";
import type { TooltipProps } from "recharts";
import type { BandCategoryRow, CategoryRow } from "@/lib/types";
import { pct, signedPct, signedPctAxis, eurosExact } from "@/lib/format";
import { bandSpan, byKey } from "@/lib/band";
import { symmetricAxis } from "@/lib/axis";
import { ROUGE, GREEN, CREME, ENCRE, GRIS, GRIS_PALE, LISERE, TICK } from "./theme";
import { useNarrow } from "./useNarrow";

/* ── extended row ─────────────────────────────────────────────────── */

interface ProcessedRow extends CategoryRow {
  barValue: number;   // median_change_pct ?? 0
  isNull: boolean;
  /** ±10 pt land-share band: whisker [below, above] and its ends */
  err: [number, number] | null;
  bandLo: number | null;
  bandHi: number | null;
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
      {row.bandLo !== null && row.bandHi !== null && (
        <p style={{ color: GRIS_PALE }}>
          Fourchette (±10&nbsp;pt de part foncière)&nbsp;: {signedPct(row.bandLo)}{" "}
          à {signedPct(row.bandHi)}
        </p>
      )}
    </div>
  );
}

/* ── value column ──────────────────────────────────────────────────
   Values sit in a fixed column on the right (a second, label-only Y axis)
   rather than at the bar ends: on phones the end labels ran into the
   category names and the ±10 pt whiskers. A category whose percentage is
   undefined (vacant land: today's modelled TFPB is 0 €) shows its median
   change in euros instead of "n. d.".
────────────────────────────────────────────────────────────────────── */

function valueText(row: ProcessedRow): string {
  if (!row.isNull) return signedPct(row.median_change_pct);
  const sign = row.median_change_eur > 0 ? "+" : row.median_change_eur < 0 ? "−" : "";
  return `${sign}${eurosExact(Math.abs(row.median_change_eur))}*`;
}

function makeValueTick(data: ProcessedRow[]) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return function ValueTick(props: any): ReactElement<SVGElement> {
    const row = data.find((r) => r.label_fr === props.payload?.value);
    if (!row) return <g />;
    const fill = row.isNull ? ENCRE : row.barValue >= 0 ? ROUGE : GREEN;
    return (
      <text
        x={props.x + 6}
        y={props.y}
        textAnchor="start"
        dominantBaseline="central"
        fontSize={11}
        fontWeight={600}
        fill={fill}
        fontFamily="var(--font-body)"
      >
        {valueText(row)}
      </text>
    );
  };
}

/* ── component ────────────────────────────────────────────────────── */

export interface CategoryImpactBarsProps {
  byCategory: CategoryRow[];
  /** Low / high legs of the ±10 pt land-share band (optional). */
  band?: {
    low?: BandCategoryRow[] | null;
    high?: BandCategoryRow[] | null;
  };
}

export default function CategoryImpactBars({
  byCategory,
  band,
}: CategoryImpactBarsProps) {
  const narrow = useNarrow();
  const low = byKey(band?.low, "category");
  const high = byKey(band?.high, "category");
  /* Sort: most positive → least positive → negative; null rows last */
  const sortedData: ProcessedRow[] = [...byCategory]
    .map((row) => {
      const span = bandSpan(
        row.median_change_pct,
        low.get(row.category)?.median_change_pct,
        high.get(row.category)?.median_change_pct,
      );
      return {
        ...row,
        barValue: row.median_change_pct ?? 0,
        isNull: row.median_change_pct === null,
        err: span?.err ?? null,
        bandLo: span?.lo ?? null,
        bandHi: span?.hi ?? null,
      };
    })
    .sort((a, b) => {
      if (a.isNull && !b.isNull) return 1;
      if (!a.isNull && b.isNull) return -1;
      return b.barValue - a.barValue;
    });

  /* Symmetric axis on round ticks (labels live in their own column) */
  const nonNull = sortedData
    .filter((r) => !r.isNull)
    .flatMap((r) => [r.barValue, r.bandLo ?? r.barValue, r.bandHi ?? r.barValue]);
  const minVal = nonNull.length ? Math.min(...nonNull) : -10;
  const maxVal = nonNull.length ? Math.max(...nonNull) : 10;
  const absMax = Math.max(Math.abs(minVal), Math.abs(maxVal), 5);
  const axis = symmetricAxis(absMax, { headroom: 1.05, maxTicksPerSide: narrow ? 2 : 4 });
  const domain: [number, number] = [-axis.lim, axis.lim];

  const cellFill = (entry: ProcessedRow): string => {
    if (entry.isNull) return GRIS_PALE;
    return entry.barValue >= 0 ? ROUGE : GREEN;
  };

  const BAR_HEIGHT = 38;
  const chartHeight = sortedData.length * BAR_HEIGHT + 64;

  const valueTick = makeValueTick(sortedData);
  const vacant = sortedData.find((r) => r.isNull);

  return (
    <figure aria-label="Variation médiane de l'impôt par catégorie de bien">
    <ResponsiveContainer width="100%" height={chartHeight}>
      <BarChart
        layout="vertical"
        data={sortedData}
        margin={{ top: 8, right: 4, bottom: 28, left: 0 }}
        barSize={22}
        barCategoryGap="30%"
      >
        <XAxis
          type="number"
          domain={domain}
          ticks={axis.ticks}
          interval={0}
          tickFormatter={signedPctAxis}
          tick={TICK}
          axisLine={{ stroke: LISERE }}
          tickLine={{ stroke: LISERE }}
        />
        <YAxis
          type="category"
          dataKey="label_fr"
          width={narrow ? 112 : 200}
          tick={TICK}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          yAxisId="values"
          orientation="right"
          type="category"
          dataKey="label_fr"
          width={narrow ? 64 : 80}
          tick={valueTick}
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
        >
          {sortedData.map((entry, idx) => (
            <Cell key={`cat-cell-${idx}`} fill={cellFill(entry)} />
          ))}
          <ErrorBar
            dataKey="err"
            direction="x"
            width={6}
            stroke={ENCRE}
            strokeWidth={1}
          />
        </Bar>
      </BarChart>
    </ResponsiveContainer>
      <figcaption className="sr-only">
        {sortedData.map((r) => `${r.label_fr} : ${valueText(r)}`).join(" ; ")}
      </figcaption>
      {vacant && (
        <p className="text-xs text-gris font-body mt-1 max-w-3xl leading-relaxed">
          * {vacant.label_fr}&nbsp;: la taxe actuelle modélisée est de 0&nbsp;€
          (le non-bâti relève de la TFPNB, hors du périmètre modélisé), donc la
          variation en pourcentage n&apos;est pas définie. Le chiffre indiqué est
          la hausse médiane en euros par parcelle.
        </p>
      )}
    </figure>
  );
}
