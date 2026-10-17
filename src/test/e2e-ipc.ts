// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { mockIPC } from "@tauri-apps/api/mocks";
import type {
  About,
  ContentText,
  Failure,
  GameOpened,
  NewGameInput,
  NewGameOptions,
  PlayerProfile,
  RosterView,
  SaveSummary,
} from "../bindings";
import newGameOptions from "./fixtures/new-game-options.json";
import player from "./fixtures/player.json";
import roster from "./fixtures/roster.json";
import oncaRoster from "./fixtures/roster-onca.json";
import savedGames from "./fixtures/saves.json";

/**
 * A stand-in backend for browser-only E2E runs (`vite --mode e2e`). It
 * answers with views the real backend produced (`src/test/fixtures`, kept
 * current by a Rust test) and the core package's real text, and remembers
 * the saves a test creates. Rosters exist for Azure Tigers and Onça Gaming;
 * any other team is unknown, so a wrong team id fails the test.
 *
 * A test can ask for a broken package with
 * `window.__ESM_E2E__ = { brokenPackage: true }` before the page loads.
 */
declare global {
  interface Window {
    __ESM_E2E__?: { brokenPackage?: boolean; saves?: boolean };
  }
}

const packageText = import.meta.glob<string>("../../content/core/locales/*/*.ftl", {
  query: "?raw",
  import: "default",
  eager: true,
});

function contentText(): ContentText[] {
  return Object.entries(packageText).map(([path, source]) => {
    const [locale = "en", file = ""] = path.split("/locales/")[1]?.split("/") ?? [];
    return { locale, file: `locales/${locale}/${file}`, source };
  });
}

function failure(id: string, args: Record<string, string> = {}): Failure {
  return {
    messages: [
      {
        id,
        args: Object.entries(args).map(([name, value]) => ({
          name,
          value: { kind: "text", value },
        })),
      },
    ],
  };
}

/** The roster fixtures, by team id. */
const rosters = new Map<string, RosterView>(
  [roster, oncaRoster].map((view) => [view.team.id, view as RosterView]),
);

/** `team-onca_gaming` → `team:onca_gaming`: the team a save's name message names. */
function teamOf(save: SaveSummary): string {
  return save.status === "ready" ? save.teamMessage.replace("-", ":") : "";
}

const brokenPackage: Failure = {
  messages: [
    {
      id: "problem-unknown-field",
      args: [
        { name: "field", value: { kind: "text", value: "reputaton" } },
        { name: "file", value: { kind: "text", value: "teams/seorabeol/azure_tigers.json" } },
        { name: "path", value: { kind: "text", value: "reputaton" } },
      ],
    },
  ],
};

export function installIpcMocks(): void {
  const options = window.__ESM_E2E__ ?? {};
  const saves: SaveSummary[] = options.saves ? [...(savedGames as SaveSummary[])] : [];
  // The open save's file and team.
  let open: { file: string; team: string } | undefined;

  const handlers: Record<string, (args: Record<string, unknown>) => unknown> = {
    get_about: (): About => ({ version: "0.0.0-e2e" }),
    // With no save open, the real backend reads the package for its text.
    get_content_text: (): ContentText[] => {
      if (options.brokenPackage && open === undefined) {
        throw brokenPackage;
      }
      return contentText();
    },
    get_new_game_options: (): NewGameOptions => {
      if (options.brokenPackage) {
        throw brokenPackage;
      }
      return newGameOptions as NewGameOptions;
    },
    start_new_game: (args): GameOpened => {
      const input = args.input as NewGameInput;
      if (input.managerName.trim() === "") {
        throw failure("error-manager-name-empty");
      }
      const taken = saves.some(
        (save) =>
          save.status === "ready" && save.name.toLowerCase() === input.saveName.toLowerCase(),
      );
      if (taken) {
        throw failure("error-save-name-taken", { name: input.saveName });
      }
      const file = `${input.saveName.toLowerCase().replace(/[^a-z0-9]+/g, "-")}.esmsave`;
      saves.unshift({
        status: "ready",
        file,
        inUse: false,
        name: input.saveName,
        managerName: input.managerName,
        teamMessage: input.team.replace(":", "-"),
        gameDate: "2027-01-01",
        lastPlayedAt: 1_792_100_000,
      });
      open = { file, team: input.team };
      return { ...open, teamMessage: input.team.replace(":", "-") };
    },
    list_saves: (): SaveSummary[] => saves,
    open_save: (args): GameOpened => {
      const file = args.file as string;
      const index = saves.findIndex((candidate) => candidate.file === file);
      const save = saves[index];
      if (save === undefined) {
        throw failure("error-save-not-found", { file });
      }
      // Opening plays it, so it moves to the top of the list.
      saves.splice(index, 1);
      saves.unshift(save.status === "ready" ? { ...save, lastPlayedAt: 1_792_100_000 } : save);
      open = { file, team: teamOf(save) };
      return { ...open, teamMessage: open.team.replace(":", "-") };
    },
    get_roster: (args): RosterView => {
      if (open === undefined) {
        throw failure("error-no-save-open");
      }
      const team = (args.team as string | null) ?? open.team;
      const view = rosters.get(team);
      if (view === undefined) {
        throw failure("error-unknown-team", { team });
      }
      return view;
    },
    get_player: (args): PlayerProfile => {
      const id = args.id as string;
      if (open === undefined || id !== "player:kairos") {
        throw failure("error-unknown-player", { player: id });
      }
      return player as PlayerProfile;
    },
    "plugin:window|close": () => null,
  };

  mockIPC((command, args) => {
    const handler = handlers[command];
    if (handler === undefined) {
      throw new Error(`No E2E mock for command "${command}"`);
    }
    return handler((args ?? {}) as Record<string, unknown>);
  });
}
