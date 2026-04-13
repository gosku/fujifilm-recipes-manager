# ADR 004 — Recipe import: browser file upload over native file picker

**Status**: Accepted
**Date**: 2026-04-12

---

## Context

### The problem

Right now, the only way to create a `FujifilmRecipe` record is by importing an image file that has a recipe encoded in its EXIF data. This is a side effect of `process_image` — the recipe is created incidentally while the image itself is the primary object being imported.

This is limiting because recipes can be shared independently of the images that contain them. A common case: someone shares a JPEG purely as a vehicle for the recipe settings — the image itself is irrelevant. There is currently no way to extract only the recipe from that file through the web UI; the user would have to run a management command.

### Management commands are not enough

Management commands work well for bulk operations and administrative tasks, but they are not a substitute for UI-level interactions. Core user workflows — including importing a recipe — need to be accessible from the browser.

### Why not reuse the image import flow

Importing a recipe from a file is superficially similar to importing an image: both start from a JPEG file. However, the two flows have a critical difference around the filepath:

- **Image import** needs the filepath to persist it on the `Image` record, so the app can locate and render the original file later. This means the file must already live somewhere stable on the filesystem — the user's photo library. The app assumes it does not own or manage those files.
- **Recipe import** does not store the filepath. Only the EXIF-derived recipe settings matter; the file is discarded after extraction.

This distinction makes a browser file upload (where the server never learns the original path) valid for recipe import but not for image import. Adapting the image import flow to accept browser uploads would require the app to also copy, store, and maintain the uploaded file — turning it into an image catalogue, which is explicitly out of scope. This approach is therefore only suitable for recipe import.

---

## Options considered

### Option A — Server-side native file dialog (tkinter / zenity)

A Django endpoint spawns an OS-level file dialog on the server (e.g. via Python's `tkinter.filedialog` or the `zenity` CLI on Linux). The dialog returns a filesystem path; the view passes it directly to the domain operation with no tempfile needed.

**Why we did not choose this option:**

1. **Architecturally wrong for a web app.** Even though the server and browser are on the same machine, mixing a GUI toolkit into a web server process is a category error. It conflates the server process with the desktop session.
2. **Ties the server to a display.** `tkinter` requires a running X or Wayland session. The app would break in any headless or SSH context.
3. **Not composable.** Future deployments (e.g. running the server as a systemd service) would silently fail when no display is available.

### Option B — Plain text input (user types or pastes the path)

A plain `<input type="text">` where the user types a filesystem path. The view receives the string and passes it directly to the domain — zero overhead, no tempfile.

**Why we did not choose this option:**

1. **Poor UX.** Typing a full filesystem path is error-prone and not a web-standard interaction.
2. **Inconsistent with web conventions.** Users expect a file picker, not a text field, for file selection.

### Option C — Tauri shell wrapping the web UI

[Tauri](https://tauri.app) is a Rust-based desktop shell that hosts a webview. It injects JS APIs (e.g. `window.__TAURI__.dialog.open()`) that call into the Rust layer, which has full OS access and can return a real filesystem path. The path is then POSTed to Django as a plain string — no tempfile needed.

**Why we did not choose this option:**

1. **Disproportionate to the problem.** Introducing a Rust build chain, Tauri packaging, and a desktop distribution model to gain a native file picker is a large architectural shift for a small UX improvement.
2. **Contradicts the project's web-based identity.** The app is deliberately web-based. Wrapping it in a desktop shell to work around a browser security boundary is the wrong trade-off.
3. **Browser's `<input type="file">` already solves the user need.** It is the web-standard mechanism for file selection and is universally understood.

### Option D — Browser `<input type="file">` with file contents upload ✓ chosen

The browser's standard file picker. The user selects a file; the browser transfers the file contents (not the path) to the server via a multipart POST. The application layer writes the contents to a tempfile and calls the domain operation with the resulting path. The tempfile is deleted when the operation completes.

---

## Decision

Use `<input type="file">` for file selection. The responsibility is split across layers:

- **Interface layer** (Django view): receives the multipart upload and reads `request.FILES["image"]` into bytes. This is a pure translation — HTTP multipart → `bytes` — with no side effects.
- **Application layer** (use case): owns the tempfile lifecycle. Writing bytes to `/tmp/` is a side-effectful OS operation with its own failure modes (permissions, disk space). It belongs in the orchestration layer, not the interface or domain.
- **Domain layer**: unchanged. `get_or_create_recipe_from_filepath(filepath=tmp.name)` is called with a plain path and has no awareness of where the file originated.

```
interface:    request.FILES["image"].read()  →  bytes        (translation: HTTP → bytes)
application:  bytes → tempfile → filepath                    (OS coordination, owns cleanup)
domain:       filepath → exif → FujifilmRecipe               (business logic, unchanged)
```

---

## Rationale

| Criterion | Native dialog | Text input | Tauri | File upload ✓ |
|---|---|---|---|---|
| Web-standard interaction | ✗ | ✗ | ✗ | ✓ |
| Works headless / as a service | ✗ | ✓ | ✗ | ✓ |
| No build toolchain beyond Python | ✓ | ✓ | ✗ | ✓ |
| No tempfile overhead | ✓ | ✓ | ✓ | ✗ |
| Domain layer unchanged | ✓ | ✓ | ✓ | ✓ |

The tempfile overhead is the only real cost. For an infrequent user action like importing a recipe, it is acceptable.

---

## Consequences

- A file is written to `/tmp/` and deleted per import request. Python's `tempfile.NamedTemporaryFile` handles cleanup automatically, including on exceptions.
- The browser's security model means the original filesystem path of the file is never available to JS or Django. This is a feature, not a limitation — it keeps the app within web conventions.
- `get_or_create_recipe_from_filepath` requires no changes.
- A new use case (e.g. `import_recipe_from_file_content`) is the correct home for the tempfile logic when it is implemented.
