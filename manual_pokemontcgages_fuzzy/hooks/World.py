# Object classes from AP core, to represent an entire MultiWorld and this individual World that's part of it
from worlds.AutoWorld import World
from BaseClasses import MultiWorld, CollectionState, ItemClassification

# Object classes from Manual -- extending AP core -- representing items and locations that are used in generation
from ..Items import ManualItem
from ..Locations import ManualLocation

# Raw JSON data from the Manual apworld, respectively:
#          data/game.json, data/items.json, data/locations.json, data/regions.json
#
from ..Data import game_table, item_table, location_table, region_table

# These helper methods allow you to determine if an option has been set, or what its value is, for any player in the multiworld
from ..Helpers import is_option_enabled, get_option_value

# calling logging.info("message") anywhere below in this file will output the message to both console and log file
import logging
import re
import math
import json

from .functions import get_pack_names, get_enemy_cards

########################################################################################
## Order of method calls when the world generates:
##    1. create_regions - Creates regions and locations
##    2. create_items - Creates the item pool
##    3. set_rules - Creates rules for accessing regions and locations
##    4. generate_basic - Runs any post item pool options, like place item/category
##    5. pre_fill - Creates the victory location
##
## The create_item method is used by plando and start_inventory settings to create an item from an item name.
## The fill_slot_data method will be used to send data to the Manual client for later use, like deathlink.
########################################################################################


# Use this function to change the valid filler items to be created to replace item links or starting items.
# Default value is the `filler_item_name` from game.json
def hook_get_filler_item_name(world: World, multiworld: MultiWorld, player: int) -> str | bool:
    # let's just use anything that's a possible filler in the pool as a possible filler item name
    possible_filler_names = [
        i['name'] for i in world.item_name_to_item.values()
            if i.get('filler', False) == True
    ]

    # pick one of the fillers at random and send it back
    return world.random.choice(possible_filler_names)


# Called before regions and locations are created. Not clear why you'd want this, but it's here. Victory location is included, but Victory event is not placed yet.
def before_create_regions(world: World, multiworld: MultiWorld, player: int):
    # here, we want to set (to false) any category options that are associated with
    #   card packs that weren't included in the packs to play
    # we do this in the before_create_regions hook because it's the first hook that happens during generation
    #   so we ensure that any option changes we make are accounted for in any other Manual/normal gen steps

    # so, first, let's figure out what packs were not included...
    enabled_packs = world.options.packs.value
    all_packs = get_pack_names()
    packs_to_remove = [
        p for p in all_packs 
            if p != '_default' and p not in enabled_packs
    ]

    # ... then, we just set the corresponding category option, which we defined in our Data.py hook
    for pack in packs_to_remove:

        # getattr() lets us use a string as the property name for a class object,
        #   so it's a property we can reference by name dynamically (like below)
        pack_option = getattr(world.options, f"pack_remove_{pack}")
        pack_option.value = False


# Called after regions and locations are created, in case you want to see or modify that information. Victory location is included.
def after_create_regions(world: World, multiworld: MultiWorld, player: int):
    # here, we want to remove any locations that are associated with
    #   card packs that weren't included in the packs to play

    # so, first, let's figure out what packs were not included...
    enabled_packs = world.options.packs.value
    all_packs = get_pack_names()
    packs_to_remove = [
        p for p in all_packs 
            if p != '_default' and p not in enabled_packs
    ]
    location_names_to_remove = []

    # ... then, let's get a list of locations from those packs
    for pack in packs_to_remove:
        location_names_to_remove.extend([
            name for name, l in world.location_name_to_location.items()
                if pack in l.get('category', [])
        ])

    # finally, we loop over our regions and their locations, and remove
    #   the ones that we identified
    for region in multiworld.get_regions(player):
        for location in region.get_locations():
            if location.name in location_names_to_remove:
                region.locations.remove(location)


# The item pool before starting items are processed, in case you want to see the raw item pool at that stage
def before_create_items_starting(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    # here, we want to remove any items that are associated with
    #   card packs that weren't included in the packs to play
    # also, after that, we want to remove any items that were banned
    #   via the banned_cards YAML option

    # so, first, let's figure out what packs were not included...
    enabled_packs = world.options.packs.value
    all_packs = get_pack_names()
    packs_to_remove = [
        p for p in all_packs 
            if p != '_default' and p not in enabled_packs
    ]

    item_names_to_remove = []

    # ... then, let's get a list of items from those packs
    for pack in packs_to_remove:
        item_names_to_remove.extend([
            name for name, i in world.item_name_to_item.items()
                if pack in i.get('category', [])
        ])

    # finally, we set the item pool to be all of the items that don't have names in that list to remove
    item_pool = [
        i for i in item_pool if i.name not in item_names_to_remove
    ]

    # now, for the banned cards, let's see if any were specified and, if so,
    #   loop them and remove them from the item pool as well
    if world.options.banned_cards.value:
        for banned_card in world.options.banned_cards.value:
            found_card = [
                i for i in item_pool if i.name == banned_card
            ]

            for found in found_card:
                item_pool.remove(found)

    # okay, all done modifying the pool, make sure to return it (even if you don't modify it!)
    return item_pool


# The item pool after starting items are processed but before filler is added, in case you want to see the raw item pool at that stage
def before_create_items_filler(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    # first and briefly, this is a good place to customize your world's filler_item_name programmatically
    #   since you've be able to account for world properties, options, etc.
    # so we'll just do a quick string demo here, but you can write code to make this
    #   more random / depend on other things
    world.filler_item_name = "Ham Sandwich"


    # also, now that the usual starting items have been processed by Manual, 
    #   we say what starting items we want to start with,
    #   then we can loop over that and precollect them
    # just so happens that the starting items JSON format is nice and descriptive :)
    starting_pokemon_count = world.options.starting_pokemon_count.value # defaults to 3

    # if they put in something other than a number, make it a number and the default of 3
    if type(starting_pokemon_count) != int:
        starting_pokemon_count = 3

    starting_items = [
        {
            "item_categories": ["Supporter - Draw"],
            "random": 1
        },
        {
            "item_categories": ["Trainer - Search"],
            "random": 1
        },
        {
            "item_categories": ["Pokemon"],
            "random": starting_pokemon_count
        }
    ]

    for starting in starting_items:
        # get all items that have at least the category or categories we want
        possible_item_names = []
        
        for category in starting['item_categories']:
            possible_item_names.extend(
                # spacing out the list comprehension here maybe makes it easier to follow
                [
                    name for name, i in world.item_name_to_item.items()
                        if category in i.get("category", []) # .get() accounts for the key not existing and provides a default if it doesn't
                ]
            )
        
        # remove any duplicate names from the list of possible items
        possible_item_names = set(possible_item_names)

        # we add the list of items that have this specific category to our possible items
        possible_items = [
            i for i in item_pool 
                if i.name in possible_item_names
        ]
        
        # pick a random possible item(s) to start with, then precollect them and,
        #   since we just took them, remove them from the item pool
        for _ in range(starting['random']): # loops from 0 to starting['random'] - 1
            random_starting_item = world.random.choice(possible_items)
            multiworld.push_precollected(random_starting_item)
            possible_items.remove(random_starting_item) # don't allow choosing the exact same item again
            item_pool.remove(random_starting_item) # remove it from the pool since we're starting with it

    # once we're done, return our modified item pool
    return item_pool


# The complete item pool prior to being set for generation is provided here, in case you want to make changes to it
def after_create_items(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    # so, manual has already added filler and finalized the item pool... 
    #   but let's pretend we want to fully customize how filler is placed
    # first, let's remove *all* of the filler from the pool
    new_item_pool = [
        i for i in item_pool if i.classification != ItemClassification.filler
    ]

    # then, let's see how many fillers we need based on how many we removed
    needed = len(item_pool) - len(new_item_pool)

    # then, let's add a bunch of ham sandwich fillers instead
    for _ in range(needed):
        new_item_pool.append(world.create_item('Ham Sandwich'))

    # finally, we return our customized item pool instead of the one that was sent in
    return new_item_pool


# Called before rules for accessing regions and locations are created. Not clear why you'd want this, but it's here.
def before_set_rules(world: World, multiworld: MultiWorld, player: int):
    # like the comment above says, there's really not much that you'd want to do here
    #   set_rules comes right after create_items, and nothing notable happens
    #     between the end of create_items and the beginning of set_rules
    #     so, most of the time, you'd just use after_create_items instead
    # if you're wanting to change requirements for locations/regions, you have to do it
    #   after Manual processes the requires, and by overwriting access rules directly
    #   (as demonstrated below)
    #   (if you modify the requires strings, you're changing them for 
    #     every player of this world in a multi, not just the current one)
    pass    


# Called after rules for accessing regions and locations are created, in case you want to see or modify that information.
def after_set_rules(world: World, multiworld: MultiWorld, player: int):
    # first, we're going to customize the requirements for the victory location
    # this might look complicated, but you're only interested in two parts:
    #   1. the multiworld.get_location that gets your victory location by name
    #   2. the victory_location.access_rule = blah blah line
    # the rest is just calculations i'm doing for the requirement values i want :)

    # use the location_name_to_location lookup to find the victory location name
    #   then return the first list item in the resulting list (with next())
    #   (you can also just do the next() without the iter(list), which turns the list into an iterator,
    #      but wanted to demo it with a list because i know most next() examples don't use it)
    victory_name = next(
        iter([
            name for name, location in world.location_name_to_location.items()
                if location.get('victory') == True
        ])
    )
    victory_location = multiworld.get_location(victory_name, player) # we need to find the victory location to alter its requirements
    goal_percentage = 0.8 # for victory, the player should have received 80% of all item types
    
    # first, let's get a list of all the unique item categories from the progression items
    #   (since CollectionState only tracks progression items)
    #
    # this nested list comprehension basically says:
    #   "loop item rows and loop their category field, then 
    #      return the categories in the category field"
    # think of it as "loop from the top down, return whatever at the front" for writing it out :)
    item_categories = [
        cat for i in world.item_name_to_item.values()
            for cat in i.get('category', []) if i.get('progression') == True
    ]
    item_categories = list(set(item_categories)) # using a set removes duplicates, then we turn it back into a list
    item_categories = [cat for cat in item_categories if ' - ' in cat] # cheap way to filter for only complex categories (like "Trainer - Search")

    # next, we'll store a list of item categories and the amounts of each that match the percentage above
    goal_amounts = {} 

    for category in item_categories:
        # we can use the item_name_to_item table to look up an item's categories by the item name
        goal_amounts[category] = len([
            i for i in multiworld.get_items()
                if i.player == player and i.name != '__Victory__'
                    and category in world.item_name_to_item[i.name].get('category', [])
        ])
        # now that we have the total, apply the percentage to get the adjusted total
        goal_amounts[category] = math.floor(goal_amounts[category] * goal_percentage)

    # okay! now we need a function that checks the counts in CollectionState against the counts we want...
    def check_goal_amounts(state: CollectionState):
        # check the count per category and, if the count is off, return False as soon as we can
        for cat, count in goal_amounts.items():
            if not state.has_group(cat, player, count):
                return False
            
        return True
    
    # ... so we can set that function to the access rule on the victory location!
    victory_location.access_rule = lambda state: check_goal_amounts(state)

    #########################

    # okay, now that we demonstrated setting an access_rule on a location,
    #   let's do the same thing for a region.
    # the process for a region is a bit different because regions themselves
    #   don't have access rules
    #     rather, their entrances/exits do. we use region exits, so target those.

    region_to_change = multiworld.get_region('30 HP', player) # get the region by name from the multiworld

    # now, let's loop over the exits for that region and make the new access rule
    for region_exit in region_to_change.exits:
        # this access_rule essentially just says "this is always accessible"
        # for an example of one that uses state to calculate something, 
        #   see the victory location access_rule above
        multiworld.get_entrance(region_exit.name, player).access_rule = lambda state: True


# The item name to create is provided before the item is created, in case you want to make changes to it
def before_create_item(item_name: str, world: World, multiworld: MultiWorld, player: int) -> str:
    
    # here, we use the item's categories to figure out what classification 
    #   it should be based on our game's design
    # REMINDER: this updates all instances of the item, not just the one being created here

    # cards that unlock evolutions, are tutor or draw supporters, 
    #   or are tutor items are progression
    progression_categories = ['Pokemon', 'Supporter - Search', 'Supporter - Draw', 'Trainer - Search']
    
    item_from_table = world.item_name_to_item.get(item_name)

    # if the card's categories intersect at all with progression cats, it's progression
    if set(item_from_table.get('category', [])).intersection(progression_categories):
        item_from_table['progression'] = True

    # otherwise, the item is useful,
    #   except if it's already been flagged as filler in the item table
    elif not item_from_table.get('filler'):
        item_from_table['useful'] = True

        # remove the classifications that would override useful, 
        #   if present on the item from the item table
        for removing_classification in ['progression', 'progression_skip_balancing']:
            if removing_classification in item_from_table.keys(): # you don't have to use .keys() here, but I like how verbose it is
                del item_from_table[removing_classification]
    else:
        item_from_table['filler'] = True

    return item_name


# The item that was created is provided after creation, in case you want to modify the item
def after_create_item(item: ManualItem, world: World, multiworld: MultiWorld, player: int) -> ManualItem:
    
    # here, we use the item's categories to figure out what classification 
    #   it should be based on our game's design
    # REMINDER: this updates ONLY this instance of the item, not all items like above
    #   (and, yes, you would not do both approaches; more often than not, you'd do this one)
    
    # cards that unlock evolutions, are tutor or draw supporters, 
    #   or are tutor items are progression
    progression_categories = ['Pokemon', 'Supporter - Search', 'Supporter - Draw', 'Trainer - Search']

    item_from_table = world.item_name_to_item.get(item.name)

    # if the card's categories intersect at all with progression cats, it's progression
    if set(item_from_table.get('category', [])).intersection(progression_categories):
        item.classification = ItemClassification.progression

    # otherwise, the item is useful,
    #   except if it's already been flagged as filler in the item table
    elif not item_from_table.get('filler'):
        item.classification = ItemClassification.useful
    else:
        item.classification = ItemClassification.filler

    return item


# This method is run towards the end of pre-generation, before the place_item options have been handled and before AP generation occurs
def before_generate_basic(world: World, multiworld: MultiWorld, player: int) -> list:
    # here, we want to check the "late power pokemon" option and, if it's present and set,
    #   then we need to force the "power" pokemon (big HP ones with rule boxes) into the
    #   back half (or so) of locations
    # if it's not set, we can just return out because we then have nothing to do in this hook
    if not world.options.late_power_pokemon.value:
        return
    
    # so since the option is on, let's get a list of the item names that have
    #   EX/ex/GX/V at the end of them
    power_pokemon = [
        i for i in multiworld.get_items()
            # name ends in a space followed by EX/ex/GX/V followed by a non-numeric set abbreviation followed by a numeric set number
            if i.player == player and re.search(r'\s(EX|ex|GX|V)\s\w+\s\d+$', i.name) 
    ]

    # now, let's get the last half (or so) of locations so we can place those pokemon there
    # to make this easy, let's get the max hp available in regions currently,
    #   then cut that in half and find all the locations that have that HP or higher
    max_hp = max([
        # regions are named things like "50 HP", so 
        #   split on space and get the first split for the number
        int(r.name.split(' ')[0]) for r in multiworld.get_regions(player)
            if re.search(r'\d+ HP', r.name) # only get max of regions named "X HP"
    ])
    required_hp = math.ceil(max_hp / 2) # round down so we have more available locations
    
    # now, we find the locations that have at least the required hp
    available_locations = [
        l for l in multiworld.get_locations(player)
            if re.search(r'\d+ HP', l.name) and int(l.name.split(' ')[0]) >= required_hp
    ]

    # finally, loop over the "power" pokemon, pick locations at random, 
    #   and place the pokemon at the chosen location until there are no
    #   more "power" pokemon left
    for pp in power_pokemon:
        if len(available_locations) == 0: 
            break

        location_to_place_at = world.random.choice(available_locations)
        location_to_place_at.place_locked_item(pp) # place the item at the location...
        multiworld.itempool.remove(pp) # ... then remove it from the itempool since it doesn't need placing anymore

        # and we already chose the location at random, so remove it from our list of available locs
        available_locations.remove(location_to_place_at)


# This method is run at the very end of pre-generation, once the place_item options have been handled and before AP generation occurs
def after_generate_basic(world: World, multiworld: MultiWorld, player: int):
    # pretend that the code in before_generate_basic is here instead.
    #   ... and that's how you can use after_generate_basic.
    # because they're basically the same :P
    pass


# This is called before slot data is set and provides an empty dict ({}), in case you want to modify it before Manual does
def before_fill_slot_data(slot_data: dict, world: World, multiworld: MultiWorld, player: int) -> dict:
    # we want to pick the list of enemies based on the packs that are included,
    #   then pass that list to our custom client
    # so we'll add that list to slot data and retrieve it in the client that way

    enabled_packs = world.options.packs.value
    # seed the enemy list with the enemies in default so, if other packs are missing HPs,
    #   we at least have a default enemy to take on
    enemies = {
        card['HP']: [f"{card['Card Name']} {card['Set Name']} {card['Set Number']}"]
            for card in get_enemy_cards('_default')
    }

    for pack in get_pack_names():
        if pack not in enabled_packs:
            continue

        for card in get_enemy_cards(pack):
            enemies[card['HP']].append(f"{card['Card Name']} {card['Set Name']} {card['Set Number']}")

    # pick an enemy at random, for each HP amount, from the available options
    enemy_choices = {
        hp: world.random.choice(cards) 
            for hp, cards in enemies.items()
    }

    slot_data['enemies'] = json.dumps(enemy_choices)

    return slot_data
    

# This is called after slot data is set and provides the slot data at the time, in case you want to check and modify it after Manual is done with it
def after_fill_slot_data(slot_data: dict, world: World, multiworld: MultiWorld, player: int) -> dict:  
    # pretend this is the same as the before_fill_slot_data method above
    #   since they're interchangeable for hook usage
    return slot_data


# This is called right at the end, in case you want to write stuff to the spoiler log
def before_write_spoiler(world: World, multiworld: MultiWorld, spoiler_handle) -> None:
    ascii_art = """
    ⢀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⢻⣿⡗⢶⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣠⣄
    ⠀⢻⣇⠀⠈⠙⠳⣦⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⠶⠛⠋⣹⣿⡿
    ⠀⠀⠹⣆⠀⠀⠀⠀⠙⢷⣄⣀⣀⣀⣤⣤⣤⣄⣀⣴⠞⠋⠉⠀⠀⠀⢀⣿⡟⠁
    ⠀⠀⠀⠙⢷⡀⠀⠀⠀⠀⠉⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡾⠋⠀⠀
    ⠀⠀⠀⠀⠈⠻⡶⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣠⡾⠋⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⣼⠃⠀⢠⠒⣆⠀⠀⠀⠀⠀⠀⢠⢲⣄⠀⠀⠀⢻⣆⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⢰⡏⠀⠀⠈⠛⠋⠀⢀⣀⡀⠀⠀⠘⠛⠃⠀⠀⠀⠈⣿⡀⠀⠀⠀⠀
    ⠀⠀⠀⠀⣾⡟⠛⢳⠀⠀⠀⠀⠀⣉⣀⠀⠀⠀⠀⣰⢛⠙⣶⠀⢹⣇⠀⠀⠀⠀
    ⠀⠀⠀⠀⢿⡗⠛⠋⠀⠀⠀⠀⣾⠋⠀⢱⠀⠀⠀⠘⠲⠗⠋⠀⠈⣿⠀⠀⠀⠀
    ⠀⠀⠀⠀⠘⢷⡀⠀⠀⠀⠀⠀⠈⠓⠒⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⡇⠀⠀⠀
    ⠀⠀⠀⠀⠀⠈⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣧⠀⠀⠀
    ⠀⠀⠀⠀⠀⠈⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠁⠀
    """

    spoiler_handle.write(ascii_art + "\n") # \n is a newline, like pressing Enter on the keyboard

    spoiler_handle.write("Oh my god... \n")
    spoiler_handle.write("What did you do to Pikachu?!\n")
