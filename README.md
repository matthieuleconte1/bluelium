<p align="center">
  <img src="docs/bluelium-header.svg" alt="Diagram of the Bluelium window: tabs, address bar, page and AI panel" width="820">
</p>

<h1 align="center">Bluelium</h1>

<p align="center">
  A personal browser: <a href="https://github.com/imputnet/helium">Helium</a> with a different interface.
</p>

<p align="center">
  <img alt="macOS Apple Silicon" src="https://img.shields.io/badge/macOS-Apple%20Silicon-3450d1?style=flat-square">
  <img alt="Linux x86_64" src="https://img.shields.io/badge/Linux-x86__64-3450d1?style=flat-square">
  <img alt="Based on Helium" src="https://img.shields.io/badge/base-Helium-555e8a?style=flat-square">
  <img alt="Chromium 158" src="https://img.shields.io/badge/Chromium-158-555e8a?style=flat-square">
  <img alt="License GPL-3.0" src="https://img.shields.io/badge/license-GPL--3.0-555e8a?style=flat-square">
  <img alt="Status: personal project" src="https://img.shields.io/badge/status-personal%20project-b5651d?style=flat-square">
</p>

<p align="center">
  <a href="#features">Features</a> ·
  <a href="#install">Install</a> ·
  <a href="#updates">Updates</a> ·
  <a href="#how-it-works">How it works</a> ·
  <a href="#building">Building</a> ·
  <a href="#credits">Credits</a>
</p>

> **Unofficial fork.** Bluelium is not affiliated with imputnet or endorsed by
> the Helium team. Report Bluelium issues here, not on the Helium repository.

## Overview

Bluelium is a fork of [Helium](https://github.com/imputnet/helium), itself based
on ungoogled-chromium. The engine and privacy protections are Helium's;
Bluelium changes the interface: themes, toolbar, AI panel, Night mode, new tab
page, animations.

- **Personal project.** One person, no support, no warranty.
- **Largely written with AI agents.** I direct, review and test in daily use.
- **Unsigned by Apple.** The macOS app uses a self-signed certificate, without
  notarization.
- **Windows: in progress.** An x64 installer is built on GitHub Actions but
  not published until it has been tested.

For a stable browser maintained by a team, use
[Helium](https://github.com/imputnet/helium).

## Features

**Ready**: built and used daily. **Tuning**: works, still being refined.

| Feature | macOS | Linux | Details |
|---|:---:|:---:|---|
| **Prism themes** | Ready | Ready | Prism, Slate, Amber, Sage, Lilac and Rose, light and dark. Light, Dark, OLED, Night and System modes. Compact tabs and toolbar. |
| **Page color in the toolbar** | Tuning | Tuning | Frame, tabs and toolbar take a tint from the page, with a fade. Menus keep the theme colors. |
| **Night mode** | Ready | Tuning | Red-on-black interface and a warm filter on web pages. <kbd>Alt</kbd>+<kbd>Shift</kbd>+<kbd>N</kbd>. |
| **AI panel** | Ready | Ready | Claude, ChatGPT, Gemini and Le Chat in the side panel, using the profile's session. |
| **Toolbar** | Ready | Ready | Redrawn icons, pinned extensions grouped, blocker shield, customizable layout. |
| **Shimmer new tab** | Ready | Ready | [Shimmer Tab](https://github.com/dmitthedazed/shimmer-tab) built in: tab management, top sites, recently closed. |
| **Split view** | Ready | Ready | Drag a tab onto another to open both side by side. |
| **Animations** | Tuning | Tuning | Trackpad back/forward gesture, sliding tab indicator, synced toolbar color. |
| **PDF.js viewer** | Tuning | Tuning | Offline Mozilla viewer in the browser's colors ([details](docs/pdfjs.md)). |
| **Hold ⌘Q to quit** | Ready | n/a | Redrawn glass capsule with a progress gauge. |
| **Chrome Web Store** | Ready | Ready | Once Helium's extension services are enabled. |

On macOS, <kbd>Alt</kbd>+<kbd>Shift</kbd> is <kbd>⌥</kbd><kbd>⇧</kbd>.
Release notes: [`docs/patch-notes/`](docs/patch-notes/).

**Known limits**

- macOS: window buttons are not perfectly aligned with the tabs.
- Linux: install Instrument Sans yourself ([`assets/InstrumentSans.ttf`](assets/InstrumentSans.ttf)).
- The working name "Glyphe" remains in code, patches and the Linux install folder.

## Install

| | macOS (Apple Silicon) | Linux (x86_64) |
|---|---|---|
| Package | `bluelium-<version>-macos-arm64.dmg` | `Bluelium-<version>-x86_64.AppImage` or `bluelium-<version>.tar.zst` |
| Download | [Releases](https://github.com/matthieuleconte1/bluelium/releases) | [Latest release](https://github.com/matthieuleconte1/bluelium/releases/latest) |
| Updates | Built in (Sparkle, every 6 h) | AppImage: built in. Archive: see [Updates](#updates) |

Check every download against its `.sha256`.

<details>
<summary><b>macOS</b></summary>

<br>

Drag **Bluelium.app** to `~/Applications`. On first launch, right-click and
choose **Open**, or:

```sh
xattr -dr com.apple.quarantine ~/Applications/Bluelium.app
```

Bluelium runs alongside Helium with its own bundle ID
(`io.github.matthieuleconte1.bluelium`) and profile
(`~/Library/Application Support/Bluelium`). To copy your Helium profile
(tabs, bookmarks, history, extensions, passwords, cookies), quit both browsers
and run `tools/migrate-helium-macos.sh`. The Helium profile is left untouched.

</details>

<details>
<summary><b>Linux AppImage</b></summary>

<br>

```sh
chmod +x Bluelium-*.AppImage
./Bluelium-<version>-x86_64.AppImage
```

The AppImage checks for updates at launch (at most every 6 h), verifies the
SHA-256 and replaces itself if its file is writable. The new version is used
on the next launch. Disable with `BLUELIUM_NO_UPDATE=1` or by creating
`~/.config/bluelium/no-appimage-update`.

</details>

<details>
<summary><b>Linux archive</b></summary>

<br>

```sh
mkdir -p ~/Applications && tar --zstd -xf bluelium-*.tar.zst -C ~/Applications
mv ~/Applications/bluelium-* ~/Applications/helium-glyphe
~/Applications/helium-glyphe/helium-wrapper --user-data-dir="$HOME/.config/helium-glyphe"
```

The update scripts rely on the `helium-glyphe` path.
`autobuild/switch-to-bluelium.sh` moves an existing Helium profile and menu
entry to Bluelium (`--revert` to go back).

</details>

## Updates

The macOS app and the AppImage update themselves. For the Linux archive, or
for a launchd agent on macOS, install the updater once from a clone:

| | macOS | Linux |
|---|---|---|
| Install | `autobuild/install-updater-macos.sh` | `autobuild/install-updater.sh` |
| Schedule | launchd agent, every 2 h | systemd user timer, every 2 h |
| Status | `bluelium-update-macos --status` | `glyphe-update --status` |

The updater installs the new release while Bluelium is closed and keeps the
previous version next to it.

## How it works

Changes are not hand-written patches. Each one is a Python **spec** in
[`specs/`](specs/): files to create and text replacements in the Chromium
sources. [`specs/SERIES`](specs/SERIES) sets the order and can limit a spec to
`linux` or `mac`.

Each build:

1. Fetches the latest stable Helium
   ([helium-linux](https://github.com/imputnet/helium-linux) or
   [helium-macos](https://github.com/imputnet/helium-macos)).
2. Runs Helium's steps: patches, substitutions, translations, resources.
3. Applies the specs with `tools/apply-series.py` and regenerates the `.patch`
   files. A spec that no longer applies stops the build and is named.
4. Compiles, packages and publishes.

| Platform | Builder | Output |
|---|---|---|
| Linux | Build machine, nightly | AppImage and `.tar.zst`, x86_64 (arm64 builds untested) |
| macOS | GitHub Actions, nightly | Signed `.dmg` and Sparkle appcast |
| Windows | GitHub Actions, nightly | Unsigned x64 installer, published by hand after testing |

Releases are named `v<Helium version>-<color>`, for example
`v0.22.5.1-vert-celadon`. The color identifies the Bluelium patch series: same
patches, same color on macOS and Linux. It is derived from the series' last
commit, from Wikipedia's
[list of color names](https://fr.wikipedia.org/wiki/Liste_de_noms_de_couleur)
(`tools/couleur.py`). A failed build opens a GitHub issue, closed by the next
successful one.

| Folder | Contents |
|---|---|
| `specs/` | The specs, source of truth |
| `patches/glyphe/` | Generated `.patch` files |
| `tools/` | Spec tooling, profile migration, measurements |
| `scripts/` | Build and packaging scripts |
| `autobuild/` | Linux auto-build and updaters |
| `docs/` | Work notes and release notes |

## Building

Building Chromium takes hours, a lot of disk space and memory.

<details>
<summary><b>macOS, locally</b> (Xcode, 100 GB free on APFS)</summary>

<br>

Prerequisites, as for
[helium-macos](https://github.com/imputnet/helium-macos/blob/main/docs/building.md):

```sh
brew install python@3.13 wget zstd coreutils readline
python3 -m pip install requests pillow
xcodebuild -downloadComponent MetalToolchain
```

```sh
scripts/build-macos.sh                          # arm64, in ~/bluelium-build
PATCH_ONLY=1 scripts/build-macos.sh             # only check that the series applies
SKIP_FETCH=1 PGO=false scripts/build-macos.sh   # rebuild the existing tree, no PGO
PUBLISH=1 scripts/build-macos.sh                # publish the .dmg on GitHub
```

| Variable | Effect | Default |
|---|---|---|
| `BLUELIUM_MAC_WORK` | Work folder | `~/bluelium-build` |
| `HELIUM_TAG` | helium-macos version | Latest stable |
| `JOBS` | Parallel compile jobs | `8` |
| `MIN_FREE_GB` | Required free space | `100` |
| `KEEP_GOING=1` | Continue past errors | |

exFAT does not support the symlinks Chromium needs. On an exFAT drive, build
inside an APFS image:

```sh
hdiutil create -size 200g -type SPARSEBUNDLE -fs APFS \
  -volname BlueliumBuild /Volumes/MyDrive/bluelium.sparsebundle
hdiutil attach /Volumes/MyDrive/bluelium.sparsebundle
BLUELIUM_MAC_WORK=/Volumes/BlueliumBuild scripts/build-macos.sh
```

</details>

<details>
<summary><b>macOS, on GitHub Actions</b> (nightly, 15 to 20 h)</summary>

<br>

`.github/workflows/build-macos.yml` builds the latest helium-macos with the
series from `main`, unless already published. Like Helium's CI, compilation
is split into jobs under 6 h that pass the build tree along.

- **Publishing** happens only if `docs/patch-notes/<version>.html` is in
  `main`. Otherwise the `.dmg` stays in the run for 14 days and an issue says
  so; push the page, then run the workflow with **publier** set to the run ID.
- **On failure** the build state is kept, the workflow resumes once by
  itself, then opens an `auto-build-macos` issue. Resume by hand with
  **reprendre** set to the run ID.
- **Own Mac**: register it as a
  [self-hosted runner](https://docs.github.com/actions/hosting-your-own-runners)
  and set the `MACOS_RUNNER` variable to `["self-hosted","macOS"]`. No 6 h
  limit; about 120 GB free needed.

Repository secrets:

```sh
base64 -i bluelium.p12 | gh secret set MACOS_SIGN_P12   # "Bluelium Code Signing" identity
gh secret set MACOS_SIGN_P12_PASSWORD
gh secret set SPARKLE_PRIVATE_KEY < ~/.config/bluelium/sparkle-private-key
```

</details>

<details>
<summary><b>Windows, on GitHub Actions</b> (nightly, x64)</summary>

<br>

`.github/workflows/build-windows.yml` builds the latest
[helium-windows](https://github.com/imputnet/helium-windows) with the series
for `win` (`scripts/build-windows.py`), in jobs under 6 h like macOS.

- **Not published automatically.** A finished build opens an
  `auto-build-windows` issue "Windows <version> prêt à tester" linking the
  installer (run artifact `windows-paquet`, 14 days). After testing, add
  Windows to `docs/patch-notes/<version>.html`, push it, then run the workflow
  with **publier** set to the run ID.
- **On failure** an `auto-build-windows` issue is opened. Resume with
  **reprendre** set to the run ID. A manual cancel opens nothing.
- Unsigned (SmartScreen asks for confirmation), no built-in updates yet.
  Installs to `%LOCALAPPDATA%\Bluelium`, alongside Helium.

</details>

<details>
<summary><b>Linux</b> (about 250 GB of disk, 32 GB of RAM)</summary>

<br>

1. Clone [helium-linux](https://github.com/imputnet/helium-linux) and add the
   `[shimmer-tab]` and `[pdfjs]` sections of this repo's `downloads.ini` to its
   own.
2. Follow its procedure up to the end of source preparation.
3. Apply the series:

   ```sh
   python3 tools/apply-series.py <helium-linux>/build/src <this repo> <output dir> linux
   ```

4. Resume Helium's procedure to compile.

`tools/sync-builder.sh` installs the nightly auto-build on a build machine
reachable over SSH (`--now` starts it, `--patch-only` only checks the series).
The host is set in `~/.config/bluelium/builder.env`:

```sh
BLUELIUM_BUILDER=root@build-machine
BLUELIUM_JUMP=root@jump-host      # optional
```

The machine reads `GH_TOKEN` from `/root/glyphe/github.env` (scoped to this
repo, Contents and Issues write).

</details>

## Credits

- [Helium](https://github.com/imputnet/helium),
  [helium-linux](https://github.com/imputnet/helium-linux) and
  [helium-macos](https://github.com/imputnet/helium-macos) by imputnet,
  including the [Chromium source tarballs](https://github.com/imputnet/chromium-tarballs).
- ungoogled-chromium ([LICENSE.ungoogled_chromium](LICENSE.ungoogled_chromium), BSD)
  and Chromium, under their own licenses.
- [Shimmer Tab](https://github.com/dmitthedazed/shimmer-tab) by dmitthedazed (GPL-3.0).
- [PDF.js](https://github.com/mozilla/pdf.js) by Mozilla (Apache-2.0).
- Instrument Sans (SIL OFL, [license](assets/OFL-InstrumentSans.txt)).
- [Material Symbols](https://github.com/google/material-design-icons/tree/master/variablefont)
  by Google (Apache-2.0, [details](assets/icons/MATERIAL_SYMBOLS_SOURCE.md)).

Bluelium is licensed under **GPL-3.0** ([LICENSE](LICENSE)), like Helium.
Helium, Claude, ChatGPT, Gemini and Le Chat names and logos belong to their
owners; see [NOTICE.md](NOTICE.md).
