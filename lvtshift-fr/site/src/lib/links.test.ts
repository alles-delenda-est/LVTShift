import { describe, it, expect } from "vitest";
import { isAnchorHref, isInternalHref, isSafeExternalHref } from "@/lib/links";

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

  it("rejects tabs and newlines that browsers strip before resolving", () => {
    for (const h of ["/\t/evil", "/\n/evil", "/\r\n/evil", "/\t\\evil", " /evil", "/ok path"]) {
      expect(isInternalHref(h)).toBe(false);
    }
  });

  it("treats absolute URLs, anchors and empty values as not internal", () => {
    expect(isInternalHref("https://www.insee.fr")).toBe(false);
    expect(isInternalHref("mailto:contact@example.org")).toBe(false);
    expect(isInternalHref("#section")).toBe(false);
    expect(isInternalHref("")).toBe(false);
    expect(isInternalHref(undefined)).toBe(false);
  });
});

describe("isSafeExternalHref / isAnchorHref", () => {
  it("allows only http(s) and mailto externally", () => {
    expect(isSafeExternalHref("https://www.insee.fr/x")).toBe(true);
    expect(isSafeExternalHref("HTTP://example.org")).toBe(true);
    expect(isSafeExternalHref("mailto:a@b.fr")).toBe(true);
    for (const h of ["javascript:alert(1)", "JaVaScRiPt:x", " javascript:x",
                     "data:text/html,x", "vbscript:x", "java\tscript:x", "//evil", ""]) {
      expect(isSafeExternalHref(h)).toBe(false);
    }
  });

  it("recognises same-page anchors", () => {
    expect(isAnchorHref("#hypotheses")).toBe(true);
    expect(isAnchorHref("#a b")).toBe(false);
    expect(isAnchorHref("/x#a")).toBe(false);
  });
});
