// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import type { RosterPlayer } from "../bindings";

/**
 * Re-sorting the roster table (roster spec: "The UI may re-sort the table by
 * a column"). It only reorders the rows the backend sent; ties keep the
 * backend's order, which is role order then nickname.
 */
const SORT_KEYS = ["role", "nickname", "name", "nationality", "age", "overall"] as const;
export type SortKey = (typeof SORT_KEYS)[number];
type SortOrder = "ascending" | "descending";

export interface RosterSort {
  key: SortKey;
  order: SortOrder;
}

/** The backend's own order. */
export const DEFAULT_SORT: RosterSort = { key: "role", order: "ascending" };

/** Numbers read best largest first; text from A. */
const FIRST_ORDER: Record<SortKey, SortOrder> = {
  role: "ascending",
  nickname: "ascending",
  name: "ascending",
  nationality: "ascending",
  age: "descending",
  overall: "descending",
};

/** A sort as search parameters; the default one is left out of the URL. */
export interface SortSearch {
  sort?: SortKey;
  order?: SortOrder;
}

export function sortSearch(sort: RosterSort): SortSearch {
  return sort.key === DEFAULT_SORT.key && sort.order === DEFAULT_SORT.order
    ? {}
    : { sort: sort.key, order: sort.order };
}

/** The sort after a click on `key`'s header: the same column flips, another starts fresh. */
export function nextSort(current: RosterSort, key: SortKey): RosterSort {
  if (current.key === key) {
    return { key, order: current.order === "ascending" ? "descending" : "ascending" };
  }
  return { key, order: FIRST_ORDER[key] };
}

/** A sort from the URL's search parameters; anything unknown is the default. */
export function parseSort(key: unknown, order: unknown): RosterSort {
  const known = SORT_KEYS.find((candidate) => candidate === key);
  if (known === undefined) {
    return DEFAULT_SORT;
  }
  return { key: known, order: order === "descending" ? "descending" : "ascending" };
}

/** `players` in `sort`'s order. `name` gives the full name as shown. */
export function sortPlayers(
  players: readonly RosterPlayer[],
  sort: RosterSort,
  name: (player: RosterPlayer) => string,
  collator: Intl.Collator,
): RosterPlayer[] {
  const value = (player: RosterPlayer, index: number): string | number => {
    switch (sort.key) {
      case "role":
        return index;
      case "nickname":
        return player.nickname;
      case "name":
        return name(player);
      case "nationality":
        return player.nationality.code;
      case "age":
        return player.age;
      case "overall":
        return player.overall;
    }
  };
  const direction = sort.order === "ascending" ? 1 : -1;
  return players
    .map((player, index) => ({ player, index, value: value(player, index) }))
    .sort((a, b) => {
      const compared =
        typeof a.value === "number" && typeof b.value === "number"
          ? a.value - b.value
          : collator.compare(String(a.value), String(b.value));
      return compared === 0 ? a.index - b.index : compared * direction;
    })
    .map(({ player }) => player);
}
