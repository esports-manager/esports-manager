// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";
import { commands } from "../bindings";
import { testQueryClient } from "../test/render";
import { useAbout } from "./useAbout";

vi.mock("../bindings", () => ({ commands: { getAbout: vi.fn() } }));

describe("useAbout", () => {
  it("returns what the backend reports", async () => {
    // Given
    vi.mocked(commands.getAbout).mockResolvedValue({ version: "0.4.0" });
    const client = testQueryClient();
    const wrapper = ({ children }: { children: ReactNode }) => (
      <QueryClientProvider client={client}>{children}</QueryClientProvider>
    );
    // When
    const { result } = renderHook(() => useAbout(), { wrapper });
    // Then
    await waitFor(() => expect(result.current.data).toEqual({ version: "0.4.0" }));
    expect(commands.getAbout).toHaveBeenCalledTimes(1);
  });
});
