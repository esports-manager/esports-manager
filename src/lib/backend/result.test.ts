// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { describe, expect, it } from "vitest";
import type { Failure } from "../../bindings";
import { BackendFailure, failureMessages, unwrap } from "./result";

const failure: Failure = { messages: [{ id: "error-save-in-use", args: [] }] };

describe("unwrap", () => {
  it("returns the data of an ok result", async () => {
    await expect(unwrap(Promise.resolve({ status: "ok" as const, data: 42 }))).resolves.toBe(42);
  });

  it("throws the messages of an error result", async () => {
    const result = unwrap(Promise.resolve({ status: "error" as const, error: failure }));
    await expect(result).rejects.toBeInstanceOf(BackendFailure);
    await expect(result).rejects.toThrow("error-save-in-use");
  });
});

describe("failureMessages", () => {
  it("gives a backend failure's messages, and nothing for other errors", () => {
    expect(failureMessages(new BackendFailure(failure))).toEqual(failure.messages);
    expect(failureMessages(new Error("boom"))).toEqual([]);
    expect(new BackendFailure(failure).name).toBe("BackendFailure");
  });
});
