import type { MDXComponents } from "mdx/types";
import Link from "next/link";
import type { AnchorHTMLAttributes } from "react";

// Single source of MDX prose styling for the campaign pagers. The persistent
// site header owns the only <h1>; PagerLayout renders the page title as <h2>,
// so MDX section headings start at <h3>. Authors write `##`/`###` and get
// styled <h3>/<h4> — the visual hierarchy below the page title.

function MdxLink({ href = "", ...props }: AnchorHTMLAttributes<HTMLAnchorElement>) {
  const isInternal = href.startsWith("/");
  if (isInternal) {
    return (
      <Link href={href} className="text-rouge underline underline-offset-2 hover:text-marine">
        {props.children}
      </Link>
    );
  }
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="text-rouge underline underline-offset-2 hover:text-marine"
      {...props}
    />
  );
}

export function useMDXComponents(components: MDXComponents): MDXComponents {
  return {
    h1: ({ children }) => (
      <h3 className="font-display text-xl md:text-2xl font-medium text-marine mt-10 mb-3 leading-snug">
        {children}
      </h3>
    ),
    h2: ({ children }) => (
      <h3 className="font-display text-xl md:text-2xl font-medium text-marine mt-10 mb-3 leading-snug">
        {children}
      </h3>
    ),
    h3: ({ children }) => (
      <h4 className="font-display text-lg font-medium text-marine mt-7 mb-2 leading-snug">
        {children}
      </h4>
    ),
    h4: ({ children }) => (
      <h5 className="font-body text-sm font-semibold uppercase tracking-[0.1em] text-gris mt-6 mb-2">
        {children}
      </h5>
    ),
    p: ({ children }) => (
      <p className="font-body text-base text-encre leading-relaxed my-4">{children}</p>
    ),
    ul: ({ children }) => (
      <ul className="font-body text-base text-encre leading-relaxed my-4 pl-5 list-disc space-y-1.5 marker:text-gris">
        {children}
      </ul>
    ),
    ol: ({ children }) => (
      <ol className="font-body text-base text-encre leading-relaxed my-4 pl-5 list-decimal space-y-1.5 marker:text-gris">
        {children}
      </ol>
    ),
    li: ({ children }) => <li className="pl-1">{children}</li>,
    strong: ({ children }) => <strong className="font-semibold text-encre">{children}</strong>,
    em: ({ children }) => <em className="italic">{children}</em>,
    blockquote: ({ children }) => (
      <blockquote className="border-l-4 border-rouge pl-5 my-6 text-encre [&_p]:text-sm [&_p]:text-gris">
        {children}
      </blockquote>
    ),
    hr: () => <hr className="my-8 border-lisere" />,
    a: MdxLink,
    ...components,
  };
}
