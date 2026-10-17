// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import type { Failure, Message } from "../../bindings";

/** A use case failed; its messages say why (ADR 0007). */
export class BackendFailure extends Error {
  readonly messages: Message[];

  constructor(failure: Failure) {
    super(failure.messages.map((message) => message.id).join(", "));
    this.name = "BackendFailure";
    this.messages = failure.messages;
  }
}

type Result<T> = { status: "ok"; data: T } | { status: "error"; error: Failure };

/** The data of a command's result, or a thrown `BackendFailure` for TanStack Query. */
export async function unwrap<T>(result: Promise<Result<T>>): Promise<T> {
  const settled = await result;
  if (settled.status === "error") {
    throw new BackendFailure(settled.error);
  }
  return settled.data;
}

/** The messages of an error, if it came from the backend. */
export function failureMessages(error: unknown): Message[] {
  return error instanceof BackendFailure ? error.messages : [];
}
