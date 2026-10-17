// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import "./styles/index.css";
import { QueryClient } from "@tanstack/react-query";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";
import { DEFAULT_LOCALE, negotiateLocales } from "./lib/i18n/locales";

async function start(root: HTMLElement): Promise<void> {
  if (import.meta.env.MODE === "e2e") {
    // Browser-only E2E runs have no Tauri backend; this branch is removed
    // from normal builds.
    const { installIpcMocks } = await import("./test/e2e-ipc");
    installIpcMocks();
  }

  // The backend is in the same process: a failure won't fix itself by
  // retrying, and the user should see it at once.
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  const locales = negotiateLocales(navigator.languages);
  document.documentElement.lang = locales[0] ?? DEFAULT_LOCALE;

  createRoot(root).render(
    <StrictMode>
      <App locales={locales} queryClient={queryClient} />
    </StrictMode>,
  );
}

const root = document.getElementById("root");
if (root === null) {
  throw new Error("index.html is missing the #root element");
}
void start(root);
