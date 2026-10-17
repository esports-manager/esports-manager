// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { LocalizationProvider } from "@fluent/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { type RenderOptions, render } from "@testing-library/react";
import type { ReactElement, ReactNode } from "react";
import { createLocalization } from "../lib/i18n/localization";

/** A query client that fails fast instead of retrying, for tests. */
export function testQueryClient(): QueryClient {
  return new QueryClient({ defaultOptions: { queries: { retry: false } } });
}

/** Renders `ui` inside the app's providers, in the given locale. */
export function renderWithProviders(
  ui: ReactElement,
  { locale = "en", ...options }: RenderOptions & { locale?: string } = {},
) {
  const client = testQueryClient();
  const wrapper = ({ children }: { children: ReactNode }) => (
    <LocalizationProvider l10n={createLocalization([locale])}>
      <QueryClientProvider client={client}>{children}</QueryClientProvider>
    </LocalizationProvider>
  );
  return render(ui, { wrapper, ...options });
}
