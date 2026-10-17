// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! File names for saves (saves spec).

/// The file stem for a save name: lowercase ASCII letters and digits, with
/// every other run of characters turned into one `-`. A name with no ASCII
/// letter or digit gets `save`.
pub fn slug(name: &str) -> String {
    let mut slug = String::new();
    let mut gap = false;
    for c in name.chars() {
        if c.is_ascii_alphanumeric() {
            if gap && !slug.is_empty() {
                slug.push('-');
            }
            gap = false;
            slug.push(c.to_ascii_lowercase());
        } else {
            gap = true;
        }
    }
    if slug.is_empty() {
        "save".to_owned()
    } else {
        slug
    }
}

/// How many numbered stems to try before giving up on short names.
const MAX_NUMBER: u32 = 10_000;

/// `stem`, or `stem-2`, `stem-3`, … : the first that `taken` doesn't hold.
/// After `MAX_NUMBER` tries it falls back to `stem-<process id>-<n>`.
pub fn free_stem(stem: &str, taken: impl Fn(&str) -> bool) -> String {
    if !taken(stem) {
        return stem.to_owned();
    }
    (2..=MAX_NUMBER)
        .map(|n| format!("{stem}-{n}"))
        .find(|candidate| !taken(candidate))
        .unwrap_or_else(|| format!("{stem}-{}-{MAX_NUMBER}", std::process::id()))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn slugs_keep_ascii_letters_and_digits() {
        assert_eq!(slug("Ana's Tigers"), "ana-s-tigers");
        assert_eq!(slug("  Tigers!! 2027 "), "tigers-2027");
        assert_eq!(slug("Tigers!"), "tigers");
        assert_eq!(slug("Onça"), "on-a");
    }

    #[test]
    fn names_without_ascii_get_a_fallback() {
        assert_eq!(slug("호랑이"), "save");
        assert_eq!(slug("!!!"), "save");
        assert_eq!(slug(""), "save");
    }

    #[test]
    fn taken_stems_get_a_number() {
        assert_eq!(free_stem("tigers", |_| false), "tigers");
        assert_eq!(free_stem("tigers", |s| s == "tigers"), "tigers-2");
        assert_eq!(
            free_stem("tigers", |s| s == "tigers" || s == "tigers-2"),
            "tigers-3"
        );
        let fallback = format!("tigers-{}-10000", std::process::id());
        assert_eq!(free_stem("tigers", |s| s != fallback), fallback);
    }
}
