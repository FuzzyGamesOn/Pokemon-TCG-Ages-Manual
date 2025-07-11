# Object classes from AP that represent different types of options that you can create
from Options import OptionList, FreeText, NumericOption, Toggle, \
                    DefaultOnToggle, Choice, TextChoice, Range, NamedRange, \
                    Visibility

# These helper methods allow you to determine if an option has been set, or what its value is, for any player in the multiworld
from ..Helpers import is_option_enabled, get_option_value



####################################################################
# NOTE: At the time that options are created, Manual has no concept of the multiworld or its own world.
#       Options are defined before the world is even created.
#
# Example of creating your own option:
#
#   class MakeThePlayerOP(Toggle):
#       """Should the player be overpowered? Probably not, but you can choose for this to do... something!"""
#       display_name = "Make me OP"
#
#   options["make_op"] = MakeThePlayerOP
#
#
# Then, to see if the option is set, you can call is_option_enabled or get_option_value.
#####################################################################

class Packs(OptionList):
    """List of card packs to include beyond the Default set.
    """
    display_name = "Packs"

class StartingPokemonCount(Range):
    """Number of Pokemon cards to randomly start with at the start of the playthrough.
    """
    display_name = "Starting Cards Per Pack"
    range_start = 0
    range_end = 10
    default = 3

class BannedCards(OptionList):
    """List of cards that should be banned from the current playthrough.
    """
    display_name = "Banned Cards"

class LatePowerPokemon(DefaultOnToggle):
    """Forces all EX/ex/GX/V/whatever big body Pokemon to be placed in
    locations in the second half of the playthrough.

    Note: This will likely make the playthrough harder / possibly more balanced than it normally would be.
    """
    display_name = "Late Power Pokemon"


# This is called before any manual options are defined, in case you want to define your own with a clean slate or let Manual define over them
def before_options_defined(options: dict) -> dict:
    # If you're wanting to add custom options, add them here. 
    # Versions of Manual from 2025 on will no longer support adding them elsewhere.
    #
    # And make sure to name them in a unique way. Example: Don't have a 'goal' option; have a 'goal_orbs' option or something instead.
    # (Otherwise, Manual will overwrite your 'goal' option with its core 'goal' option.)


    # You don't have to use dict.update().
    # You can add them individually like:
    #   options['blah'] = YourOptionClass
    options.update({
        'packs': Packs,
        'starting_pokemon_count': StartingPokemonCount,
        'banned_cards': BannedCards,
        'late_power_pokemon': LatePowerPokemon
    })

    return options


# This is called after any manual options are defined, in case you want to see what options are defined or want to modify the defined options
def after_options_defined(options: dict) -> dict:
    # If you want to *modify* existing options -- whether your own or Manual's -- do that here.

    # We have some category options that are defined when we create our categories,
    #   but we want to hide those in the spoiler / YAML. So let's do that here.
    for option in options.keys():
        if 'pack_remove_' in option:
            options[option].visibility = Visibility.none

    return options
