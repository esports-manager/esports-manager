// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { Localized, useLocalization } from "@fluent/react";
import { Link } from "@tanstack/react-router";
import type { AttributeView } from "../bindings";
import { FailureList } from "../components/Failure";
import { NationalityBadge } from "../components/NationalityBadge";
import { usePersonName } from "../components/PersonName";
import { backLink } from "../components/styles";
import { usePlayer } from "../hooks/game";
import { failureMessages } from "../lib/backend/result";
import { ContentText, messageText } from "../lib/i18n/content";
import { formatCalendarDate } from "../lib/i18n/dates";
import { DEFAULT_SORT, type RosterSort, sortSearch } from "./rosterSort";

/**
 * One player: identity, overall, and attributes by group; hidden ones are
 * unknown. `team` and `sort` are the roster's, kept for the way back.
 */
export function Player({
  id,
  team: rosterTeam,
  sort = DEFAULT_SORT,
}: {
  id: string;
  /** The roster this profile was opened from, when it wasn't the user's team. */
  team?: string | undefined;
  sort?: RosterSort;
}) {
  const { l10n } = useLocalization();
  const profile = usePlayer(id);
  const name = usePersonName();
  // Back goes to the roster the profile came from, before the profile loads too.
  const back = (team: string | undefined) => ({
    ...(team === undefined ? {} : { team }),
    ...sortSearch(sort),
  });
  if (profile.isError) {
    return (
      <section className="mx-auto flex max-w-3xl flex-col gap-4">
        <Localized id="profile-back">
          <Link to="/roster" search={back(rosterTeam)} className={backLink} />
        </Localized>
        <FailureList
          heading={l10n.getString("app-backend-error")}
          messages={failureMessages(profile.error)}
        />
      </section>
    );
  }
  if (!profile.isSuccess) {
    return (
      <section className="mx-auto flex max-w-3xl flex-col gap-4">
        <Localized id="profile-back">
          <Link to="/roster" search={back(rosterTeam)} className={backLink} />
        </Localized>
        <Localized id="app-loading">
          <p className="text-muted" />
        </Localized>
      </section>
    );
  }
  const { player, team, birthDate, skills, traits, hidden } = profile.data;
  return (
    <section className="mx-auto flex max-w-3xl flex-col gap-4">
      <Localized id="profile-back">
        <Link to="/roster" search={back(team.id)} className={backLink} />
      </Localized>
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h2 className="font-semibold text-2xl">{player.nickname}</h2>
        <Localized id="profile-overall" vars={{ overall: player.overall }}>
          <p className="font-semibold text-xl" />
        </Localized>
      </div>
      <p className="flex flex-wrap items-center gap-x-2 text-muted">
        <span>{name(player)}</span>
        <span>
          <ContentText id={player.roleMessage} />
        </span>
        <Localized id="profile-age" vars={{ age: player.age }}>
          <span />
        </Localized>
        <span>
          {l10n.getString("profile-nationality", {
            country: messageText(l10n, player.nationality.nameMessage),
            code: player.nationality.code,
          })}
        </span>
        <NationalityBadge nationality={player.nationality} />
      </p>
      <p className="text-muted">
        <ContentText id={team.nameMessage} />
        {" · "}
        {l10n.getString("profile-born", { date: formatCalendarDate(birthDate, "long") })}
      </p>
      <div className="grid gap-6 sm:grid-cols-2">
        <AttributeGroup heading={l10n.getString("profile-skills")} attributes={skills} />
        <div className="flex flex-col gap-6">
          <AttributeGroup heading={l10n.getString("profile-traits")} attributes={traits} />
          <AttributeGroup heading={l10n.getString("profile-hidden")} attributes={hidden} />
        </div>
      </div>
    </section>
  );
}

function AttributeGroup({ heading, attributes }: { heading: string; attributes: AttributeView[] }) {
  const { l10n } = useLocalization();
  const unknown = (
    <>
      <span aria-hidden="true">{l10n.getString("profile-unknown")}</span>
      <span className="sr-only">{l10n.getString("profile-unknown-label")}</span>
    </>
  );
  return (
    <div>
      <h3 className="mb-2 font-semibold">{heading}</h3>
      <dl className="flex flex-col">
        {attributes.map((attribute) => (
          <div
            key={attribute.nameMessage}
            className="flex justify-between border-border border-t py-1"
          >
            <dt>
              <ContentText id={attribute.nameMessage} />
            </dt>
            <dd className="font-semibold tabular-nums">{attribute.value ?? unknown}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}
