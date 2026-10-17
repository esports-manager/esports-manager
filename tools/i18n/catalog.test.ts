// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { describe, expect, it } from "vitest";
import { checkParity, type ParsedCatalog, parseCatalog } from "./catalog";

const parsed = (text: string, name = "x/main.ftl"): ParsedCatalog => parseCatalog([{ name, text }]);

describe("parseCatalog", () => {
  it("collects messages, terms and the variables they use", () => {
    const { catalog, errors } = parsed(
      "-brand = Game\nhello = Hi { $name }, welcome to { -brand }\n    .title = { $count } new\n",
    );
    expect(errors).toEqual([]);
    expect(catalog).toEqual(
      new Map([
        ["-brand", new Set()],
        ["hello", new Set(["name", "count"])],
      ]),
    );
  });

  it("reports invalid syntax and duplicates", () => {
    const { errors } = parsed("ok = fine\nok = again\nbroken = { $\n");
    expect(errors).toEqual([
      'x/main.ftl: "ok" is defined more than once',
      'x/main.ftl: invalid Fluent syntax near "broken = { $"',
    ]);
  });
});

describe("checkParity", () => {
  const catalogs = (entries: Record<string, string>) =>
    new Map(Object.entries(entries).map(([locale, text]) => [locale, parsed(text)]));

  it("passes when every locale matches the reference", () => {
    expect(
      checkParity("en", catalogs({ en: "a = A { $n }\n", "pt-BR": "a = Á { $n }\n" })),
    ).toEqual([]);
  });

  it("reports missing, extra and mismatched entries", () => {
    const violations = checkParity(
      "en",
      catalogs({ en: "a = A { $n }\nb = B\n", "pt-BR": "a = A { $m }\nc = C\n" }),
    );
    expect(violations).toEqual([
      'pt-BR: "a" uses {m} but en uses {n}',
      'pt-BR: missing "b"',
      'pt-BR: "c" is not defined in en',
    ]);
  });

  it("reports a missing reference locale", () => {
    expect(checkParity("en", catalogs({ "pt-BR": "a = A\n" }))).toEqual([
      'the reference locale "en" has no catalog',
    ]);
  });

  it("includes syntax errors from every locale", () => {
    expect(checkParity("en", catalogs({ en: "a = { $\n" }))).toHaveLength(1);
  });
});
