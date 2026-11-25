/**
 * Word-wrap an SVG axis label into lines of at most `maxChars` characters.
 * Used on narrow mobile charts so long French property-category names neither
 * clip off the left edge nor wrap into 3–4 lines that collide vertically.
 */
export function wrapLabel(text: string, maxChars: number): string[] {
  const trimmed = text.trim();
  if (!trimmed || maxChars <= 0 || trimmed.length <= maxChars) return [trimmed];
  const words = trimmed.split(/\s+/);
  const lines: string[] = [];
  let current = "";
  for (const word of words) {
    if (!current) {
      current = word;
    } else if (current.length + 1 + word.length <= maxChars) {
      current = `${current} ${word}`;
    } else {
      lines.push(current);
      current = word;
    }
  }
  if (current) lines.push(current);
  return lines;
}
