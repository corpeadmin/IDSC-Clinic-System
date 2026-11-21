"""Package the built SPA and same-origin API routes using Vercel Build Output v3."""

import json
import os
import shutil
from pathlib import Path
from urllib.parse import urlsplit


def https_origin(value):
    parsed = urlsplit(value)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password
            or parsed.path not in ("", "/") or parsed.query or parsed.fragment
            or parsed.hostname in ("localhost", "127.0.0.1", "::1")):
        raise ValueError("Set an HTTPS public origin without credentials, paths or queries.")
    return value.rstrip("/")


def prepare(root, backend_origin):
    backend = https_origin(backend_origin)
    root = Path(root).resolve()
    source = root / "frontend" / "dist"
    output = root / ".vercel" / "output"
    if not (source / "index.html").is_file():
        raise ValueError("Build frontend/dist before packaging the release.")
    if source.is_symlink() or any(path.is_symlink() for path in source.rglob("*")):
        raise ValueError("The frontend build must not contain symbolic links.")
    # Output is an ignored build directory, never a source or private env folder.
    if output.exists():
        raise ValueError("Build output already exists; use a fresh release checkout.")
    output.mkdir(parents=True)
    shutil.copytree(source, output / "static")
    routes = [
        {"src": "^/(api(?:/.*)?|admin(?:/.*)?|docs/?|health/?|static(?:/.*)?)$",
         "dest": backend + "/$1", "headers": {"Cache-Control": "no-store"}},
        {"handle": "filesystem"},
        {"src": "^/.*$", "dest": "/index.html", "headers": {"Cache-Control": "no-store"}},
    ]
    (output / "config.json").write_text(json.dumps({"version": 3, "routes": routes}, indent=2), encoding="utf-8")
    return output


if __name__ == "__main__":
    try:
        result = prepare(Path(__file__).resolve().parents[1], os.environ["CLINIC_BACKEND_ORIGIN"])
    except (KeyError, ValueError) as exc:
        raise SystemExit(str(exc)) from None
    print("Prepared static website and same-origin API/Swagger/health/admin routes.")
