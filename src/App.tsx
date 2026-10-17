// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { LocalizationProvider } from "@fluent/react";
import { type QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { RouterProvider } from "@tanstack/react-router";
import { type ReactNode, useMemo } from "react";
import { useContentText } from "./hooks/game";
import { createLocalization } from "./lib/i18n/localization";
import { router } from "./router";

interface AppProps {
  /** The user's preferred languages, best first. */
  locales: readonly string[];
  queryClient: QueryClient;
}

/**
 * The game's catalogs plus the package text of the open save (team, region
 * and role names). Until that text arrives, the game's own catalogs serve.
 */
function Localization({ locales, children }: { locales: readonly string[]; children: ReactNode }) {
  const content = useContentText();
  const l10n = useMemo(
    () => createLocalization(locales, content.data ?? []),
    [locales, content.data],
  );
  return <LocalizationProvider l10n={l10n}>{children}</LocalizationProvider>;
}

export function App({ locales, queryClient }: AppProps) {
  return (
    <QueryClientProvider client={queryClient}>
      <Localization locales={locales}>
        <RouterProvider router={router} />
      </Localization>
    </QueryClientProvider>
  );
}
