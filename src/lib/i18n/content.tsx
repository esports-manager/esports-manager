// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Text whose message id comes from the backend (ADR 0007): DTO fields ending
 * in `Message`, and the `Message` values use cases return. This is the only
 * place a message id is not a literal; the i18n gate exempts this file and
 * nothing else.
 */
import { type ReactLocalization, useLocalization } from "@fluent/react";
import type { Message } from "../../bindings";

/** A backend message, with its arguments; `message` arguments are resolved first. */
export function renderMessage(l10n: ReactLocalization, message: Message): string {
  const args: Record<string, string | number> = {};
  for (const { name, value } of message.args) {
    args[name] = value.kind === "message" ? l10n.getString(value.value) : value.value;
  }
  return l10n.getString(message.id, args);
}

/** The text of a message id from a DTO, such as a team's `nameMessage`. */
export function messageText(l10n: ReactLocalization, id: string): string {
  return l10n.getString(id);
}

/** Renders a DTO message id, such as a team's or a role's name. */
export function ContentText({ id }: { id: string }) {
  const { l10n } = useLocalization();
  return <>{messageText(l10n, id)}</>;
}

/** Renders a message a use case returned, such as an error. */
export function MessageText({ message }: { message: Message }) {
  const { l10n } = useLocalization();
  return <>{renderMessage(l10n, message)}</>;
}
