// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { useLocalization } from "@fluent/react";
import { Outlet } from "@tanstack/react-router";

/** The frame around every screen. Navigation arrives with the first screens. */
export function Shell() {
  const { l10n } = useLocalization();
  return (
    <div className="min-h-screen bg-surface-base text-primary">
      <header className="border-b border-border bg-surface-raised px-4 py-3">
        <h1 className="font-semibold text-lg">{l10n.getString("app-title")}</h1>
      </header>
      <main className="p-4">
        <Outlet />
      </main>
    </div>
  );
}
