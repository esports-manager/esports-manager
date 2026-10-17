// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import type { Crest as CrestView } from "../bindings";

/**
 * A team's procedural crest: its tag on its first colour, bordered in its
 * second (ADR 0010). The text colour comes from Rust, which picks it for
 * contrast; the tag is the team's name to assistive technology elsewhere, so
 * the crest itself is decorative.
 */
export function Crest({ crest, size = "md" }: { crest: CrestView; size?: "sm" | "md" }) {
  const dimensions = size === "sm" ? "h-8 w-8 text-[0.6rem]" : "h-12 w-12 text-xs";
  return (
    <span
      aria-hidden="true"
      className={`inline-flex shrink-0 items-center justify-center rounded-full border-2 font-bold tracking-wide ${dimensions}`}
      style={{ backgroundColor: crest.fill, borderColor: crest.border, color: crest.text }}
    >
      {crest.tag}
    </span>
  );
}
