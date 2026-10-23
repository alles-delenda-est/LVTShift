import Link from "next/link";

const NAV_LINKS = [
  { label: "Accueil",                    href: "/" },
  { label: "Résultats",                  href: "/resultats" },
  { label: "Justice",                    href: "/justice" },
  { label: "Voie juridique",             href: "/voie-juridique" },
  { label: "Logement abordable",         href: "/logement-abordable" },
  { label: "Exonérations & protections", href: "/exonerations-protections" },
  { label: "Sceptiques",                 href: "/sceptiques" },
  { label: "Outils existants",           href: "/outils-existants" },
  { label: "Méthodologie",               href: "/methodologie" },
  { label: "Sources",                    href: "/sources" },
] as const;

export default function Nav() {
  return (
    <nav aria-label="Navigation principale" className="bg-marine">
      <div className="max-w-6xl mx-auto px-6">
        <ul className="flex flex-wrap" role="list">
          {NAV_LINKS.map(({ label, href }) => (
            <li key={href}>
              <Link
                href={href}
                className="block px-3 py-2.5 text-xs text-white/75 hover:text-white hover:bg-white/10 transition-colors duration-150 whitespace-nowrap tracking-wide"
              >
                {label}
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </nav>
  );
}
