// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import type { RosterPlayer } from "../bindings";
import { renderWithProviders } from "../test/render";
import { Crest } from "./Crest";
import { NationalityBadge } from "./NationalityBadge";
import { usePersonName } from "./PersonName";
import { StrengthStars } from "./StrengthStars";

function player(given: string, family: string, nameOrder: RosterPlayer["nameOrder"]): RosterPlayer {
  return {
    id: "player:x",
    nickname: "X",
    givenName: given,
    familyName: family,
    nameOrder,
    roleId: "role:mid",
    roleMessage: "role-mid",
    nationality: { id: "nationality:kr", code: "KR", nameMessage: "nationality-kr" },
    age: 20,
    overall: 70,
  };
}

function Name({ of }: { of: RosterPlayer }) {
  const name = usePersonName();
  return <span>{name(of)}</span>;
}

describe("PersonName", () => {
  it("follows the nationality's name order", () => {
    // spec: ROST-003
    // Given a Korean player Han Do-yun and a Brazilian player Caio Ribeiro
    const korean = player("Do-yun", "Han", "family-first");
    const brazilian = player("Caio", "Ribeiro", "given-first");
    // When their full names are shown
    renderWithProviders(
      <>
        <Name of={korean} />
        <Name of={brazilian} />
      </>,
    );
    // Then they read family-first and given-first
    expect(screen.getByText("Han Do-yun")).toBeInTheDocument();
    expect(screen.getByText("Caio Ribeiro")).toBeInTheDocument();
  });
});

describe("Crest", () => {
  it("draws the tag in the colours Rust chose", () => {
    renderWithProviders(
      <Crest crest={{ tag: "AZT", fill: "#1E5AA8", border: "#F2C14E", text: "#FFFFFF" }} />,
    );
    const crest = screen.getByText("AZT");
    expect(crest).toHaveStyle({
      backgroundColor: "#1E5AA8",
      borderColor: "#F2C14E",
      color: "#FFFFFF",
    });
    expect(crest).toHaveAttribute("aria-hidden", "true");
  });
});

describe("StrengthStars", () => {
  it("shows stars and says how many", () => {
    renderWithProviders(<StrengthStars stars={4} />, { locale: "pt-BR" });
    const stars = screen.getByRole("img", { name: "4 de 5 estrelas" });
    expect(stars).toHaveTextContent("★★★★☆");
  });
});

describe("NationalityBadge", () => {
  it("shows the code and names the country", () => {
    renderWithProviders(
      <NationalityBadge
        nationality={{ id: "nationality:kr", code: "KR", nameMessage: "app-title" }}
      />,
    );
    expect(screen.getByText("KR")).toHaveAttribute("title", "eSports Manager");
  });
});
