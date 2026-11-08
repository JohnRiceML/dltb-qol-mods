"""Build the "Buy All Components" shop button mod for Dying Light: The Beast.

Adds a footer button to the vendor screen (hold the key bound to the pad's L3 action).
Every 0.25 s it buys one stack of a craft component the vendor sells, using
the game's own BuyAllItems action, until nothing qualifies (or 80 steps).

    python -I build_buy_components.py [game_dir] [out.pak]
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import modkit  # noqa: E402

GUI = "gui/ingame_menu_pc/menushop_pc.gui"

BTN_ID = "btn_buy_components"
BTN_TEXT = "Buy All Components"
PRESS_ACTION = "_ACTION_GUI_PAD_L3"   # L3 on controller, Z on keyboard
HOLD_TIME = "1.000000"
STEP_DELAY = "0.250000"
MAX_STEPS = "80"
COMPONENT_CATEGORIES = ("CraftComponent", "CraftPart")


def build_nodes(first_id, root_uuid, btn_uuid):
    ids = iter(range(first_id, first_id + 100))
    n = {k: next(ids) for k in (
        "press", "reset_steps", "timer", "on_timer", "clear_bought", "seq",
        "cats", "for_cats", "not_bought", "get_bought", "cat_branch", "cat_data",
        "for_items", "item_branch", "item", "is_comp", "and_comp_buy",
        "and_afford_fit", "not_buyback", "has_count", "and_buyback_count",
        "and_all", "buy_branch", "set_bought", "buy",
        "after_branch", "get_bought2", "get_steps", "inc_steps", "set_steps",
        "steps_ok", "continue_branch")}

    def var(field):
        return {"type": "GuiComponent", "element": ".", "element_uuid": root_uuid,
                "component_class": "gui::ILogicComponent", "field": field}

    def src(node, prop, value=""):
        return {"src_node": n[node], "src_prop": prop, "value": value}

    shop_ctx = {"type": "DataContext", "class": "MenuShopController"}
    x = [0]

    def meta():
        x[0] += 300
        return {"x": -6000.0 + x[0], "y": 9000.0}

    nodes = [
        {"type": "CActionOnButtonPress", "id": n["press"], "Next": n["reset_steps"],
         "field_path": {"type": "GuiComponent", "element": f"screen/footer/btns/{BTN_ID}",
                        "element_uuid": btn_uuid, "component_class": "gui::IButtonComponent"}},
        {"type": "CActionSetInt", "id": n["reset_steps"], "Value": {"value": "0"},
         "Next": n["timer"], "field_path": var("bulk_steps")},
        {"type": "CActionStartTimer", "id": n["timer"], "Duration": {"value": STEP_DELAY},
         "TickInterval": {"value": "0.000000"}, "Loop": {"value": "0"}, "StopPrevious": {"value": "1"}},
        {"type": "CActionOnTimerFinished", "id": n["on_timer"], "Next": n["clear_bought"],
         "Timer": src("timer", "Timer")},
        {"type": "CActionSetBool", "id": n["clear_bought"], "Value": {"value": "0"},
         "Next": n["seq"], "field_path": var("bulk_bought")},
        {"type": "CActionSequence", "id": n["seq"], "Action0": n["for_cats"],
         "Action1": n["after_branch"], "sequence": ["Action1"]},
        # for each category on the vendor list
        {"type": "CActionGetRawPtrVector", "id": n["cats"],
         "field_path": dict(shop_ctx, datasource_path="m_ItemList", field="m_Categories"),
         "ptr_class": "GuiItemListCategory"},
        {"type": "CActionForEach", "id": n["for_cats"],
         "wc_spec_type": [{"wc_id": 0, "wc_type_vec": "RawPtr", "wc_type_nvec": "RawPtrVector",
                           "wc_subtype": "GuiItemListCategory"}],
         "Loop": n["cat_branch"], "Vector": src("cats", "Value")},
        {"type": "CActionGetBool", "id": n["get_bought"], "field_path": var("bulk_bought")},
        {"type": "CActionNot", "id": n["not_bought"], "Value": src("get_bought", "Value", "0")},
        {"type": "CActionBranch", "id": n["cat_branch"], "Condition": src("not_bought", "Result", "1"),
         "True": n["for_items"]},
        {"type": "CActionDecomposeClass", "id": n["cat_data"], "Pointer": src("for_cats", "Elem"),
         "rtti": "GuiItemListCategory"},
        # for each item in the category: stop looking once something was bought this step
        {"type": "CActionForEach", "id": n["for_items"],
         "wc_spec_type": [{"wc_id": 0, "wc_type_vec": "RawPtr", "wc_type_nvec": "RawPtrVector",
                           "wc_subtype": "GuiInventoryItemData"}],
         "Loop": n["item_branch"], "Vector": src("cat_data", "m_Items")},
        {"type": "CActionBranch", "id": n["item_branch"], "Condition": src("not_bought", "Result", "1"),
         "True": n["buy_branch"]},
        {"type": "CActionDecomposeClass", "id": n["item"], "Pointer": src("for_items", "Elem"),
         "rtti": "GuiShopItemData"},
        None,  # is_comp: written as raw text below (needs duplicate wc_subtype keys like the game's files)
        {"type": "CActionAnd", "id": n["and_comp_buy"], "Value1": src("is_comp", "Result", "0"),
         "Value2": src("item", "m_CanBuy", "0")},
        {"type": "CActionAnd", "id": n["and_afford_fit"], "Value1": src("item", "m_CanAfford", "0"),
         "Value2": src("item", "m_DoesFitIntoInv", "0")},
        {"type": "CActionNot", "id": n["not_buyback"], "Value": src("item", "m_IsBuybackItem", "0")},
        {"type": "CActionCompareInt", "id": n["has_count"], "Value1": src("item", "m_AffordsCount", "0"),
         "Value2": {"value": "0"}, "Comparator": {"value": "Greater"}},
        {"type": "CActionAnd", "id": n["and_buyback_count"], "Value1": src("not_buyback", "Result", "0"),
         "Value2": src("has_count", "Result", "0")},
        {"type": "CActionAnd", "id": n["and_all"], "Value1": src("and_comp_buy", "Result", "0"),
         "Value2": src("and_afford_fit", "Result", "0")},
    ]
    final_and = next(ids)
    nodes += [
        {"type": "CActionAnd", "id": final_and, "Value1": src("and_all", "Result", "0"),
         "Value2": src("and_buyback_count", "Result", "0")},
        {"type": "CActionBranch", "id": n["buy_branch"],
         "Condition": {"src_node": final_and, "src_prop": "Result", "value": "0"}, "True": n["set_bought"]},
        {"type": "CActionSetBool", "id": n["set_bought"], "Value": {"value": "1"}, "Next": n["buy"],
         "field_path": var("bulk_bought")},
        {"type": "CActionEmitGameDataEvent", "id": n["buy"], "m_Action": {"value": "BuyAllItems"},
         "m_Index": src("item", "m_Index", "0"), "m_SlotType": src("item", "m_SlotType", "Unknown"),
         "m_Count": {"value": "1"}, "m_NewFilterType": {"value": "All"},
         "m_TradeOutcome": {"value": "Unknown"}, "field_path": shop_ctx, "msg_rtti": "MenuShopActionEvent"},
        # after the scan: if something was bought, wait and go again (up to MAX_STEPS)
        {"type": "CActionGetBool", "id": n["get_bought2"], "field_path": var("bulk_bought")},
        {"type": "CActionBranch", "id": n["after_branch"], "Condition": src("get_bought2", "Value", "0"),
         "True": n["set_steps"]},
        {"type": "CActionGetInt", "id": n["get_steps"], "field_path": var("bulk_steps")},
        {"type": "CActionAddInt", "id": n["inc_steps"], "Value1": src("get_steps", "Value", "0"),
         "Value2": {"value": "1"}},
        {"type": "CActionSetInt", "id": n["set_steps"], "Value": src("inc_steps", "Result", "0"),
         "Next": n["continue_branch"], "field_path": var("bulk_steps")},
        {"type": "CActionCompareInt", "id": n["steps_ok"], "Value1": src("get_steps", "Value", "0"),
         "Value2": {"value": MAX_STEPS}, "Comparator": {"value": "Less"}},
        {"type": "CActionBranch", "id": n["continue_branch"], "Condition": src("steps_ok", "Result", "0"),
         "True": n["timer"]},
    ]
    parts = []
    for node in nodes:
        if node is None:
            cases = ",".join(f'"{c}":{{"value":"1"}}' for c in COMPONENT_CATEGORIES)
            sv = ",".join(f'{{"switch_name":"{c}","switch_val_keyword":"{c}"}}' for c in COMPONENT_CATEGORIES)
            parts.append(
                '{"type":"CActionSelectUsingEnum","id":%d,"wc_spec_type":[{"wc_id":0,"wc_type_vec":"Bool",'
                '"wc_type_nvec":"BoolVector"},{"wc_id":1,"wc_type_vec":"Enum","wc_type_nvec":"Unknown",'
                '"wc_subtype":"EItemCategory","wc_subtype":"EItemCategory"}],"Selector":{"src_node":%d,'
                '"src_prop":"m_InternalItemCategory","value":"Unknown"},%s,"Default":{"value":"0"},'
                '"meta":{"x":-6000.0,"y":9300.0},"switch_val":[%s],"enum_data_name":"EItemCategory"}'
                % (n["is_comp"], n["item"], cases, sv))
        else:
            node = dict(node)
            node["meta"] = meta()
            parts.append(json.dumps(node, separators=(",", ":")))
    return ",".join(parts)


def patch_gui(gui):
    assert BTN_ID not in gui, "button already present"
    root = json.loads(gui)
    root_uuid = root["uuid"]

    # 1) footer button: clone Sell All Valuables, retarget it
    s, e = modkit.object_span(gui, '"Id":"btn_sell_all_valuables"')
    btn = json.loads(gui[s:e])
    btn_uuid = modkit.stable_uuid(BTN_ID)
    btn["uuid"], btn["Id"] = btn_uuid, BTN_ID
    for c in btn["components"]:
        if c["class"] == "gui::ILogicComponent":
            c["dyn_fields"] = [{"name": "button_icon", "type": "string", "value": f"%KEY({PRESS_ACTION})"},
                               {"name": "button_text", "type": "string", "value": BTN_TEXT}]
        if c["class"] == "gui::IButtonComponent":
            c["PressAction"], c["HoldTime"] = PRESS_ACTION, HOLD_TIME
    gui = gui[:e] + "," + json.dumps(btn, separators=(",", ":")) + gui[e:]

    # 2) screen variables used as loop state
    m = re.search(r'"type":"CVariablesComponentSymbolData","dyn_fields":\[', gui)
    gui = (gui[:m.end()] + '{"name":"bulk_bought","type":"bool","value":"0"},'
           '{"name":"bulk_steps","type":"int","value":"0"},' + gui[m.end():])

    # 3) action graph nodes
    m = re.search(r'"type":"CActionGraphSymbolData","uuid":"[^"]+","hash":"[^"]*","nodes":\[', gui)
    graph_start = m.end()
    first_id = max(int(i) for i in re.findall(r'"id":(\d+),', gui)) + 1
    gui = gui[:graph_start] + build_nodes(first_id, root_uuid, btn_uuid) + "," + gui[graph_start:]

    json.loads(gui)  # still valid JSON
    return gui


def build(game=None):
    text, bom = modkit.GameFiles(game).read_utf8(GUI)
    return {GUI: modkit.encode_utf8(patch_gui(text), bom)}


if __name__ == "__main__":
    modkit.cli(build, "data7.pak")
