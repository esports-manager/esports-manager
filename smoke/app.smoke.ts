// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Smoke test of the real desktop binary through tauri-driver (ADR 0008):
 * the app starts, the frontend loads, a command reaches the Rust side, and
 * the app finds a save the CLI made in the same environment.
 *
 * Build first with `pnpm tauri build --debug --no-bundle` and
 * `cargo build -p cli`; `just smoke` does all of it. Needs tauri-driver and,
 * on Linux, WebKitWebDriver.
 */
import { type ChildProcess, spawn, spawnSync } from "node:child_process";
import { existsSync, rmSync, writeFileSync } from "node:fs";
import { createConnection } from "node:net";
import { join } from "node:path";
import { remote } from "webdriverio";

const DRIVER_PORT = 4444;
const binaryName = process.platform === "win32" ? "esports-manager.exe" : "esports-manager";
const binaryDir = join(import.meta.dirname, "../target/debug");
const application = join(binaryDir, binaryName);
const cli = join(binaryDir, process.platform === "win32" ? "esm.exe" : "esm");
// Nothing the app writes may land in the OS data folder of the machine
// running the test. Driven runs get a scratch XDG_DATA_HOME (Linux, where the
// smoke test runs); the portable check uses target/debug/data.
const scratchData = join(binaryDir, "smoke-data");
const portableMarker = join(binaryDir, "portable");
const portableData = join(binaryDir, "data");
// Where the OS data folder points during the portable run, to prove nothing
// lands there.
const portableScratch = join(binaryDir, "smoke-portable-os-data");

function waitForPort(port: number, timeoutMs: number): Promise<void> {
  const deadline = Date.now() + timeoutMs;
  return new Promise((resolve, reject) => {
    const attempt = () => {
      const socket = createConnection({ port, host: "127.0.0.1" });
      socket.once("connect", () => {
        socket.end();
        resolve();
      });
      socket.once("error", () => {
        socket.destroy();
        if (Date.now() > deadline) {
          reject(new Error(`tauri-driver did not listen on port ${port}`));
        } else {
          setTimeout(attempt, 200);
        }
      });
    };
    attempt();
  });
}

async function main(): Promise<void> {
  for (const binary of [application, cli]) {
    if (!existsSync(binary)) {
      throw new Error(`${binary} not found; run \`just smoke\``);
    }
  }
  // A run stopped half-way can leave the marker, which would put both
  // binaries in portable mode.
  rmSync(portableMarker, { force: true });
  rmSync(scratchData, { recursive: true, force: true });
  // The OS data folder can only be pointed elsewhere on Linux (XDG_DATA_HOME);
  // elsewhere the CLI would write into the real one, so the check is skipped.
  const sharedFolderCheck = process.platform === "linux";
  if (sharedFolderCheck) {
    // spec: SAVE-007
    // Given a save the CLI made without --data-dir, in this environment
    const created = spawnSync(
      cli,
      ["new-game", "--manager", "Ana", "--team", "team:azure_tigers", "--save", "Smoke Save"],
      { env: { ...process.env, XDG_DATA_HOME: scratchData }, encoding: "utf8" },
    );
    if (created.status !== 0) {
      throw new Error(`esm new-game failed: ${created.stderr}`);
    }
  }
  const driver: ChildProcess = spawn("tauri-driver", ["--port", String(DRIVER_PORT)], {
    stdio: "inherit",
    env: { ...process.env, XDG_DATA_HOME: scratchData },
  });
  try {
    await waitForPort(DRIVER_PORT, 15_000);
    const browser = await remote({
      hostname: "127.0.0.1",
      port: DRIVER_PORT,
      logLevel: "warn",
      capabilities: { "tauri:options": { application } } as WebdriverIO.Capabilities,
    });
    try {
      const heading = await browser.$("h1");
      await heading.waitForDisplayed({ timeout: 20_000 });
      const title = await heading.getText();
      if (title !== "eSports Manager") {
        throw new Error(`unexpected heading "${title}"`);
      }
      const version = await browser.$('[data-testid="version"]');
      await version.waitForDisplayed({ timeout: 20_000 });
      const text = await version.getText();
      if (!/^v\d+\.\d+\.\d+$/.test(text)) {
        throw new Error(`unexpected version text "${text}"`);
      }
      if (!existsSync(join(scratchData, "esports-manager", "saves"))) {
        throw new Error(`the app did not create its saves folder under ${scratchData}`);
      }
      if (sharedFolderCheck) {
        // When the desktop app, in the same environment, lists its saves
        await (await browser.$("a=Load Game")).click();
        // Then it finds the CLI's save: both resolved the same data folder
        const save = await browser.$("button*=Smoke Save");
        await save.waitForDisplayed({ timeout: 20_000 });
      }
      console.log(
        `smoke test passed: "${title}" ${text}, shared data folder checked: ${sharedFolderCheck}`,
      );
    } finally {
      await browser.deleteSession();
    }
  } finally {
    driver.kill();
  }
}

/**
 * Starts the app in portable mode for a few seconds and checks that the
 * webview kept its data inside the portable folder (SAVE-006). WebKitWebDriver
 * can't drive a webview with its own data folder, so this run isn't driven.
 */
async function portable(): Promise<void> {
  rmSync(portableData, { recursive: true, force: true });
  rmSync(portableScratch, { recursive: true, force: true });
  writeFileSync(portableMarker, "");
  try {
    const app = spawn(application, [], {
      stdio: "inherit",
      env: { ...process.env, XDG_DATA_HOME: portableScratch },
    });
    const folders = ["saves", "webview"].map((folder) => join(portableData, folder));
    const deadline = Date.now() + 60_000;
    while (!folders.every(existsSync) && Date.now() < deadline && app.exitCode === null) {
      await new Promise((resolve) => setTimeout(resolve, 500));
    }
    app.kill();
    for (const folder of folders) {
      if (!existsSync(folder)) {
        throw new Error(`portable mode did not create ${folder} (app exit code ${app.exitCode})`);
      }
    }
    if (existsSync(portableScratch)) {
      throw new Error(`portable mode wrote to the OS data folder ${portableScratch}`);
    }
    console.log(`portable check passed: data in ${portableData}, nothing outside it`);
  } finally {
    rmSync(portableMarker, { force: true });
    rmSync(portableData, { recursive: true, force: true });
    rmSync(portableScratch, { recursive: true, force: true });
  }
}

await main();
await portable();
