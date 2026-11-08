BUY ALL COMPONENTS  v1.0.0
Dying Light: The Beast

Adds a "Buy All Components" button to the vendor screen. One hold buys
every crafting component and crafting part the vendor sells, instead of
opening each item one by one.

Tested on game build: ph-ft patch08 (30 Oct 2026), single player.


HOW TO USE
At a vendor, HOLD the new footer button for about one second:
  - Controller: L3
  - Keyboard:   the key the button shows next to its label (the key bound
                to the pad's L3 action)

It then buys one stack roughly every quarter second and stops by itself
when nothing is left that qualifies (or after 80 steps). It only buys
items that:
  - are crafting components / crafting parts,
  - you can afford,
  - fit in your inventory,
  - are not buy-back items.
It uses the game's own "buy all" action for each item, so prices and
stack sizes are exactly what a manual purchase would give.


INSTALL
1. Close the game.
2. Copy ph_ft\source\data7.pak from this zip into the same folder in your game:
   <Steam>\steamapps\common\Dying Light The Beast\ph_ft\source\
   (or unzip the whole zip into the game's main folder and let it merge).
3. Start the game and visit a vendor.

UNINSTALL
Delete data7.pak from ph_ft\source.


NOTES
- Offline / single player only. The game checks its files at start-up
  and flags modded paks ("Bad crc" in its log). Remove the mod before
  playing online or in co-op, or every player needs the same mod files.
- Replaces one file: gui/ingame_menu_pc/menushop_pc.gui. Another mod that
  replaces that file will conflict with this one.
- A game update that changes that file can break or undo this mod. The
  source and a rebuild script (reads your own game files) are on GitHub -
  see the mod page for the link.
- data7.pak can be renamed to any other free slot, data4 to data7.
  Those four are the ones confirmed to load.


CREDITS
Made with Claude Code. Dying Light: The Beast belongs to Techland; this
mod adds one button and its logic to the vendor screen file.
