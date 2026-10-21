/**
 * Classify the hrefs written in MDX content.
 *
 * Internal: root-relative paths ("/resultats", "/methodologie#x"). Anything
 * the browser could resolve against another host is not internal: "//host",
 * "/\host", and also "/<tab>/host", because browsers strip tabs and newlines
 * from URLs before resolving them. So a path must start with a single "/" not
 * followed by "/" or "\", and contain no whitespace, control character or
 * backslash anywhere.
 *
 * External links are only rendered as links for http(s) and mailto; other
 * schemes (javascript:, data:, vbscript:…) are rendered as plain text.
 */

const CONTROL_OR_SPACE_OR_BACKSLASH = /[\u0000- \u007f\\]/;

/** True when the link targets a path on this site. */
export function isInternalHref(href: string | undefined | null): boolean {
  if (!href) return false;
  return /^\/(?![/\\])/.test(href) && !CONTROL_OR_SPACE_OR_BACKSLASH.test(href);
}

/** True for a same-page anchor ("#section"). */
export function isAnchorHref(href: string | undefined | null): boolean {
  return !!href && /^#[\w-]+$/.test(href);
}

/** True for an external link we are willing to render: http(s) or mailto. */
export function isSafeExternalHref(href: string | undefined | null): boolean {
  if (!href || CONTROL_OR_SPACE_OR_BACKSLASH.test(href)) return false;
  return /^(https?:\/\/|mailto:)/i.test(href);
}
