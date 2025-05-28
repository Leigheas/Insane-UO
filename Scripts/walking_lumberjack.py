# Walking Lumberjack
# for InsaneUO 
# By: InstaCare/Kitsune/Crafty Kitsune

# Lumberjacking now with enhanced QOL features!
# Features:
#		* Ability to auto-detect your blue beetles and adjust accordingly
#		* Can still manually set your beetle serials and amount of beetles if you wish to
#		* Automatically cuts logs into boards to help with weight.
#		* Will move all resources to blue beetle (multiple beetles if used)
#		* Will cram the beetles full untill it hits the weight you set.
#		* Will chop trees when you walk up to them

# How To Setup:
# 1. If you are wanting your beetles to be auto-detected, make sure auto_detect_beetles = True.
# 		if not make sure auto_detect_beetles = False.
# 2. If not using auto-detect beetles then you will need to set number_of_beetles_to_use to 
#		the amount of beetles you want to use.
#		Then you will need to set the serial for each beetle (BEETLE1_SERIAL, BEETLE2_SERIAL ect.)
#		(Razor Enhanced > Inspect Entity > target beetle > Serial
# 3. Now set the max weight you want crammed into your beetle(s) with max_beetle_weight
#		1500 is a good amount and is the default.
# 4. Set the serial to the axe under AXE_SERIAL in the serials section.
#		Razor Enhanced > Inspect Entity > target axe > Serial
# 5. wood_logs and blue_beetle_body_id should not need to be changed unless your shard is different.
# 6. under LJ_RESOURCES are the itemid for the items that will be transferred to your beetle(s).
#		there is a list of items and their id so if you want to remove any and add them 
#		back later you can.
#
# 
from System.Collections.Generic import List
from System import Byte
import sys

# ***************************************
# ****	Settings (Can Change) Start  ****
# ***************************************
debug_mode = False 								# set to true if needing to see debug messages
auto_detect_beetles = True      				# change to true to auto detect beetles
max_beetle_weight = 1500 						# change to how full you want your beetle to be
max_weight = Player.MaxWeight
start_chopping_logs_weight = max_weight - 50    #adjust as needed
stop_chopping_trees_weight = max_weight - 10    #adjust as needed
delay_drag = 600 								#only adjust due to lag

# serials
AXE_SERIAL = 0x40F9310B  						# Change to your axe serial

# ===== ItemID =====
wood_logs = 0x1BDD								# change only if the ItemID for logs are different
blue_beetle_body_id = 0x0317    				# Change if needed

# Resource types to move to beetle
# add/remove the itemid from LJ_RESOURCES to tell system what to move. 
# reference id included for easy of use:
# boards            0x1BD7  switch            0x2F5F
# bark fragment     0x318F  parasitic plant   0x3190
# lumi fungi        0x3191  brilliant amber       0x3199
# crystal shard     0x5738
LJ_RESOURCES = [0x1BD7, 0x2F5F, 0x318F, 0x3190, 0x3191, 0x3199, 0x5738]

# *************************************
# ****  Settings (Can Change) End  ****
# *************************************


# ***********************************************
# ****  No Need to Change beyond this point  ****
# ***********************************************

# find nearby blue beetles and pull in their serial and name.
def find_blue_beetles_with_serials():
    beetles = []
    fil = Mobiles.Filter()
    fil.Enabled = True
    fil.RangeMax = 4
    fil.Notorieties = List[Byte](bytes([1]))
    
    for mob in Mobiles.ApplyFilter(fil):
        if mob.Body == blue_beetle_body_id and mob.Notoriety == 1:
            beetles.append(mob.Serial)
    return beetles
    
if auto_detect_beetles == False: # manual adding
    #change this to the total number of blue beetles you want to use (MAX IS 5)
    number_of_beetles_to_use = 3

    BEETLE1_SERIAL = 0x000787BF   # Change to your beetle serial
    BEETLE2_SERIAL = 0x0008FF98
    BEETLE3_SERIAL = 0x0008F967
    BEETLE4_SERIAL = 0x00000000
    BEETLE5_SERIAL = 0x00000000
    
    BEETLE_SERIALS = [BEETLE1_SERIAL, BEETLE2_SERIAL, BEETLE3_SERIAL, BEETLE4_SERIAL, BEETLE5_SERIAL]   
else: # auto detect beetles
    beetle_info = find_blue_beetles_with_serials()
    BEETLE_SERIALS = beetle_info
    number_of_beetles_to_use = len(BEETLE_SERIALS)
"""    
    #BEETLE_SERIALS = find_blue_beetles_nearby()
    #number_of_beetles_to_use = len(BEETLE_SERIALS)
"""


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
            Player.HeadMessage(2125, f'Beetle {i+1} not found! Check BEETLE_SERIALS[{i}] value.')
            raise Exception(f"Beetle {i+1} not found!")

        Mobiles.WaitForProps(beetle, 200)
        weight = Mobiles.GetPropValue(beetle, "Weight")
        if debug_mode == True:
            print(f"Beetle {i+1} weight: {weight}")

        backpack = beetle.Backpack
        if not backpack:
            #Misc.SendMessage(f"Beetle {i+1} backpack not found!")
            Player.HeadMessage(2125, f'Beetle {i+1} backpack not found!!')
            raise Exception(f"Beetle {i+1} backpack not found!")

        # Dynamically assign variables in the global namespace
        globals()[f'beetle{i+1}'] = beetle
        globals()[f'beetle{i+1}_weight'] = weight
        globals()[f'beetle{i+1}_backpack'] = backpack

def set_beetle_weight_globals(number_of_beetles_to_use):
    if auto_detect_beetles == False:
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
    else:
        for i in range(number_of_beetles_to_use):
            serial = BEETLE_SERIALS[i]
            beetle = Mobiles.FindBySerial(serial)
            Mobiles.WaitForProps(beetle, 200)
            globals()[f'beetle{i+1}_weight'] = Mobiles.GetPropValue(beetle, "Weight")


def chop_logs():
    log = Items.FindByID(wood_logs, -1, Player.Backpack.Serial)
    while log is not None:
        Items.UseItem(axe_serial)
        Target.WaitForTarget(5000, False)
        Target.TargetExecute(log)
        Misc.Pause(1000)
        log = Items.FindByID(wood_logs, -1, Player.Backpack.Serial)

def get_next_non_full_beetle():
    # Returns the index and serial of the next beetle that isnt full.
    # Returns None if all beetles are full
    for i in range(number_of_beetles_to_use):
        weight = globals().get(f'beetle{i+1}_weight', None)
        serial = BEETLE_SERIALS[i]
        backpack = globals().get(f'beetle{i+1}_backpack', None)
        if weight is not None and backpack is not None and weight < max_beetle_weight:
            return i, serial, backpack
        else:
            current_beetle = str(i)
            Player.HeadMessage(2125, f'Beetle {i} is full, going to next beetle!!')
    return None

def move_resources():
    global all_beetles_full
    all_beetles_full = False 
    
    set_beetle_weight_globals(number_of_beetles_to_use) # update beetle weights
    for resource_id in LJ_RESOURCES:
        resources = Items.FindAllByID(resource_id, -1, Player.Backpack.Serial, False)
        for res in resources:
            beetle_info = get_next_non_full_beetle()
            if beetle_info is None:
                Player.HeadMessage(2125, 'ALL BEETLES FULL!!!!')
                all_beetles_full = True
                return
            beetle_index, _, beetle_backpack = beetle_info

            # Get the weight per single item
            # For stackables, the "Weight" property is usually total weight; divide by amount.
            total_item_weight = Items.GetPropValue(res, "Weight")
            amount = int(total_item_weight / 1)
            current_beetle_weight = globals().get(f'beetle{beetle_index+1}_weight', 0)
            available_beetle_weight = max_beetle_weight - current_beetle_weight
            if debug_mode == True:
                Player.HeadMessage(2125, f"DEBUG avail beetle weight: {available_beetle_weight}")

            if total_item_weight is None or amount is None or amount == 0:
                Player.HeadMessage(2125, f"Cannot determine weight/amount for item {res.Serial}!")
                continue

            #weight_per_item = float(total_item_weight) / amount
            weight_per_item = 1
            if debug_mode == True:
                   Player.HeadMessage(2125, f"DEBUG weight per item: {weight_per_item}")

            # How many can we move and not exceed max_beetle_weight?
            max_movable = int(available_beetle_weight // weight_per_item)
            if debug_mode == True:
                Player.HeadMessage(2125, f"DEBUG max movable: {max_movable}")
            if max_movable <= 0:
                Player.HeadMessage(2125, f"Not enough space in Beetle {beetle_index+1}, skipping!")
                continue

            # Move only as much as fits (never more than whats left in the stack)
            move_amount = min(amount, max_movable)
            if debug_mode == True:
                Player.HeadMessage(2125, f"DEBUG move amount: {move_amount}")
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
    
    
   # if debug_mode == True:
   #     for serial in beetle_info:
   #         Misc.SendMessage(f"Detected beetle: (serial: {hex(serial)})")
    
    # If getting heavy, chop up the logs.
    if Player.Weight >= start_chopping_logs_weight:
        #Misc.SendMessage("Heavy, chopping logs...")
        Player.HeadMessage(2125, 'Heavy, dumping to beetles if room')
        chop_logs()
        move_resources()
        Misc.Pause(600)
    # Stop chopping trees when we can\'t carry more.
    if Player.Weight >= stop_chopping_trees_weight:
        #Misc.SendMessage("Too heavy.... Stop")
        Player.HeadMessage(2125, 'Too heavy... Stopping')
        break
