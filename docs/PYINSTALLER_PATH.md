# PyInstaller package path fix

The Intel macOS build command explicitly passes `--paths .` so the repository root is on the module discovery path when the entrypoint is under `packaging/`. The build still requires a real Intel macOS GitHub Actions runner and manual launch testing. This change does not sign or notarize the application.
