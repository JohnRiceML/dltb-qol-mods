# Dying Light: The Beast – quality-of-life mods

Two small single-player mods, plus the scripts that build them from your own game files.

| Mod | What it does |
|---|---|
| **North-Up Map** (`north_up_map/`) | The map opens with north at the top instead of rotated with north in the bottom-left. |
| **Buy All Components** (`buy_all_components/`) | Adds a "Buy All Components" button to the vendor screen. Hold it and the vendor's crafting components and parts you can afford and carry are bought for you, one stack at a time. |

Tested on game build `ph-ft` patch08 (30 Oct 2026), single player only.

## Install (no building needed)

Download the zips from the [Nexus page](#) or the Releases tab, then copy `ph_ft/source/data5.pak` (map) and/or `data7.pak` (shop) into

```
<Steam>\steamapps\common\Dying Light The Beast\ph_ft\source\
```

Delete the pak to uninstall. Each zip has a `README.txt` with the details.

## Build from your own game files

Requires Python 3.9+ and a Steam install of the game. Nothing from the game is stored in this repo: the scripts read `data0.pak` / `data1.pak` on your machine and change one thing in each.

```
python build.py              # writes dist/*.zip
python build.py --install    # also copies the paks into your game folder (game closed)
python build.py --uninstall  # removes them again
```

The game folder is found automatically for Steam installs. Otherwise pass it as an argument or set `DLTB_GAME`.

After a game patch, run `build.py` again. The scripts assert on the exact lines they change, so if Techland changed those files you get an error instead of a broken pak.

## How it works

- **North-Up Map** – the open-world level scripts set `f_m3d_map_ppfx_rotation` to `-90`; with the level's north at 125°, that put north in the bottom-left. The mod sets it to `125` in `dlc_frontier.scr` and `dlc_frontier_permaworld.scr`.
- **Buy All Components** – clones the vendor screen's *Sell All Valuables* footer button into a new button in `menushop_pc.gui`, and adds a small action graph: on hold, a 0.25 s timer loops over the vendor's item list, and for the first item that is a crafting component/part, buyable, affordable, fits the inventory and isn't buy-back, emits the game's own `BuyAllItems` event. It repeats until nothing qualifies (max 80 steps).

`.pak` files are plain zip files that override the same paths in the game's own paks.

## Limits

- **Offline only.** The game checks its pak files at start-up and logs `Bad crc` for modded ones. Remove the mods before playing online or in co-op, or all players need identical files.
- The mods replace whole files (`menushop_pc.gui`, the two level scripts), so they conflict with any other mod that replaces the same files.
- Only pak slots `data4`–`data7` are confirmed to load (`data8` did not).

## License

The scripts are MIT licensed (see `LICENSE`). Dying Light: The Beast and its files belong to Techland; this project is not affiliated with or endorsed by Techland.
