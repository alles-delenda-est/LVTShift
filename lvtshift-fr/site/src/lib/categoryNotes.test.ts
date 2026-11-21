import { describe, expect, it } from "vitest";
import { categoryNotes, hasCategoryNotes, socialTotalSentence } from "./categoryNotes";
import { publishedCategories } from "./disclosure";
import { loadCommune } from "./data";

const NBSP = " ";

describe("socialTotalSentence", () => {
  it("says « hausse » for a rise and « baisse » for a fall, without a doubled sign", () => {
    expect(socialTotalSentence(3.4)).toBe(
      `Dans ce territoire, l'impôt total des bailleurs sociaux est en hausse de 3,4${NBSP}%.`,
    );
    expect(socialTotalSentence(-14.1)).toBe(
      `Dans ce territoire, l'impôt total des bailleurs sociaux est en baisse de 14,1${NBSP}%.`,
    );
  });
  it("handles a flat total and a withheld one", () => {
    expect(socialTotalSentence(0)).toMatch(/reste stable/);
    expect(socialTotalSentence(null)).toBeNull();
    expect(socialTotalSentence(undefined)).toBeNull();
  });
});

describe("categoryNotes on published payloads", () => {
  it("Paris: social housing total rises, so the note says « hausse »", () => {
    const notes = categoryNotes(publishedCategories(loadCommune("paris").by_category));
    expect(notes.social?.totalSentence).toMatch(/en hausse de 3,4/);
    expect(notes.industrial?.median).toBe(`−87,5${NBSP}%`);
    expect(notes.collective).not.toBeNull();
  });
  it("Cahors: no published social housing category, so no social note", () => {
    const notes = categoryNotes(publishedCategories(loadCommune("cahors").by_category));
    expect(notes.social).toBeNull();
    expect(hasCategoryNotes(notes)).toBe(true);
  });
  it("Grenoble: industrial median rises; the note gives the local figure", () => {
    const notes = categoryNotes(publishedCategories(loadCommune("grenoble").by_category));
    expect(notes.industrial?.median).toMatch(/^\+/);
    expect(notes.social?.totalSentence).toMatch(/en baisse de 30,7/);
  });
  it("no rows, no notes", () => {
    expect(hasCategoryNotes(categoryNotes([]))).toBe(false);
  });
});
