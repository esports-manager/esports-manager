// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { App } from "./App";
import { commands } from "./bindings";
import { testQueryClient } from "./test/render";

vi.mock("./bindings", () => ({
  commands: { getAbout: vi.fn(), getContentText: vi.fn() },
}));

describe("App", () => {
  it("renders the shell and the main menu", async () => {
    // Given
    vi.mocked(commands.getAbout).mockResolvedValue({ version: "1.2.3" });
    vi.mocked(commands.getContentText).mockResolvedValue({ status: "ok", data: [] });
    // When
    render(<App locales={["en"]} queryClient={testQueryClient()} />);
    // Then
    expect(await screen.findByRole("heading", { name: "eSports Manager" })).toBeInTheDocument();
    expect(await screen.findByTestId("version")).toHaveTextContent("v1.2.3");
    expect(screen.getByRole("link", { name: "New Game" })).toHaveAttribute("href", "/new");
    expect(screen.getByRole("link", { name: "Load Game" })).toHaveAttribute("href", "/load");
    expect(screen.getByRole("button", { name: "Quit" })).toBeInTheDocument();
  });
});
