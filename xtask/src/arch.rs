// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! Architecture test: the crate graph matches ADR 0001.

use std::collections::{BTreeMap, BTreeSet};
use std::path::Path;

use anyhow::{Context, Result};
use cargo_metadata::{DependencyKind, PackageId};

use crate::config::Architecture;
use crate::workspace::{self, TOOLING};

/// What the check needs to know about one workspace crate.
#[derive(Debug, Default, PartialEq, Eq)]
pub struct CrateDeps {
    /// Workspace crates it depends on, through any kind of dependency.
    pub workspace: BTreeSet<String>,
    /// Every package in its normal and build dependency tree.
    pub transitive: BTreeSet<String>,
}

pub fn run(root: &Path, config: &Architecture) -> Result<Vec<String>> {
    Ok(check(config, &graph(&workspace::metadata(root)?)?))
}

fn graph(metadata: &cargo_metadata::Metadata) -> Result<BTreeMap<String, CrateDeps>> {
    let resolve = metadata
        .resolve
        .as_ref()
        .context("cargo metadata has no resolve graph")?;
    let names: BTreeMap<&PackageId, &str> = metadata
        .packages
        .iter()
        .map(|package| (&package.id, package.name.as_str()))
        .collect();
    let members: BTreeSet<&PackageId> = metadata.workspace_members.iter().collect();
    let nodes: BTreeMap<&PackageId, &cargo_metadata::Node> =
        resolve.nodes.iter().map(|node| (&node.id, node)).collect();

    let mut graph = BTreeMap::new();
    for member in &members {
        let node = nodes
            .get(member)
            .context("workspace member missing from resolve graph")?;
        let workspace = node
            .deps
            .iter()
            .filter(|dep| members.contains(&dep.pkg))
            .filter_map(|dep| names.get(&dep.pkg).map(|name| (*name).to_owned()))
            .collect();

        let mut transitive = BTreeSet::new();
        let mut pending = vec![*member];
        let mut seen = BTreeSet::new();
        while let Some(id) = pending.pop() {
            if !seen.insert(id) {
                continue;
            }
            let Some(node) = nodes.get(id) else { continue };
            for dep in &node.deps {
                let runtime = dep.dep_kinds.iter().any(|info| {
                    matches!(info.kind, DependencyKind::Normal | DependencyKind::Build)
                });
                if runtime {
                    if let Some(name) = names.get(&dep.pkg) {
                        transitive.insert((*name).to_owned());
                    }
                    pending.push(&dep.pkg);
                }
            }
        }

        let name = names
            .get(member)
            .context("workspace member has no package")?;
        graph.insert(
            (*name).to_owned(),
            CrateDeps {
                workspace,
                transitive,
            },
        );
    }
    Ok(graph)
}

/// Compares the crate graph against the allowed edges and banned crates.
pub fn check(config: &Architecture, graph: &BTreeMap<String, CrateDeps>) -> Vec<String> {
    let mut violations = Vec::new();

    for (name, deps) in graph {
        if TOOLING.contains(&name.as_str()) {
            continue;
        }
        let Some(allowed) = config.allowed.get(name) else {
            violations.push(format!(
                "crate `{name}` is not listed in quality.toml [architecture.allowed]; \
                 new crates need an ADR 0001 change"
            ));
            continue;
        };
        for dep in &deps.workspace {
            if !allowed.contains(dep) {
                violations.push(format!(
                    "crate `{name}` depends on `{dep}`, which ADR 0001 does not allow"
                ));
            }
        }
        for banned in config.banned.get(name).into_iter().flatten() {
            if deps.transitive.contains(banned) {
                violations.push(format!(
                    "crate `{name}` pulls in `{banned}`, which ADR 0001 bans from pure crates"
                ));
            }
        }
    }

    for name in config.allowed.keys().chain(config.banned.keys()) {
        if !graph.contains_key(name) {
            violations.push(format!(
                "quality.toml names crate `{name}`, which is not a workspace member"
            ));
        }
    }

    violations
}

#[cfg(test)]
mod tests {
    use super::*;

    fn config() -> Architecture {
        Architecture {
            allowed: BTreeMap::from([
                ("domain".to_owned(), vec![]),
                ("app".to_owned(), vec!["domain".to_owned()]),
            ]),
            banned: BTreeMap::from([("domain".to_owned(), vec!["tokio".to_owned()])]),
        }
    }

    fn deps(workspace: &[&str], transitive: &[&str]) -> CrateDeps {
        CrateDeps {
            workspace: workspace.iter().map(|&name| name.to_owned()).collect(),
            transitive: transitive.iter().map(|&name| name.to_owned()).collect(),
        }
    }

    #[test]
    fn a_graph_matching_the_rules_passes() {
        let graph = BTreeMap::from([
            ("domain".to_owned(), deps(&[], &["serde"])),
            ("app".to_owned(), deps(&["domain"], &["domain", "serde"])),
            ("xtask".to_owned(), deps(&["app"], &["tokio"])),
        ]);
        assert_eq!(check(&config(), &graph), Vec::<String>::new());
    }

    #[test]
    fn an_edge_pointing_outward_is_reported() {
        let graph = BTreeMap::from([
            ("domain".to_owned(), deps(&["app"], &["app"])),
            ("app".to_owned(), deps(&["domain"], &["domain"])),
        ]);
        assert_eq!(
            check(&config(), &graph),
            ["crate `domain` depends on `app`, which ADR 0001 does not allow"]
        );
    }

    #[test]
    fn a_banned_crate_deep_in_the_tree_is_reported() {
        let graph = BTreeMap::from([
            ("domain".to_owned(), deps(&[], &["some-wrapper", "tokio"])),
            ("app".to_owned(), deps(&["domain"], &[])),
        ]);
        assert_eq!(
            check(&config(), &graph),
            ["crate `domain` pulls in `tokio`, which ADR 0001 bans from pure crates"]
        );
    }

    #[test]
    fn an_unlisted_crate_is_reported() {
        let graph = BTreeMap::from([
            ("domain".to_owned(), deps(&[], &[])),
            ("app".to_owned(), deps(&["domain"], &[])),
            ("rogue".to_owned(), deps(&[], &[])),
        ]);
        let violations = check(&config(), &graph);
        assert_eq!(violations.len(), 1);
        assert!(violations[0].starts_with("crate `rogue` is not listed"));
    }

    #[test]
    fn a_stale_config_entry_is_reported() {
        let graph = BTreeMap::from([("domain".to_owned(), deps(&[], &[]))]);
        assert_eq!(
            check(&config(), &graph),
            ["quality.toml names crate `app`, which is not a workspace member"]
        );
    }

    #[test]
    fn the_repository_graph_passes() {
        let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("..");
        let quality = crate::config::Quality::load(&root.join("quality.toml")).unwrap();
        assert_eq!(
            run(&root, &quality.architecture).unwrap(),
            Vec::<String>::new()
        );
    }
}
