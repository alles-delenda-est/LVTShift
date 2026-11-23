"use client";

/**
 * CategoryImpactBars — horizontal diverging bars per property category,
 * with a 3-mode switcher:
 *   - "household" (default): Par logement (ménage type) — uses
 *     household_median_change_pct for private residential categories (grouped
 *     at the top), separated by a dashed divider from non-residential and
 *     social-landlord categories displayed below by parcel ("(par parcelle)"),
 *     so two different units are never interleaved on the same sort order.
 *   - "median": Par parcelle (médiane) — median_change_pct, one metric for
 *     every category, so every bar is comparable with every other.
 *   - "total": Total catégorie — total_change_pct across the whole category.
 *
 * Colour convention:
 *   positive (pays more)  → rouge  (#b5281e)
 *   negative (pays less)  → green  (#2a6244)
 *   null (no % defined)   → gris pâle — bar at 0, value shown in € or "—"
 *
 * Null categories (e.g. Terrain nu / non bâti — 100 % pay more, but today's
 * modelled tax is 0 € so the % change is undefined) are kept visible:
 * zero-width bar at the reference line, the median change in euros in the
 * value column, and a footnote saying why.
 *
 * Where the run counts the unbuilt-land tax the reform replaces, vacant land
 * has a real percentage, usually far off the scale of the other categories
 * (today's tax rests on 1961 cadastral values): its bar is cut at the edge,
 * its value shown as a multiple, and a note gives the euro median.
 *
 * Values sit in a fixed column on the right (a second, label-only Y axis)
 * rather than at the bar ends: on phones the end labels ran into the
 * category names and the band whiskers.
 *
 * A second column gives the category's total change: medians can all fall
 * while the levy stays the same, when a minority pays much more (La Rochelle:
 * houses −5.4 % at the median, +14.7 % in total).
 */

import { ReactElement, useState } from "react";
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
import {
  MULTIPLE_FROM_PCT, pct, signedChange, signedPctAxis, euros, eurosExact,
} from "@/lib/format";
import { bandSpan, byKey, categoryBandValue } from "@/lib/band";
import { categoryAmount, BASIS_LABEL } from "@/lib/categoryAmount";
import { symmetricAxis } from "@/lib/axis";
import { ROUGE, GREEN, CREME, ENCRE, GRIS, GRIS_PALE, LISERE, TICK } from "./theme";
import { useNarrow } from "./useNarrow";

export type CategoryBarMode = "household" | "median" | "total";

const MODE_OPTIONS: { id: CategoryBarMode; label: string }[] = [
  { id: "household", label: "Par logement (ménage type)" },
  { id: "median", label: "Par parcelle (médiane)" },
  { id: "total", label: "Total catégorie" },
];

/* ── extended row ─────────────────────────────────────────────────── */

interface ProcessedRow extends PublishedCategoryRow {
  /** Active percentage plotted for the chosen mode (null if undefined/withheld). */
  displayPct: number | null;
  /** Bar value plotted on the axis (0 when null, clamped to axis limit when offScale). */
  barValue: number;
  isNull: boolean;
  /** True in "household" mode when the category has no per-dwelling median and falls back to parcel. */
  isParcelFallback: boolean;
  /** A rise too large for the axis (vacant land): bar cut short, value as a multiple. */
  offScale: boolean;
  /** sensitivity band: whisker [below, above] and its ends */
  err: [number, number] | null;
  bandLo: number | null;
  bandHi: number | null;
}

function signedEurosExact(n: number): string {
  const sign = n > 0 ? "+" : n < 0 ? "−" : "";
  return `${sign}${eurosExact(Math.abs(n))}`;
}

/** The category's total change: % where today's tax is positive, else € (vacant land). */
function totalText(row: PublishedCategoryRow): string {
  if (row.total_change_pct != null) return signedChange(row.total_change_pct);
  const e = row.total_change_eur;
  if (e == null) return "—";
  return `${e > 0 ? "+" : e < 0 ? "−" : ""}${euros(Math.abs(e))}*`;
}

function totalColour(row: PublishedCategoryRow): string {
  const v = row.total_change_pct ?? row.total_change_eur;
  return v == null || row.total_change_pct == null ? ENCRE : v >= 0 ? ROUGE : GREEN;
}

function valueText(row: ProcessedRow, mode: CategoryBarMode): string {
  if (mode === "total") {
    if (!row.isNull) return signedChange(row.displayPct) + (row.offScale ? "†" : "");
    return totalText(row);
  }
  if (!row.isNull) return signedChange(row.displayPct) + (row.offScale ? "†" : "");
  const eur =
    mode === "household" && !row.isParcelFallback && row.median_change_eur_per_dwelling != null
      ? row.median_change_eur_per_dwelling
      : row.median_change_eur;
  return `${signedEurosExact(eur)}*`;
}

/* ── tooltip ──────────────────────────────────────────────────────── */

function makeCatTooltip(mode: CategoryBarMode) {
  return function CatTooltip({ active, payload }: TooltipProps<number, string>) {
    if (!active || !payload?.length) return null;
    const row = payload[0]?.payload as ProcessedRow;
    const useDwelling = mode === "household" && !row.isParcelFallback;
    const amount = categoryAmount(row);
    const eur = useDwelling
      ? (row.median_change_eur_per_dwelling ?? row.median_change_eur)
      : (amount.eur ?? row.median_change_eur);

    return (
      <div
        style={{
          background: ENCRE,
          color: CREME,
          padding: "0.75rem 1rem",
          fontSize: 12,
          fontFamily: "var(--font-body)",
          border: `1px solid ${GRIS}`,
          maxWidth: 280,
          lineHeight: 1.65,
        }}
      >
        <p style={{ fontWeight: 600, marginBottom: "0.25rem" }}>
          {row.label_fr}
          {mode === "household" && row.isParcelFallback && (
            <span style={{ fontWeight: 400, color: GRIS_PALE }}> (par parcelle)</span>
          )}
        </p>

        {mode === "total" && (
          totalText(row) !== "—" ? (
            <p style={{ fontWeight: 600 }}>
              Variation totale de la catégorie&nbsp;: {totalText(row)}
            </p>
          ) : (
            <p style={{ color: GRIS_PALE }}>
              Total non publié (une parcelle pèse plus d&apos;un dixième)
            </p>
          )
        )}

        {useDwelling ? (
          <>
            <p>
              Variation médiane, par logement&nbsp;:{" "}
              {row.isNull ? "n. d." : signedChange(row.displayPct)}
            </p>
            <p>
              {row.median_change_eur_per_dwelling != null
                ? <>En montant&nbsp;: {signedEurosExact(eur)}/logement/an</>
                : <>En montant, par parcelle&nbsp;: {signedEurosExact(eur)}</>}
            </p>
            {row.share_dwellings_paying_more_pct != null && (
              <p>
                Logements payant davantage&nbsp;:{" "}
                {pct(row.share_dwellings_paying_more_pct)}
              </p>
            )}
          </>
        ) : (
          <>
            <p>
              Variation médiane, par parcelle&nbsp;:{" "}
              {row.median_change_pct === null ? "n. d." : signedChange(row.median_change_pct)}
            </p>
            <p>
              En montant, {BASIS_LABEL[amount.basis]}&nbsp;:{" "}
              {signedEurosExact(eur)}
            </p>
            <p>Parcelles payant davantage&nbsp;: {pct(row.share_paying_more_pct)}</p>
          </>
        )}

        {mode !== "total" && totalText(row) !== "—" && (
          <p>Variation totale de la catégorie&nbsp;: {totalText(row)}</p>
        )}
        {row.bandLo !== null && row.bandHi !== null && (
          <p style={{ color: GRIS_PALE }}>
            Fourchette (coût du bâti ±20&nbsp;%)&nbsp;: {signedChange(row.bandLo)}{" "}
            à {signedChange(row.bandHi)}
          </p>
        )}
      </div>
    );
  };
}

/* ── axis tick renderers ──────────────────────────────────────────── */

function makeCategoryTick(data: ProcessedRow[], mode: CategoryBarMode, narrow: boolean) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return function CategoryTick(props: any): ReactElement<SVGElement> {
    const label: string = props.payload?.value ?? "";
    const row = data.find((r) => r.label_fr === label);
    const showFallback = mode === "household" && row?.isParcelFallback;
    const x: number = props.x ?? 0;
    const y: number = props.y ?? 0;
    if (!showFallback) {
      return (
        <text
          x={x}
          y={y}
          textAnchor="end"
          dominantBaseline="central"
          fontSize={11}
          fill={ENCRE}
          fontFamily="var(--font-body)"
        >
          {label}
        </text>
      );
    }
    return (
      <g>
        <text
          x={x}
          y={narrow ? y : y - 5}
          textAnchor="end"
          dominantBaseline="central"
          fontSize={11}
          fill={ENCRE}
          fontFamily="var(--font-body)"
        >
          {narrow ? `${label}‡` : label}
        </text>
        {!narrow && (
          <text
            x={x}
            y={y + 8}
            textAnchor="end"
            dominantBaseline="central"
            fontSize={9.5}
            fontStyle="italic"
            fill={GRIS}
            fontFamily="var(--font-body)"
          >
            (par parcelle)
          </text>
        )}
      </g>
    );
  };
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

function makeValueTick(data: ProcessedRow[], mode: CategoryBarMode) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return function ValueTick(props: any): ReactElement<SVGElement> {
    const row = data.find((r) => r.label_fr === props.payload?.value);
    if (!row) return <g />;
    const fill = row.isNull ? ENCRE : (row.displayPct ?? 0) >= 0 ? ROUGE : GREEN;
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
        {valueText(row, mode)}
      </text>
    );
  };
}

/* ── component ────────────────────────────────────────────────────── */

export interface CategoryImpactBarsProps {
  byCategory: PublishedCategoryRow[];
  /** True when the run counts the unbuilt-land tax the reform replaces. */
  unbuiltReplaced?: boolean;
  /** Low / high legs of the sensitivity band (optional). */
  band?: {
    low?: BandCategoryRow[] | null;
    high?: BandCategoryRow[] | null;
  };
}

export default function CategoryImpactBars({
  byCategory,
  unbuiltReplaced = false,
  band,
}: CategoryImpactBarsProps) {
  const narrow = useNarrow();
  const hasHouseholdData = byCategory.some((r) => r.household_median_change_pct != null);
  const hasTotals = byCategory.some((r) => totalText(r) !== "—");
  // Per-dwelling by default (falling back to parcel median on payloads
  // without dwelling figures); in "household" mode, residential per-dwelling
  // rows are grouped above non-residential per-parcel rows with a divider.
  const [requestedMode, setRequestedMode] = useState<CategoryBarMode>("household");
  const mode: CategoryBarMode =
    requestedMode === "household" && !hasHouseholdData
      ? "median"
      : requestedMode === "total" && !hasTotals
        ? "median"
        : requestedMode;

  const low = byKey(band?.low, "category");
  const high = byKey(band?.high, "category");

  /* Sort: in "household" mode, per-dwelling residential categories first, then
     per-parcel fallback categories below (never interleaving two units). Within
     each group: most positive → least positive → negative; null rows last. */
  const sortedData: ProcessedRow[] = [...byCategory]
    .map((row) => {
      let displayPct: number | null;
      let isParcelFallback = false;
      let span = null;

      if (mode === "household") {
        if (row.household_median_change_pct != null) {
          displayPct = row.household_median_change_pct;
        } else {
          displayPct = row.median_change_pct;
          isParcelFallback = true;
        }
        const bandMetric = isParcelFallback ? "median" : "household";
        span = bandSpan(
          displayPct,
          categoryBandValue(low.get(row.category), bandMetric),
          categoryBandValue(high.get(row.category), bandMetric),
        );
      } else if (mode === "median") {
        displayPct = row.median_change_pct;
        span = bandSpan(
          displayPct,
          categoryBandValue(low.get(row.category), "median"),
          categoryBandValue(high.get(row.category), "median"),
        );
      } else {
        displayPct = row.total_change_pct ?? null;
      }

      const offScale = (displayPct ?? 0) >= MULTIPLE_FROM_PCT;
      return {
        ...row,
        displayPct,
        barValue: displayPct ?? 0,
        isNull: displayPct === null,
        isParcelFallback,
        offScale,
        err: offScale ? null : (span?.err ?? null),
        bandLo: span?.lo ?? null,
        bandHi: span?.hi ?? null,
      };
    })
    .sort((a, b) => {
      if (mode === "household" && a.isParcelFallback !== b.isParcelFallback) {
        return a.isParcelFallback ? 1 : -1;
      }
      if (a.isNull && !b.isNull) return 1;
      if (!a.isNull && b.isNull) return -1;
      return b.barValue - a.barValue;
    });

  /* Symmetric axis on round ticks (labels live in their own column); a rise
     too large for the scale is left out of it and its bar cut at the limit */
  const nonNull = sortedData
    .filter((r) => !r.isNull && !r.offScale)
    .flatMap((r) => [r.barValue, r.bandLo ?? r.barValue, r.bandHi ?? r.barValue]);
  const minVal = nonNull.length ? Math.min(...nonNull) : -10;
  const maxVal = nonNull.length ? Math.max(...nonNull) : 10;
  const absMax = Math.max(Math.abs(minVal), Math.abs(maxVal), 5);

  const showSecondTotalCol = hasTotals && mode !== "total";
  const axis = symmetricAxis(absMax, {
    headroom: 1.05,
    maxTicksPerSide: narrow ? (showSecondTotalCol ? 1 : 2) : 4,
  });
  const domain: [number, number] = [-axis.lim, axis.lim];
  for (const r of sortedData) if (r.offScale) r.barValue = axis.lim;

  const cellFill = (entry: ProcessedRow): string => {
    if (entry.isNull) return GRIS_PALE;
    return entry.barValue >= 0 ? ROUGE : GREEN;
  };

  const BAR_HEIGHT = mode === "household" && !narrow ? 42 : 38;
  const chartHeight = sortedData.length * BAR_HEIGHT + 64;

  const catTick = makeCategoryTick(sortedData, mode, narrow);
  const valueTick = makeValueTick(sortedData, mode);
  const totalTick = makeTotalTick(sortedData);
  const withheldTotal = hasTotals && sortedData.some((r) => totalText(r) === "—");
  const colWidth = narrow ? 58 : 80;
  const vacant = sortedData.find(
    (r) => r.isNull && r.category === "Vacant Land" && (mode !== "total" || r.total_change_eur != null),
  );
  const offScale = sortedData.filter((r) => r.offScale);
  const vacantTaxed = unbuiltReplaced
    ? sortedData.find((r) => !r.isNull && r.category === "Vacant Land")
    : undefined;
  const otherNull = sortedData.find(
    (r) => r.isNull && r.category !== "Vacant Land" && (mode !== "total" || r.total_change_eur != null),
  );
  const hasDwellingRows = mode === "household" && sortedData.some((r) => !r.isParcelFallback);
  const hasFallbackRows = mode === "household" && sortedData.some((r) => r.isParcelFallback);
  const firstFallbackLabel =
    hasDwellingRows && hasFallbackRows
      ? sortedData.find((r) => r.isParcelFallback)?.label_fr
      : undefined;
  const hasAnyBand = sortedData.some((r) => r.bandLo !== null && r.bandHi !== null);
  const hasBandProp = Boolean(band?.low?.length || band?.high?.length);
  const availableModes = MODE_OPTIONS.filter(
    (m) => (m.id !== "household" || hasHouseholdData) && (m.id !== "total" || hasTotals),
  );
  const primaryColLabel =
    mode === "household" ? "Ménage" : mode === "median" ? "Médiane" : "Total";

  return (
    <figure aria-label="Variation de l'impôt par catégorie de bien">
      {availableModes.length > 1 && (
        <div
          role="group"
          aria-label="Mode d'affichage du graphique par catégorie"
          className="flex flex-wrap gap-1.5 mb-4"
        >
          {availableModes.map((opt) => {
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

      {(showSecondTotalCol || mode === "total") && (
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
          <span style={{ width: colWidth, paddingLeft: 6 }}>{primaryColLabel}</span>
          {showSecondTotalCol && (
            <span style={{ width: colWidth, paddingLeft: 6 }}>Total</span>
          )}
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
            width={narrow ? 120 : 210}
            tick={catTick}
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
          {showSecondTotalCol && (
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
            content={makeCatTooltip(mode)}
            cursor={{ fill: "rgba(0,0,0,0.04)" }}
          />
          <ReferenceLine x={0} stroke={ENCRE} strokeWidth={1.5} />
          {firstFallbackLabel && (
            <ReferenceLine
              y={firstFallbackLabel}
              position="start"
              stroke={LISERE}
              strokeWidth={1.5}
              strokeDasharray="4 4"
            />
          )}
          <Bar dataKey="barValue" isAnimationActive={false}>
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
          .map(
            (r) =>
              `${r.label_fr} : ${primaryColLabel.toLowerCase()} ${valueText(r, mode).replace("†", "")}` +
              (showSecondTotalCol ? `, total ${totalText(r)}` : ""),
          )
          .join(" ; ")}
      </figcaption>

      {hasFallbackRows && (
        <p className="text-xs text-gris font-body mt-1 max-w-3xl leading-relaxed">
          {narrow ? "‡ " : ""}En mode «&nbsp;Par logement&nbsp;», les catégories
          résidentielles privées figurent en haut, pondérées par le nombre de
          logements (un immeuble de 40 logements compte 40 fois). Sous le trait
          pointillé, les catégories non résidentielles et les bailleurs sociaux
          sont affichés à part par parcelle.
        </p>
      )}
      {mode === "median" && hasHouseholdData && (
        <p className="text-xs text-gris font-body mt-1 max-w-3xl leading-relaxed">
          Chaque barre donne la variation médiane par parcelle : un immeuble y
          compte pour une seule parcelle, quel que soit son nombre de logements.
          Pour les logements, le montant au survol est celui du ménage type, en
          euros par logement et par an.
        </p>
      )}
      {vacant && (
        <p className="text-xs text-gris font-body mt-1 max-w-3xl leading-relaxed">
          * {vacant.label_fr}&nbsp;: la taxe actuelle modélisée est de 0&nbsp;€
          (le non-bâti relève de la TFPNB, hors du périmètre modélisé), donc la
          variation en pourcentage n&apos;est pas définie. Les chiffres
          indiqués sont en euros : la hausse médiane par parcelle et, en total,
          les nouvelles cotisations de toute la catégorie.
        </p>
      )}
      {offScale.length > 0 && (
        <p className="text-xs text-gris font-body mt-1 max-w-3xl leading-relaxed">
          † Barre coupée au bord du graphique : la hausse dépasse l&apos;échelle.
          «&nbsp;×3&nbsp;» signifie que l&apos;impôt est multiplié par trois.
        </p>
      )}
      {vacantTaxed && (
        <p className="text-xs text-gris font-body mt-1 max-w-3xl leading-relaxed">
          {vacantTaxed.label_fr}&nbsp;: ces terrains ne paient aujourd&apos;hui
          que la taxe foncière sur les propriétés non bâties et sa taxe
          additionnelle, que la réforme remplace. Assises sur des valeurs
          cadastrales de 1961, elles sont très faibles : la hausse est donc
          forte en proportion (montant médian&nbsp;:{" "}
          {eurosExact(Math.abs(vacantTaxed.median_change_eur))} par parcelle et
          par an). Faute de données par parcelle, le modèle répartit la taxe
          actuelle selon la surface : ce chiffre est une moyenne communale.
        </p>
      )}
      {otherNull && (
        <p className="text-xs text-gris font-body mt-1 max-w-3xl leading-relaxed">
          * {otherNull.label_fr}&nbsp;: la parcelle médiane ne paie rien
          aujourd&apos;hui (exonérée), donc la variation médiane en pourcentage
          n&apos;est pas définie ; elle est donnée en euros.
        </p>
      )}
      {hasTotals && (
        <p className="text-xs text-gris font-body mt-1 max-w-3xl leading-relaxed">
          {mode === "total"
            ? "Chaque barre donne la variation totale de l'impôt de la catégorie (somme des nouvelles cotisations rapportée au total actuel)."
            : "La colonne « Total » donne la variation de l'impôt de toute la catégorie : les médianes peuvent baisser partout quand une minorité de parcelles paie beaucoup plus, à produit constant."}
          {withheldTotal && (
            <>
              {" "}Un tiret signale un total non publié : une seule parcelle y
              pèserait plus d&apos;un dixième.
            </>
          )}
        </p>
      )}
      {hasAnyBand && (
        <p className="text-xs text-gris font-body italic mt-2 max-w-3xl leading-relaxed">
          Les traits fins indiquent la fourchette obtenue en faisant varier le coût
          du bâti de ±20&nbsp;% (hypothèses basse et haute), ce qui déplace la
          valeur du sol des parcelles bâties d&apos;un quartier à l&apos;autre : la
          valeur du sol étant imputée, seule une conclusion qui tient sur toute la
          fourchette est robuste.
        </p>
      )}
      {mode === "total" && !hasAnyBand && hasBandProp && (
        <p className="text-xs text-gris font-body italic mt-2 max-w-3xl leading-relaxed">
          La fourchette sur le coût du bâti (±20&nbsp;%) est publiée pour les
          médianes (par logement et par parcelle), pas pour les totaux par catégorie.
        </p>
      )}
    </figure>
  );
}
