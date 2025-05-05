#Bod Sorting Script for InsaneUO
#from InstaCare/Kitsune/Crafty Kitsune
#any issues or problems please let me know on the IUO discord
#InsaneUO Discord: https://discord.gg/CjBhM6vJZr

#This is a work in progress and by no means finished.
#Current Bugs:
#Bod gathering needs a little work, will only attempt to get one bod



'''
Notes:
option to pull from central book and then sort out.
    -possibly pull 100 at a time then sort....
sort by material.



'''

from System.Collections.Generic import List
from System import Byte

global total_lbods, total_sbods, total_sbods_with_no_lbods

#========================== MISC Settings ================================
# Constants for settings and configuration
DRAG_DELAY_MILLISECONDS = 700
IS_USING_NO_LBOD_BOOK = True  # Toggle for using a book for small BODs without an associated large BOD
#following options not used yet, WIP
USING_SERIALS_FOR_BOD_BOOK = True  # Toggle for identifying BOD books by serials or names 
CONTINUOUS_BOD_GATHER = True # Toggled thru gump to enable continuously trying to gather bod
is_paused = False

# Prompt the user to select a container for BODs
BOD_CONTAINER_SERIAL = Target.PromptTarget('Select container with BODs')

# Resolve the container
BOD_CONTAINER = Items.FindBySerial(BOD_CONTAINER_SERIAL)
if not BOD_CONTAINER:
    raise ValueError("No BOD container found. Please select a valid container.")
Items.UseItem(BOD_CONTAINER)
Misc.Pause(DRAG_DELAY_MILLISECONDS)

total_lbods = 0
total_sbods = 0
total_sbods_with_no_lbods = 0

#============================Item IDs and Metadata========================
# Constants for item IDs
BOD_ITEM_ID = 0x2258
IGNORED_CONTAINER_SERIAL = None

# BOD mappings for different skills
#change sbod_book, lbod_book, and no_lbod_book to the serials for the books you want to use
BOD_MAPPINGS = {
    "alchemy": {"color": 0x09c9, "sbod_book": 0x401ACBA1, "lbod_book": 0x401ACAF4, "no_lbod_book": 0x4015EF10},
    "blacksmith": {"color": 0x044e, "sbod_book": 0x4010898A, "lbod_book": 0x4010898C, "no_lbod_book": 0x41047C73},
    "carpentry": {"color": 0x05e8, "sbod_book": 0x403CDD3A, "lbod_book": 0x403CDD5F, "no_lbod_book": 0x4015EEE7},
    "cooking": {"color": 0x0491, "sbod_book": 0x401ACB48, "lbod_book": 0x401ACAB6, "no_lbod_book": 0x4015EEEA},
    "fletching": {"color": 0x0591, "sbod_book": 0x40108952, "lbod_book": 0x40108953, "no_lbod_book": 0x4015EEF2},
    "inscription": {"color": 0x0a26, "sbod_book": 0x400DD21B, "lbod_book": 0x400DD1EA, "no_lbod_book": 0x4015EEFA},
    "tinkering": {"color": 0x0455, "sbod_book": 0x40108954, "lbod_book": 0x40108968, "no_lbod_book": 0x4015EF03},
    "tailoring": {"color": 0x0483, "sbod_book": 0x40108990, "lbod_book": 0x40108995, "no_lbod_book": 0x4015EEE0},
}

# List of excluded items by skill
EXCLUDED_ITEMS = {
    "alchemy": ["greater heal potion", "greater cure potion", "agility potion", "strength potion"],
    "blacksmith": ["bascinet", "close helm", "helmet", "norse helm", "female plate chest", "bronze shield", "tear kite shield", "metal shield", "buckler", "metal kite shield"],
    "carpentry": ["foot stool", "barrel staves", "barrel lid", "stool", "small crate", "medium crate", "large crate", "wooden chest"],
    "cooking": ["sweet dough", "cake mix", "cookie mix", "unbaked quiche", "unbaked meat pie", "uncooked sausage pizza", "uncooked cheese pizza", "quiche", "meat pie", "sausage pizza", "cheese pizza", "baked fruit pie", "baked peach cobbler", "baked apple pie", "baked pumpkin pie"],
    "fletching": ["kindling", "shaft"],
    "inscription": ["reactive armor", "bless", "create food", "magic arror", "night sight", "harm", "magic trap", "magic untrap", "protection", "fireball", "magic lock", "poison", "telekinisis", "teleport", "unlock", "wall of stone", "arch cure", "arch protection", "fire field", "lightning", "mana drain", "incognito", "mind blast", "poison field", "dispel", "energy bolt", "explosion", "invisibility", "mark", "mass curse", "paralyze field", "reveal", "energy field", "gate travel", "mass dispel", "earthquake", "energy vortex", "resurrection", "lich form", "vengeful spirit", "wraith form", "vampiric embrace"],
    "tinkering": ["barrel tap", "barrel hoops", "pewter mug", "clipper", "tongs", "sledge hammer", "saw", "froe", "flour sifter", "nunchaku", "hatchet", "pickaxe", "cleaver", "pitchfork", "lantern", "candelabra", "gears", "axle", "springs", "axle gears", "clock parts", "clock", "potion keg", "clock frame", "metal container engraver", "sextant parts"],
    "tailoring": ["scales"],
}

#============================ Helper Functions ===========================
def find_item(item_id, container, color=-1, ignore_containers=[]):
    """
    Recursively searches for items by ID and color within a container.
    """
    ignore_color = (color == -1)
    if isinstance(item_id, int):
        items = (item for item in container.Contains if item.ItemID == item_id and (ignore_color or item.Hue == color))
    elif isinstance(item_id, list):
        items = (item for item in container.Contains if item.ItemID in item_id and (ignore_color or item.Hue == color))
    else:
        raise ValueError("Invalid item_id type passed to find_item.", item_id, container)
    
    found_item = next(items, None)
    if found_item:
        return found_item

    # Search subcontainers
    for subcontainer in (item for item in container.Contains if item.IsContainer and item.Serial not in ignore_containers):
        found_item = find_item(item_id, subcontainer, color, ignore_containers)
        if found_item:
            return found_item

def move_item(item, destination_bag, amount=0):
    """
    Moves an item to the specified destination.
    """
    Items.Move(item, destination_bag, amount)
    Misc.Pause(DRAG_DELAY_MILLISECONDS)

def is_small_bod(bod):
    """
    Determines if a BOD is small based on its properties.
    """
    props = Items.GetPropStringList(bod)
    return any("small" in prop.lower() for prop in props)

def has_no_large_bod(current_bod, bod_type, excluded_items):
# Get the properties of the current BOD
    props = Items.GetPropStringList(current_bod)
    
    # Sanitize the props received
    # Done so it will match against both filled and unfilled BODs
    chars_to_remove = ':01234'
    stripped_props = [s.translate({ord(c): None for c in chars_to_remove}) for s in props]
        
    # Get the list of excluded items for the specified category
    excluded_list = EXCLUDED_ITEMS.get(bod_type.lower(), [])
    
    # Check if any of the sanitized properties match the excluded items
    for prop in stripped_props:
        if any(prop.strip().lower() == item.strip().lower() for item in excluded_list):
            return True

    return False
    
#def bod_material_type():
    #placeholder

def sort_bod(bod_type=None):
    """
    Sorts BODs of a specific type into their respective books.
    If no bod_type is provided, processes all types.
    """
    global total_lbods, total_sbods, total_sbods_with_no_lbod

    # Reset global counters
    total_lbods = 0
    total_sbods = 0
    total_sbods_with_no_lbod = 0

    # Determine which BOD types to process
    bod_types_to_process = [bod_type] if bod_type else BOD_MAPPINGS.keys()

    for current_bod_type in bod_types_to_process:
        bod_map = BOD_MAPPINGS[current_bod_type]
        excluded = [item.lower() for item in EXCLUDED_ITEMS.get(current_bod_type, [])]

        current_bod = find_item(BOD_ITEM_ID, BOD_CONTAINER, bod_map["color"], [IGNORED_CONTAINER_SERIAL])
        while current_bod:
            if is_small_bod(current_bod):
                if IS_USING_NO_LBOD_BOOK and has_no_large_bod(current_bod, current_bod_type, excluded):
                    move_item(current_bod, bod_map["no_lbod_book"])
                    total_sbods_with_no_lbod += 1
                else:
                    move_item(current_bod, bod_map["sbod_book"])
                    total_sbods += 1
            else:
                move_item(current_bod, bod_map["lbod_book"])
                total_lbods += 1
            current_bod = find_item(BOD_ITEM_ID, BOD_CONTAINER, bod_map["color"], [IGNORED_CONTAINER_SERIAL]) 

def gather_bod(range=4, npc_bod_gump_id=0x9bade6ea, specific_npc_suffix=None):
   
    #Based on the code from omgarturo from InsaneUO discord
    #https://discord.gg/sTEcgq9xNA
    #modified to take specific suffix as target
  
    # Define the allowed suffixes
    allowed_suffixes = ["scribe", "alchemist", "carpenter", "bowyer", "tinker", "tailor", "blacksmith", "cook"]

    # Validate the specific_npc_suffix against allowed_suffixes
    if specific_npc_suffix and specific_npc_suffix not in allowed_suffixes:
        raise ValueError(f"Invalid NPC suffix '{specific_npc_suffix}'. Must be one of {allowed_suffixes}.")
    
    no_bod_available = "An offer may be available in"
    
    def get_yellows_in_range(range):
        """
        Filters NPCs by notoriety (yellow = 7) within the specified range.

        Parameters:
            range (int): Range to filter NPCs.

        Returns:
            list: List of NPCs within range with yellow notoriety.
        """
        fil = Mobiles.Filter()
        fil.Enabled = True
        fil.RangeMax = 4
        fil.Notorieties = List[Byte](bytes([7]))
        fil.IsGhost = False
        fil.Friend = False
        fil.CheckLineOfSight = False
        return Mobiles.ApplyFilter(fil)

    iterations = 0
    max_iterations = 4  # Set the minimum number of times to check for bods

    while iterations < max_iterations:
        npcs = get_yellows_in_range(range)
        for npc in npcs:
            for prop in npc.Properties:
                # Check if the NPCs property matches the specific suffix or any allowed suffix
                if specific_npc_suffix:
                    suffixes_to_check = [specific_npc_suffix]
                else:
                    suffixes_to_check = allowed_suffixes

                if any(suffix in prop.ToString() for suffix in suffixes_to_check):
                    Misc.UseContextMenu(npc.Serial, "Bulk Order Info", 3000)
                    Misc.Pause(1000)
                    gid = Gumps.CurrentGump()
                    # Increment the iteration counter
                    iterations += 1
                    
                    if gid is not None and gid != 0:
                        Gumps.SendAction(gid, 1)
                        print(f"Accepted BOD from {specific_npc_suffix or 'any allowed NPC'} with Gump ID: {gid}")
                    else:
                        print(f"No BODs available from {specific_npc_suffix or 'any allowed NPC'}")
    
    
            
        
#=============================== GUMP ===============================
setX = 200
setY = 300
page = 0
is_using_no_lbod_book = True

def sbod_with_no_lbod_switch():
    global is_using_no_lbod_book  # Declare as global
    is_using_no_lbod_book = not is_using_no_lbod_book  # Toggle the value
        
def sendgump():
    gd = Gumps.CreateGump(movable=True) 
    Gumps.AddPage(gd, 0)

    #Gumps.AddBackground(gd, 0, 0, 781, 503, 1755)
    Gumps.AddBackground(gd, 0, 0, 200, 325, 1755) 
    Gumps.AddAlphaRegion(gd,0, 0, 190, 325)
    
    Gumps.AddPage(gd, 1)#page 1
    if is_using_no_lbod_book:
        Gumps.AddLabel(gd, 35, 15, 0x064a, "Put sbods with no lbod")
        Gumps.AddLabel(gd, 35, 30, 0x064a, "into its own book (ON)")
        Gumps.AddButton(gd, 4, 17, 5828, 5828, 9, 1, 0)
    else:
        Gumps.AddLabel(gd, 35, 15, 0x064a, "Put sbods with no lbod")
        Gumps.AddLabel(gd, 35, 30, 0x064a, "into its own book (ON)")
        Gumps.AddButton(gd, 4, 17, 5828, 5828, 9, 1, 0)
    
    #=============Sorting Stuff=============    
    Gumps.AddLabel(gd, 35, 71, 0x09c9, "Sort Alchemy Bods")
    Gumps.AddButton(gd, 4, 67, 1154, 1154, 1, 1, 0)
    Gumps.AddTooltip(gd, r"Sort Alchemy Bods")
    Gumps.AddLabel(gd, 35, 95, 0x044e, "Sort Blacksmith Bods")
    Gumps.AddButton(gd, 4, 91, 1154, 1154, 2, 1, 0)
    Gumps.AddTooltip(gd, r"Sort Blacksmith Bods")
    Gumps.AddLabel(gd, 35, 119, 0x05e8, "Sort Carpentry Bods")
    Gumps.AddButton(gd, 4, 115, 1154, 1154, 3, 1, 0)
    Gumps.AddTooltip(gd, r"Sort Carpentry Bods")
    Gumps.AddLabel(gd, 35, 143, 0x0491, "Sort Cooking Bods")
    Gumps.AddButton(gd, 4, 139, 1154, 1154, 4, 1, 0)
    Gumps.AddTooltip(gd, r"Sort Cooking Bods")
    Gumps.AddLabel(gd, 35, 167, 0x0591, "Sort Fletching Bods")
    Gumps.AddButton(gd, 4, 163, 1154, 1154, 5, 1, 0)
    Gumps.AddTooltip(gd, r"Sort Fletching Bods")
    Gumps.AddLabel(gd, 35, 190, 0x0a26, "Sort Inscription Bods")
    Gumps.AddButton(gd, 4, 187, 1154, 1154, 6, 1, 0)
    Gumps.AddTooltip(gd, r"Sort Inscription Bods")
    Gumps.AddLabel(gd, 35, 214, 0x0455, "Sort Tinkering Bods")
    Gumps.AddButton(gd, 4, 210, 1154, 1154, 7, 1, 0)
    Gumps.AddTooltip(gd, r"Sort Tinkering Bods")
    Gumps.AddLabel(gd, 35, 238, 0x0492, "Sort Tailoring Bods")
    Gumps.AddButton(gd, 4, 233, 1154, 1154, 8, 1, 0)
    Gumps.AddTooltip(gd, r"Sort Tailoring Bods")
    Gumps.AddLabel(gd, 35, 262, 0x0492, r"Sort All Bods")
    Gumps.AddButton(gd, 4, 255, 1154, 1154, 19, 1, 0)
    Gumps.AddTooltip(gd, r"Sort All Bods")
    
    Gumps.AddLabel(gd, 35, 286, 0x064a, r"Goto Gathering")
    Gumps.AddButton(gd, 4, 284, 5540, 5541, 1, 0, 2)
    #Gumps.AddButton(gd,x,y,normalID,pressedID,buttonID,type,param)
   
    Gumps.AddPage(gd, 2) #page 2
    #=============BOD Collection Stuff=============
    Gumps.AddLabel(gd, 35, 71, 0x09c9, "Gather Alchemy Bods")
    Gumps.AddButton(gd, 4, 67, 1154, 1154, 10, 1, 0)
    Gumps.AddTooltip(gd, r"Gather Alchemy Bods")
    Gumps.AddLabel(gd, 35, 95, 0x044e, "Gather Blacksmith Bods")
    Gumps.AddButton(gd, 4, 91, 1154, 1154, 11, 1, 0)
    Gumps.AddTooltip(gd, r"Gather Blacksmith Bods")
    Gumps.AddLabel(gd, 35, 119, 0x05e8, "Gather Carpentry Bods")
    Gumps.AddButton(gd, 4, 115, 1154, 1154, 12, 1, 0)
    Gumps.AddTooltip(gd, r"Gather Carpentry Bods")
    Gumps.AddLabel(gd, 35, 143, 0x0491, "Gather Cooking Bods")
    Gumps.AddButton(gd, 4, 139, 1154, 1154, 13, 1, 0)
    Gumps.AddTooltip(gd, r"Gather Cooking Bods")
    Gumps.AddLabel(gd, 35, 167, 0x0591, "Gather Fletching Bods")
    Gumps.AddButton(gd, 4, 163, 1154, 1154, 14, 1, 0)
    Gumps.AddTooltip(gd, r"Gather Fletching Bods")
    Gumps.AddLabel(gd, 35, 193, 0x0a26, "Gather Inscription Bods")
    Gumps.AddButton(gd, 4, 187, 1154, 1154, 15, 1, 0)
    Gumps.AddTooltip(gd, "Gather Inscription Bods")
    Gumps.AddLabel(gd, 35, 214, 0x0455, "Gather Tinkering Bods")
    Gumps.AddButton(gd, 4, 210, 1154, 1154, 16, 1, 0)
    Gumps.AddTooltip(gd, r"Gather Tinkering Bods")
    Gumps.AddLabel(gd, 35, 238, 0x0492, "Gather Tailoring Bods")
    Gumps.AddButton(gd, 4, 233, 1154, 1154, 17, 1, 0)
    Gumps.AddTooltip(gd, r"Gather Tailoring Bods")
    
    #gather all
    #Gumps.AddLabel(gd, 35, 262, 0x09c9, "Gather All Bods In Room")
    #Gumps.AddButton(gd, 4, 256, 1154, 1154, 18, 1, 0)
    #Gumps.AddTooltip(gd, r"Gather All Bods")
    
    Gumps.AddLabel(gd, 35, 286, 0x064a, r"Goto Sorting")
    Gumps.AddButton(gd, 4, 284, 5537, 5538, 1, 0, 1)

    #Gumps.AddLabel(gd, 4, 333, 0x09c9, f"SORTED TOTALS Lbods: {total_lbods} Sbods: {total_sbods} Sbods with no LBODs: {total_sbods_with_no_lbods}")

    Gumps.SendGump(987654, Player.Serial, setX, setY, gd.gumpDefinition, gd.gumpStrings)
    buttoncheck() 

def buttoncheck():
    Gumps.WaitForGump(987654, 60000)
    Gumps.CloseGump(987654)
    gd = Gumps.GetGumpData(987654)
    
    #===== BOD Sorting Buttons =====
    if gd.buttonid == 1: 
        sort_bod("alchemy")
    elif gd.buttonid == 2:
        sort_bod("blacksmith")
    elif gd.buttonid == 3:
        sort_bod("carpentry")
    elif gd.buttonid == 4:
        sort_bod("cooking")
    elif gd.buttonid == 5:
        sort_bod("fletching")
    elif gd.buttonid == 6:
        sort_bod("inscription")
    elif gd.buttonid == 7:
        sort_bod("tinkering")
    elif gd.buttonid == 8:
        sort_bod("tailoring")  
    elif gd.buttonid == 9:
        sbod_with_no_lbod_switch()
    #===== BOD Gathering Buttons =====
    elif gd.buttonid == 10:
        gather_bod(specific_npc_suffix="alchemist")
    elif gd.buttonid == 11:
        gather_bod(specific_npc_suffix="blacksmith")
    elif gd.buttonid == 12:
        gather_bod(specific_npc_suffix="carpenter")
    elif gd.buttonid == 13:
        gather_bod(specific_npc_suffix="cook")
    elif gd.buttonid == 14:
        gather_bod(specific_npc_suffix="bowyer")
    elif gd.buttonid == 15:
        gather_bod(specific_npc_suffix="scribe")
    elif gd.buttonid == 16:
        gather_bod(specific_npc_suffix="tinker")
    elif gd.buttonid == 17:
        gather_bod(specific_npc_suffix="tailor") 
    elif gd.buttonid == 18:
        gather_bod() 
    elif gd.buttonid == 19:
        sort_bod()

while Player.Connected: 
    sendgump()
    Misc.Pause(750)