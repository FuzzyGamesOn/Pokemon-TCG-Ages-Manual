# Hooks in Pokemon TCG: Ages
This is intended as a Manual apworld that demonstrates some common hooks usage. As such, this apworld completely avoids (for education purposes) the Manual templating syntax and purely uses hooks for everything.

"But what is everything?" Well... have a look below!

## Creating the JSON data files
### Creating the game JSON
- [hooks/Data.py](Data.py) -> `after_load_game_file`

### Creating the items JSON
- [hooks/Data.py](Data.py) -> `after_load_item_file`

### Creating the locations JSON
- [hooks/Data.py](Data.py) -> `after_load_location_file`

### Creating the regions JSON
- [hooks/Data.py](Data.py) -> `after_load_region_file`

### Creating the categories JSON
- [hooks/Data.py](Data.py) -> `after_load_category_file`

## Dynamic or duplicated requirements for locations/regions
_Reminder: These functions are not defined by Manual. You add these. (They also don't have to start with "has", or any other prefix.)_
- [hooks/Rules.py](Rules.py) -> `has*`

## Modifying options at generation
### Setting category options from a custom option
- [hooks/World.py](World.py) -> `before_create_regions`

### Creating custom options
_Only do this from the `before` hook. The `after` hook will no longer work for this._
- [hooks/Options.py](Options.py) -> `before_options_defined`

### Hiding category options in the spoiler log / YAML template
- [hooks/Options.py](Options.py) -> `after_options_defined`

## Modifying items at generation
### Customizing filler item name
- [hooks/World.py](World.py) -> `before_create_items_filler`

### Customizing filler item name each time a filler is added automatically by Manual
- [hooks/World.py](World.py) -> `hook_get_filler_item_name`

### Removing items based on options
- [hooks/World.py](World.py) -> `before_create_items_starting`
  
### Setting starting items based on options
- [hooks/World.py](World.py) -> `before_create_items_filler`

### Customizing the addition of filler items
- [hooks/World.py](World.py) -> `after_create_items`

### Customizing an item's classification when created
_Works in both of these but affects different things, so demonstrating both. `before` affects all instances of this item. `after` affects only the one being created._
- [hooks/World.py](World.py) -> `before_create_item`
- [hooks/World.py](World.py) -> `after_create_item`

### Forcing items to be placed at certain locations based on options
_See [Forcing certain locations to have certain items based on options](#forcing-certain-locations-to-have-certain-items-based-on-options)._

### Write the player's starting items, etc. to slot data
_Works in both of these with no changes, so I picked before. You can pick either. Also, this step is basically just "write stuff to slot data for the client"._
- [hooks/World.py](World.py) -> `before_fill_slot_data`
- [hooks/World.py](World.py) -> `after_fill_slot_data`

## Modifying regions and locations at generation
### Removing locations based on options
- [hooks/World.py](World.py) -> `after_create_regions`

### Customizing the requirements for locations (including victory)
- [hooks/World.py](World.py) -> `after_set_rules`

### Customizing the requirements for regions
_Listed locations and regions separately because the process for changing requirements for regions requires a couple steps compared to the single step location change._
- [hooks/World.py](World.py) -> `after_set_rules`

### Forcing certain locations to have certain items based on options
_Works in both "before"/"after" with no changes, so I just put it in the "before" one. The only difference between "before" and "after" is that `place_item_*` settings run in between the two._ 

_Also, there's very little worth doing at the "generate\_basic" step, since items/locations/regions should be set in stone by then._
- [hooks/World.py](World.py) -> `before_generate_basic`

### Listing custom entrance data for hinted locations
_Could be done in `before` or `after` hook. `before` lets Manual overwrite it with data from your JSON, `after` lets your hook have the final say._
- [hooks/World.py](World.py) -> `after_extend_hint_information`

## Modifying the Spoiler Log
### Writing custom information about the current playthrough
- [hooks/World.py](World.py) -> `before_write_spoiler`

