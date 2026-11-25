"use client";

/**
 * VariantTerm — an inline glossary term ("cas central", "variante locale")
 * with an explanation that opens on hover, keyboard focus or tap.
 *
 * The two variants are the site's two estimates of what businesses pay in
 * today's taxe foncière; readers met the labels with no definition on the
 * home page. Tap toggles the note because iOS Safari does not focus a button
 * on tap, so a hover/focus-only tooltip would never open on phones. When
 * open, the note shifts left as needed to stay inside the viewport.
 */

import Link from "next/link";
import { ReactNode, useEffect, useId, useLayoutEffect, useRef, useState } from "react";

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
  const [shift, setShift] = useState(0);
  const rootRef = useRef<HTMLSpanElement>(null);
  // How the last press began: a touch tap also fires an emulated mouseenter
  // and (on Android) a focus before its click, so hover and focus must not
  // open the note for touch, or the click's toggle would close it at once.
  const pointerType = useRef<string>("");
  const boxRef = useRef<HTMLSpanElement>(null);
  const id = useId();
  // Dismiss on outside tap/click (critical on touch devices where hover/blur
  // do not fire reliably).
  useEffect(() => {
    if (!open) return;
    const onPointerDown = (e: PointerEvent) => {
      if (rootRef.current && !rootRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("pointerdown", onPointerDown);
    return () => document.removeEventListener("pointerdown", onPointerDown);
  }, [open]);
  // Keep the note on screen: measure once it is open, nudge it left if it
  // would run past the right edge (8 px margin).
  useLayoutEffect(() => {
    if (!open || !boxRef.current) {
      setShift(0);
      return;
    }
    const box = boxRef.current.getBoundingClientRect();
    const overflow = box.right - shift - (document.documentElement.clientWidth - 8);
    setShift(overflow > 0 ? Math.min(overflow, box.left - shift - 8) : 0);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);
  const note = NOTES[kind];
  const underline =
    tone === "dark" ? "decoration-creme/60 focus-visible:outline-creme" : "decoration-gris focus-visible:outline-marine";
  return (
    <span
      ref={rootRef}
      className="relative inline-block"
      onPointerEnter={(e) => e.pointerType === "mouse" && setOpen(true)}
      onPointerLeave={(e) => e.pointerType === "mouse" && setOpen(false)}
      onPointerDown={(e) => { pointerType.current = e.pointerType; }}
      onFocus={() => { if (!pointerType.current) setOpen(true); }}   // keyboard
      onBlur={(e) => {
        // stay open while focus moves to the "En savoir plus" link inside
        if (!e.currentTarget.contains(e.relatedTarget as Node | null)) setOpen(false);
      }}
      onKeyDown={(e) => e.key === "Escape" && setOpen(false)}
    >
      <button
        type="button"
        aria-expanded={open}
        aria-describedby={id}
        onClick={() => {
          // mouse: hover already opened it, a click keeps it open; touch and
          // pen: a tap toggles; keyboard (Enter/Space, no pointer): toggles
          if (pointerType.current === "mouse") setOpen(true);
          else setOpen((v) => !v);
          pointerType.current = "";
        }}
        className={`cursor-help underline decoration-dotted underline-offset-2 focus-visible:outline-2 focus-visible:outline-offset-2 ${underline}`}
      >
        {children}
        <span aria-hidden="true" className="ml-0.5 align-super text-[0.7em] opacity-70">ⓘ</span>
      </button>
      <span
        id={id}
        role="tooltip"
        ref={boxRef}
        style={shift ? { left: -shift } : undefined}
        className={`${open ? "block" : "hidden"} absolute left-0 top-full z-30 w-80 max-w-[85vw] pt-2`}
      >
        <span className="block space-y-1.5 border border-lisere bg-white p-3 text-left text-xs font-normal normal-case tracking-normal leading-snug text-encre shadow-lg">
          <strong className="block font-semibold text-marine">{note.title}</strong>
          {note.lines.map((line, i) => (
            <span key={i} className="block">{line}</span>
          ))}
          <Link
            href="/methodologie#taxe-actuelle"
            className="block underline underline-offset-2 text-marine"
          >
            En savoir plus
          </Link>
        </span>
      </span>
    </span>
  );
}
