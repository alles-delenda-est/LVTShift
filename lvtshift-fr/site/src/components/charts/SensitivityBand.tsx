"use client";

/**
 * SensitivityBand — a compact strip showing how the headline figures
 * change across three land-share scenarios (low / base / high).
 *
 * Layout: 4-column table — row label in column 0, then one column per
 * scenario.  The "base" column uses a marine tint and bolder numerals
 * so the central estimate reads immediately.
 *
 * Pure HTML — no Recharts needed.
 */

import type { Sensitivity, SensitivityLeg } from "@/lib/types";
import { pct, signedPct } from "@/lib/format";
import { MARINE, CREME, ENCRE, GRIS, LISERE } from "./theme";

const BG_BASE = "#e8edf5"; // light marine tint for the "base" column

export interface SensitivityBandProps {
  sensitivity: Sensitivity;
}

interface ScenarioDef {
  key: "low" | "base" | "high";
  colLabel: string;
  sublabel: string;
  leg: SensitivityLeg;
  isBase: boolean;
}

const cell: React.CSSProperties = {
  padding: "0.7rem 0.875rem",
  verticalAlign: "middle",
  borderBottom: `1px solid ${LISERE}`,
};

const valueStyle = (isBase: boolean): React.CSSProperties => ({
  fontFamily: "var(--font-display)",
  fontSize: "1.25rem",
  lineHeight: 1,
  color: isBase ? MARINE : ENCRE,
  fontWeight: isBase ? 600 : 400,
  textAlign: "center",
  display: "block",
});

const labelStyle: React.CSSProperties = {
  fontFamily: "var(--font-body)",
  fontSize: "0.8125rem",
  color: ENCRE,
};

const subLabelStyle: React.CSSProperties = {
  fontFamily: "var(--font-body)",
  fontSize: "0.6875rem",
  fontStyle: "italic",
  color: GRIS,
  marginTop: "0.15rem",
  display: "block",
};

export default function SensitivityBand({ sensitivity }: SensitivityBandProps) {
  const { delta_pt, low, base, high } = sensitivity;

  const scenarios: ScenarioDef[] = [
    {
      key: "low",
      colLabel: "Hypothèse basse",
      sublabel: `−${delta_pt} pt de part foncière`,
      leg: low,
      isBase: false,
    },
    {
      key: "base",
      colLabel: "Estimation centrale",
      sublabel: `Part foncière : ${pct(base.land_share_pct)}`,
      leg: base,
      isBase: true,
    },
    {
      key: "high",
      colLabel: "Hypothèse haute",
      sublabel: `+${delta_pt} pt de part foncière`,
      leg: high,
      isBase: false,
    },
  ];

  const headerBg = (isBase: boolean) =>
    isBase ? MARINE : CREME;
  const headerColor = (isBase: boolean) =>
    isBase ? "rgba(246,244,240,0.9)" : GRIS;
  const headerSubColor = (isBase: boolean) =>
    isBase ? "rgba(246,244,240,0.6)" : GRIS;

  return (
    <div
      style={{
        border: `1px solid ${LISERE}`,
        overflowX: "auto",
        fontFamily: "var(--font-body)",
      }}
    >
      <table
        style={{
          width: "100%",
          borderCollapse: "collapse",
          tableLayout: "auto",
        }}
      >
        <thead>
          <tr>
            {/* Empty label column */}
            <th
              style={{
                ...cell,
                background: CREME,
                width: "34%",
                borderBottom: `1px solid ${LISERE}`,
              }}
            />
            {scenarios.map(({ key, colLabel, sublabel, isBase }) => (
              <th
                key={key}
                scope="col"
                style={{
                  ...cell,
                  background: headerBg(isBase),
                  textAlign: "center",
                  borderTop: `3px solid ${isBase ? MARINE : LISERE}`,
                  width: "22%",
                }}
              >
                <span
                  style={{
                    display: "block",
                    fontSize: "0.6875rem",
                    letterSpacing: "0.07em",
                    textTransform: "uppercase",
                    color: headerColor(isBase),
                    fontWeight: 400,
                  }}
                >
                  {colLabel}
                </span>
                <span
                  style={{
                    display: "block",
                    fontSize: "0.6875rem",
                    fontStyle: "italic",
                    color: headerSubColor(isBase),
                    marginTop: "0.2rem",
                    fontWeight: 400,
                  }}
                >
                  {sublabel}
                </span>
              </th>
            ))}
          </tr>
        </thead>

        <tbody>
          {/* Row: Transfert brut */}
          <tr>
            <th scope="row" style={{ ...cell, background: CREME }}>
              <span style={labelStyle}>Transfert brut</span>
              <span style={subLabelStyle}>% du prélèvement total</span>
            </th>
            {scenarios.map(({ key, leg, isBase }) => (
              <td
                key={key}
                style={{ ...cell, background: isBase ? BG_BASE : CREME }}
              >
                <span style={valueStyle(isBase)}>
                  {pct(leg.gross_pct_of_levy)}
                </span>
              </td>
            ))}
          </tr>

          {/* Row: Variation médiane résidentielle */}
          <tr>
            <th
              scope="row"
              style={{
                ...cell,
                background: CREME,
                borderBottom: "none",
              }}
            >
              <span style={labelStyle}>Variation médiane résidentielle</span>
              <span style={subLabelStyle}>logements</span>
            </th>
            {scenarios.map(({ key, leg, isBase }) => (
              <td
                key={key}
                style={{
                  ...cell,
                  background: isBase ? BG_BASE : CREME,
                  borderBottom: "none",
                }}
              >
                <span style={valueStyle(isBase)}>
                  {signedPct(leg.median_change_pct_residential)}
                </span>
              </td>
            ))}
          </tr>
        </tbody>
      </table>
    </div>
  );
}
