// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! Converts each package definition into its domain type.
//!
//! Every definition is destructured exhaustively, so a new field that isn't
//! converted is a compile error, and a bound field that isn't used fails
//! `unused_variables`. Rest patterns are banned in this module and a CI check
//! enforces it (ADR 0005): nothing is validated and then ignored. `$schema`
//! is bound as `_` on purpose; it is editor metadata, not content.

use std::str::FromStr;

use domain::date::GameDate;
use domain::generation::Constants;
use domain::id::ContentId;
use domain::rating::Rating;
use domain::world::{
    Colour, Competition, CountryCode, NameOrder, NamePool, Nationality, Region, Reputation, Tag,
    Team, WorldSettings,
};
use esports::Genre;
use esports::moba::attributes::{MobaSkill, OverallAttribute};
use esports::moba::content::{GenerationParams, PinnedAttributes, PinnedPlayer, RosterRules};
use esports::moba::roles::RoleSet;

use app::content::Manifest;

use crate::defs::{
    CompetitionDef, GenerationDef, ManifestDef, NameOrderDef, NamePoolDef, NationalityDef,
    NicknamePoolDef, PinnedAttributesDef, PlayerDef, RegionDef, RoleDef, RoleSetDef, TeamDef,
    WeightKey, WorldDef,
};
use crate::parse::{Entry, join};
use app::content::{PackageError, Problem};

/// A converted value and where it came from, for later cross-checks.
#[derive(Debug)]
pub struct Located<T> {
    pub file: String,
    pub path: String,
    pub value: T,
}

impl<T> Located<T> {
    pub fn error(&self, field: &str, problem: Problem) -> PackageError {
        PackageError::new(&self.file, join(&self.path, field), problem)
    }
}

/// Collects problems while converting one entity, whose definition the
/// caller has taken apart.
struct Converter<'a> {
    file: String,
    path: String,
    errors: &'a mut Vec<PackageError>,
    ok: bool,
}

impl<'a> Converter<'a> {
    fn new(file: String, path: String, errors: &'a mut Vec<PackageError>) -> Self {
        Self {
            file,
            path,
            errors,
            ok: true,
        }
    }

    fn fail(&mut self, field: &str, problem: Problem) {
        let error = PackageError::new(&self.file, join(&self.path, field), problem);
        self.errors.push(error);
        self.ok = false;
    }

    /// The entity's own id, which must be of `kind`.
    fn own_id(&mut self, field: &str, text: &str, kind: &str) -> Option<ContentId> {
        let id = self.reference(field, text)?;
        if id.kind() != kind {
            self.fail(
                field,
                Problem::WrongKind {
                    id,
                    expected: kind.to_owned(),
                },
            );
            return None;
        }
        Some(id)
    }

    /// An id this entity refers to. Whether it exists is checked later.
    fn reference(&mut self, field: &str, text: &str) -> Option<ContentId> {
        let id = ContentId::parse(text).ok();
        if id.is_none() {
            self.fail(
                field,
                Problem::InvalidId {
                    id: text.to_owned(),
                },
            );
        }
        id
    }

    fn date(&mut self, field: &str, text: &str) -> Option<GameDate> {
        let date = GameDate::from_str(text).ok();
        if date.is_none() {
            self.fail(field, Problem::InvalidFormat);
        }
        date
    }

    fn rating(&mut self, field: &str, points: Option<u32>) -> Option<Rating> {
        let points = points?;
        let rating = Rating::from_points(points).ok();
        if rating.is_none() {
            self.fail(field, Problem::OutOfRange);
        }
        rating
    }

    fn finish<V>(self, value: Option<V>) -> Option<Located<V>> {
        let value = value.filter(|_| self.ok)?;
        Some(Located {
            file: self.file,
            path: self.path,
            value,
        })
    }
}

pub fn manifest(entry: Entry<ManifestDef>, errors: &mut Vec<PackageError>) -> Option<Manifest> {
    let ManifestDef {
        schema: _,
        id,
        version,
        title,
        license,
        authors,
        genre,
        locales,
    } = entry.def;
    let mut c = Converter::new(entry.file, entry.path, errors);
    let id_ok = ContentId::is_slug(&id);
    if !id_ok {
        c.fail("id", Problem::InvalidId { id: id.clone() });
    }
    let parts: Vec<&str> = version.split('.').collect();
    let version_ok = parts.len() == 3
        && parts
            .iter()
            .all(|part| !part.is_empty() && part.bytes().all(|b| b.is_ascii_digit()));
    if !version_ok {
        c.fail("version", Problem::InvalidFormat);
    }
    let parsed_genre = Genre::from_str(&genre).ok();
    if parsed_genre.is_none() {
        c.fail("genre", Problem::UnsupportedGenre { genre });
    }
    if locales.is_empty() {
        c.fail("locales", Problem::Empty);
    }
    let value = parsed_genre.map(|genre| Manifest {
        id,
        version,
        title,
        license,
        authors,
        genre,
        locales,
    });
    c.finish(value).map(|located| located.value)
}

pub fn world(entry: Entry<WorldDef>, errors: &mut Vec<PackageError>) -> Option<WorldSettings> {
    let WorldDef {
        schema: _,
        start_date,
    } = entry.def;
    let mut c = Converter::new(entry.file, entry.path, errors);
    let start_date = c.date("start_date", &start_date);
    c.finish(start_date.map(|start_date| WorldSettings { start_date }))
        .map(|located| located.value)
}

pub fn region(entry: Entry<RegionDef>, errors: &mut Vec<PackageError>) -> Option<Located<Region>> {
    let RegionDef {
        schema: _,
        id,
        level,
        nationalities,
    } = entry.def;
    let mut c = Converter::new(entry.file, entry.path, errors);
    let id = c.own_id("id", &id, "region");
    let mut mix = Vec::new();
    for (nationality, weight) in nationalities {
        let field = format!("nationalities.{nationality}");
        if let Some(nationality) = c.reference(&field, &nationality) {
            mix.push((nationality, weight));
        }
    }
    let value = id.map(|id| Region {
        id,
        level,
        nationalities: mix,
    });
    c.finish(value)
}

pub fn nationality(
    entry: Entry<NationalityDef>,
    errors: &mut Vec<PackageError>,
) -> Option<Located<Nationality>> {
    let NationalityDef {
        schema: _,
        id,
        code,
        name_order,
    } = entry.def;
    let mut c = Converter::new(entry.file, entry.path, errors);
    let id = c.own_id("id", &id, "nationality");
    let code = CountryCode::parse(&code);
    if code.is_none() {
        c.fail("code", Problem::InvalidFormat);
    }
    let name_order = match name_order {
        NameOrderDef::GivenFirst => NameOrder::GivenFirst,
        NameOrderDef::FamilyFirst => NameOrder::FamilyFirst,
    };
    let value = id.zip(code).map(|(id, code)| Nationality {
        id,
        code,
        name_order,
    });
    c.finish(value)
}

pub fn name_pool(
    entry: Entry<NamePoolDef>,
    errors: &mut Vec<PackageError>,
) -> Option<Located<NamePool>> {
    let NamePoolDef {
        schema: _,
        id,
        nationality,
        given,
        family,
    } = entry.def;
    let mut c = Converter::new(entry.file, entry.path, errors);
    let id = c.own_id("id", &id, "name_pool");
    let nationality = c.reference("nationality", &nationality);
    let value = id.and(nationality).map(|nationality| NamePool {
        nationality,
        given,
        family,
    });
    c.finish(value)
}

pub fn nickname_pool(
    entry: Entry<NicknamePoolDef>,
    errors: &mut Vec<PackageError>,
) -> Option<Located<Vec<String>>> {
    let NicknamePoolDef {
        schema: _,
        id,
        nicknames,
    } = entry.def;
    let mut c = Converter::new(entry.file, entry.path, errors);
    let id = c.own_id("id", &id, "nickname_pool");
    c.finish(id.map(|_| nicknames))
}

pub fn competition(
    entry: Entry<CompetitionDef>,
    errors: &mut Vec<PackageError>,
) -> Option<Located<Competition>> {
    let CompetitionDef {
        schema: _,
        id,
        region,
        teams,
    } = entry.def;
    let mut c = Converter::new(entry.file, entry.path, errors);
    let id = c.own_id("id", &id, "competition");
    let region = c.reference("region", &region);
    let teams: Vec<ContentId> = teams
        .iter()
        .enumerate()
        .filter_map(|(index, team)| c.reference(&format!("teams[{index}]"), team))
        .collect();
    let value = id
        .zip(region)
        .map(|(id, region)| Competition { id, region, teams });
    c.finish(value)
}

pub fn team(entry: Entry<TeamDef>, errors: &mut Vec<PackageError>) -> Option<Located<Team>> {
    let TeamDef {
        schema: _,
        id,
        region,
        tag,
        colours,
        reputation,
    } = entry.def;
    let mut c = Converter::new(entry.file, entry.path, errors);
    let id = c.own_id("id", &id, "team");
    let region = c.reference("region", &region);
    let tag = Tag::parse(&tag);
    if tag.is_none() {
        c.fail("tag", Problem::InvalidFormat);
    }
    let [first, second] = colours;
    let mut colour = |index: usize, text: &str| {
        let colour = Colour::parse(text);
        if colour.is_none() {
            c.fail(&format!("colours[{index}]"), Problem::InvalidFormat);
        }
        colour
    };
    let colours = colour(0, &first).zip(colour(1, &second));
    let reputation_value = Reputation::new(reputation);
    if reputation_value.is_none() {
        c.fail("reputation", Problem::OutOfRange);
    }
    let value = (|| {
        let (first, second) = colours?;
        Some(Team {
            id: id?,
            region: region?,
            tag: tag?,
            colours: [first, second],
            reputation: reputation_value?,
        })
    })();
    c.finish(value)
}

pub fn player(
    entry: Entry<PlayerDef>,
    errors: &mut Vec<PackageError>,
) -> Option<Located<PinnedPlayer>> {
    let PlayerDef {
        schema: _,
        id,
        team,
        role,
        nickname,
        given_name,
        family_name,
        nationality,
        birth_date,
        attributes,
    } = entry.def;
    let mut c = Converter::new(entry.file, entry.path, errors);
    let id = c.own_id("id", &id, "player");
    let team = c.reference("team", &team);
    let role = c.reference("role", &role);
    let nationality = nationality.and_then(|text| c.reference("nationality", &text));
    let birth_date = birth_date.and_then(|text| c.date("birth_date", &text));
    let PinnedAttributesDef {
        mechanics,
        laning,
        game_sense,
        awareness,
        positioning,
        champion_pool_breadth,
        shotcalling,
        teamwork,
        aggression,
        composure,
        work_ethic,
        consistency,
        potential,
    } = attributes;
    let mut rating =
        |field: &str, points: Option<u32>| c.rating(&format!("attributes.{field}"), points);
    let attributes = PinnedAttributes {
        mechanics: rating("mechanics", mechanics),
        laning: rating("laning", laning),
        game_sense: rating("game_sense", game_sense),
        awareness: rating("awareness", awareness),
        positioning: rating("positioning", positioning),
        champion_pool_breadth: rating("champion_pool_breadth", champion_pool_breadth),
        shotcalling: rating("shotcalling", shotcalling),
        teamwork: rating("teamwork", teamwork),
        aggression: rating("aggression", aggression),
        composure: rating("composure", composure),
        work_ethic: rating("work_ethic", work_ethic),
        consistency: rating("consistency", consistency),
        potential: rating("potential", potential),
    };
    let value = (|| {
        Some(PinnedPlayer {
            id: id?,
            team: team?,
            role: role?,
            nickname,
            given_name,
            family_name,
            nationality,
            birth_date,
            attributes,
        })
    })();
    c.finish(value)
}

/// The role set and the roster shape it comes with.
pub fn role_set(
    entry: Entry<RoleSetDef>,
    errors: &mut Vec<PackageError>,
) -> Option<Located<(RoleSet, RosterRules)>> {
    let RoleSetDef {
        schema: _,
        id,
        roles,
        subs,
    } = entry.def;
    let mut c = Converter::new(entry.file, entry.path, errors);
    let id = c.own_id("id", &id, "role_set");
    let mut definitions = Vec::new();
    let declared = roles.len();
    for (index, role) in roles.into_iter().enumerate() {
        let RoleDef { id, weights } = role;
        if let Some(id) = c.own_id(&format!("roles[{index}].id"), &id, "role") {
            definitions.push((
                id,
                weights
                    .into_iter()
                    .map(|(key, w)| (attribute(key), w))
                    .collect(),
            ));
        }
    }
    // When every role id failed, those errors are reported already; an
    // empty role set on top would be a second, misleading error.
    let role_set = if definitions.is_empty() && declared > 0 {
        None
    } else {
        match RoleSet::new(definitions) {
            Ok(role_set) => Some(role_set),
            Err(problems) => {
                for problem in problems {
                    c.fail("roles", Problem::RoleSet(problem));
                }
                None
            }
        }
    };
    let value = id
        .and(role_set)
        .map(|role_set| (role_set, RosterRules { subs }));
    c.finish(value)
}

const fn attribute(key: WeightKey) -> OverallAttribute {
    match key {
        WeightKey::Mechanics => OverallAttribute::Skill(MobaSkill::Mechanics),
        WeightKey::Laning => OverallAttribute::Skill(MobaSkill::Laning),
        WeightKey::GameSense => OverallAttribute::Skill(MobaSkill::GameSense),
        WeightKey::Awareness => OverallAttribute::Skill(MobaSkill::Awareness),
        WeightKey::Positioning => OverallAttribute::Skill(MobaSkill::Positioning),
        WeightKey::ChampionPoolBreadth => OverallAttribute::Skill(MobaSkill::ChampionPoolBreadth),
        WeightKey::Shotcalling => OverallAttribute::Skill(MobaSkill::Shotcalling),
        WeightKey::Teamwork => OverallAttribute::Teamwork,
        WeightKey::Composure => OverallAttribute::Composure,
    }
}

pub fn generation(
    entry: Entry<GenerationDef>,
    errors: &mut Vec<PackageError>,
) -> Option<Located<GenerationParams>> {
    let GenerationDef {
        schema: _,
        id,
        mu_base,
        mu_per_reputation,
        sigma_base,
        sigma_per_reputation,
        sigma_min,
        attribute_spread,
        bias_scale,
        style_mean,
        style_spread,
        consistency_mean,
        consistency_spread,
        potential_peak_age,
        potential_per_year,
        potential_spread,
        age_mean,
        age_spread,
        age_min,
        age_max,
        nickname_pool_factor,
    } = entry.def;
    let mut c = Converter::new(entry.file, entry.path, errors);
    let id = c.own_id("id", &id, "generation");
    let non_negative = [
        ("sigma_min", sigma_min),
        ("attribute_spread", attribute_spread),
        ("style_spread", style_spread),
        ("consistency_spread", consistency_spread),
        ("potential_spread", potential_spread),
        ("age_spread", age_spread),
    ];
    for (field, value) in non_negative {
        if value < 0.0 {
            c.fail(field, Problem::OutOfRange);
        }
    }
    if age_min > age_max {
        c.fail("age_min", Problem::OutOfRange);
    }
    if nickname_pool_factor == 0 {
        c.fail("nickname_pool_factor", Problem::OutOfRange);
    }
    let value = id.map(|_| GenerationParams {
        common: Constants {
            mu_base,
            mu_per_reputation,
            sigma_base,
            sigma_per_reputation,
            sigma_min,
            style_mean,
            style_spread,
            consistency_mean,
            consistency_spread,
            potential_peak_age,
            potential_per_year,
            potential_spread,
            age_mean,
            age_spread,
            age_min,
            age_max,
            nickname_pool_factor,
        },
        attribute_spread,
        bias_scale,
    });
    c.finish(value)
}

/// Every converted entity of one kind, in file order.
pub fn all<D, V>(
    entries: Vec<Entry<D>>,
    errors: &mut Vec<PackageError>,
    convert: impl Fn(Entry<D>, &mut Vec<PackageError>) -> Option<Located<V>>,
) -> Vec<Located<V>> {
    entries
        .into_iter()
        .filter_map(|entry| convert(entry, errors))
        .collect()
}
