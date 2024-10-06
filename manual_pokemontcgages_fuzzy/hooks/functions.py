# added some convenience functions in here so we can access them from any hook files

import os
import pkgutil
import csv
import re

from io import StringIO

from Utils import local_path
from worlds.AutoWorld import World


###
# File, item, and location functions
###

# we have to get the raw data from our CSV files to pass to a parser, so had to copy our own version of this method
# this gets the contents of the file from pkgutil and passes it back as a "file" for csv parsing later
def get_csv_file(*args) -> dict:
    fname = os.path.join("data", *args)
    package_base_name = re.sub(r'\.hooks\.\w+$', '.Data', __name__)

    try:
        filedata = pkgutil.get_data(package_base_name, fname).decode()
    except:
        filedata = ""

    return StringIO(filedata)

def get_packs() -> list:
    pack_data_file = 'pack_list.csv' # has the list of available packs
    rows = []

    with get_csv_file(pack_data_file) as opened_file:
        reader = csv.DictReader(opened_file)

        for row in reader:
            rows.append(row)

    return rows

def get_pack_names() -> list:
    return [
        pack['Pack Directory'] for pack in get_packs()
    ]

def get_cards(pack_name: str) -> list:
    card_data_file = 'card_list.csv' # has the raw non-structured item (card) data
    rows = []

    with get_csv_file(pack_name, card_data_file) as opened_file:
        reader = csv.DictReader(opened_file)

        for row in reader:
            rows.append(row)
            
    return rows

def get_evo_cards(pack_name: str) -> list:
    evo_data_file = 'evolutions_list.csv'
    rows = []

    with get_csv_file(pack_name, evo_data_file) as opened_file:
        reader = csv.DictReader(opened_file)

        for row in reader:
            rows.append(row)
    
    return rows

def get_unique_evos(pack_name: str) -> list:
    evo_cards = get_evo_cards(pack_name)
    evo_cards = [f"{card['Evolution Card Name']} {card['Evolution Set Name']} {card['Evolution Set Number']}" for card in evo_cards]

    return sorted(list(set(evo_cards))) # use a set to eliminate dupes, then convert it back to a list, then sort it

def get_energy_cards(pack_name: str) -> list:
    energy_data_file = 'energy_list.csv'
    rows = []

    with get_csv_file(pack_name, energy_data_file) as opened_file:
        reader = csv.DictReader(opened_file)

        for row in reader:
            rows.append(row)
    
    rows = [f"{card['Energy Card Name']}" for card in rows]

    return rows

def get_enemy_cards(pack_name: str) -> list:
    enemy_data_file = 'enemies.csv'
    rows = []

    with get_csv_file(pack_name, enemy_data_file) as opened_file:
        reader = csv.DictReader(opened_file)

        for row in reader:
            rows.append(row)
    
    return rows

def get_card_picture(card_name: str):
    for pack in get_pack_names():
        cards = get_cards(pack)
        cards = {
            f"{card['Card Name']} {card['Set Name']} {card['Set Number']}":card['Card Image URL']
                for card in cards
        }

        if card_name in cards:
            return cards[card_name]
        
    return ""

def get_evo_picture(card_name: str):
    for pack in get_pack_names():
        evo_cards = get_evo_cards(pack)
        evo_cards = {
            f"{card['Evolution Card Name']} {card['Evolution Set Name']} {card['Evolution Set Number']}":card['Card Image URL']
                for card in evo_cards
        }

        if card_name in evo_cards:
            return evo_cards[card_name]
        
    return ""

def get_enemy_picture(card_name: str):
    for pack in get_pack_names():
        enemy_cards = get_enemy_cards(pack)
        enemy_cards = {
            f"{card['Card Name']} {card['Set Name']} {card['Set Number']}":card['Card Image URL']
                for card in enemy_cards
        }

        if card_name in enemy_cards:
            return enemy_cards[card_name]
        
    return ""

# get only the list of HP values that are in the pack
def get_hp_list(pack_name: str) -> list:
    return list(set(
        card['HP'] for card in get_cards(pack_name)
    ))

# gets the total number of each HP separately, so we can add proportional numbers of locations
def get_hp_distribution(pack_name: str) -> dict:
    hp_power_levels = sorted(set(card['HP'] for card in get_cards(pack_name)), key=int) # get the unique hp values from the cards

    # figure out how many of each hp is there
    hp_distribution = { 
        int(hp): len([
                card['HP'] for card in get_cards(pack_name) if card['HP'] == hp
            ]) 
        for hp in hp_power_levels 
    } 

    return hp_distribution

# gets a running percentage of hp values up to the point of each hp key
def get_hp_distribution_percentages(pack_name: str) -> dict:
    hp_distribution = get_hp_distribution(pack_name)
    hp_total = sum(hp_distribution.values())

    # figure out how many hps are less than or equal to each hp value,
    #   then represent that as a percentage of the total number of hp values (including dupes)
    hp_distribution_percentages = { 
        hp: sum([
                val for key, val in hp_distribution.items() if key <= hp and key > 0
            ]) / hp_total
        for hp in hp_distribution.keys()
    }

    return hp_distribution_percentages

def get_itempool_total_by_category(world: World, category_name: str) -> int:
    item_names = [
        i['name'] for i in world.item_name_to_item.values() 
            if category_name in i.get('category', [])
    ]

    return len([
        i for i in world.multiworld.itempool 
            if i.player == world.player and i.name in item_names
    ])


###
# Options functions
#
# (Demonstrating that you can do this for organization, 
#   but not going to use them for simplicity of examples.)
###

def options_get_packs(world: World) -> list:
    return world.options.packs.value

def options_get_starting_pokemon_count(world: World) -> int:
    return world.options.starting_pokemon_count.value

def options_get_banned_cards(world: World) -> list:
    return world.options.banned_cards.value

def options_get_late_power_pokemon(world: World) -> bool:
    return world.options.late_power_pokemon.value


###
# Logging functions
###

# this lets us change how we want to output any debug in a central place
def show_output(output_text: str):
    # change this to True to see the output while developing the world
    if False:
        print(output_text)
