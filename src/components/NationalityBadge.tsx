// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { useLocalization } from "@fluent/react";
import type { NationalityView } from "../bindings";
import { messageText } from "../lib/i18n/content";

/** The country code as a badge; its accessible name is the country's name. */
export function NationalityBadge({ nationality }: { nationality: NationalityView }) {
  const { l10n } = useLocalization();
  return (
    <abbr
      title={messageText(l10n, nationality.nameMessage)}
      className="rounded-sm border border-border px-1.5 py-0.5 font-mono text-muted text-xs no-underline"
    >
      {nationality.code}
    </abbr>
  );
}
