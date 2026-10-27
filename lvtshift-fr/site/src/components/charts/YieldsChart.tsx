"use client";

/**
 * YieldsChart — what each scenario asks a land value tax to raise.
 *
 * One stacked horizontal bar per scenario, split by family of tax replaced,
 * in Md€. The IFI toggle adds the IFI to scenarios 2 and 3 only. Totals and
 * the indicative national rate sit in a fixed column on the right.
 *
 * Colours: FAMILY_COLORS in lib/yields (validated palette, fixed order).
 */

import { ReactElement, useId, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  LabelList,
} from "recharts";
import type { TooltipProps } from "recharts";
import {
  FAMILIES,
  FAMILY_COLORS,
  SCENARIO_LABELS,
  stackRows,
  mdEur,
  type FamilyKey,
  type StackRow,
  type YieldsData,
} from "@/lib/yields";
import { CREME, ENCRE, GRIS, LISERE, TICK } from "./theme";
import { useNarrow } from "./useNarrow";

/** Ink for labels drawn inside a segment. */
const INK_ON: Record<FamilyKey, string> = {
  tf: "#ffffff",
  thrs: "#ffffff",
  dmto: ENCRE,
  gains: "#ffffff",
  ifi: ENCRE,
  rents: "#ffffff",
};

const pctFr = (n: number) =>
  `${n.toLocaleString("fr-FR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} %`;

function Legend({ families }: { families: readonly (typeof FAMILIES)[number][] }) {
  return (
    <ul className="flex flex-wrap gap-x-5 gap-y-1 text-xs font-body text-encre mb-2" role="list">
      {families.map((f) => (
        <li key={f.key} className="flex items-center gap-1.5">
          <span
            aria-hidden="true"
            className="inline-block w-2.5 h-2.5 rounded-sm"
            style={{ background: FAMILY_COLORS[f.key] }}
          />
          {f.label}
        </li>
      ))}
    </ul>
  );
}

function SegmentTooltip({ active, payload }: TooltipProps<number, string>) {
  if (!active || !payload?.length) return null;
  const p = payload[0];
  const fam = FAMILIES.find((f) => f.key === p.dataKey);
  const row = p.payload as ChartRow;
  if (!fam || !p.value) return null;
  return (
    <div
      style={{
        background: ENCRE,
        color: CREME,
        padding: "0.6rem 0.9rem",
        fontSize: 12,
        fontFamily: "var(--font-body)",
        lineHeight: 1.6,
        maxWidth: 260,
      }}
    >
      <p style={{ fontWeight: 600 }}>{fam.label}</p>
      <p>
        {mdEur(p.value as number)}&nbsp;Md€ — {Math.round((100 * (p.value as number)) / row.total)}&nbsp;% du
        {" "}scénario {row.scenario.slice(1)}
      </p>
    </div>
  );
}

interface ChartRow extends StackRow, Record<string, unknown> {
  name: string;
}

function flatten(rows: StackRow[]): ChartRow[] {
  return rows.map((r) => ({ ...r, ...r.segments, name: r.scenario }));
}

export default function YieldsChart({ data }: { data: YieldsData }) {
  const narrow = useNarrow();
  const toggleId = useId();
  const [withIfi, setWithIfi] = useState(false);
  const rows = flatten(stackRows(data, withIfi));
  const families = FAMILIES.filter((f) => rows.some((r) => r.segments[f.key] > 0));
  const max = Math.max(...rows.map((r) => r.total));
  const domainMax = Math.ceil(max / 10000) * 10000;

  // Label a segment only when it is wide enough to hold its value.
  const minLabelled = domainMax * (narrow ? 0.12 : 0.06);

  const ScenarioTick = (props: { x: number; y: number; payload: { value: string } }): ReactElement<SVGElement> => {
    const sc = props.payload.value as keyof typeof SCENARIO_LABELS;
    return (
      <g transform={`translate(${props.x},${props.y})`}>
        <text x={-8} y={-4} textAnchor="end" fontSize={12} fontWeight={600} fill={ENCRE} fontFamily="var(--font-body)">
          {SCENARIO_LABELS[sc].short}
        </text>
        {!narrow && (
          <text x={-8} y={11} textAnchor="end" fontSize={11} fill={GRIS} fontFamily="var(--font-body)">
            {sc === "S1" ? "TF + THRS + DMTO" : sc === "S2" ? `+ plus-values${withIfi ? " + IFI" : ""}` : "+ loyers"}
          </text>
        )}
      </g>
    );
  };

  const TotalTick = (props: { x: number; y: number; payload: { value: string } }): ReactElement<SVGElement> => {
    const row = rows.find((r) => r.name === props.payload.value);
    if (!row) return <g />;
    return (
      <g transform={`translate(${props.x},${props.y})`}>
        <text x={8} y={-4} fontSize={13} fontWeight={600} fill={ENCRE} fontFamily="var(--font-body)">
          {mdEur(row.total)}&nbsp;Md€
        </text>
        <text x={8} y={11} fontSize={11} fill={GRIS} fontFamily="var(--font-body)">
          {narrow ? `≈ ${pctFr(row.rate)}` : `≈ ${pctFr(row.rate)} du foncier`}
        </text>
      </g>
    );
  };

  return (
    <figure aria-labelledby={`${toggleId}-cap`}>
      <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
        <Legend families={families} />
        <label htmlFor={toggleId} className="flex items-center gap-2 text-sm font-body text-encre cursor-pointer select-none">
          <input
            id={toggleId}
            type="checkbox"
            role="switch"
            aria-checked={withIfi}
            checked={withIfi}
            onChange={(e) => setWithIfi(e.target.checked)}
            className="peer sr-only"
          />
          <span
            aria-hidden="true"
            className="relative inline-block w-9 h-5 rounded-full bg-lisere peer-checked:bg-marine transition-colors peer-focus-visible:ring-2 peer-focus-visible:ring-marine/40
                       after:content-[''] after:absolute after:top-0.5 after:left-0.5 after:w-4 after:h-4 after:rounded-full after:bg-white after:transition-transform peer-checked:after:translate-x-4"
          />
          Inclure l&apos;IFI (scénarios 2 et 3)
        </label>
      </div>
      <ResponsiveContainer width="100%" height={rows.length * 64 + 40}>
        <BarChart
          layout="vertical"
          data={rows}
          margin={{ top: 4, right: 0, bottom: 4, left: 0 }}
          barCategoryGap="28%"
        >
          <XAxis
            type="number"
            domain={[0, domainMax]}
            tickFormatter={(v: number) => `${(v / 1000).toLocaleString("fr-FR")}`}
            tick={TICK}
            axisLine={{ stroke: LISERE }}
            tickLine={{ stroke: LISERE }}
          />
          <YAxis
            type="category"
            dataKey="name"
            width={narrow ? 78 : 150}
            tick={ScenarioTick}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            yAxisId="totals"
            orientation="right"
            type="category"
            dataKey="name"
            width={narrow ? 104 : 140}
            tick={TotalTick}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<SegmentTooltip />} shared={false} cursor={{ fill: "rgba(0,0,0,0.04)" }} />
          {FAMILIES.map((f) => (
            <Bar
              key={f.key}
              dataKey={f.key}
              stackId="y"
              fill={FAMILY_COLORS[f.key]}
              stroke={CREME}
              strokeWidth={2}
              isAnimationActive={false}
            >
              <LabelList
                dataKey={f.key}
                position="center"
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                content={(p: any) => {
                  const v = Number(p.value);
                  if (!v || v < minLabelled) return null;
                  return (
                    <text
                      x={p.x + p.width / 2}
                      y={p.y + p.height / 2}
                      textAnchor="middle"
                      dominantBaseline="central"
                      fontSize={11}
                      fontWeight={600}
                      fill={INK_ON[f.key]}
                      fontFamily="var(--font-body)"
                    >
                      {mdEur(v)}
                    </text>
                  );
                }}
              />
            </Bar>
          ))}
        </BarChart>
      </ResponsiveContainer>
      <p className="text-xs text-gris font-body mt-1" aria-hidden="true">
        Milliards d&apos;euros par an
      </p>
      <figcaption id={`${toggleId}-cap`} className="sr-only">
        Recettes à remplacer par scénario
        {withIfi ? ", IFI compris" : ""} :{" "}
        {rows
          .map(
            (r) =>
              `${SCENARIO_LABELS[r.scenario].short}, ${mdEur(r.total)} milliards d'euros (` +
              families
                .filter((f) => r.segments[f.key] > 0)
                .map((f) => `${f.label} ${mdEur(r.segments[f.key])}`)
                .join(", ") +
              ")",
          )
          .join(" ; ")}
      </figcaption>
    </figure>
  );
}
