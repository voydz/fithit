from __future__ import annotations

import io
import json
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from typing import Any

import typer
from rich.console import Console

from .parse import parse_content

console = Console()

DEFAULT_SEATABLE_EXTERNAL_LINK = "https://cloud.seatable.io/dtable/external-links/d08506897d274835bdab/"


def _build_download_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise typer.BadParameter("Ungültige URL. Bitte eine vollständige SeaTable-URL angeben.")

    if "download-zip" in parsed.path:
        return url

    parts = parsed.path.strip("/").split("/")
    if "external-links" not in parts:
        raise typer.BadParameter(
            "URL muss eine SeaTable External-Link-URL sein (…/dtable/external-links/<token>/)."
        )
    idx = parts.index("external-links")
    if len(parts) <= idx + 1 or not parts[idx + 1]:
        raise typer.BadParameter("External-Link-Token fehlt in der URL.")

    token = parts[idx + 1]
    return f"{parsed.scheme}://{parsed.netloc}/dtable/external-links/{token}/download-zip/"


def _download_dtable(download_url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(download_url, headers={"User-Agent": "fithit-cli"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
    except urllib.error.HTTPError as exc:
        raise typer.BadParameter(f"Download fehlgeschlagen ({exc.code}): {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise typer.BadParameter(f"Download fehlgeschlagen: {exc.reason}") from exc

    if not data:
        raise typer.BadParameter("Download leer.")
    if not data.startswith(b"PK"):
        raise typer.BadParameter("Download ist keine .dtable ZIP-Datei.")
    return data


def _load_content_from_zip(data: bytes) -> dict[str, Any]:
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            with zf.open("content.json") as f:
                return json.load(f)
    except KeyError as exc:
        raise typer.BadParameter("content.json fehlt in der .dtable Datei.") from exc
    except zipfile.BadZipFile as exc:
        raise typer.BadParameter("Download ist kein gültiges ZIP (.dtable).") from exc


def fetch_cmd(*, url: str | None, output: str | None) -> None:
    external_url = url or DEFAULT_SEATABLE_EXTERNAL_LINK
    download_url = _build_download_url(external_url)

    console.print(f"Download: {download_url}")
    data = _download_dtable(download_url)
    content = _load_content_from_zip(data)

    parse_content(content=content, source=download_url, output=output)
