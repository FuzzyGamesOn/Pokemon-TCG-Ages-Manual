from worlds.AutoWorld import World
from BaseClasses import MultiWorld, CollectionState
from .functions import get_itempool_total_by_category

import math


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
