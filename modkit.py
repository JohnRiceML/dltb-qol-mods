"""Shared helpers for the Dying Light: The Beast mod builders.

Every builder exposes build(game) -> {path_in_pak: bytes}; this module reads
the game's original files, writes .pak files and installs them.
"""
import filecmp
import os
import re
import shutil
import subprocess
import uuid
import zipfile

GAME_DIR = "Dying Light The Beast"
GAME_EXE = "DyingLightGame_TheBeast_x64_rwdi.exe"


def source_dir(game):
    return os.path.join(game, "ph_ft", "source")


def find_game():
    """Steam install folder: $DLTB_GAME, else the first Steam library that has the game (None if not found)."""
    env = os.environ.get("DLTB_GAME")
    if env:
        return env
    libraries = []
    for var in ("ProgramFiles(x86)", "ProgramFiles"):
        steam = os.path.join(os.environ.get(var, ""), "Steam")
        libraries.append(steam)
        vdf = os.path.join(steam, "steamapps", "libraryfolders.vdf")
        if os.path.exists(vdf):
            with open(vdf, encoding="utf-8", errors="replace") as f:
                libraries += [p.replace("\\\\", "\\") for p in re.findall(r'"path"\s+"([^"]+)"', f.read())]
    for lib in libraries:
        game = os.path.join(lib, "steamapps", "common", GAME_DIR)
        if os.path.isdir(source_dir(game)):
            return game
    return None


DEFAULT_GAME = find_game()


def resolve_game(game=None):
    game = game or DEFAULT_GAME
    if not game or not os.path.isdir(source_dir(game)):
        raise SystemExit(
            "Could not find Dying Light: The Beast.\n"
            "Pass the game folder (the one that contains ph_ft) as an argument, or set DLTB_GAME.")
    return game


class GameFiles:
    """Read-only access to the original files in data0.pak / data1.pak."""

    def __init__(self, game=None):
        game = resolve_game(game)
        self.paks = [zipfile.ZipFile(os.path.join(source_dir(game), p)) for p in ("data0.pak", "data1.pak")]

    def read(self, path):
        for pak in self.paks:
            try:
                return pak.read(path)
            except KeyError:
                pass
        raise KeyError(f"{path} not found in data0.pak/data1.pak")

    def read_utf8(self, path):
        """Returns (text, had_bom) so the BOM can be written back unchanged."""
        raw = self.read(path)
        return raw.decode("utf-8-sig"), raw.startswith(b"\xef\xbb\xbf")

    def read_latin1(self, path):
        return self.read(path).decode("latin-1")


def encode_utf8(text, bom):
    return (b"\xef\xbb\xbf" if bom else b"") + text.encode("utf-8")


def stable_uuid(name):
    """Same name -> same GUI uuid, so rebuilds produce identical files."""
    return "{%s}" % uuid.uuid5(uuid.NAMESPACE_URL, "dltb-mod/" + name)


def object_span(text, marker, start_tag='{"class":'):
    """(start, end) of the JSON object that directly contains marker."""
    s = text.rindex(start_tag, 0, text.index(marker))
    return s, brace_end(text, s)


def brace_end(text, start):
    """Index just past the {...} object that begins at text[start] (string-aware)."""
    depth, in_str, esc = 0, False, False
    for j in range(start, len(text)):
        c = text[j]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return j + 1
    raise ValueError(f"unbalanced object at {start}")


def write_pak(out_path, files):
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with zipfile.ZipFile(out_path, "w") as out:
        for path, data in files.items():
            # fixed timestamp: identical content always gives an identical pak
            out.writestr(zipfile.ZipInfo(path, date_time=(1980, 1, 1, 0, 0, 0)), data,
                         compress_type=zipfile.ZIP_DEFLATED)
    print(f"wrote {out_path} ({len(files)} file(s))")


def game_running():
    try:
        tasks = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {GAME_EXE}"],
                               capture_output=True, text=True, check=False).stdout
    except FileNotFoundError:  # not on Windows
        return False
    return GAME_EXE.lower() in tasks.lower()


def install(pak_path, game=None):
    """Copy a built pak into ph_ft/source (skipped when identical)."""
    dest = os.path.join(source_dir(resolve_game(game)), os.path.basename(pak_path))
    if os.path.exists(dest) and filecmp.cmp(pak_path, dest, shallow=False):
        print(f"{os.path.basename(dest)}: already up to date")
        return
    shutil.copyfile(pak_path, dest)
    print(f"{os.path.basename(dest)}: installed")


def uninstall(pak_name, game=None):
    """Remove a mod pak from ph_ft/source."""
    dest = os.path.join(source_dir(resolve_game(game)), pak_name)
    if os.path.exists(dest):
        os.remove(dest)
        print(f"{pak_name}: removed")
    else:
        print(f"{pak_name}: not installed")


def cli(build, default_out, flags=()):
    """Standard builder entry point: [--flag ...] [game_dir] [out.pak]."""
    import sys
    args = [a for a in sys.argv[1:] if a not in flags]
    opts = {f.lstrip("-").replace("-", "_"): f in sys.argv for f in flags}
    game = args[0] if args else None
    out = args[1] if len(args) > 1 else default_out
    write_pak(out, build(game, **opts))
