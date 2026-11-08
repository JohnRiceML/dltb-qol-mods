"""Build the North-Up Map mod for Dying Light: The Beast.

The open-world level sets the 3D map's rotation to -90; with the level's
north at 125 that puts north bottom-left. Setting it to 125 puts north up.

    python -I build_map_north_up.py [--flipped] [game_dir] [out.pak]

--flipped uses -55 instead (180 degrees off), in case north ends up at the bottom.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import modkit  # noqa: E402

LEVEL_FILES = ("maps/dlc_frontier/dlc_frontier.scr", "maps/dlc_frontier/dlc_frontier_permaworld.scr")
ORIGINAL = 'VarFloat("f_m3d_map_ppfx_rotation", -90.00000000000000000000)'
NORTH_UP = 125
FLIPPED = -55


def build(game=None, flipped=False):
    src = modkit.GameFiles(game)
    new = 'VarFloat("f_m3d_map_ppfx_rotation", %d.00000000000000000000)' % (FLIPPED if flipped else NORTH_UP)
    files = {}
    for path in LEVEL_FILES:
        text = src.read_latin1(path)
        assert text.count(ORIGINAL) == 1, f"map rotation line not found in {path} - game patched?"
        files[path] = text.replace(ORIGINAL, new).encode("latin-1")
    return files


if __name__ == "__main__":
    modkit.cli(build, "data5.pak", flags=("--flipped",))
