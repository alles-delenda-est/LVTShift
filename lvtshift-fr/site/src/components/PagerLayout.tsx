import type { ReactNode } from "react";

// Shared readable-article wrapper for the campaign pagers. Renders the page
// title as the page's <h2> (the persistent header owns the only <h1>); the MDX
// body — styled by src/mdx-components.tsx — starts at <h3>.

export interface PagerLayoutProps {
  eyebrow: string;
  title: string;
  lede?: string;
  children: ReactNode;
}

export default function PagerLayout({ eyebrow, title, lede, children }: PagerLayoutProps) {
  return (
    <article className="max-w-3xl mx-auto px-6 py-10">
      <header className="mb-8 border-b border-lisere pb-6">
        <p className="text-xs uppercase tracking-[0.18em] text-gris mb-2">{eyebrow}</p>
        <h2 className="font-display text-2xl md:text-[1.9rem] font-medium text-marine leading-tight">
          {title}
        </h2>
        {lede && (
          <p className="font-body text-lg text-gris max-w-2xl leading-relaxed mt-3">{lede}</p>
        )}
      </header>
      <div>{children}</div>
      <footer className="mt-12 pt-6 border-t border-lisere">
        <p className="text-sm text-gris">
          Les chiffres cités sont des imputations modélisées à partir de données
          ouvertes, agrégées par commune et catégorie de bien.{" "}
          <a href="/resultats" className="text-rouge underline underline-offset-2 hover:text-marine">
            Explorer les résultats commune par commune →
          </a>
        </p>
      </footer>
    </article>
  );
}
