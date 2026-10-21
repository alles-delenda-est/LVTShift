import { describe, it, expect } from "vitest";
import { isInternalHref } from "@/lib/links";

describe("isInternalHref", () => {
  it("treats root-relative paths as internal", () => {
    expect(isInternalHref("/")).toBe(true);
    expect(isInternalHref("/resultats")).toBe(true);
    expect(isInternalHref("/methodologie#hypotheses")).toBe(true);
  });

  it("treats protocol-relative and backslash tricks as external", () => {
    expect(isInternalHref("//evil.example")).toBe(false);
    expect(isInternalHref("//evil.example/resultats")).toBe(false);
    expect(isInternalHref("/\\evil.example")).toBe(false);
  });

  it("treats absolute URLs, anchors and empty values as external", () => {
    expect(isInternalHref("https://www.insee.fr")).toBe(false);
    expect(isInternalHref("mailto:contact@example.org")).toBe(false);
    expect(isInternalHref("#section")).toBe(false);
    expect(isInternalHref("")).toBe(false);
    expect(isInternalHref(undefined)).toBe(false);
  });
});
