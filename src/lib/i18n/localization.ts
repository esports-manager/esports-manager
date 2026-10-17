// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { FluentBundle, FluentResource } from "@fluent/bundle";
import { ReactLocalization } from "@fluent/react";
import type { ContentText } from "../../bindings";
import { type Locale, negotiateLocales } from "./locales";

const sources = import.meta.glob<string>("../../locales/*/*.ftl", {
  query: "?raw",
  import: "default",
  eager: true,
});

/** All `.ftl` sources of one locale, in file-name order. */
function sourcesFor(locale: Locale): string[] {
  const prefix = `../../locales/${locale}/`;
  return Object.keys(sources)
    .filter((path) => path.startsWith(prefix))
    .sort()
    .flatMap((path) => sources[path] ?? []);
}

/**
 * The game's messages for `locale`, plus the package text (`content`) of the
 * same locale: team, region, role and country names (packages spec).
 */
export function createBundle(locale: Locale, content: readonly ContentText[] = []): FluentBundle {
  // No bidi isolation marks: every shipped locale is left-to-right.
  const bundle = new FluentBundle(locale, { useIsolating: false });
  for (const source of sourcesFor(locale)) {
    const errors = bundle.addResource(new FluentResource(source));
    if (errors.length > 0) {
      throw new Error(`Invalid Fluent messages for ${locale}: ${errors.join("; ")}`);
    }
  }
  for (const text of content.filter((text) => text.locale === locale)) {
    // The package loader has already checked its text; a package can't
    // override the game's own messages, so clashes are skipped.
    bundle.addResource(new FluentResource(text.source));
  }
  return bundle;
}

/**
 * The localization for the user's preferred languages, with English
 * fallback; a name missing in one locale falls back to the next (PKG-011).
 */
export function createLocalization(
  requested: readonly string[],
  content: readonly ContentText[] = [],
): ReactLocalization {
  return new ReactLocalization(
    negotiateLocales(requested).map((locale) => createBundle(locale, content)),
  );
}
