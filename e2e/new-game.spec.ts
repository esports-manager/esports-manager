// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { expect, test } from "@playwright/test";
import { expectNoHorizontalScroll, expectNoViolations, startGame, tabTo } from "./support";

test("the main menu shows the game and its version", async ({ page }) => {
  // Given the game is running
  // When the user opens it
  await page.goto("/");
  // Then the shell, the backend's version and the menu are shown
  await expect(page.getByRole("heading", { name: "eSports Manager" })).toBeVisible();
  await expect(page.getByTestId("version")).toHaveText("v0.0.0-e2e");
  await expect(page.getByRole("link", { name: "New Game" })).toBeVisible();
});

test("the wizard ends on the roster", async ({ page }) => {
  // spec: NEWG-008
  // Given the main menu
  // When the user enters a manager name, picks a team and starts
  await startGame(page);
  // Then the roster of that team is shown
  await expect(page.getByText("Seorabeol Pro League")).toBeVisible();
  await expect(
    page.getByRole("link", { name: "Kairos, view profile" }).locator("visible=true"),
  ).toBeVisible();
});

test("the wizard works with the keyboard alone", async ({ page }) => {
  // spec: NEWG-009
  // Given the main menu
  await page.goto("/");
  await expect(page.getByTestId("version")).toBeVisible();
  // When the user completes New Game with Tab, the arrow keys, Space and Enter
  await tabTo(page, page.getByRole("link", { name: "New Game" }));
  await page.keyboard.press("Enter");
  await tabTo(page, page.getByLabel("Manager name"));
  await page.keyboard.type("Ana");
  await page.keyboard.press("Enter");
  // The step's heading takes focus; the region tabs are one Tab stop.
  await expect(page.getByRole("heading", { name: "Choose your team" })).toBeFocused();
  const pindorama = page.getByRole("tab", { name: "Liga Pindorama" });
  await tabTo(page, pindorama);
  await page.keyboard.press("ArrowRight");
  const seorabeol = page.getByRole("tab", { name: "Seorabeol Pro League" });
  await expect(seorabeol).toBeFocused();
  await expect(seorabeol).toHaveAttribute("aria-selected", "true");
  // Tab into the team group, then move through it with the arrow keys.
  await page.keyboard.press("Tab");
  await page.keyboard.press("ArrowRight");
  await page.keyboard.press("ArrowLeft");
  await page.keyboard.press("Space");
  await expect(page.getByRole("radio", { name: /Azure Tigers/ })).toBeChecked();
  await tabTo(page, page.getByRole("button", { name: "Next" }));
  await page.keyboard.press("Enter");
  await expect(page.getByRole("heading", { name: "Name your save" })).toBeFocused();
  await tabTo(page, page.getByLabel("Save name"));
  await page.keyboard.press("Enter");
  // Then the roster is shown
  await expect(page.getByRole("heading", { name: "Azure Tigers" })).toBeVisible();
});

test("Enter picks a team card", async ({ page }) => {
  await page.goto("/new");
  await page.getByLabel("Manager name").fill("Ana");
  await page.getByRole("button", { name: "Next" }).click();
  await page.getByRole("radio", { name: /Capivara Club/ }).focus();
  await page.keyboard.press("Enter");
  await expect(page.getByRole("radio", { name: /Capivara Club/ })).toBeChecked();
});

test("the chosen team stays in view after switching region", async ({ page }) => {
  await page.goto("/new");
  await page.getByLabel("Manager name").fill("Ana");
  await page.getByRole("button", { name: "Next" }).click();
  await page.getByRole("tab", { name: "Seorabeol Pro League" }).click();
  await page.getByText("Azure Tigers").click();
  await page.getByRole("tab", { name: "Liga Pindorama" }).click();
  await expect(page.getByText("Team: Azure Tigers")).toBeVisible();
  await page.getByRole("button", { name: "Next" }).click();
  await expect(page.getByText("Team: Azure Tigers")).toBeVisible();
});

test("going back keeps what was typed", async ({ page }) => {
  // spec: NEWG-010
  // Given the wizard on step 2, with manager name "Ana"
  await page.goto("/new");
  await page.getByLabel("Manager name").fill("Ana");
  await page.getByRole("button", { name: "Next" }).click();
  await expect(page.getByText("Step 2 of 3")).toBeVisible();
  // When the user goes back to step 1
  await page.getByRole("button", { name: "Back" }).click();
  // Then the manager name still holds "Ana"
  await expect(page.getByLabel("Manager name")).toHaveValue("Ana");
});

test("the save name defaults to the team's name, and the game opens on that team", async ({
  page,
}) => {
  await page.goto("/new");
  await page.getByLabel("Manager name").fill("Ana");
  await page.getByRole("button", { name: "Next" }).click();
  await page.getByRole("tab", { name: "Liga Pindorama" }).click();
  await page.getByText("Onça Gaming").click();
  await page.getByRole("button", { name: "Next" }).click();
  await expect(page.getByLabel("Save name")).toHaveValue("Onça Gaming");
  await page.getByRole("button", { name: "Start" }).click();
  await expect(page.getByRole("heading", { name: "Onça Gaming" })).toBeVisible();
});

test("problems from the backend are shown on the last step", async ({ page }) => {
  await page.goto("/new");
  await page.getByRole("button", { name: "Next" }).click();
  await page.getByRole("tab", { name: "Seorabeol Pro League" }).click();
  await page.getByText("Azure Tigers").click();
  await page.getByRole("button", { name: "Next" }).click();
  await page.getByRole("button", { name: "Start" }).click();
  await expect(page.getByRole("alert")).toContainText("Enter a manager name.");
});

test.describe("with a broken package", () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      window.__ESM_E2E__ = { brokenPackage: true };
    });
  });

  test("a broken package shows its report", async ({ page }) => {
    // spec: NEWG-007
    // Given a core package with a validation error
    // When a new game is started in the UI
    await page.goto("/new");
    // Then the report is shown with the error's file and path
    const alert = page.getByRole("alert");
    await expect(alert).toContainText("teams/seorabeol/azure_tigers.json");
    await expect(alert).toContainText('unknown field "reputaton"');
  });
});

test.describe("with saves", () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      window.__ESM_E2E__ = { saves: true };
    });
  });

  test("Load Game opens a save on its roster", async ({ page }) => {
    // spec: NEWG-011
    // Given two saves in the data folder, for different teams
    await page.goto("/");
    // When the user opens Load Game and picks the one listed second
    await page.getByRole("link", { name: "Load Game" }).click();
    const rows = page.getByRole("listitem").getByRole("button");
    await expect(rows).toHaveCount(2);
    await expect(rows.first()).toContainText("Ana's Tigers");
    await rows.nth(1).click();
    // Then the roster of that save's team is shown
    await expect(page.getByRole("heading", { name: "Onça Gaming" })).toBeVisible();
  });

  test("a save name already taken is reported", async ({ page }) => {
    await page.goto("/new");
    await page.getByLabel("Manager name").fill("Ana");
    await page.getByRole("button", { name: "Next" }).click();
    await page.getByRole("tab", { name: "Seorabeol Pro League" }).click();
    await page.getByText("Azure Tigers").click();
    await page.getByRole("button", { name: "Next" }).click();
    await page.getByLabel("Save name").fill("ana's tigers");
    await page.getByRole("button", { name: "Start" }).click();
    await expect(page.getByRole("alert")).toContainText(
      'A save named "ana\'s tigers" already exists.',
    );
  });

  test("an opened save moves to the top of the list", async ({ page }) => {
    await page.goto("/load");
    await page.getByRole("button", { name: /Bia's Onça/ }).click();
    await expect(page.getByRole("heading", { name: "Onça Gaming" })).toBeVisible();
    // Back through the app: reloading the page would reset the stand-in backend.
    await page.getByRole("link", { name: "Back" }).click();
    await page.getByRole("link", { name: "Load Game" }).click();
    await expect(page.getByRole("listitem").getByRole("button").first()).toContainText(
      "Bia's Onça",
    );
  });

  test("Load Game passes the accessibility audit", async ({ page }) => {
    // spec: NEWG-013
    await page.goto("/load");
    await expect(page.getByRole("button", { name: /Ana's Tigers/ })).toBeVisible();
    await expectNoViolations(page);
    await expectNoHorizontalScroll(page);
  });
});

test("the menu and every New Game step pass the accessibility audit", async ({ page }) => {
  // spec: NEWG-013
  // Given the main menu and each New Game step
  await page.goto("/");
  await expect(page.getByTestId("version")).toBeVisible();
  // When each is shown, in this project's layout
  // Then axe reports nothing and the page doesn't scroll sideways
  await expectNoViolations(page);
  await expectNoHorizontalScroll(page);
  await page.getByRole("link", { name: "New Game" }).click();
  await page.getByLabel("Manager name").fill("Ana");
  await expectNoViolations(page);
  await page.getByRole("button", { name: "Next" }).click();
  await page.getByText("Onça Gaming").click();
  await expectNoViolations(page);
  await expectNoHorizontalScroll(page);
  await page.getByRole("button", { name: "Next" }).click();
  await expectNoViolations(page);
  await page.goto("/load");
  await expect(page.getByText("No saves yet.")).toBeVisible();
  await expectNoViolations(page);
});

test.describe("for a Brazilian Portuguese user", () => {
  test.use({ locale: "pt-BR" });

  test("the document language follows the user's locale", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("html")).toHaveAttribute("lang", "pt-BR");
    await expect(page.getByRole("link", { name: "Novo Jogo" })).toBeVisible();
  });
});
