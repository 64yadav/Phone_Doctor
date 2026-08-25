# DigiVaani Phone Doctor

A lightweight, **no-root** Android device health & cleanup companion.
Built by **64yadav** under the **DigiVaani64** brand.

Companion app to [DigiVaani PC Doctor](https://github.com/64yadav) — same
spirit, adapted for what's actually possible on Android **without root**.

## What it does (v1.0)

- 💾 **Storage overview** — total / used / free space, live progress bar
- 🔋 **Battery status** — percentage + charging state
- ⚙️ **RAM & CPU monitor** — live usage stats (where the platform allows)
- 🧹 **Large File Scan** — finds files 50MB+ in accessible storage, so you
  know what's actually eating space

## Why no Deep Clean / Service Optimizer / System Repair like the PC version?

Android sandboxes every app for security — without **root access**, an app
simply cannot touch another app's files, disable system services, or run
anything like `sfc`/`DISM`. This app intentionally stays within what a
normal, non-rooted phone allows. A root-only "Pro" version could unlock
PC Doctor-style deep cleanup later — see `docs/root-features.md` (future).

## Requirements to build

- Python 3.10+
- [Buildozer](https://buildozer.readthedocs.io/) (Linux or WSL — Buildozer
  does not build Android APKs natively on Windows)
  ```bash
  pip install buildozer
  ```
- Java JDK + Android SDK/NDK — Buildozer downloads these automatically on
  first run

## Build the APK

```bash
buildozer android debug
```

The finished APK will be at `bin/digivaanphonedoctor-1.0-debug.apk`.
Copy it to your phone and install it (you'll need to allow "Install from
unknown sources" once, since it's unsigned).

## Run on desktop (for quick testing, before building the APK)

```bash
pip install -r requirements.txt
python main.py
```

This runs the same UI in a Kivy desktop window — handy for checking layout
changes fast without a full Android build each time. Battery/RAM/CPU stats
will use desktop values instead of the phone's, since `plyer`'s battery
API is Android-only.

## Project structure

| File | Purpose |
|---|---|
| `main.py` | The entire app — UI + logic |
| `buildozer.spec` | Android build configuration (permissions, version, icon, etc.) |
| `requirements.txt` | Python packages needed |
| `icon.png` | App icon (add your own 512x512 PNG here before building) |

## License

MIT — see [LICENSE](LICENSE).

## Links

- Website: https://64yadav.github.io/DigiVaani
- GitHub: https://github.com/64yadav
- Telegram: https://t.me/DigiVaani
