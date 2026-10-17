// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { defineConfig, devices } from "@playwright/test";

const port = 1421;

/**
 * Browser E2E tests against the Vite build with a mocked backend
 * (src/test/e2e-ipc.ts). Every test runs at a desktop and a compact
 * (phone) size, because every screen has both layouts (ADR 0006).
 */
export default defineConfig({
  testDir: "e2e",
  forbidOnly: Boolean(process.env.CI),
  reporter: process.env.CI ? [["github"], ["html", { open: "never" }]] : "list",
  use: { baseURL: `http://localhost:${port}`, trace: "retain-on-failure" },
  webServer: {
    command: `pnpm exec vite --mode e2e --port ${port} --strictPort`,
    url: `http://localhost:${port}`,
    reuseExistingServer: !process.env.CI,
  },
  projects: [
    {
      name: "desktop",
      use: { ...devices["Desktop Chrome"], viewport: { width: 1440, height: 900 } },
    },
    { name: "compact", use: { ...devices["Pixel 7"] } },
  ],
});
