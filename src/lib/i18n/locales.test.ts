// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { describe, expect, it } from "vitest";
import { DEFAULT_LOCALE, negotiateLocales, SUPPORTED_LOCALES } from "./locales";

describe("negotiateLocales", () => {
  it("prefers an exact match and falls back to English", () => {
    expect(negotiateLocales(["pt-BR"])).toEqual(["pt-BR", "en"]);
  });

  it("matches a language without a region to the regional locale", () => {
    expect(negotiateLocales(["pt"])).toEqual(["pt-BR", "en"]);
  });

  it("uses English alone when English is the best match", () => {
    expect(negotiateLocales(["en-GB", "pt-BR"])).toEqual(["en", "pt-BR"]);
  });

  it("uses English when nothing requested is supported", () => {
    expect(negotiateLocales(["ja-JP"])).toEqual(["en"]);
  });

  it("uses English when nothing is requested", () => {
    expect(negotiateLocales([])).toEqual(["en"]);
  });

  it("ships English as the default", () => {
    expect(SUPPORTED_LOCALES).toContain(DEFAULT_LOCALE);
    expect(DEFAULT_LOCALE).toBe("en");
  });
});
