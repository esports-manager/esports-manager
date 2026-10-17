// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Dates as the UI's language writes them. The backend sends a calendar date
 * (`2027-01-01`, no time zone) or a moment (seconds since the Unix epoch);
 * the frontend formats them and never computes with them.
 */

/** The UI's language, which `main.tsx` puts on the document. */
function uiLocale(): string | undefined {
  return document.documentElement.lang || undefined;
}

/** A calendar date, read in UTC so no time zone moves it a day. */
export function formatCalendarDate(date: string, style: "medium" | "long" = "medium"): string {
  return new Intl.DateTimeFormat(uiLocale(), { dateStyle: style, timeZone: "UTC" }).format(
    new Date(`${date}T00:00:00Z`),
  );
}

/** A moment, in the user's own time zone. */
export function formatMoment(seconds: number): string {
  return new Intl.DateTimeFormat(uiLocale(), { dateStyle: "medium", timeStyle: "short" }).format(
    new Date(seconds * 1000),
  );
}
