// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { useLocalization } from "@fluent/react";
import type { RosterPlayer } from "../bindings";

/** A player's full name, in their nationality's name order (roster spec). */
export function usePersonName(): (player: RosterPlayer) => string {
  const { l10n } = useLocalization();
  return (player) =>
    l10n.getString("person-full-name", {
      order: player.nameOrder,
      given: player.givenName,
      family: player.familyName,
    });
}
