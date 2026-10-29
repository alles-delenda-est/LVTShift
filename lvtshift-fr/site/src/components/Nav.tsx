"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_LINKS = [
  { label: "Accueil",                    href: "/" },
  { label: "Résultats",                  href: "/resultats" },
  { label: "Scénarios",                  href: "/scenarios" },
  { label: "Justice",                    href: "/justice" },
  { label: "Voie juridique",             href: "/voie-juridique" },
  { label: "Logement abordable",         href: "/logement-abordable" },
  { label: "Exonérations & protections", href: "/exonerations-protections" },
  { label: "Sceptiques",                 href: "/sceptiques" },
  { label: "Outils existants",           href: "/outils-existants" },
  { label: "Méthodologie",               href: "/methodologie" },
  { label: "Sources",                    href: "/sources" },
] as const;

/** Strip a trailing slash so "/resultats/" and "/resultats" match. */
function normalise(path: string | null): string {
  if (!path || path === "/") return "/";
  return path.replace(/\/+$/, "");
}

export default function Nav() {
  const current = normalise(usePathname());

  return (
    <nav aria-label="Navigation principale" className="bg-marine">
      <div className="max-w-6xl mx-auto px-3 md:px-6">
        {/* Phones: one horizontally scrollable row (the wrapped menu took four
            rows, a third of the first screen). From md up: wrap as before. */}
        <ul
          className="flex overflow-x-auto md:flex-wrap md:overflow-visible [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
          role="list"
        >
          {NAV_LINKS.map(({ label, href }) => {
            const active = current === href;
            return (
              <li key={href} className="shrink-0">
                <Link
                  href={href}
                  aria-current={active ? "page" : undefined}
                  className={`block px-3 py-2.5 text-xs whitespace-nowrap tracking-wide transition-colors duration-150 border-b-2 ${
                    active
                      ? "text-white border-rouge"
                      : "text-white/75 border-transparent hover:text-white hover:bg-white/10"
                  }`}
                >
                  {label}
                </Link>
              </li>
            );
          })}
        </ul>
      </div>
    </nav>
  );
}
