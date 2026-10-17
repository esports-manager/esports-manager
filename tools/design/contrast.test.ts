// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { checkTextContrast, contrastRatio, hexTokens, luminance } from "./contrast";

describe("contrast", () => {
  it("computes WCAG luminance at the extremes", () => {
    expect(luminance("#000000")).toBe(0);
    expect(luminance("#ffffff")).toBeCloseTo(1, 10);
  });

  it("matches known WCAG ratios", () => {
    expect(contrastRatio("#ffffff", "#000000")).toBeCloseTo(21, 5);
    expect(contrastRatio("#777777", "#ffffff")).toBeCloseTo(4.48, 2);
    expect(contrastRatio("#ffffff", "#777777")).toBeCloseTo(4.48, 2);
  });

  it("reads hex tokens and ignores other declarations", () => {
    const tokens = hexTokens(":root { --a-b: #AABBCC; --size: 1rem; --c: #123; }");
    expect(tokens).toEqual(new Map([["a-b", "#aabbcc"]]));
  });

  it("reports every text/surface pair below AA", () => {
    const tokens = new Map([
      ["text-good", "#ffffff"],
      ["text-bad", "#444444"],
      ["surface-dark", "#000000"],
    ]);
    expect(checkTextContrast(tokens)).toEqual([
      "--text-bad on --surface-dark is 2.16:1, below 4.5:1",
    ]);
  });

  it("fails when there is nothing to check", () => {
    expect(checkTextContrast(new Map())).toEqual(["no --text-* or --surface-* tokens found"]);
  });

  it("the design tokens meet AA for text on every surface", () => {
    const css = readFileSync(join(import.meta.dirname, "../../src/styles/tokens.css"), "utf8");
    expect(checkTextContrast(hexTokens(css))).toEqual([]);
  });

  it("button text meets AA on the button and on its hover state", () => {
    const css = readFileSync(join(import.meta.dirname, "../../src/styles/tokens.css"), "utf8");
    const tokens = hexTokens(css);
    const text = tokens.get("text-on-accent") ?? "";
    for (const background of ["accent-strong", "accent-hover"]) {
      expect(contrastRatio(text, tokens.get(background) ?? "#ffffff")).toBeGreaterThanOrEqual(4.5);
    }
  });
});
