// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { afterEach, describe, expect, it } from "vitest";
import { formatCalendarDate, formatMoment } from "./dates";

describe("dates", () => {
  afterEach(() => {
    document.documentElement.lang = "";
  });

  it("formats a calendar date in the document's language, whatever the time zone", () => {
    document.documentElement.lang = "en";
    expect(formatCalendarDate("2027-01-01")).toBe("Jan 1, 2027");
    expect(formatCalendarDate("1997-03-14", "long")).toBe("March 14, 1997");
    document.documentElement.lang = "pt-BR";
    expect(formatCalendarDate("2027-01-01", "long")).toBe("1 de janeiro de 2027");
  });

  it("formats a moment with its time", () => {
    document.documentElement.lang = "en";
    const expected = new Intl.DateTimeFormat("en", {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(new Date(1_792_000_000_000));
    expect(formatMoment(1_792_000_000)).toBe(expected);
  });
});
