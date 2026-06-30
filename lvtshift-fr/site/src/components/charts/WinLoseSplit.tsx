"use client";

/**
 * WinLoseSplit — stacked horizontal bar per property category showing
 * the share that pays MORE (rouge) vs. the share that pays LESS (marine).
 *
 * Sorted descending by share_paying_more_pct so the most contentious
 * categories appear first — the honesty rule applied to sort order.
 *
 * Caption names "Maison individuelle" (Single Family Residential) and
 * its specific share.
 */

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
import type { CategoryRow } from "@/lib/types";
import { pct } from "@/lib/format";
import { MARINE, ROUGE, CREME, ENCRE, GRIS, LISERE, TICK } from "./theme";

/* ── data shape ─────────────────────────────────────────────────── */

interface WinLoseRow {
  label_fr: string;
  more: number;
  less: number;
  count_paying_more: number;
  parcels: number;
  share_paying_more_pct: number | null;
}

/* ── tooltip ─────────────────────────────────────────────────────── */

function CustomTooltip({ active, payload }: TooltipProps<number, string>) {
  if (!active || !payload?.length) return null;
  const row = payload[0]?.payload as WinLoseRow;
  return (
    <div
      style={{
        background: ENCRE,
        color: CREME,
        padding: "0.75rem 1rem",
        fontSize: 12,
        fontFamily: "var(--font-body)",
        border: `1px solid ${GRIS}`,
        maxWidth: 260,
        lineHeight: 1.65,
      }}
    >
      <p style={{ fontWeight: 600, marginBottom: "0.25rem" }}>{row.label_fr}</p>
      <p>
        Paie davantage&nbsp;:{" "}
        <strong style={{ color: "#e87878" }}>
          {pct(row.share_paying_more_pct)}
        </strong>{" "}
        ({row.count_paying_more.toLocaleString("fr-FR")} parcelles)
      </p>
      <p>
        Paie moins ou pareil&nbsp;:{" "}
        <strong style={{ color: "#6ec4a4" }}>
          {pct(row.share_paying_more_pct === null ? null : 100 - row.share_paying_more_pct)}
        </strong>
      </p>
    </div>
  );
}

/* ── component ───────────────────────────────────────────────────── */

export interface WinLoseSplitProps {
  byCategory: CategoryRow[];
}

export default function WinLoseSplit({ byCategory }: WinLoseSplitProps) {
  /* Build chart data — sorted most contentious first */
  const data: WinLoseRow[] = [...byCategory]
    .sort(
      (a, b) =>
        (b.share_paying_more_pct ?? 0) - (a.share_paying_more_pct ?? 0)
    )
    .map((row) => ({
      label_fr: row.label_fr,
      more: row.share_paying_more_pct ?? 0,
      less: 100 - (row.share_paying_more_pct ?? 0),
      count_paying_more: row.count_paying_more,
      parcels: row.parcels,
      share_paying_more_pct: row.share_paying_more_pct,
    }));

  /* Owner-occupier caption */
  const sfr = byCategory.find((r) => r.category === "Single Family Residential");
  const caption = sfr
    ? `Parmi les maisons individuelles, ${pct(sfr.share_paying_more_pct)} paient davantage.`
    : null;

  const BAR_HEIGHT = 34;
  const chartHeight = data.length * BAR_HEIGHT + 64;

  return (
    <div>
      <ResponsiveContainer width="100%" height={chartHeight}>
        <BarChart
          layout="vertical"
          data={data}
          margin={{ top: 8, right: 72, bottom: 28, left: 8 }}
          barSize={20}
          barCategoryGap="30%"
        >
          <XAxis
            type="number"
            domain={[0, 100]}
            tickFormatter={(v: number) => `${v} %`}
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
            content={<CustomTooltip />}
            cursor={{ fill: "rgba(0,0,0,0.04)" }}
          />
          <Bar
            dataKey="more"
            stackId="split"
            fill={ROUGE}
            name="Paie davantage"
            isAnimationActive={false}
          >
            <LabelList
              dataKey="more"
              position="insideRight"
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              formatter={(v: any) =>
                typeof v === "number" && v > 12 ? pct(v) : ""
              }
              style={{
                fill: CREME,
                fontSize: 10,
                fontFamily: "var(--font-body)",
              }}
            />
          </Bar>
          <Bar
            dataKey="less"
            stackId="split"
            fill={MARINE}
            name="Paie moins ou pareil"
            isAnimationActive={false}
          />
        </BarChart>
      </ResponsiveContainer>

      {caption && (
        <p
          style={{
            fontFamily: "var(--font-body)",
            fontSize: "0.8125rem",
            fontStyle: "italic",
            color: GRIS,
            marginTop: "0.5rem",
            paddingLeft: "1rem",
            borderLeft: `2px solid ${LISERE}`,
          }}
        >
          {caption}
        </p>
      )}
    </div>
  );
}
