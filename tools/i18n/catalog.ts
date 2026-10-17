// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Reads Fluent catalogs into a comparable shape: every entry (message or
 * term) with the variables it uses (ADR 0007).
 */
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { type Expression, Junk, Message, type Pattern, parse, Term, Visitor } from "@fluent/syntax";

/** Entry id → the `$variables` it references. Term ids start with `-`. */
type Catalog = Map<string, Set<string>>;

export interface ParsedCatalog {
  catalog: Catalog;
  errors: string[];
}

class VariableCollector extends Visitor {
  readonly names = new Set<string>();
  override visitVariableReference(node: { id: { name: string } }): void {
    this.names.add(node.id.name);
  }
}

function variablesOf(...patterns: (Pattern | Expression | null)[]): Set<string> {
  const collector = new VariableCollector();
  for (const pattern of patterns) {
    if (pattern !== null) {
      collector.visit(pattern);
    }
  }
  return collector.names;
}

/** Parses one or more `.ftl` sources that together form one locale. */
export function parseCatalog(sources: readonly { name: string; text: string }[]): ParsedCatalog {
  const catalog: Catalog = new Map();
  const errors: string[] = [];
  for (const { name, text } of sources) {
    for (const entry of parse(text, {}).body) {
      if (entry instanceof Junk) {
        errors.push(`${name}: invalid Fluent syntax near "${entry.content.trim().slice(0, 40)}"`);
        continue;
      }
      if (!(entry instanceof Message || entry instanceof Term)) {
        continue;
      }
      const id = entry instanceof Term ? `-${entry.id.name}` : entry.id.name;
      if (catalog.has(id)) {
        errors.push(`${name}: "${id}" is defined more than once`);
      }
      const attributes = entry.attributes.map((attribute) => attribute.value);
      catalog.set(id, variablesOf(entry.value, ...attributes));
    }
  }
  return { catalog, errors };
}

/** Loads `<root>/<locale>/*.ftl` for every locale directory. */
export function loadCatalogs(root: string): Map<string, ParsedCatalog> {
  const catalogs = new Map<string, ParsedCatalog>();
  for (const locale of readdirSync(root).sort()) {
    const dir = join(root, locale);
    const sources = readdirSync(dir)
      .filter((file) => file.endsWith(".ftl"))
      .sort()
      .map((file) => ({ name: `${locale}/${file}`, text: readFileSync(join(dir, file), "utf8") }));
    catalogs.set(locale, parseCatalog(sources));
  }
  return catalogs;
}

/**
 * Every locale must define exactly the entries of the reference locale,
 * each with the same variables.
 */
export function checkParity(
  reference: string,
  catalogs: ReadonlyMap<string, ParsedCatalog>,
): string[] {
  const violations = [...catalogs.values()].flatMap((parsed) => parsed.errors);
  const base = catalogs.get(reference);
  if (base === undefined) {
    return [...violations, `the reference locale "${reference}" has no catalog`];
  }
  for (const [locale, { catalog }] of catalogs) {
    if (locale === reference) {
      continue;
    }
    for (const [id, variables] of base.catalog) {
      const translated = catalog.get(id);
      if (translated === undefined) {
        violations.push(`${locale}: missing "${id}"`);
        continue;
      }
      const expected = [...variables].sort().join(", ");
      const actual = [...translated].sort().join(", ");
      if (expected !== actual) {
        violations.push(`${locale}: "${id}" uses {${actual}} but ${reference} uses {${expected}}`);
      }
    }
    for (const id of catalog.keys()) {
      if (!base.catalog.has(id)) {
        violations.push(`${locale}: "${id}" is not defined in ${reference}`);
      }
    }
  }
  return violations;
}
