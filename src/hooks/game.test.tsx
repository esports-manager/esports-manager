// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { QueryClientProvider } from "@tanstack/react-query";
import { act, renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { commands } from "../bindings";
import { testQueryClient } from "../test/render";
import {
  useContentText,
  useNewGameOptions,
  useOpenSave,
  usePlayer,
  useQuit,
  useRoster,
  useSaves,
  useStartNewGame,
} from "./game";

vi.mock("../bindings", () => ({
  commands: {
    getContentText: vi.fn(),
    getNewGameOptions: vi.fn(),
    listSaves: vi.fn(),
    getRoster: vi.fn(),
    getPlayer: vi.fn(),
    startNewGame: vi.fn(),
    openSave: vi.fn(),
  },
}));

const close = vi.fn();
vi.mock("@tauri-apps/api/window", () => ({ getCurrentWindow: () => ({ close }) }));

function ok<T>(data: T) {
  return Promise.resolve({ status: "ok" as const, data });
}

function wrapper() {
  const client = testQueryClient();
  return {
    client,
    wrapper: ({ children }: { children: ReactNode }) => (
      <QueryClientProvider client={client}>{children}</QueryClientProvider>
    ),
  };
}

beforeEach(() => vi.clearAllMocks());

describe("the game's queries", () => {
  it("ask the backend for what each screen shows", async () => {
    vi.mocked(commands.getContentText).mockReturnValue(ok([]));
    vi.mocked(commands.getNewGameOptions).mockReturnValue(ok({ regions: [] }));
    vi.mocked(commands.listSaves).mockReturnValue(ok([]));
    vi.mocked(commands.getRoster).mockReturnValue(ok("roster" as never));
    vi.mocked(commands.getPlayer).mockReturnValue(ok("player" as never));
    const { wrapper: w } = wrapper();
    const results = [
      renderHook(() => useContentText(), { wrapper: w }).result,
      renderHook(() => useNewGameOptions(), { wrapper: w }).result,
      renderHook(() => useSaves(), { wrapper: w }).result,
      renderHook(() => useRoster("team:b"), { wrapper: w }).result,
      renderHook(() => useRoster(), { wrapper: w }).result,
      renderHook(() => usePlayer("player:kairos"), { wrapper: w }).result,
    ];
    for (const result of results) {
      await waitFor(() => expect(result.current.isSuccess).toBe(true));
    }
    expect(commands.getRoster).toHaveBeenCalledWith("team:b");
    expect(commands.getRoster).toHaveBeenCalledWith(null);
    expect(commands.getPlayer).toHaveBeenCalledWith("player:kairos");
  });
});

describe("the game's mutations", () => {
  it("refresh everything that depends on the open save", async () => {
    vi.mocked(commands.startNewGame).mockReturnValue(
      ok({ file: "a.esmsave", team: "team:a", teamMessage: "team-a" }),
    );
    vi.mocked(commands.openSave).mockReturnValue(
      ok({ file: "a.esmsave", team: "team:a", teamMessage: "team-a" }),
    );
    const { client, wrapper: w } = wrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");
    const start = renderHook(() => useStartNewGame(), { wrapper: w }).result;
    const input = { managerName: "Ana", team: "team:a", saveName: "A", seed: null };
    await act(() => start.current.mutateAsync(input));
    expect(commands.startNewGame).toHaveBeenCalledWith(input);
    const open = renderHook(() => useOpenSave(), { wrapper: w }).result;
    await act(() => open.current.mutateAsync("a.esmsave"));
    expect(commands.openSave).toHaveBeenCalledWith("a.esmsave");
    const keys = invalidate.mock.calls.map(([filters]) => filters?.queryKey?.[0]);
    expect(keys).toEqual(expect.arrayContaining(["contentText", "saves"]));
  });

  it("drop the previous save's rosters and profiles, even when nothing shows them", async () => {
    // Given a roster and a profile cached from one save, and no screen showing them
    vi.mocked(commands.openSave).mockReturnValue(
      ok({ file: "b.esmsave", team: "team:b", teamMessage: "team-b" }),
    );
    const { client, wrapper: w } = wrapper();
    client.setQueryData(["roster", null], { stale: true });
    client.setQueryData(["player", "player:kairos"], { stale: true });
    // When another save is opened
    const open = renderHook(() => useOpenSave(), { wrapper: w }).result;
    await act(() => open.current.mutateAsync("b.esmsave"));
    // Then nothing of the first save is left to show
    expect(client.getQueryData(["roster", null])).toBeUndefined();
    expect(client.getQueryData(["player", "player:kairos"])).toBeUndefined();
  });

  it("quit closes the window", async () => {
    const { wrapper: w } = wrapper();
    const quit = renderHook(() => useQuit(), { wrapper: w }).result;
    await act(() => quit.current.mutateAsync());
    expect(close).toHaveBeenCalled();
  });
});
