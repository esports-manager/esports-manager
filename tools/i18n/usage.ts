// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Finds which Fluent messages the UI code uses, and user-visible text that
 * bypasses Fluent (ADR 0007).
 */
import { parseSync } from "oxc-parser";

/** JSX attributes whose string values are shown to the user. */
const VISIBLE_ATTRIBUTES = new Set([
  "alt",
  "aria-description",
  "aria-label",
  "label",
  "placeholder",
  "title",
]);

export interface Usage {
  /** Message ids used through `<Localized id="…">` or `getString("…")`. */
  ids: string[];
  /** Problems found, as `file:line: message`. */
  violations: string[];
}

interface AstNode {
  type: string;
  start: number;
  [key: string]: unknown;
}

function isNode(value: unknown): value is AstNode {
  return typeof value === "object" && value !== null && typeof (value as AstNode).type === "string";
}

function children(node: AstNode): AstNode[] {
  return Object.values(node).flatMap((value) =>
    Array.isArray(value) ? value.filter(isNode) : isNode(value) ? [value] : [],
  );
}

function stringLiteral(node: unknown): string | undefined {
  return isNode(node) && node.type === "Literal" && typeof node.value === "string"
    ? node.value
    : undefined;
}

function nameOf(node: unknown): string | undefined {
  return isNode(node) && typeof node.name === "string" ? node.name : undefined;
}

export function findUsage(file: string, source: string): Usage {
  const ids: string[] = [];
  const violations: string[] = [];
  const lineOf = (offset: number) => source.slice(0, offset).split("\n").length;
  const report = (node: AstNode, message: string) =>
    violations.push(`${file}:${lineOf(node.start)}: ${message}`);

  const { program, errors } = parseSync(file, source);
  for (const error of errors) {
    violations.push(`${file}: could not parse: ${error.message}`);
  }

  const visit = (node: AstNode): void => {
    if (node.type === "JSXText" && typeof node.value === "string" && node.value.trim()) {
      report(node, `text "${node.value.trim()}" must come from a Fluent message`);
    }
    if (node.type === "JSXAttribute") {
      const name = nameOf(node.name);
      const value = stringLiteral(node.value);
      if (name !== undefined && VISIBLE_ATTRIBUTES.has(name) && value?.trim()) {
        report(node, `attribute ${name}="${value}" must come from a Fluent message`);
      }
    }
    if (node.type === "JSXOpeningElement" && nameOf(node.name) === "Localized") {
      const attributes = (node.attributes as unknown[]).filter(isNode);
      const idAttribute = attributes.find((attribute) => nameOf(attribute.name) === "id");
      const id = idAttribute === undefined ? undefined : stringLiteral(idAttribute.value);
      if (id === undefined) {
        report(node, "<Localized> needs a string-literal id so it can be checked");
      } else {
        ids.push(id);
      }
    }
    if (node.type === "CallExpression") {
      const callee = node.callee;
      if (
        isNode(callee) &&
        callee.type === "MemberExpression" &&
        nameOf(callee.property) === "getString"
      ) {
        const [first] = (node.arguments as unknown[]).filter(isNode);
        const id = stringLiteral(first);
        if (id === undefined) {
          report(node, "getString() needs a string-literal id so it can be checked");
        } else {
          ids.push(id);
        }
      }
    }
    for (const child of children(node)) {
      visit(child);
    }
  };
  visit(program as unknown as AstNode);

  return { ids, violations };
}

/**
 * Every used id must exist in the reference catalog, and every message in it
 * must be used somewhere. Terms (`-name`) are used by messages, not code.
 */
export function checkUsage(
  usedIds: ReadonlySet<string>,
  catalogIds: ReadonlySet<string>,
): string[] {
  const violations: string[] = [];
  for (const id of [...usedIds].sort()) {
    if (!catalogIds.has(id)) {
      violations.push(`message "${id}" is used in code but not defined in the en catalog`);
    }
  }
  for (const id of [...catalogIds].sort()) {
    if (!id.startsWith("-") && !usedIds.has(id)) {
      violations.push(`message "${id}" is defined but never used`);
    }
  }
  return violations;
}

/**
 * Message ids Rust code refers to (ADR 0007: ids used in TS or Rust). Rust
 * names a message as `Message::new("…")`, which must exist; any other string
 * literal that happens to be a catalog id (such as the `attribute-…` ids a
 * function returns) also counts as a use.
 *
 * Only shipped code uses a message: test files (`tests/`, `*_tests.rs`) and
 * everything from a file's inline test module (`#[cfg(test)] mod … {`) on
 * are still checked for unknown ids, but don't keep a message alive. A
 * `#[cfg(test)] mod drift;` line elsewhere doesn't end the shipped code.
 */
export function findRustUsage(
  file: string,
  source: string,
  catalogIds: ReadonlySet<string>,
): Usage {
  const ids = new Set<string>();
  const violations: string[] = [];
  const lineOf = (offset: number) => source.slice(0, offset).split("\n").length;
  const testsStart = isRustTestFile(file) ? 0 : (source.match(RUST_TEST_MODULE)?.index ?? -1);
  const shipped = testsStart === -1 ? source : source.slice(0, testsStart);
  for (const match of source.matchAll(/Message::new\(\s*"([^"]*)"/g)) {
    const id = match[1] ?? "";
    if (match.index < shipped.length) {
      ids.add(id);
    }
    if (!catalogIds.has(id)) {
      violations.push(
        `${file}:${lineOf(match.index)}: message "${id}" is not defined in the en catalog`,
      );
    }
  }
  for (const match of shipped.matchAll(/"([a-z][a-z0-9]*(?:-[a-z0-9]+)+)"/g)) {
    const id = match[1] ?? "";
    if (catalogIds.has(id)) {
      ids.add(id);
    }
  }
  return { ids: [...ids], violations };
}

/** `#[cfg(test)]`, any other attributes, then an inline `mod name {`. */
const RUST_TEST_MODULE = /#\[cfg\(test\)\]\s*(?:#\[[^\]]*\]\s*)*mod\s+\w+\s*\{/;

function isRustTestFile(file: string): boolean {
  const parts = file.split(/[\\/]/);
  return parts.includes("tests") || (parts.at(-1) ?? "").endsWith("_tests.rs");
}
