// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { describe, expect, it } from "vitest";
import { checkUsage, findRustUsage, findUsage } from "./usage";

describe("findUsage", () => {
  it("collects ids from <Localized> and getString()", () => {
    const usage = findUsage(
      "a.tsx",
      'const a = <Localized id="title"><h1 /></Localized>;\nconst b = l10n.getString("loading");\n',
    );
    expect(usage).toEqual({ ids: ["title", "loading"], violations: [] });
  });

  it("reports visible text and attributes written in code", () => {
    const usage = findUsage(
      "a.tsx",
      'const a = <p title="Hi">\n  Hello\n</p>;\nconst b = <img alt="" className="x" />;\n',
    );
    expect(usage.violations).toEqual([
      'a.tsx:1: attribute title="Hi" must come from a Fluent message',
      'a.tsx:1: text "Hello" must come from a Fluent message',
    ]);
  });

  it("allows whitespace-only text between elements", () => {
    expect(findUsage("a.tsx", "const a = <div>\n  <span />\n</div>;").violations).toEqual([]);
  });

  it("requires literal ids so they can be checked", () => {
    const usage = findUsage("a.tsx", "const a = <Localized id={k} />;\nl10n.getString(k);\n");
    expect(usage.violations).toEqual([
      "a.tsx:1: <Localized> needs a string-literal id so it can be checked",
      "a.tsx:2: getString() needs a string-literal id so it can be checked",
    ]);
  });

  it("reports parse errors", () => {
    expect(findUsage("a.tsx", "const = ;").violations[0]).toMatch(/^a\.tsx: could not parse/);
  });
});

describe("checkUsage", () => {
  it("passes when used ids and messages match, ignoring terms", () => {
    expect(checkUsage(new Set(["a"]), new Set(["a", "-brand"]))).toEqual([]);
  });

  it("reports undefined and unused messages", () => {
    expect(checkUsage(new Set(["a", "z"]), new Set(["a", "b"]))).toEqual([
      'message "z" is used in code but not defined in the en catalog',
      'message "b" is defined but never used',
    ]);
  });
});

describe("findRustUsage", () => {
  const catalog = new Set(["error-storage", "attribute-mechanics"]);

  it("collects ids named with Message::new and flags unknown ones", () => {
    const source =
      'let a = Message::new("error-storage");\nlet b = Message::new( "error-missing" );\n';
    const usage = findRustUsage("a.rs", source, catalog);
    expect(usage.ids.sort()).toEqual(["error-missing", "error-storage"]);
    expect(usage.violations).toEqual([
      'a.rs:2: message "error-missing" is not defined in the en catalog',
    ]);
  });

  it("counts other literals only when they are catalog ids", () => {
    const usage = findRustUsage(
      "a.rs",
      'match x { A => "attribute-mechanics", B => "not-a-message" }',
      catalog,
    );
    expect(usage.ids).toEqual(["attribute-mechanics"]);
    expect(usage.violations).toEqual([]);
  });

  it("ignores ids that only tests use, but still checks them", () => {
    const shipped = 'fn a() -> &str { "attribute-mechanics" }\n';
    const tests =
      '#[cfg(test)]\nmod tests { const B: &str = "error-storage"; fn c() { Message::new("error-gone"); } }\n';
    const usage = findRustUsage("crates/a/src/lib.rs", shipped + tests, catalog);
    expect(usage.ids).toEqual(["attribute-mechanics"]);
    expect(usage.violations).toEqual([
      'crates/a/src/lib.rs:3: message "error-gone" is not defined in the en catalog',
    ]);
    for (const file of ["crates/a/tests/e2e.rs", "crates/a/src/game_tests.rs"]) {
      expect(findRustUsage(file, 'const A: &str = "error-storage";', catalog).ids).toEqual([]);
    }
  });

  it("a test module declared elsewhere doesn't end the shipped code", () => {
    const source = '#[cfg(test)]\nmod drift;\n\nfn a() -> &str { "error-storage" }\n';
    expect(findRustUsage("crates/a/src/lib.rs", source, catalog).ids).toEqual(["error-storage"]);
  });
});
