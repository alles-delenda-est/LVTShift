"use client";

/**
 * VariantTerm — an inline glossary term ("cas central", "variante locale")
 * with an explanation that opens on hover, keyboard focus or tap.
 *
 * The two variants are the site's two estimates of what businesses pay in
 * today's taxe foncière; readers met the labels with no definition on the
 * home page. Tap toggles the note because iOS Safari does not focus a button
 * on tap, so a hover/focus-only tooltip would never open on phones.
 */

import Link from "next/link";
import { ReactNode, useId, useState } from "react";

export type VariantKind = "central" | "local";

const NOTES: Record<VariantKind, { title: string; lines: string[] }> = {
  central: {
    title: "Cas central",
    lines: [
      "Pour savoir qui gagne, il faut savoir ce que chaque type de bien paie aujourd'hui. Aucune donnée publique ne donne la part des bureaux, commerces et usines dans la taxe foncière d'une commune.",
      "Le cas central l'estime à partir des données ouvertes, recalées sur le total national de la Cour des comptes.",
    ],
  },
  local: {
    title: "Variante locale",
    lines: [
      "Une seconde estimation de la même part : commune par commune, à partir de la taxe d'habitation de 2017, qui portait encore sur tous les logements occupés.",
      "En ville, elle attribue davantage aux entreprises : les ménages paient alors moins aujourd'hui, et la réforme leur est moins favorable. Les montants après réforme sont les mêmes ; seul le point de départ change.",
    ],
  },
};

export default function VariantTerm({
  kind,
  children,
  tone = "light",
}: {
  kind: VariantKind;
  children: ReactNode;
  /** "dark" for use on the navy hero panel. */
  tone?: "light" | "dark";
}) {
  const [open, setOpen] = useState(false);
  const id = useId();
  const note = NOTES[kind];
  const underline =
    tone === "dark" ? "decoration-creme/60 focus-visible:outline-creme" : "decoration-gris focus-visible:outline-marine";
  return (
    <span className="group relative inline-block" onMouseLeave={() => setOpen(false)}>
      <button
        type="button"
        aria-expanded={open}
        aria-describedby={id}
        onClick={() => setOpen((o) => !o)}
        onKeyDown={(e) => e.key === "Escape" && setOpen(false)}
        onBlur={() => setOpen(false)}
        className={`cursor-help underline decoration-dotted underline-offset-2 focus-visible:outline-2 focus-visible:outline-offset-2 ${underline}`}
      >
        {children}
        <span aria-hidden="true" className="ml-0.5 align-super text-[0.7em] opacity-70">ⓘ</span>
      </button>
      <span
        id={id}
        role="tooltip"
        className={`${open ? "visible" : "invisible"} group-hover:visible group-focus-within:visible absolute left-0 top-full z-30 block w-80 max-w-[85vw] pt-2`}
      >
        <span className="block space-y-1.5 border border-lisere bg-white p-3 text-left text-xs font-normal normal-case tracking-normal leading-snug text-encre shadow-lg">
          <strong className="block font-semibold text-marine">{note.title}</strong>
          {note.lines.map((line, i) => (
            <span key={i} className="block">{line}</span>
          ))}
          <Link
            href="/methodologie#taxe-actuelle"
            className="block underline underline-offset-2 text-marine"
            onMouseDown={(e) => e.preventDefault()}
          >
            En savoir plus
          </Link>
        </span>
      </span>
    </span>
  );
}
