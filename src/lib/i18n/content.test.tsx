// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { LocalizationProvider } from "@fluent/react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import type { Message, ContentText as Text } from "../../bindings";
import { ContentText, MessageText, messageText, renderMessage } from "./content";
import { createLocalization } from "./localization";

const teams: Text[] = [
  { locale: "en", file: "locales/en/teams.ftl", source: "team-a = Azure Tigers\n" },
  { locale: "pt-BR", file: "locales/pt-BR/teams.ftl", source: "team-b = Equipe B\n" },
];

describe("renderMessage", () => {
  it("passes text, number and message arguments", () => {
    const l10n = createLocalization(["en"], teams);
    const message: Message = {
      id: "cli-team",
      args: [
        { name: "tag", value: { kind: "text", value: "AZT" } },
        { name: "name", value: { kind: "message", value: "team-a" } },
        { name: "stars", value: { kind: "number", value: 5 } },
        { name: "id", value: { kind: "text", value: "team:a" } },
      ],
    };
    expect(renderMessage(l10n, message)).toBe("AZT  Azure Tigers  5/5  team:a");
  });

  it("falls back to English for package names a locale lacks", () => {
    // spec: PKG-011
    // Given a team named in en only
    const l10n = createLocalization(["pt-BR"], teams);
    // When it is shown in pt-BR
    // Then the English name is shown
    expect(messageText(l10n, "team-a")).toBe("Azure Tigers");
    expect(messageText(l10n, "team-b")).toBe("Equipe B");
  });
});

describe("the components", () => {
  it("render backend message ids and messages", () => {
    const l10n = createLocalization(["en"], teams);
    render(
      <LocalizationProvider l10n={l10n}>
        <span>
          <ContentText id="team-a" />
        </span>
        <span>
          <MessageText message={{ id: "error-save-newer", args: [] }} />
        </span>
      </LocalizationProvider>,
    );
    expect(screen.getByText("Azure Tigers")).toBeInTheDocument();
    expect(
      screen.getByText("This save was made by a newer version of the game."),
    ).toBeInTheDocument();
  });
});
