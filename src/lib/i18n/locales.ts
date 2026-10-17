// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { negotiateLanguages } from "@fluent/langneg";

/** Locales the game ships, complete for every message (ADR 0007). */
export const SUPPORTED_LOCALES = ["en", "pt-BR"] as const;
export type Locale = (typeof SUPPORTED_LOCALES)[number];

/** Used when nothing the user asks for is supported, and as the fallback. */
export const DEFAULT_LOCALE: Locale = "en";

function isLocale(value: string): value is Locale {
  return (SUPPORTED_LOCALES as readonly string[]).includes(value);
}

/**
 * The supported locales that best match `requested`, best first, always
 * ending with the default so a missing message falls back to English.
 */
export function negotiateLocales(requested: readonly string[]): Locale[] {
  const matched = negotiateLanguages(requested, SUPPORTED_LOCALES, {
    defaultLocale: DEFAULT_LOCALE,
  }).filter(isLocale);
  return matched.includes(DEFAULT_LOCALE) ? matched : [...matched, DEFAULT_LOCALE];
}
