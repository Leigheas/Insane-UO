# Walking Lumberjack
# original code source unknown, modified by InstaCare/Kitsune/Crafty Kitsune

# How to use:
# 1. Set axe_serial to your axe serial (Razor Enhanced > Inspect Entity > target axe > Serial)
# 2. Set beetle_serial to your beetle serial (Razor Enhanced > Inspect Entity > target beetle > Serial)

WOOD_LOGS = 0x1BDD
WOOD_BOARDS = 0x1BD7
AXE_SERIAL = 0x40F9310B  # Change to your axe serial

auto_detect_beetles = false     # change to true to autodetect following beetles 
BLUE_BEETLE_BODY_ID = 0x0317    # Change if needed

if auto_detect_beetles == false:
    #change this to the total number of blue beetles you want to use (MAX IS 5)
    number_of_beetles_to_use = 3

    BEETLE1_SERIAL = 0x000787BF   # Change to your beetle serial
    BEETLE2_SERIAL = 0x0008FF98
    BEETLE3_SERIAL = 0x0008F967
    BEETLE4_SERIAL = 0x00000000
    BEETLE5_SERIAL = 0x00000000
else:
    beetle_info = find_blue_beetles_with_names()
    BEETLE_SERIALS = [serial for serial, name in beetle_info]
    BEETLE_NAMES = [name for serial, name in beetle_info]
    number_of_beetles_to_use = len(BEETLE_SERIALS)
"""    
    #BEETLE_SERIALS = find_blue_beetles_nearby()
    #number_of_beetles_to_use = len(BEETLE_SERIALS)
"""

max_beetle_weight = 1500 # change to how full you want your beetle to be

BEETLE_SERIALS = [BEETLE1_SERIAL, BEETLE2_SERIAL, BEETLE3_SERIAL, BEETLE4_SERIAL, BEETLE5_SERIAL]

# Resource types to move to beetle
# itemids for resources gained, for easy remove/add
# boards            0x1BD7
# switch            0x2F5F
# bark fragment     0x318F
# parasitic plant   0x3190
# lumi fungi        0x3191 
# brill amber       0x3199
# crystal shard     0x5738
LJ_RESOURCES = [0x1BD7, 0x2F5F, 0x318F, 0x3190, 0x3191, 0x3199, 0x5738]

max_weight = Player.MaxWeight
start_chopping_logs_weight = max_weight - 50    #adjust as needed
stop_chopping_trees_weight = max_weight - 10    #adjust as needed
delay_drag = 600 #only adjust due to lag

# find nearby blue beetles and pull in their serial and name.
def find_blue_beetles_with_names():
    beetles = []
    fil = Mobiles.Filter()
    fil.Enabled = True
    fil.RangeMax = 4
    fil.Notorieties = List[Byte](bytes([1]))
    
    for mob in Mobiles.ApplyFilter(fil):
        if mob.Body == BLUE_BEETLE_BODY_ID and mob.Notoriety == 1:
            beetles.append((mob.Serial, mob.Name))
    return beetles

def setup_beetles(BEETLE_SERIALS, number_of_beetles_to_use):
    """
    Scans thru beetles to pull their serials and backpacks for use 
    thru the script.
    
    Args:
        BEETLE_SERIALS: List of beetle serial numbers.
        number_of_beetles_to_use: Number of beetles to process.
    """
    for i in range(number_of_beetles_to_use):
        serial = BEETLE_SERIALS[i]
        beetle = Mobiles.FindBySerial(serial)
        if not beetle:
            #Misc.SendMessage(f"Beetle {i+1} not found! Check BEETLE_SERIALS[{i}] value.")
            Player.HeadMessage(2125, 'Beetle {i+1} not found! Check BEETLE_SERIALS[{i}] value.')
            raise Exception(f"Beetle {i+1} not found!")

        Mobiles.WaitForProps(beetle, 200)
        weight = Mobiles.GetPropValue(beetle, "Weight")
        print(f"Beetle {i+1} weight: {weight}")

        backpack = beetle.Backpack
        if not backpack:
            #Misc.SendMessage(f"Beetle {i+1} backpack not found!")
            Player.HeadMessage(2125, 'Beetle {i+1} backpack not found!!')
            raise Exception(f"Beetle {i+1} backpack not found!")

        # Dynamically assign variables in the global namespace
        globals()[f'beetle{i+1}'] = beetle
        globals()[f'beetle{i+1}_weight'] = weight
        globals()[f'beetle{i+1}_backpack'] = backpack

def set_beetle_weight_globals(number_of_beetles_to_use):
    if number_of_beetles_to_use >= 1:
        beetle1 = Mobiles.FindBySerial(BEETLE1_SERIAL)
        Mobiles.WaitForProps(beetle1, 200)
        globals()['beetle1_weight'] = Mobiles.GetPropValue(beetle1, "Weight")
    if number_of_beetles_to_use >= 2:
        beetle2 = Mobiles.FindBySerial(BEETLE2_SERIAL)
        Mobiles.WaitForProps(beetle2, 200)
        globals()['beetle2_weight'] = Mobiles.GetPropValue(beetle2, "Weight")
    if number_of_beetles_to_use >= 3:
        beetle3 = Mobiles.FindBySerial(BEETLE3_SERIAL)
        Mobiles.WaitForProps(beetle3, 200)
        globals()['beetle3_weight'] = Mobiles.GetPropValue(beetle3, "Weight")
    if number_of_beetles_to_use >= 4:
        beetle4 = Mobiles.FindBySerial(BEETLE4_SERIAL)
        Mobiles.WaitForProps(beetle4, 200)
        globals()['beetle4_weight'] = Mobiles.GetPropValue(beetle4, "Weight")
    if number_of_beetles_to_use >= 5:
        beetle5 = Mobiles.FindBySerial(BEETLE5_SERIAL)
        Mobiles.WaitForProps(beetle5, 200)
        globals()['beetle5_weight'] = Mobiles.GetPropValue(beetle5, "Weight")

def chop_logs():
    log = Items.FindByID(WOOD_LOGS, -1, Player.Backpack.Serial)
    while log is not None:
        Items.UseItem(axe_serial)
        Target.WaitForTarget(5000, False)
        Target.TargetExecute(log)
        Misc.Pause(1000)
        log = Items.FindByID(WOOD_LOGS, -1, Player.Backpack.Serial)

def get_next_non_full_beetle():
    # Returns the index and serial of the next beetle that isn't full.
    # Returns None if all beetles are full
    for i in range(number_of_beetles_to_use):
        weight = globals().get(f'beetle{i+1}_weight', None)
        serial = BEETLE_SERIALS[i]
        backpack = globals().get(f'beetle{i+1}_backpack', None)
        if weight is not None and backpack is not None and weight < max_beetle_weight:
            return i, serial, backpack
        else
            Player.HeadMessage(2125, 'Beetle {i+1} is full, going to next beetle!!')
    return None

def move_resources():
    set_beetle_weight_globals(number_of_beetles_to_use) # update beetle weights
    for resource_id in LJ_RESOURCES:
        resources = Items.FindAllByID(resource_id, -1, Player.Backpack.Serial, False)
        for res in resources:
            beetle_info = get_next_non_full_beetle()
            if beetle_info is None:
                Player.HeadMessage(2125, 'ALL BEETLES FULL!!!!')
                return
            beetle_index, _, beetle_backpack = beetle_info

            # Get the weight per single item (sometimes called "weight per unit" in UO)
            # For stackables, the "Weight" property is usually total weight; divide by amount.
            total_item_weight = Items.GetPropValue(res, "Weight")
            amount = Items.GetPropValue(res, "Amount") or 1
            current_beetle_weight = globals().get(f'beetle{beetle_index+1}_weight', 0)
            available_beetle_weight = max_beetle_weight - current_beetle_weight

            if total_item_weight is None or amount is None or amount == 0:
                Player.HeadMessage(2125, f"Cannot determine weight/amount for item {res.Serial}!")
                continue

            weight_per_item = float(total_item_weight) / amount

            # How many can we move and not exceed max_beetle_weight?
            max_movable = int(available_beetle_weight // weight_per_item)
            if max_movable <= 0:
                Player.HeadMessage(2125, f"Not enough space in Beetle {beetle_index+1}, skipping!")
                continue

            # Move only as much as fits (never more than what's left in the stack)
            move_amount = min(amount, max_movable)
            Items.Move(res, beetle_backpack.Serial, move_amount)
            Misc.Pause(delay_drag)
            set_beetle_weight_globals(number_of_beetles_to_use) # update beetle weights
"""
def move_resources():
    set_beetle_weight_globals(number_of_beetles_to_use) # update beetle weights
    for resource_id in LJ_RESOURCES:
        resources = Items.FindAllByID(resource_id, -1, Player.Backpack.Serial, False)
        for res in resources:
            beetle_info = get_next_non_full_beetle()
            if beetle_info is None:
                #Misc.SendMessage("All beetles are full! Cannot move more resources.")
                Player.HeadMessage(2125, 'ALL BEETLES FULL!!!!')
                return
            _, _, beetle_backpack = beetle_info
            Items.Move(res, beetle_backpack.Serial, 0)
            Misc.Pause(delay_drag)
            set_beetle_weight_globals(number_of_beetles_to_use) # update beetle weights
"""

""" original move_resources code
def move_resources():
    set_beetle_weight_globals(number_of_beetles_to_use) # update beetle weights
    for resource_id in LJ_RESOURCES:
        resources = Items.FindAllByID(resource_id, -1, Player.Backpack.Serial, False)
        for res in resources:
            Items.Move(res, beetle1_backpack.Serial, 0)
            Misc.Pause(delay_drag)
            set_beetle_weight_globals(number_of_beetles_to_use) # update beetle weights
"""
# Initialize Beetle information
setup_beetles(BEETLE_SERIALS, number_of_beetles_to_use) # pull in serials and backpack info
set_beetle_weight_globals(number_of_beetles_to_use) # pull in initial weights

# Equip your axe if not already equipped.
axe_serial = Player.GetItemOnLayer('LeftHand')
if not axe_serial:
    #Misc.SendMessage('No axe found in hand! Equipping...')
    Player.HeadMessage(2125, 'No axe found in hand! Equipping')
    axe_serial = AXE_SERIAL
    Player.EquipItem(axe_serial)
    Misc.Pause(600)

# Chop trees as you run up against them, until you are too heavy.
while True:
    Journal.Clear()
    Target.TargetResource(AXE_SERIAL, "wood")
    Misc.Pause(500)
    
    # If getting heavy, chop up the logs.
    if Player.Weight >= start_chopping_logs_weight:
        #Misc.SendMessage("Heavy, chopping logs...")
        Player.HeadMessage(2125, 'Heavy, chopping logs...')
        chop_logs()
        move_resources()
        Misc.Pause(600)
    # Stop chopping trees when we can't carry more.
    if Player.Weight >= stop_chopping_trees_weight:
        #Misc.SendMessage("Too heavy.... Stop")
        Player.HeadMessage(2125, 'Too heavy... Stopping')
        break
