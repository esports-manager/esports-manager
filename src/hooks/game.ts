// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getCurrentWindow } from "@tauri-apps/api/window";
import { commands, type NewGameInput } from "../bindings";
import { unwrap } from "../lib/backend/result";

/**
 * Queries that depend on which save is open. Rosters and profiles are
 * dropped, not just refetched: player ids repeat across worlds, so a cached
 * one would briefly show the previous save's data.
 */
const REFRESHED_ON_SAVE_CHANGE = ["contentText", "saves"];
const DROPPED_ON_SAVE_CHANGE = ["roster", "player"];

/** The package text the UI's Fluent bundles need: team, region and role names. */
export function useContentText() {
  return useQuery({
    queryKey: ["contentText"],
    queryFn: () => unwrap(commands.getContentText()),
  });
}

export function useNewGameOptions() {
  return useQuery({
    queryKey: ["newGameOptions"],
    queryFn: () => unwrap(commands.getNewGameOptions()),
  });
}

export function useSaves() {
  return useQuery({ queryKey: ["saves"], queryFn: () => unwrap(commands.listSaves()) });
}

/** The roster of `team`, or of the user's team. */
export function useRoster(team?: string | undefined) {
  return useQuery({
    queryKey: ["roster", team ?? null],
    queryFn: () => unwrap(commands.getRoster(team ?? null)),
  });
}

export function usePlayer(id: string) {
  return useQuery({ queryKey: ["player", id], queryFn: () => unwrap(commands.getPlayer(id)) });
}

function useSaveChange<T>(run: (input: T) => ReturnType<typeof commands.openSave>) {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (input: T) => unwrap(run(input)),
    onSuccess: async () => {
      for (const key of DROPPED_ON_SAVE_CHANGE) {
        client.removeQueries({ queryKey: [key] });
      }
      await Promise.all(
        REFRESHED_ON_SAVE_CHANGE.map((key) => client.invalidateQueries({ queryKey: [key] })),
      );
    },
  });
}

/** Creates a game and opens it. */
export function useStartNewGame() {
  return useSaveChange((input: NewGameInput) => commands.startNewGame(input));
}

export function useOpenSave() {
  return useSaveChange((file: string) => commands.openSave(file));
}

/** Closes the window, which ends the app (main menu, desktop only). */
export function useQuit() {
  return useMutation({ mutationFn: () => getCurrentWindow().close() });
}
