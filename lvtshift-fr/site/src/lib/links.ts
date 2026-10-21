/**
 * Decide whether an MDX link points inside this site.
 *
 * Only root-relative paths ("/resultats", "/methodologie#x") are internal.
 * A protocol-relative URL ("//evil.example") also starts with "/" but the
 * browser resolves it against another host, so it must be treated as
 * external (opened in a new tab with rel="noopener noreferrer"). A
 * backslash after the leading slash ("/\evil.example") is normalised to "//"
 * by browsers, so it is excluded for the same reason.
 *
 * @param href - The raw href written in the MDX source.
 * @returns True when the link targets a path on this site.
 */
export function isInternalHref(href: string | undefined | null): boolean {
  if (!href) return false;
  return href.startsWith("/") && !href.startsWith("//") && !href.startsWith("/\\");
}
