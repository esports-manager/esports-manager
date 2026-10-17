// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { describe, expect, it } from "vitest";
import type { RosterPlayer } from "../bindings";
import { DEFAULT_SORT, nextSort, parseSort, sortPlayers, sortSearch } from "./rosterSort";

function player(nickname: string, overall: number, age: number, code = "KR"): RosterPlayer {
  return {
    id: `player:${nickname.toLowerCase()}`,
    nickname,
    givenName: nickname,
    familyName: "X",
    nameOrder: "given-first",
    roleId: "role:mid",
    roleMessage: "role-mid",
    nationality: { id: `nationality:${code.toLowerCase()}`, code, nameMessage: "n" },
    age,
    overall,
  };
}

const collator = new Intl.Collator("en");
const nickname = (p: RosterPlayer) => p.nickname;
// The backend's order: role order, then nickname.
const players = [player("Zed", 70, 20), player("ana", 80, 25, "BR"), player("Bo", 80, 19)];

describe("roster sorting", () => {
  it("keeps the backend's order by default", () => {
    expect(sortPlayers(players, DEFAULT_SORT, nickname, collator)).toEqual(players);
  });

  it("sorts text with the locale's collation, ignoring case", () => {
    const sorted = sortPlayers(
      players,
      { key: "nickname", order: "ascending" },
      nickname,
      collator,
    );
    expect(sorted.map(nickname)).toEqual(["ana", "Bo", "Zed"]);
  });

  it("sorts numbers, and keeps the backend's order for ties in either direction", () => {
    const down = sortPlayers(players, { key: "overall", order: "descending" }, nickname, collator);
    expect(down.map(nickname)).toEqual(["ana", "Bo", "Zed"]);
    const up = sortPlayers(players, { key: "overall", order: "ascending" }, nickname, collator);
    expect(up.map(nickname)).toEqual(["Zed", "ana", "Bo"]);
    const byAge = sortPlayers(players, { key: "age", order: "ascending" }, nickname, collator);
    expect(byAge.map(nickname)).toEqual(["Bo", "Zed", "ana"]);
  });

  it("sorts by the name as shown and by country code", () => {
    const shown = (p: RosterPlayer) => (p.nickname === "Zed" ? "Aaron" : "Zoe");
    const byName = sortPlayers(players, { key: "name", order: "ascending" }, shown, collator);
    expect(byName.map(nickname)).toEqual(["Zed", "ana", "Bo"]);
    const byCountry = sortPlayers(
      players,
      { key: "nationality", order: "ascending" },
      nickname,
      collator,
    );
    expect(byCountry.map(nickname)).toEqual(["ana", "Zed", "Bo"]);
  });

  it("flips the same column and starts a new one in its natural order", () => {
    expect(nextSort(DEFAULT_SORT, "role")).toEqual({ key: "role", order: "descending" });
    expect(nextSort(DEFAULT_SORT, "overall")).toEqual({ key: "overall", order: "descending" });
    expect(nextSort({ key: "overall", order: "descending" }, "overall")).toEqual({
      key: "overall",
      order: "ascending",
    });
    expect(nextSort(DEFAULT_SORT, "nickname")).toEqual({ key: "nickname", order: "ascending" });
  });

  it("reads a sort from the URL, falling back to the default", () => {
    expect(parseSort("age", "descending")).toEqual({ key: "age", order: "descending" });
    expect(parseSort("age", "sideways")).toEqual({ key: "age", order: "ascending" });
    expect(parseSort("salary", "descending")).toEqual(DEFAULT_SORT);
    expect(parseSort(undefined, undefined)).toEqual(DEFAULT_SORT);
  });

  it("leaves the default sort out of the URL", () => {
    expect(sortSearch(DEFAULT_SORT)).toEqual({});
    expect(sortSearch({ key: "age", order: "descending" })).toEqual({
      sort: "age",
      order: "descending",
    });
  });
});
