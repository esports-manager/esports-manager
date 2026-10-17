// @generated automatically by Diesel CLI.

diesel::table! {
    competition_teams (competition_id, position) {
        competition_id -> Text,
        position -> Integer,
        team_id -> Text,
    }
}

diesel::table! {
    competitions (id) {
        id -> Text,
        position -> Integer,
        region_id -> Text,
    }
}

diesel::table! {
    content_texts (locale, file) {
        locale -> Text,
        file -> Text,
        source -> Text,
    }
}

diesel::table! {
    nationalities (id) {
        id -> Text,
        position -> Integer,
        code -> Text,
        name_order -> Text,
    }
}

diesel::table! {
    packages (id) {
        id -> Text,
        position -> Integer,
        version -> Text,
        content_hash -> Binary,
    }
}

diesel::table! {
    players (id) {
        id -> Text,
        position -> Integer,
        team_id -> Text,
        role_id -> Text,
        starter -> Bool,
        nickname -> Text,
        given_name -> Text,
        family_name -> Text,
        nationality_id -> Text,
        birth_date -> Text,
        mechanics -> Integer,
        laning -> Integer,
        game_sense -> Integer,
        awareness -> Integer,
        positioning -> Integer,
        champion_pool_breadth -> Integer,
        shotcalling -> Integer,
        teamwork -> Integer,
        aggression -> Integer,
        composure -> Integer,
        work_ethic -> Integer,
        consistency -> Integer,
        potential -> Integer,
    }
}

diesel::table! {
    region_nationalities (region_id, nationality_id) {
        region_id -> Text,
        nationality_id -> Text,
        weight -> Integer,
    }
}

diesel::table! {
    regions (id) {
        id -> Text,
        position -> Integer,
        level -> Integer,
    }
}

diesel::table! {
    roles (id) {
        id -> Text,
        position -> Integer,
        mechanics_weight -> Integer,
        laning_weight -> Integer,
        game_sense_weight -> Integer,
        awareness_weight -> Integer,
        positioning_weight -> Integer,
        champion_pool_breadth_weight -> Integer,
        shotcalling_weight -> Integer,
        teamwork_weight -> Integer,
        composure_weight -> Integer,
    }
}

diesel::table! {
    save_meta (id) {
        id -> Integer,
        name -> Text,
        manager_name -> Text,
        team_id -> Text,
        genre -> Text,
        seed -> BigInt,
        game_version -> Text,
        game_date -> Text,
        created_at -> BigInt,
        last_played_at -> BigInt,
    }
}

diesel::table! {
    teams (id) {
        id -> Text,
        position -> Integer,
        region_id -> Text,
        tag -> Text,
        colour_fill -> Text,
        colour_border -> Text,
        reputation -> Integer,
    }
}

diesel::joinable!(competition_teams -> competitions (competition_id));
diesel::joinable!(competition_teams -> teams (team_id));
diesel::joinable!(competitions -> regions (region_id));
diesel::joinable!(players -> nationalities (nationality_id));
diesel::joinable!(players -> roles (role_id));
diesel::joinable!(players -> teams (team_id));
diesel::joinable!(region_nationalities -> nationalities (nationality_id));
diesel::joinable!(region_nationalities -> regions (region_id));
diesel::joinable!(save_meta -> teams (team_id));
diesel::joinable!(teams -> regions (region_id));

diesel::allow_tables_to_appear_in_same_query!(
    competition_teams,
    competitions,
    content_texts,
    nationalities,
    packages,
    players,
    region_nationalities,
    regions,
    roles,
    save_meta,
    teams,
);
