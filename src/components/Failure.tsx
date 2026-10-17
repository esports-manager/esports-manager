// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import type { Message } from "../bindings";
import { MessageText } from "../lib/i18n/content";

/** What went wrong, as the backend's messages, under a heading message. */
export function FailureList({ heading, messages }: { heading: string; messages: Message[] }) {
  return (
    <div role="alert" className="rounded-md border border-negative p-3">
      <p className="font-semibold text-negative">{heading}</p>
      <ul className="mt-2 list-disc pl-5 text-primary text-sm">
        {messages.map((message, index) => (
          // Messages have no identity of their own; their order is stable.
          // biome-ignore lint/suspicious/noArrayIndexKey: see above
          <li key={index}>
            <MessageText message={message} />
          </li>
        ))}
      </ul>
    </div>
  );
}
