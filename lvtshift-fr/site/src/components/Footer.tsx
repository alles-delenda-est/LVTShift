import Link from "next/link";

export default function Footer() {
  return (
    <footer className="border-t border-lisere bg-white mt-16">
      <div className="max-w-6xl mx-auto px-6 py-10">
        <p className="text-xs text-gris leading-relaxed max-w-2xl">
          <span className="font-semibold text-encre">Note méthodologique&nbsp;:</span>{" "}
          Les chiffres présentés sur ce site sont des{" "}
          <span className="font-semibold text-encre">imputations modélisées</span> à
          partir de données publiques françaises (cadastre, DVF, DGCL/OFGL). Ils
          expriment des effets{" "}
          <span className="font-semibold text-encre">agrégés par commune et catégorie de bien</span>{" "}
          — aucune facture individuelle ou par parcelle n&apos;est publiée ni ne peut
          être inférée. Les résultats indiquent un ordre de grandeur des transferts&nbsp;;
          ils ne constituent pas des projections officielles.
        </p>
        <p className="text-xs text-gris/60 mt-6">
          Pour une terre productive &middot; Données ouvertes françaises &middot;{" "}
          <Link
            href="/methodologie"
            className="underline underline-offset-2 hover:text-gris transition-colors"
          >
            Méthodologie complète
          </Link>
        </p>
      </div>
    </footer>
  );
}
