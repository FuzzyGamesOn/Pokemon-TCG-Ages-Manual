from typing import Optional
from worlds.AutoWorld import World
from ..Helpers import clamp, get_items_with_value
from BaseClasses import MultiWorld, CollectionState
from .functions import get_itempool_total_by_category

import re
import math

###
# Manual's usual examples of requirement functions
#
# Scroll past that for the ones *I'm* using in this world
###

# Sometimes you have a requirement that is just too messy or repetitive to write out with boolean logic.
# Define a function here, and you can use it in a requires string with {function_name()}.
def overfishedAnywhere(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    """Has the player collected all fish from any fishing log?"""
    for cat, items in world.item_name_groups:
        if cat.endswith("Fishing Log") and state.has_all(items, player):
            return True
    return False

# You can also pass an argument to your function, like {function_name(15)}
# Note that all arguments are strings, so you'll need to convert them to ints if you want to do math.
def anyClassLevel(world: World, multiworld: MultiWorld, state: CollectionState, player: int, level: str):
    """Has the player reached the given level in any class?"""
    for item in ["Figher Level", "Black Belt Level", "Thief Level", "Red Mage Level", "White Mage Level", "Black Mage Level"]:
        if state.count(item, player) >= int(level):
            return True
    return False

# You can also return a string from your function, and it will be evaluated as a requires string.
def requiresMelee(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    """Returns a requires string that checks if the player has unlocked the tank."""
    return "|Figher Level:15| or |Black Belt Level:15| or |Thief Level:15|"


###
# Requirement functions specific to this Pokemon apworld
###

# example usage: "requires": "{hasPercentageKeySupporters(0.35)}"
def hasPercentageKeySupporters(world: World, multiworld: MultiWorld, state: CollectionState, player: int, percentage: str):
    """Creates a requirement string for needing at least X 'key' Supporters cards.
    By 'key' Supporters, we mean the ones that offer deck consistency.
    """

    percentage = float(percentage)
    if percentage < 0: percentage = 0

    # first, get all the card names that have the category "Supporter - Draw" or "Supporter - Search"
    key_supporter_cards = [
        i['name'] for i in world.item_name_to_item.values() 
            if "Supporter - Draw" in i.get("category", []) or "Supporter - Search" in i.get("category", [])
    ]

    # then, get the total number of key supporters in our item pool, 
    #   and get the amount from the provided percentage
    total_key_supporters = get_itempool_total_by_category(world, "Supporter - Draw")
    total_key_supporters += get_itempool_total_by_category(world, "Supporter - Search")
    amount = math.floor(total_key_supporters * percentage)

    # then, get a combined total of unique key Supporter cards in state and compare that to the amount we want
    return state.count_from_list_unique(key_supporter_cards, player) >= amount

# example usage: "requires": "{hasPercentagePokemon(0.1)}"
def hasPercentagePokemon(world: World, multiworld: MultiWorld, state: CollectionState, player: int, percentage: str):
    """Checks the items in state so far to see if there's at least X Pokemon cards there."""

    percentage = float(percentage)
    if percentage < 0: percentage = 0

    # get the total number of pokemon in our item pool, 
    #   and get the amount from the provided percentage
    total_pokemon = get_itempool_total_by_category(world, "Pokemon")
    amount = math.floor(total_pokemon * percentage)

    # you can just return requirement strings, as long as these functions are 
    #   called in requirements prior to set_rules
    # also, fun fact: this is essentially a no-code alternative to the above, just with different categories
    return f"(|@Pokemon:{amount}|)" # when in doubt, wrap your req func return value in parentheses

# example usage: "requires": "{hasPercentageKeyTrainers(0.142)}"
def hasPercentageKeyTrainers(world: World, multiworld: MultiWorld, state: CollectionState, player: int, percentage: str):
    """Creates a requirement string for needing at least X 'key' Trainer cards.
    By 'key' Trainers, we mean the ones that offer deck consistency.
    """

    percentage = float(percentage)
    if percentage < 0: percentage = 0

    # get the total number of key trainers in our item pool, 
    #   and get the amount from the provided percentage
    total_pokemon = get_itempool_total_by_category(world, "Trainer - Search")
    amount = math.floor(total_pokemon * percentage)

    # this is just another requirement string like the one above
    #   but with uglier string concatenation. but you can do it this way too
    return "(|@Trainer - Search:" + str(amount) + "|)"

# example usage: "requires": "{hasTotalKeySupporters(5)}"
def hasTotalKeySupporters(world: World, multiworld: MultiWorld, state: CollectionState, player: int, total: int):
    """Creates a requirement string for needing at least X 'key' Supporters cards.
    By 'key' Supporters, we mean the ones that offer deck consistency.
    """

    # first, get all the card names that have the category "Supporter - Draw" or "Supporter - Search"
    key_supporter_cards = [
        i['name'] for i in world.item_name_to_item.values() 
            if "Supporter - Draw" in i.get("category", []) or "Supporter - Search" in i.get("category", [])
    ]

    # then, get a combined total of unique key Supporter cards and compare that to the total we want
    return state.count_from_list_unique(key_supporter_cards, player) >= total

# example usage: "requires": "{hasTotalPokemon(10)}"
def hasTotalPokemon(world: World, multiworld: MultiWorld, state: CollectionState, player: int, total: int):
    """Checks the items in state so far to see if there's at least X Pokemon cards there."""

    # you can just return requirement strings, as long as these functions are 
    #   called in requirements prior to set_rules
    # also, fun fact: this is essentially a no-code alternative to the above, just with different categories
    return f"(|@Pokemon:{total}|)" # when in doubt, wrap your req func return value in parentheses

# example usage: "requires": "{hasTotalKeyTrainers(8)}"
def hasTotalKeyTrainers(world: World, multiworld: MultiWorld, state: CollectionState, player: int, total: int):
    """Creates a requirement string for needing at least X 'key' Trainer cards.
    By 'key' Trainers, we mean the ones that offer deck consistency.
    """

    # this is just another requirement string like the one above
    #   but with uglier string concatenation. but you can do it this way too
    return "(|@Trainer - Search:" + total + "|)"



def ItemValue(world: World, multiworld: MultiWorld, state: CollectionState, player: int, args: str):
    """When passed a string with this format: 'valueName:int',
    this function will check if the player has collect at least 'int' valueName worth of items\n
    eg. {ItemValue(Coins:12)} will check if the player has collect at least 12 coins worth of items
    """

    args_list = args.split(":")
    if not len(args_list) == 2 or not args_list[1].isnumeric():
        raise Exception(f"ItemValue needs a number after : so it looks something like 'ItemValue({args_list[0]}:12)'")
    args_list[0] = args_list[0].lower().strip()
    args_list[1] = int(args_list[1].strip())

    if not hasattr(world, 'item_values_cache'): #Cache made for optimization purposes
        world.item_values_cache = {}

    if not world.item_values_cache.get(player, {}):
        world.item_values_cache[player] = {
            'state': {},
            'count': {},
            }

    if (args_list[0] not in world.item_values_cache[player].get('count', {}).keys()
            or world.item_values_cache[player].get('state') != dict(state.prog_items[player])):
        #Run First Time or if state changed since last check
        existing_item_values = get_items_with_value(world, multiworld, args_list[0])
        total_Count = 0
        for name, value in existing_item_values.items():
            count = state.count(name, player)
            if count > 0:
                total_Count += count * value
        world.item_values_cache[player]['count'][args_list[0]] = total_Count
        world.item_values_cache[player]['state'] = dict(state.prog_items[player]) #save the current gotten items to check later if its the same
    return world.item_values_cache[player]['count'][args_list[0]] >= args_list[1]


# Two useful functions to make require work if an item is disabled instead of making it inaccessible
def OptOne(world: World, multiworld: MultiWorld, state: CollectionState, player: int, item: str, items_counts: Optional[dict] = None):
    """Check if the passed item (with or without ||) is enabled, then this returns |item:count|
    where count is clamped to the maximum number of said item in the itempool.\n
    Eg. requires: "{OptOne(|DisabledItem|)} and |other items|" become "|DisabledItem:0| and |other items|" if the item is disabled.
    """
    if item == "":
        return "" #Skip this function if item is left blank
    if not items_counts:
        items_counts = world.get_item_counts()

    require_type = 'item'

    if '@' in item[:2]:
        require_type = 'category'

    item = item.lstrip('|@$').rstrip('|')

    item_parts = item.split(":")
    item_name = item
    item_count = '1'

    if len(item_parts) > 1:
        item_name = item_parts[0]
        item_count = item_parts[1]

    if require_type == 'category':
        if item_count.isnumeric():
            #Only loop if we can use the result to clamp
            category_items = [item for item in world.item_name_to_item.values() if "category" in item and item_name in item["category"]]
            category_items_counts = sum([items_counts.get(category_item["name"], 0) for category_item in category_items])
            item_count = clamp(int(item_count), 0, category_items_counts)
        return f"|@{item_name}:{item_count}|"
    elif require_type == 'item':
        if item_count.isnumeric():
            item_current_count = items_counts.get(item_name, 0)
            item_count = clamp(int(item_count), 0, item_current_count)
        return f"|{item_name}:{item_count}|"

# OptAll check the passed require string and loop every item to check if they're enabled,
def OptAll(world: World, multiworld: MultiWorld, state: CollectionState, player: int, requires: str):
    """Check the passed require string and loop every item to check if they're enabled,
    then returns the require string with items counts adjusted using OptOne\n
    eg. requires: "{OptAll(|DisabledItem| and |@CategoryWithModifedCount:10|)} and |other items|"
    become "|DisabledItem:0| and |@CategoryWithModifedCount:2| and |other items|" """
    requires_list = requires

    items_counts = world.get_item_counts()

    functions = {}
    if requires_list == "":
        return True
    for item in re.findall(r'\{(\w+)\(([^)]*)\)\}', requires_list):
        #so this function doesn't try to get item from other functions, in theory.
        func_name = item[0]
        functions[func_name] = item[1]
        requires_list = requires_list.replace("{" + func_name + "(" + item[1] + ")}", "{" + func_name + "(temp)}")
    # parse user written statement into list of each item
    for item in re.findall(r'\|[^|]+\|', requires):
        itemScanned = OptOne(world, multiworld, state, player, item, items_counts)
        requires_list = requires_list.replace(item, itemScanned)

    for function in functions:
        requires_list = requires_list.replace("{" + function + "(temp)}", "{" + func_name + "(" + functions[func_name] + ")}")
    return requires_list

# Rule to expose the can_reach_location core function
def canReachLocation(world: World, multiworld: MultiWorld, state: CollectionState, player: int, location: str):
    """Can the player reach the given location?"""
    if state.can_reach_location(location, player):
        return True
    return False
