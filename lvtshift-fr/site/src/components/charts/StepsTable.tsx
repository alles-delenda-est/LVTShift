"use client";

/**
 * StepsTable — where each group's change comes from: housing brought to
 * market values, then the move to the TVTN (end of the social housing
 * exemptions included). Each cell is in % of the group's tax today, so a row
 * adds up to its total. Pure HTML, styled like BaselineRange.
 */

import type { CategoryRow, QuintileRow } from "@/lib/types";
import { stepTable, type StepRow } from "@/lib/steps";
import { signedChange, signedPct } from "@/lib/format";
import { MARINE, CREME, ENCRE, GRIS, LISERE, ROUGE, GREEN } from "./theme";

const BG_TOTAL = "#e8edf5";

const cell: React.CSSProperties = {
  padding: "0.55rem 0.75rem",
  verticalAlign: "middle",
  borderBottom: `1px solid ${LISERE}`,
};

const value = (n: number, isTotal = false): React.CSSProperties => ({
  fontFamily: "var(--font-display)",
  fontSize: "1.05rem",
  lineHeight: 1,
  textAlign: "center",
  display: "block",
  fontWeight: isTotal ? 600 : 400,
  color: n > 0 ? ROUGE : n < 0 ? GREEN : ENCRE,
});

export interface StepsTableProps {
  byCategory: CategoryRow[];
  byQuintile: QuintileRow[] | null | undefined;
}

export default function StepsTable({ byCategory, byQuintile }: StepsTableProps) {
  const t = stepTable(byCategory, byQuintile);
  if (!t.categories.length && !t.quintiles.length) {
    return (
      <p className="text-sm text-gris font-body max-w-3xl leading-relaxed">
        Décomposition non disponible pour cette commune : ses groupes sont
        trop petits, ou trop concentrés sur quelques biens, pour être publiés.
      </p>
    );
  }
  const cols: { key: keyof StepRow; label: string; sub: string }[] = [
    { key: "revaluation", label: "1. Valeurs de marché", sub: "logements, à règles inchangées" },
    { key: "land", label: "2. Passage à la TVTN", sub: "fin des exonérations HLM comprise" },
  ];
  const head = (label: string, sub: string, total = false) => (
    <>
      <span
        style={{
          display: "block",
          fontSize: "0.6875rem",
          letterSpacing: "0.07em",
          textTransform: "uppercase",
          color: total ? "rgba(246,244,240,0.9)" : GRIS,
          fontWeight: 400,
        }}
      >
        {label}
      </span>
      <span
        style={{
          display: "block",
          fontSize: "0.6875rem",
          fontStyle: "italic",
          color: total ? "rgba(246,244,240,0.6)" : GRIS,
          marginTop: "0.2rem",
          fontWeight: 400,
        }}
      >
        {sub}
      </span>
    </>
  );
  const body = (rows: StepRow[], title: string) =>
    rows.length > 0 && (
      <>
        <tr>
          <th
            colSpan={cols.length + 2}
            scope="colgroup"
            style={{
              ...cell,
              background: CREME,
              textAlign: "left",
              fontSize: "0.6875rem",
              letterSpacing: "0.12em",
              textTransform: "uppercase",
              color: MARINE,
              fontWeight: 600,
            }}
          >
            {title}
          </th>
        </tr>
        {rows.map((r) => (
          <tr key={r.key}>
            <th scope="row" style={{ ...cell, background: CREME, textAlign: "left" }}>
              <span style={{ fontSize: "0.8125rem", color: ENCRE }}>{r.label}</span>
              {r.sublabel && (
                <span
                  style={{ fontSize: "0.6875rem", fontStyle: "italic", color: GRIS, display: "block" }}
                >
                  {r.sublabel}
                </span>
              )}
            </th>
            {cols.map((c) => (
              <td key={c.key} style={{ ...cell, background: CREME }}>
                <span style={value(r[c.key] as number)}>{signedPct(r[c.key] as number)}</span>
              </td>
            ))}
            <td style={{ ...cell, background: BG_TOTAL }}>
              <span style={value(r.total, true)}>{signedChange(r.total)}</span>
            </td>
          </tr>
        ))}
      </>
    );

  return (
    <div style={{ border: `1px solid ${LISERE}`, overflowX: "auto", fontFamily: "var(--font-body)" }}>
      <table style={{ width: "100%", borderCollapse: "collapse", minWidth: "34rem" }}>
        <thead>
          <tr>
            <th style={{ ...cell, background: CREME, width: "28%" }} />
            {cols.map((c) => (
              <th
                key={c.key}
                scope="col"
                style={{ ...cell, background: CREME, textAlign: "center", borderTop: `3px solid ${LISERE}` }}
              >
                {head(c.label, c.sub)}
              </th>
            ))}
            <th
              scope="col"
              style={{ ...cell, background: MARINE, textAlign: "center", borderTop: `3px solid ${MARINE}` }}
            >
              {head("Total", "variation de l’impôt du groupe", true)}
            </th>
          </tr>
        </thead>
        <tbody>
          {body(t.categories, "Par catégorie de bien")}
          {body(t.quintiles, "Logements, par quintile de revenu")}
        </tbody>
      </table>
    </div>
  );
}
