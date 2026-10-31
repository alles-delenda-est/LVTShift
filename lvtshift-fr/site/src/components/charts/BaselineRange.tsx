"use client";

/**
 * BaselineRange — the same results under the central share of professional
 * premises in today's tax and its published alternative.
 *
 * Open data under-record professional premises (vacant offices, premises
 * rented by public bodies): the model scales them to the national total
 * (central) and also publishes a local estimate from the 2017 taxe
 * d'habitation (older payloads: the raw CFE figure). The LVT bills are
 * identical in both columns; only today's tax, the starting point, moves.
 * Pure HTML, styled like SensitivityBand.
 */

import type { BaselineSensitivity } from "@/lib/types";
import { baselineRangeRows, altColumn } from "@/lib/baselineRange";
import { pct, signedPct } from "@/lib/format";
import { MARINE, CREME, ENCRE, GRIS, LISERE } from "./theme";

const BG_BASE = "#e8edf5";

const cell: React.CSSProperties = {
  padding: "0.6rem 0.875rem",
  verticalAlign: "middle",
  borderBottom: `1px solid ${LISERE}`,
};

const valueStyle = (isBase: boolean): React.CSSProperties => ({
  fontFamily: "var(--font-display)",
  fontSize: "1.15rem",
  lineHeight: 1,
  color: isBase ? MARINE : ENCRE,
  fontWeight: isBase ? 600 : 400,
  textAlign: "center",
  display: "block",
});

const fmtScale = (n: number) => `×${n.toLocaleString("fr-FR")}`;

export interface BaselineRangeProps {
  baseline: BaselineSensitivity;
  /** territories: income groups ranked within each commune */
  withinCommune?: boolean;
}

export default function BaselineRange({ baseline, withinCommune = false }: BaselineRangeProps) {
  const rows = baselineRangeRows(baseline, withinCommune);
  const alt = altColumn(baseline);
  const cols = [
    {
      key: "central" as const,
      label: "Estimation centrale",
      sub: `locaux professionnels ${fmtScale(baseline.pro_scale_central)}`,
      isBase: true,
    },
    {
      key: "low" as const,
      label: alt.label,
      sub: alt.sub,
      isBase: false,
    },
  ];

  return (
    <div style={{ border: `1px solid ${LISERE}`, overflowX: "auto", fontFamily: "var(--font-body)" }}>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th style={{ ...cell, background: CREME, width: "46%" }} />
            {cols.map((c) => (
              <th
                key={c.key}
                scope="col"
                style={{
                  ...cell,
                  background: c.isBase ? MARINE : CREME,
                  textAlign: "center",
                  borderTop: `3px solid ${c.isBase ? MARINE : LISERE}`,
                  width: "27%",
                }}
              >
                <span
                  style={{
                    display: "block",
                    fontSize: "0.6875rem",
                    letterSpacing: "0.07em",
                    textTransform: "uppercase",
                    color: c.isBase ? "rgba(246,244,240,0.9)" : GRIS,
                    fontWeight: 400,
                  }}
                >
                  {c.label}
                </span>
                <span
                  style={{
                    display: "block",
                    fontSize: "0.6875rem",
                    fontStyle: "italic",
                    color: c.isBase ? "rgba(246,244,240,0.6)" : GRIS,
                    marginTop: "0.2rem",
                    fontWeight: 400,
                  }}
                >
                  {c.sub}
                </span>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.label}>
              <th scope="row" style={{ ...cell, background: CREME, textAlign: "left" }}>
                <span style={{ fontSize: "0.8125rem", color: ENCRE }}>{r.label}</span>
                {r.sublabel && (
                  <span
                    style={{
                      fontSize: "0.6875rem",
                      fontStyle: "italic",
                      color: GRIS,
                      marginTop: "0.15rem",
                      display: "block",
                    }}
                  >
                    {r.sublabel}
                  </span>
                )}
              </th>
              {cols.map((c) => {
                const v = r[c.key];
                return (
                  <td key={c.key} style={{ ...cell, background: c.isBase ? BG_BASE : CREME }}>
                    <span style={valueStyle(c.isBase)}>
                      {r.format === "pct" ? pct(v) : signedPct(v)}
                    </span>
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
