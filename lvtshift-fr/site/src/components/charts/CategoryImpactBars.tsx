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
 *
 * A second column gives the category's total change: medians can all fall
 * while the levy stays the same, when a minority pays much more (La Rochelle:
 * houses −5.4 % at the median, +14.7 % in total).
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
import type { BandCategoryRow, PublishedCategoryRow } from "@/lib/types";
import { pct, signedPct, signedPctAxis, euros, eurosExact } from "@/lib/format";
import { bandSpan, byKey } from "@/lib/band";
import { categoryAmount, BASIS_LABEL } from "@/lib/categoryAmount";
import { symmetricAxis } from "@/lib/axis";
import { ROUGE, GREEN, CREME, ENCRE, GRIS, GRIS_PALE, LISERE, TICK } from "./theme";
import { useNarrow } from "./useNarrow";

/* ── extended row ─────────────────────────────────────────────────── */

interface ProcessedRow extends PublishedCategoryRow {
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
  const amount = categoryAmount(row);
  const eur = amount.eur ?? row.median_change_eur;
  const sign = eur >= 0 ? "+" : "−";
  const absEur = eurosExact(Math.abs(eur));
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
        Variation médiane, par parcelle&nbsp;:{" "}
        {row.isNull ? "n. d." : signedPct(row.median_change_pct)}
      </p>
      <p>
        En montant, {BASIS_LABEL[amount.basis]}&nbsp;: {sign}
        {absEur}
      </p>
      <p>Paie davantage&nbsp;: {pct(row.share_paying_more_pct)}</p>
      {totalText(row) !== "—" && (
        <p>Variation totale de la catégorie&nbsp;: {totalText(row)}</p>
      )}
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

/** The category's total change: % where today's tax is positive, else € (vacant land). */
function totalText(row: PublishedCategoryRow): string {
  if (row.total_change_pct != null) return signedPct(row.total_change_pct);
  const e = row.total_change_eur;
  if (e == null) return "—";
  return `${e > 0 ? "+" : e < 0 ? "−" : ""}${euros(Math.abs(e))}*`;
}

function totalColour(row: PublishedCategoryRow): string {
  const v = row.total_change_pct ?? row.total_change_eur;
  return v == null || row.total_change_pct == null ? ENCRE : v >= 0 ? ROUGE : GREEN;
}

function makeTotalTick(data: ProcessedRow[]) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return function TotalTick(props: any): ReactElement<SVGElement> {
    const row = data.find((r) => r.label_fr === props.payload?.value);
    if (!row) return <g />;
    return (
      <text
        x={props.x + 6}
        y={props.y}
        textAnchor="start"
        dominantBaseline="central"
        fontSize={11}
        fontWeight={400}
        fill={totalColour(row)}
        fontFamily="var(--font-body)"
      >
        {totalText(row)}
      </text>
    );
  };
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
  byCategory: PublishedCategoryRow[];
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
  // phones with the totals column: one tick each side keeps the labels apart
  const hasTotalsForAxis = byCategory.some(
    (r) => r.total_change_pct != null || r.total_change_eur != null,
  );
  const axis = symmetricAxis(absMax, {
    headroom: 1.05,
    maxTicksPerSide: narrow ? (hasTotalsForAxis ? 1 : 2) : 4,
  });
  const domain: [number, number] = [-axis.lim, axis.lim];

  const cellFill = (entry: ProcessedRow): string => {
    if (entry.isNull) return GRIS_PALE;
    return entry.barValue >= 0 ? ROUGE : GREEN;
  };

  const BAR_HEIGHT = 38;
  const chartHeight = sortedData.length * BAR_HEIGHT + 64;

  const valueTick = makeValueTick(sortedData);
  const totalTick = makeTotalTick(sortedData);
  const hasTotals = sortedData.some((r) => totalText(r) !== "—");
  const colWidth = narrow ? 58 : 80;
  const vacant = sortedData.find((r) => r.isNull);
  const perDwelling = sortedData.some((r) => categoryAmount(r).basis === "dwelling");

  return (
    <figure aria-label="Variation médiane et totale de l'impôt par catégorie de bien">
    {hasTotals && (
      <div
        aria-hidden="true"
        style={{
          display: "flex",
          justifyContent: "flex-end",
          paddingRight: 4,
          fontFamily: "var(--font-body)",
          fontSize: 10,
          textTransform: "uppercase",
          letterSpacing: "0.08em",
          color: GRIS,
        }}
      >
        <span style={{ width: colWidth, paddingLeft: 6 }}>Médiane</span>
        <span style={{ width: colWidth, paddingLeft: 6 }}>Total</span>
      </div>
    )}
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
          width={colWidth}
          tick={valueTick}
          axisLine={false}
          tickLine={false}
        />
        {hasTotals && (
          <YAxis
            yAxisId="totals"
            orientation="right"
            type="category"
            dataKey="label_fr"
            width={colWidth}
            tick={totalTick}
            axisLine={false}
            tickLine={false}
          />
        )}
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
        {sortedData
          .map((r) => `${r.label_fr} : médiane ${valueText(r)}, total ${totalText(r)}`)
          .join(" ; ")}
      </figcaption>
      {vacant && (
        <p className="text-xs text-gris font-body mt-1 max-w-3xl leading-relaxed">
          * {vacant.label_fr}&nbsp;: la taxe actuelle modélisée est de 0&nbsp;€
          (le non-bâti relève de la TFPNB, hors du périmètre modélisé), donc la
          variation en pourcentage n&apos;est pas définie. Les chiffres
          indiqués sont en euros : la hausse médiane par parcelle et, en total,
          les nouvelles cotisations de toute la catégorie.
        </p>
      )}
      {perDwelling && (
        <p className="text-xs text-gris font-body mt-1 max-w-3xl leading-relaxed">
          Chaque barre donne la variation médiane par parcelle : un immeuble y
          compte pour une seule parcelle, quel que soit son nombre de logements.
          Pour les logements, le montant au survol est celui du ménage type, en
          euros par logement et par an.
          {hasTotals && (
            <>
              {" "}La colonne «&nbsp;Total&nbsp;» donne la variation de
              l&apos;impôt de toute la catégorie : les médianes peuvent baisser
              partout quand une minorité de parcelles paie beaucoup plus, à
              produit constant. Un tiret signale un total non publié, parce
              qu&apos;une seule parcelle en porterait l&apos;essentiel.
            </>
          )}
        </p>
      )}
    </figure>
  );
}
