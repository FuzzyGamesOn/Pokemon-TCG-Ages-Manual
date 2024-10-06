import math

from worlds.AutoWorld import World

# added some convenience functions in here so we can access them from any hook files
from .functions import get_pack_names, get_cards, get_hp_distribution, get_hp_distribution_percentages, show_output

# called after the game.json file has been loaded
def after_load_game_file(game_table: dict) -> dict:
    """
    You can either operate on existing values from your game.json (in game_table), or write completely new ones like I do here.
    """
    
    # you can assign all of the keys below to this inside the {}, but demonstrating assigning single key-values at a time
    game_table = {}
    game_table['game'] = 'PokemonTCGAges'
    game_table['creator'] = 'Fuzzy'
    game_table['filler_item_name'] = 'favorite Digimon card' # looks funnier in the client, probably
    
    # we could set starting items here but, for education purposes, 
    #    we'll do dynamic starting items in a different hook instead

    return game_table

# called after the items.json file has been loaded, before any item loading or processing has occurred
# if you need access to the items after processing to add ids, etc., you should use the hooks in World.py
def after_load_item_file(item_table: list) -> list:
    """
    You can either operate on existing values from your items.json (in item_table), or write completely new ones like I do here.
    """

    item_table = []

    for pack in get_pack_names():
        for card in get_cards(pack):
            # don't worry about item classification, it'll be set later from the metadata stored here
            # to avoid issues with validation, set everything here to prog
            item_root_type = card['Card Type'].split(' - ')[0].strip()

            item_table.append({
                'name': f"{card['Card Name']} {card['Set Name']} {card['Set Number']}",
                'category': [
                    item_root_type, card['Card Type'], card['Set Name'], pack
                ],
                'progression': True, # capitalized in Python, not in JSON
                'metadata': card
            })

    # let's make up some item names that we wouldn't mind be used as filler by get_filler_item_name()
    possible_filler_names = [
        'Exodia the Flatulent One', 
        'Ham Sandwich', 
        'Chair For My Chair To Sit On',
        'Chris Pratt starring as Ash Ketchum',
        'Play Two Energy and See If The Opponent Notices'
    ]

    for filler_name in possible_filler_names:
        item_table.append({
            'name': filler_name,
            'category': [],
            'filler': True, # capitalized in Python, not in JSON
            'count': 0, # we want the items defined only so we can 
            'metadata': {} # we have no metadata because we made this item up
        })

    show_output(f"Loaded {len(item_table)} items.")

    return item_table

# called after the locations.json file has been loaded, before any location loading or processing has occurred
# if you need access to the locations after processing to add ids, etc., you should use the hooks in World.py
def after_load_location_file(location_table: list) -> list:
    """
    You can either operate on existing values from your locations.json (in location_table), or write completely new ones like I do here.
    """

    location_table = []
    normal_trials = []
    challenge_trials = []
    challenge_trial_types = ['No Supporters', 'No Trainers', 'No Special Energy', 'Bench - Max 3', 'Bench - Max 2']

    for pack in get_pack_names():
        # for the levels, we want half as many "normal trials" and half as many "challenge trials" (where some disadvantage is imposed on the player)
        for hp, count in get_hp_distribution(pack).items():
            if int(hp) == 0: # skip the cards that don't have HP at all (non-creature cards)
                continue

            padded_hp = str(hp).rjust(3, '0') # add fluff to left side of smaller hp categories so they sort better
            count = math.ceil(count / 2) # to have half for use in trials, rounded up
            
            for x in range(count):
                normal_trials.append({
                    'name': f'{hp} HP - Trial {x + 1}',
                    'region': f'{hp} HP',
                    'category': [f'{padded_hp} HP', 'Normal Trial', pack]
                    # could add requirements here, but just going to let the regions handle it    
                }) # range starts at 0, so increment by 1

            for htrial in challenge_trial_types:
                challenge_trials.append({
                    'name': f'{hp} HP - {htrial} Challenge',
                    'region': f'{hp} HP',
                    'category': [f'{padded_hp} HP', 'Challenge Trial', pack]
                    # could add requirements here, but just going to let the regions handle it
                })

    location_table.extend(normal_trials) # add the normal trials to the location table
    location_table.extend(challenge_trials) # add the challenge trials to the location table

    # we want to be sure to add a victory location with requirements,
    #   so the playthrough doesn't instantly beat the game
    location_table.append({
        'name': 'Did We Catch Them All?!',
        'category': ['** Victory **'], 

        # for the requires for victory, let's use the same rule functions we use below
        #   but with sufficient high percentages (like 90% or so)
        # just like below, AND.join is just a fancy way to put each row together with ANDs in between
        'requires': " AND ".join([
                        "{hasPercentageKeySupporters(0.9)}",
                        "{hasPercentageKeyTrainers(0.9)}",
                        "{hasPercentagePokemon(0.9)}",
                    ]),

        'victory': True
    })

    show_output(f"Loaded {len(location_table)} locations.")

    return location_table

# called after the locations.json file has been loaded, before any location loading or processing has occurred
# if you need access to the locations after processing to add ids, etc., you should use the hooks in World.py
def after_load_region_file(region_table: dict) -> dict:
    """
    You can either operate on existing values from your regions.json (in region_table), or write completely new ones like I do here.
    """

    region_table = {}

    for pack in get_pack_names():
        for hp, perc in get_hp_distribution_percentages(pack).items():
            hp = int(hp)
            
            if hp == 0: # skip the cards that don't have HP at all (non-creature cards)
                continue

            region_name = f'{hp} HP'
            region_table[region_name] = {
                "starting": True
            }

            # anything below 60 HP is the "intro" locations, 
            #   which you should be able to beat without hardly any received cards
            if hp >= 60:
                # fancy way of making your requires a list and then joining them with the word " AND " between them
                #   also, the %X % () syntax is an alternate way of formatting Python strings (use %s for strings),
                #     and the %.Df part specifically formats numbers to D decimal places
                region_table[region_name]['requires'] = " AND ".join([
                    "{hasPercentageKeySupporters(%.2f)}" % (perc),
                    "{hasPercentageKeyTrainers(%.2f)}" % (perc),
                    "{hasPercentagePokemon(%.2f)}" % (perc),
                ])
                
    show_output(f"Loaded {len(region_table.keys())} regions.")

    # we can verify our requires by listing them out and putting newlines in between
    show_output("\n".join([
        f"{name}: {r.get('requires', 'none')}" for name, r in region_table.items()
    ]))

    return region_table

# called after the categories.json file has been loaded
def after_load_category_file(category_table: dict) -> dict:
    """
    You can either operate on existing values from your categories.json (in category_table), or write completely new ones like I do here.
    """

    category_table = {}
    card_categories = []
    pack_categories = []

    # list the categories that we want to hide
    categories_to_hide = ['Normal Trial', 'Challenge Trial']
    
    for pack in get_pack_names():
        # we also want to hide any set name categories on the cards themselves
        card_categories.extend([
            card['Set Name'] for card in get_cards(pack)
        ])
        # we ALSO want to hide any subcategories, like "Pokemon - Lightning" or "Supporter - Search"
        card_categories.extend([
            card['Card Type'] for card in get_cards(pack) if ' - ' in card['Card Type']
        ])
        # finally, let's hide pack names too
        pack_categories.append(pack)

    # we use a set to remove any duplicates...
    card_categories = set(card_categories)
    # ... then we turn that set back into a list to add it to the end of the categories_to_hide list
    categories_to_hide.extend(list(card_categories)) # add the list of set categories to our list to hide
    categories_to_hide.extend(pack_categories) # ... and add the pack names too

    # hide the categories that we don't want to show in the client
    for category_to_hide in categories_to_hide:
        category_table[category_to_hide] = {
            'hidden': True
        }

        # if the category is a pack category, give it a yaml option to disable it
        #   so we can demonstrate setting category options from other options we defined later :)
        if category_to_hide in pack_categories and category_to_hide != '_default':
            category_table[category_to_hide]['yaml_option'] = [
                f"pack_remove_{category_to_hide}"
            ]

    show_output(f"Loaded {len(category_table.keys())} categories.")

    return category_table

# called after the meta.json file has been loaded and just before the properties of the apworld are defined. You can use this hook to change what is displayed on the webhost
# for more info check https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/world%20api.md#webworld-class
def after_load_meta_file(meta_table: dict) -> dict:
    """I could demonstrate using this, but you'll likely never use it. 
    And if you do, more adventure for you later. :)"""

    return meta_table

# called when an external tool (eg Univeral Tracker) ask for slot data to be read
# use this if you want to restore more data
# return True if you want to trigger a regeneration if you changed anything
def hook_interpret_slot_data(world: World, player: int, slot_data: dict[str, any]) -> bool:
    """
    This is just here in case you decided something random when generating your multiworld and you want Universal Tracker to know about it so it can generate the same way.
    If you don't know whether you need this or not, you probably don't.
    
    If you actually do, just store your random decisions from the first generation in slot data, then look for them here and adjust your world accordingly.
    Once you're done with that, return True to trigger a regen from UT to match your first gen, like the comment above says.
    """
    
    return False
