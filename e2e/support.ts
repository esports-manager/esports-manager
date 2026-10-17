// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import AxeBuilder from "@axe-core/playwright";
import { expect, type Locator, type Page } from "@playwright/test";

/** Starts a game through the UI: Ana, Azure Tigers, the default save name. */
export async function startGame(page: Page): Promise<void> {
  await page.goto("/");
  await page.getByRole("link", { name: "New Game" }).click();
  await page.getByLabel("Manager name").fill("Ana");
  await page.getByRole("button", { name: "Next" }).click();
  await page.getByRole("tab", { name: "Seorabeol Pro League" }).click();
  await page.getByText("Azure Tigers").click();
  await page.getByRole("button", { name: "Next" }).click();
  await page.getByRole("button", { name: "Start" }).click();
  await expect(page.getByRole("heading", { name: "Azure Tigers" })).toBeVisible();
}

/** axe finds nothing on the page as it is now. */
export async function expectNoViolations(page: Page): Promise<void> {
  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations).toEqual([]);
}

/** The page fits its viewport: nothing scrolls sideways. */
export async function expectNoHorizontalScroll(page: Page): Promise<void> {
  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
  );
  expect(overflow).toBeLessThanOrEqual(0);
}

/**
 * Presses Tab until `target` has focus, as a keyboard user would. Fails if
 * it isn't reached within `limit` presses, so the test proves it is in the
 * Tab order and not just focusable.
 */
export async function tabTo(page: Page, target: Locator, limit = 15): Promise<void> {
  for (let presses = 0; presses < limit; presses++) {
    await page.keyboard.press("Tab");
    if (await target.evaluate((element) => element === document.activeElement)) {
      return;
    }
  }
  throw new Error(`Tab didn't reach ${target} in ${limit} presses`);
}
