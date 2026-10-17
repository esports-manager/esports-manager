// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! Desktop adapter (ADR 0001). Each command translates its input, calls one
//! use case in `app`, and returns a view DTO. No game rules live here.

mod commands;
mod desktop;

use std::sync::Mutex;

use app::locations::{DataLocations, LocationError};
use tauri::Manager;

/// The command set, also used to generate the TypeScript bindings (ADR 0006).
fn specta_builder<R: tauri::Runtime>() -> tauri_specta::Builder<R> {
    tauri_specta::Builder::<R>::new().commands(tauri_specta::collect_commands![
        commands::get_about,
        commands::get_new_game_options,
        commands::get_content_text,
        commands::start_new_game,
        commands::list_saves,
        commands::open_save,
        commands::get_roster,
        commands::get_player,
    ])
}

/// The app's Tauri context. `generate_context!` may expand only once per
/// crate (on macOS it defines a symbol), so the app and its tests share it.
// It also builds Tauri's own asset table with `HashMap`, not game state, so
// ADR 0003 doesn't apply.
#[allow(clippy::disallowed_types)]
fn context<R: tauri::Runtime>() -> tauri::Context<R> {
    tauri::generate_context!()
}

/// The desktop app's data folders: the same resolver the CLI uses.
fn data_locations() -> Result<DataLocations, LocationError> {
    db::environment::locations(None)
}

/// Starts the desktop app.
///
/// # Errors
///
/// Returns an error if Tauri fails to start the window or event loop.
pub fn run() -> tauri::Result<()> {
    let builder = specta_builder::<tauri::Wry>();
    tauri::Builder::default()
        .invoke_handler(builder.invoke_handler())
        .setup(move |app| {
            builder.mount_events(app);
            let locations = data_locations()?;
            // Portable mode never falls back: an unwritable folder stops the app.
            db::environment::prepare(&locations)
                .map_err(|(dir, error)| format!("{}: {error}", dir.display()))?;
            let content = desktop::core_content(&app.path().resource_dir()?);
            app.manage(Mutex::new(desktop::Desktop::new(
                locations.saves(),
                content,
            )));

            let config = desktop::window_config(&locations);
            // The window is named after the product in tauri.conf.json.
            let title = app.config().product_name.clone().unwrap_or_default();
            let mut window =
                tauri::WebviewWindowBuilder::new(app, config.label, tauri::WebviewUrl::default())
                    .title(title)
                    .inner_size(f64::from(config.width), f64::from(config.height))
                    .min_inner_size(f64::from(config.min_width), f64::from(config.min_height));
            if let Some(dir) = config.data_directory {
                window = window.data_directory(dir);
            }
            window.build()?;
            Ok(())
        })
        .run(context())
}

#[cfg(test)]
mod tests {
    use std::path::{Path, PathBuf};
    use std::sync::Mutex;

    use tauri::ipc::{CallbackFn, InvokeBody};
    use tauri::test::{INVOKE_KEY, MockRuntime, get_ipc_response, mock_builder};
    use tauri::webview::InvokeRequest;

    use crate::desktop::Desktop;

    /// The app with its real command set on Tauri's mock runtime, and a
    /// webview to invoke commands from.
    fn mock_app(name: &str) -> (tauri::App<MockRuntime>, tauri::WebviewWindow<MockRuntime>) {
        let saves = std::env::temp_dir().join(format!("esm-ipc-{name}-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&saves);
        std::fs::create_dir_all(&saves).unwrap();
        let core: PathBuf = Path::new(env!("CARGO_MANIFEST_DIR")).join("../content/core");
        let app = mock_builder()
            .invoke_handler(super::specta_builder::<MockRuntime>().invoke_handler())
            .manage(Mutex::new(Desktop::new(saves, core)))
            // The real context, so the app's command permissions apply.
            .build(super::context())
            .unwrap();
        let webview = tauri::WebviewWindowBuilder::new(&app, "main", tauri::WebviewUrl::default())
            .build()
            .unwrap();
        (app, webview)
    }

    fn invoke(
        webview: &tauri::WebviewWindow<MockRuntime>,
        command: &str,
        body: serde_json::Value,
    ) -> serde_json::Value {
        let response = get_ipc_response(
            webview,
            InvokeRequest {
                cmd: command.to_owned(),
                callback: CallbackFn(0),
                error: CallbackFn(1),
                url: webview.url().unwrap(),
                body: InvokeBody::Json(body),
                headers: tauri::http::HeaderMap::default(),
                invoke_key: INVOKE_KEY.to_owned(),
            },
        );
        match response {
            Ok(body) => body.deserialize().unwrap(),
            Err(error) => serde_json::json!({ "error": error }),
        }
    }

    #[test]
    fn every_command_answers_over_ipc() {
        let (_app, webview) = mock_app("commands");
        let empty = serde_json::json!({});
        assert_eq!(
            invoke(&webview, "get_about", empty.clone())["version"],
            env!("CARGO_PKG_VERSION")
        );
        let options = invoke(&webview, "get_new_game_options", empty.clone());
        assert_eq!(options["regions"].as_array().unwrap().len(), 2);
        let texts = invoke(&webview, "get_content_text", empty.clone());
        assert!(
            texts
                .as_array()
                .unwrap()
                .iter()
                .any(|t| t["locale"] == "pt-BR")
        );
        assert_eq!(
            invoke(&webview, "list_saves", empty.clone()),
            serde_json::json!([])
        );
        let input = serde_json::json!({ "input": {
            "managerName": "Ana", "team": "team:azure_tigers", "saveName": "Tigers", "seed": "42" } });
        let opened = invoke(&webview, "start_new_game", input);
        assert_eq!(opened["file"], "tigers.esmsave");
        assert_eq!(invoke(&webview, "list_saves", empty)[0]["name"], "Tigers");
        let roster = invoke(&webview, "get_roster", serde_json::json!({ "team": null }));
        assert_eq!(roster["starters"].as_array().unwrap().len(), 5);
        let player = invoke(
            &webview,
            "get_player",
            serde_json::json!({ "id": "player:kairos" }),
        );
        assert_eq!(player["player"]["nickname"], "Kairos");
        let reopened = invoke(
            &webview,
            "open_save",
            serde_json::json!({ "file": "tigers.esmsave" }),
        );
        assert_eq!(reopened["team"], "team:azure_tigers");
    }

    #[test]
    fn command_failures_carry_messages() {
        let (_app, webview) = mock_app("failures");
        let roster = invoke(&webview, "get_roster", serde_json::json!({ "team": null }));
        assert_eq!(roster["error"]["messages"][0]["id"], "error-no-save-open");
    }

    // REUSE-IgnoreStart
    /// The generated bindings' licence header (ADR 0012).
    const BINDINGS_HEADER: &str = "// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>\n//\n// SPDX-License-Identifier: GPL-3.0-or-later\n";
    // REUSE-IgnoreEnd

    /// The committed bindings must match the commands (ADR 0006). Set
    /// `UPDATE_BINDINGS=1` to rewrite them (`just bindings`).
    #[test]
    fn typescript_bindings_are_up_to_date() {
        let committed = Path::new(env!("CARGO_MANIFEST_DIR")).join("../src/bindings.ts");
        let generated =
            std::env::temp_dir().join(format!("esm-bindings-{}.ts", std::process::id()));
        super::specta_builder::<tauri::Wry>()
            .export(
                specta_typescript::Typescript::default().header(BINDINGS_HEADER),
                &generated,
            )
            .unwrap();
        let generated_text = std::fs::read_to_string(&generated).unwrap();
        std::fs::remove_file(&generated).unwrap();

        if std::env::var_os("UPDATE_BINDINGS").is_some() {
            std::fs::write(&committed, &generated_text).unwrap();
        }
        let committed_text = std::fs::read_to_string(&committed).unwrap_or_default();
        assert!(
            committed_text == generated_text,
            "src/bindings.ts is out of date; run `just bindings` and commit the result"
        );
    }
}
