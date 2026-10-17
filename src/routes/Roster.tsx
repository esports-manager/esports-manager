// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { Localized, useLocalization } from "@fluent/react";
import { Link, useNavigate } from "@tanstack/react-router";
import type { RosterPlayer, TeamHeader as TeamHeaderView } from "../bindings";
import { Crest } from "../components/Crest";
import { FailureList } from "../components/Failure";
import { NationalityBadge } from "../components/NationalityBadge";
import { usePersonName } from "../components/PersonName";
import { backLink } from "../components/styles";
import { useRoster } from "../hooks/game";
import { failureMessages } from "../lib/backend/result";
import { ContentText } from "../lib/i18n/content";
import {
  DEFAULT_SORT,
  nextSort,
  type RosterSort,
  type SortKey,
  type SortSearch,
  sortPlayers,
  sortSearch,
} from "./rosterSort";

/** The team's name and league, under its crest. */
function TeamHeader({ team }: { team: TeamHeaderView }) {
  return (
    <div className="flex items-center gap-3">
      <Crest crest={team.crest} />
      <div className="flex flex-col">
        <h2 className="font-semibold text-xl">
          <ContentText id={team.nameMessage} />
        </h2>
        <p className="text-muted">
          <ContentText id={team.leagueMessage ?? team.regionMessage} />
        </p>
      </div>
    </div>
  );
}

interface RosterProps {
  team?: string | undefined;
  sort?: RosterSort;
}

/**
 * The roster: starters, then subs, as a table on wide screens and cards on
 * narrow ones. Column headers re-sort both groups; the sort is in the URL, so
 * a profile's Back link keeps it.
 */
export function Roster({ team, sort = DEFAULT_SORT }: RosterProps) {
  const { l10n } = useLocalization();
  const roster = useRoster(team);
  const back = (
    <Localized id="nav-back">
      <Link to="/" className={backLink} />
    </Localized>
  );
  if (roster.isError) {
    return (
      <section className="mx-auto flex max-w-5xl flex-col gap-4">
        {back}
        <FailureList
          heading={l10n.getString("app-backend-error")}
          messages={failureMessages(roster.error)}
        />
      </section>
    );
  }
  if (!roster.isSuccess) {
    return (
      <section className="mx-auto flex max-w-5xl flex-col gap-4">
        {back}
        <Localized id="app-loading">
          <p className="text-muted" />
        </Localized>
      </section>
    );
  }
  const view = roster.data;
  return (
    <section className="mx-auto flex max-w-5xl flex-col gap-4">
      {back}
      <TeamHeader team={view.team} />
      <PlayerGroup
        title={l10n.getString("roster-starters")}
        players={view.starters}
        team={team}
        sort={sort}
      />
      <PlayerGroup
        title={l10n.getString("roster-subs")}
        players={view.subs}
        team={team}
        sort={sort}
      />
    </section>
  );
}

interface PlayerGroupProps {
  title: string;
  players: RosterPlayer[];
  team: string | undefined;
  sort: RosterSort;
}

function PlayerGroup({ title, players, team, sort }: PlayerGroupProps) {
  const { l10n } = useLocalization();
  const name = usePersonName();
  const columns: { key: SortKey; label: string; numeric: boolean }[] = [
    { key: "role", label: l10n.getString("roster-column-role"), numeric: false },
    { key: "nickname", label: l10n.getString("roster-column-nickname"), numeric: false },
    { key: "name", label: l10n.getString("roster-column-name"), numeric: false },
    { key: "nationality", label: l10n.getString("roster-column-nationality"), numeric: false },
    { key: "age", label: l10n.getString("roster-column-age"), numeric: true },
    { key: "overall", label: l10n.getString("roster-column-overall"), numeric: true },
  ];
  const navigate = useNavigate();
  const sorted = sortPlayers(players, sort, name, new Intl.Collator(document.documentElement.lang));
  const teamSearch = team === undefined ? {} : { team };
  const profile = (player: RosterPlayer): ProfileSearch => ({
    id: player.id,
    ...teamSearch,
    ...sortSearch(sort),
  });
  return (
    <div className="flex flex-col gap-2">
      <h3 className="font-semibold text-lg">{title}</h3>
      <table className="hidden w-full border-collapse text-left sm:table">
        <caption className="sr-only">{title}</caption>
        <thead className="text-muted text-sm">
          <tr>
            {columns.map((column) => (
              <th
                key={column.key}
                scope="col"
                aria-sort={sort.key === column.key ? sort.order : undefined}
                className={`py-1 font-normal ${column.numeric ? "text-right" : ""}`}
              >
                <button
                  type="button"
                  onClick={() =>
                    navigate({
                      to: "/roster",
                      search: { ...teamSearch, ...sortSearch(nextSort(sort, column.key)) },
                      replace: true,
                    })
                  }
                  className="inline-flex min-h-11 items-center underline-offset-4 hover:underline focus-visible:outline-2 focus-visible:outline-accent-text"
                >
                  {column.label}
                </button>
                {/* Every header shows it sorts, not only on hover. */}
                <span aria-hidden="true">
                  {sort.key !== column.key ? " ↕" : sort.order === "ascending" ? " ▲" : " ▼"}
                </span>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sorted.map((player) => (
            <tr
              key={player.id}
              // The nickname is the row's link for the keyboard; a click
              // anywhere else on the row opens the same profile.
              onClick={(event) => {
                if (!(event.target as Element).closest("a")) {
                  void navigate({ to: "/player", search: profile(player) });
                }
              }}
              className="cursor-pointer border-border border-t hover:bg-surface-panel"
            >
              <td className="py-2">
                <ContentText id={player.roleMessage} />
              </td>
              <td className="py-2">
                <PlayerLink player={player} search={profile(player)} />
              </td>
              <td className="py-2">{name(player)}</td>
              <td className="py-2">
                <NationalityBadge nationality={player.nationality} />
              </td>
              <td className="py-2 text-right tabular-nums">{player.age}</td>
              <td className="py-2 text-right font-semibold tabular-nums">{player.overall}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <ul className="flex flex-col gap-2 sm:hidden">
        {sorted.map((player) => (
          <li key={player.id}>
            <PlayerCard player={player} search={profile(player)} name={name(player)} />
          </li>
        ))}
      </ul>
    </div>
  );
}

type ProfileSearch = { id: string; team?: string } & SortSearch;

function PlayerLink({ player, search }: { player: RosterPlayer; search: ProfileSearch }) {
  const { l10n } = useLocalization();
  return (
    <Link
      to="/player"
      search={search}
      aria-label={l10n.getString("roster-view-player", { nickname: player.nickname })}
      className="inline-flex min-h-11 items-center font-semibold text-accent-text underline-offset-4 hover:underline focus-visible:outline-2 focus-visible:outline-accent-text"
    >
      {player.nickname}
    </Link>
  );
}

/** A compact roster entry: the whole card is the link to the profile. */
function PlayerCard({
  player,
  search,
  name,
}: {
  player: RosterPlayer;
  search: ProfileSearch;
  name: string;
}) {
  const { l10n } = useLocalization();
  return (
    <Link
      to="/player"
      search={search}
      aria-label={l10n.getString("roster-view-player", { nickname: player.nickname })}
      className="block min-h-11 rounded-md border border-border bg-surface-raised p-3 hover:border-accent focus-visible:outline-2 focus-visible:outline-accent-text"
    >
      <span className="flex items-center justify-between gap-2">
        <span>
          <ContentText id={player.roleMessage} />
          {" · "}
          <span className="font-semibold text-accent-text">{player.nickname}</span>
        </span>
        <span className="font-semibold tabular-nums">{player.overall}</span>
      </span>
      <span className="mt-1 flex items-center gap-2 text-muted text-sm">
        <span>{name}</span>
        <NationalityBadge nationality={player.nationality} />
        <span className="tabular-nums">{player.age}</span>
      </span>
    </Link>
  );
}
