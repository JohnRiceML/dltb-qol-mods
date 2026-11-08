"""Build the Dying Light: The Beast mods from your own game files.

    python build.py [--install | --uninstall] [game_dir]

Writes dist/<Mod>-<version>.zip for each mod. Each zip holds ph_ft/source/dataN.pak plus a
README, so it can be unzipped straight into the game folder. --install / --uninstall copy or
remove the paks in your game folder directly (close the game first).

game_dir is the folder that contains ph_ft; it is found automatically for Steam installs.
"""
import importlib.util
import os
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import modkit  # noqa: E402

VERSION = "1.0.0"
MODS = (  # (folder, builder script, pak name, package name)
    ("north_up_map", "build_map_north_up.py", "data5.pak", "NorthUpMap"),
    ("buy_all_components", "build_buy_components.py", "data7.pak", "BuyAllComponents"),
)


def load(folder, script):
    path = os.path.join(HERE, folder, script)
    spec = importlib.util.spec_from_file_location(os.path.splitext(script)[0], path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_zip(path, entries):
    with zipfile.ZipFile(path, "w") as z:
        for name, data in entries:
            z.writestr(zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0)), data,
                       compress_type=zipfile.ZIP_DEFLATED)
    print(f"wrote {os.path.relpath(path, HERE)}")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    install, uninstall = "--install" in sys.argv, "--uninstall" in sys.argv
    game = modkit.resolve_game(args[0] if args else None)
    print(f"game: {game}")

    if uninstall:
        if modkit.game_running():
            raise SystemExit("Close the game first.")
        for _, _, pak, _ in MODS:
            modkit.uninstall(pak, game)
        return

    dist = os.path.join(HERE, "dist")
    for folder, script, pak, name in MODS:
        pak_path = os.path.join(dist, "paks", pak)
        modkit.write_pak(pak_path, load(folder, script).build(game))
        with open(pak_path, "rb") as f, open(os.path.join(HERE, folder, "README.txt"), "rb") as r:
            write_zip(os.path.join(dist, f"{name}-{VERSION}.zip"),
                      [(f"ph_ft/source/{pak}", f.read()), ("README.txt", r.read())])
        if install:
            if modkit.game_running():
                raise SystemExit("Close the game first.")
            modkit.install(pak_path, game)


if __name__ == "__main__":
    main()
