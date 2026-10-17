// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { createRootRoute, createRoute, createRouter } from "@tanstack/react-router";
import { LoadGame } from "./routes/LoadGame";
import { MainMenu } from "./routes/MainMenu";
import { NewGame } from "./routes/NewGame";
import { Player } from "./routes/Player";
import { Roster } from "./routes/Roster";
import { parseSort, type SortSearch, sortSearch } from "./routes/rosterSort";
import { Shell } from "./routes/Shell";

const rootRoute = createRootRoute({ component: Shell });

const menuRoute = createRoute({ getParentRoute: () => rootRoute, path: "/", component: MainMenu });

const newGameRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/new",
  component: NewGame,
});

const loadGameRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/load",
  component: LoadGame,
});

function text(value: unknown): string | undefined {
  return typeof value === "string" && value !== "" ? value : undefined;
}

function sortFrom(search: Record<string, unknown>): SortSearch {
  return sortSearch(parseSort(search.sort, search.order));
}

// Ids hold `:` and `.`, so they travel as search parameters, not path segments.
// The roster's sort travels to the profile too, so Back keeps it.
const rosterRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/roster",
  validateSearch: (search: Record<string, unknown>): { team?: string } & SortSearch => {
    const team = text(search.team);
    return { ...(team === undefined ? {} : { team }), ...sortFrom(search) };
  },
  component: function RosterRoute() {
    const { team, sort, order } = rosterRoute.useSearch();
    return <Roster team={team} sort={parseSort(sort, order)} />;
  },
});

const playerRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/player",
  validateSearch: (search: Record<string, unknown>): { id: string; team?: string } & SortSearch => {
    const team = text(search.team);
    return {
      id: text(search.id) ?? "",
      ...(team === undefined ? {} : { team }),
      ...sortFrom(search),
    };
  },
  component: function PlayerRoute() {
    const { id, team, sort, order } = playerRoute.useSearch();
    return <Player id={id} team={team} sort={parseSort(sort, order)} />;
  },
});

export const router = createRouter({
  routeTree: rootRoute.addChildren([
    menuRoute,
    newGameRoute,
    loadGameRoute,
    rosterRoute,
    playerRoute,
  ]),
});

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}
