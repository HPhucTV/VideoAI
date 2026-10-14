import { describe, it, expect } from "vitest";
import { normalizeVietnameseText } from "../rules.js";
import fixtures from "./fixtures.json" with { type: "json" };

describe("Vietnamese Phonetics Engine", () => {
  fixtures.forEach(({ input, expected }, idx) => {
    it(`Test Case #${idx + 1}: ${input}`, () => {
      const actual = normalizeVietnameseText(input);
      expect(actual).toBe(expected);
    });
  });
});
