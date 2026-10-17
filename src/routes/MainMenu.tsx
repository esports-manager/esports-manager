// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { Localized } from "@fluent/react";
import { Link } from "@tanstack/react-router";
import { primaryButton, secondaryButton } from "../components/styles";
import { useQuit } from "../hooks/game";
import { useAbout } from "../hooks/useAbout";

/** The front door: New Game, Load Game, Quit (new game spec). */
export function MainMenu() {
  const about = useAbout();
  const quit = useQuit();
  return (
    <section className="mx-auto flex max-w-sm flex-col items-stretch gap-3 pt-8 text-center">
      {about.isError ? (
        <Localized id="app-backend-error">
          <p role="alert" className="text-negative" />
        </Localized>
      ) : about.isSuccess ? (
        <Localized id="app-version" vars={{ version: about.data.version }}>
          <p data-testid="version" className="text-muted" />
        </Localized>
      ) : (
        <Localized id="app-loading">
          <p className="text-muted" />
        </Localized>
      )}
      <nav className="mt-6 flex flex-col gap-3">
        <Localized id="menu-new-game">
          <Link to="/new" className={primaryButton} />
        </Localized>
        <Localized id="menu-load-game">
          <Link to="/load" className={secondaryButton} />
        </Localized>
        <Localized id="menu-quit">
          <button type="button" className={secondaryButton} onClick={() => quit.mutate()} />
        </Localized>
      </nav>
    </section>
  );
}
