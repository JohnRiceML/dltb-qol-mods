NORTH-UP MAP  v1.0.0
Dying Light: The Beast

The in-game map opens with north at the top of the screen, instead of
rotated with north in the bottom-left corner.

Tested on game build: ph-ft patch08 (30 Oct 2026), single player.


INSTALL
1. Close the game.
2. Copy ph_ft\source\data5.pak from this zip into the same folder in your game:
   <Steam>\steamapps\common\Dying Light The Beast\ph_ft\source\
   (or unzip the whole zip into the game's main folder and let it merge).
3. Start the game. Open the map.

UNINSTALL
Delete data5.pak from ph_ft\source.


NOTES
- Offline / single player only. The game checks its files at start-up
  and flags modded paks ("Bad crc" in its log). Remove the mod before
  playing online or in co-op, or every player needs the same mod files.
- Changes two files: maps/dlc_frontier/dlc_frontier.scr and
  dlc_frontier_permaworld.scr (one line each: the 3D map rotation).
  Another mod that replaces either file will conflict with this one.
- A game update that changes those files can break or undo this mod.
  The source and a rebuild script (reads your own game files) are on
  GitHub - see the mod page for the link.
- data5.pak can be renamed to any other free slot, data4 to data7.
  Those four are the ones confirmed to load.


CREDITS
Made with Claude Code. Dying Light: The Beast belongs to Techland; this
mod only changes one value in the files above.
