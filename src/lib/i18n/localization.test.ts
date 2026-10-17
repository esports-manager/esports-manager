// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { describe, expect, it } from "vitest";
import { SUPPORTED_LOCALES } from "./locales";
import { createBundle, createLocalization } from "./localization";

describe("createBundle", () => {
  it.each(SUPPORTED_LOCALES)("loads the %s catalog", (locale) => {
    const bundle = createBundle(locale);
    expect(bundle.hasMessage("app-title")).toBe(true);
  });
});

describe("createLocalization", () => {
  it("formats messages with arguments in the preferred locale", () => {
    const l10n = createLocalization(["pt-BR"]);
    expect(l10n.getString("app-loading")).toBe("Carregando…");
    expect(l10n.getString("app-version", { version: "1.2.3" })).toBe("v1.2.3");
  });

  it("resolves terms inside messages", () => {
    expect(createLocalization(["en"]).getString("app-title")).toBe("eSports Manager");
  });

  it("falls back to English for unsupported locales", () => {
    expect(createLocalization(["ja"]).getString("app-loading")).toBe("Loading…");
  });
});

describe("package text", () => {
  it("joins the game's catalogs, in its own locale only", () => {
    const content = [
      { locale: "en", file: "locales/en/a.ftl", source: "team-a = Azure Tigers\n" },
      { locale: "pt-BR", file: "locales/pt-BR/a.ftl", source: "team-a = Tigres Azuis\n" },
    ];
    expect(createLocalization(["pt-BR"], content).getString("team-a")).toBe("Tigres Azuis");
    expect(createLocalization(["en"], content).getString("team-a")).toBe("Azure Tigers");
  });

  it("can't override the game's own messages", () => {
    const content = [{ locale: "en", file: "x.ftl", source: "app-loading = Hacked\n" }];
    expect(createLocalization(["en"], content).getString("app-loading")).toBe("Loading…");
  });
});
