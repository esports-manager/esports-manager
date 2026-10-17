// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/** WCAG contrast checks over the design tokens (ADR 0006). */

/** WCAG 2.x minimum contrast for normal-size text (level AA). */
const AA_NORMAL_TEXT = 4.5;

/** `--name: #rrggbb;` declarations in a stylesheet, by name. */
export function hexTokens(css: string): Map<string, string> {
  const tokens = new Map<string, string>();
  for (const match of css.matchAll(/--([\w-]+):\s*(#[0-9a-fA-F]{6})\s*;/g)) {
    const [, name, value] = match;
    if (name !== undefined && value !== undefined) {
      tokens.set(name, value.toLowerCase());
    }
  }
  return tokens;
}

function channel(value: number): number {
  const srgb = value / 255;
  return srgb <= 0.039_28 ? srgb / 12.92 : ((srgb + 0.055) / 1.055) ** 2.4;
}

/** Relative luminance of a `#rrggbb` colour. */
export function luminance(hex: string): number {
  const [r, g, b] = [1, 3, 5].map((start) =>
    channel(Number.parseInt(hex.slice(start, start + 2), 16)),
  );
  return 0.2126 * (r ?? 0) + 0.7152 * (g ?? 0) + 0.0722 * (b ?? 0);
}

export function contrastRatio(a: string, b: string): number {
  const [light, dark] = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return ((light ?? 0) + 0.05) / ((dark ?? 0) + 0.05);
}

/** Every `--text-*` token against every `--surface-*` token. */
export function checkTextContrast(tokens: ReadonlyMap<string, string>): string[] {
  const pick = (prefix: string) => [...tokens].filter(([name]) => name.startsWith(prefix));
  const texts = pick("text-");
  const surfaces = pick("surface-");
  if (texts.length === 0 || surfaces.length === 0) {
    return ["no --text-* or --surface-* tokens found"];
  }
  return texts.flatMap(([text, fg]) =>
    surfaces.flatMap(([surface, bg]) => {
      const ratio = contrastRatio(fg, bg);
      return ratio < AA_NORMAL_TEXT
        ? [`--${text} on --${surface} is ${ratio.toFixed(2)}:1, below ${AA_NORMAL_TEXT}:1`]
        : [];
    }),
  );
}
