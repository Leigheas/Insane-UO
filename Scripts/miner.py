# This script will mine in place until there's no ore around, then yell at you
# so you can move to a different location.
# I'd advise using the world map and zooming in so you can see the 8x8 zones.
# Then you can move to the next grid and continue mining.
# It doesnt check for beetle weight so you have to watch it yourself, after
# all it is an attended script, just automates the brainless tasks.
#
# REQUIREMENTS:
# - Some (50+) Tinkering skill, to make kits and shovels;
# - A few (~20) iron ingots, or some shovels;
# - A fire beetle;
# - A blue (giant) beetle;
#
from System.Collections.Generic import List
import sys
from System import Byte, Int32

## CONFIG ###
# Serial to your Fire Beetle
fire_beetle = Target.PromptTarget('Target your fire beetle', 43)
# Serial to your Blue (Giant) Beetle
blue_beetle = Target.PromptTarget('Target your blue beetle', 161)
#
# Toolkits should be set to 2+ if using Tinkering
# If set to 1 it might break itself, making you unable to make a new kit
# or more shovels
tool_kits_to_keep = 2
# I like this number high so it stops less often to make new shovels
shovels_to_keep = 5
#
# optional to ls
# If you have a Prospecting Tool on you, tries to increase the ore level
prospect = False
# Use Sturdy Shovels (high uses) - reward from BoDs
sturdy = False
## CONFIG ###

from AutoComplete import *

SHOVEL = 0x0F39
TOOL_KIT = 0x1EB8
ORE_TYPES = [0x19B7, 0x19B8, 0x19B9, 0x19BA]
TINKERING_GUMP = 949095101

ore_filter = Items.Filter()
ore_filter.Graphics.AddRange(ORE_TYPES)


def get_tool_kits():
    return Items.FindAllByID(TOOL_KIT, 0, Player.Backpack.Serial, True)


def get_shovels():
    return Items.FindAllByID(SHOVEL, -1 if sturdy else 0,
                             Player.Backpack.Serial, True)


def gump_check():
    if Gumps.CurrentGump() != TINKERING_GUMP:  # tinkering menu
        Items.UseItem(get_tool_kits()[0])
        Gumps.WaitForGump(TINKERING_GUMP, 2000)
        Gumps.SendAction(TINKERING_GUMP, 15) #orig 41

def make_tool_kit():
    gump_check()
    Gumps.SendAction(TINKERING_GUMP, 23)  # tool kit
    Gumps.WaitForGump(TINKERING_GUMP, 2000)
    return True


def make_shovel():
    gump_check()
    Gumps.SendAction(TINKERING_GUMP, 72)  # shovel
    Gumps.WaitForGump(TINKERING_GUMP, 2000)
    return True


def make_tools():
    kits = len(get_tool_kits())
    shovels = len(get_shovels())

    while kits < tool_kits_to_keep:
        if make_tool_kit():
           kits += 1
        Misc.Pause(200)
         
    while shovels < shovels_to_keep:
        if make_shovel():
            shovels += 1
        Misc.Pause(200)

    Gumps.CloseGump(TINKERING_GUMP)


def move_ingots():
    ingots = Items.FindAllByID(0x1BF2, -1, Player.Backpack.Serial, True)
    beetle_backpack = Mobiles.FindBySerial(blue_beetle).Backpack.Serial
    for i in ingots:
        # keep at least 50 iron ingots in pack to make tools
        Items.Move(i, beetle_backpack,
                   max(0, i.Amount - 50) if i.Hue == 0 else -1)
        Misc.Pause(600)

# credits to omgarturo https://github.com/GloriousRedLeader/omgarturo/blob/master/fm_core/core_rails.py
# Lifted this from the mining script. Returns the same thing as relative
# to player +1 based on direction. The relative function doesnt always
# work for some reason though Target.TargetExecuteRelative(Player.Serial, 1)
def get_tile_in_front(distance = 1):
    direction = Player.Direction
    playerX = Player.Position.X
    playerY = Player.Position.Y
    playerZ = Player.Position.Z
    
    if direction == 'Up':
        tileX = playerX - distance
        tileY = playerY - distance
        tileZ = playerZ
    elif direction == 'North':
        tileX = playerX
        tileY = playerY - distance
        tileZ = playerZ
    elif direction == 'Right':
        tileX = playerX + distance
        tileY = playerY - distance
        tileZ = playerZ
    elif direction == 'East':
        tileX = playerX + distance
        tileY = playerY
        tileZ = playerZ
    elif direction == 'Down':
        tileX = playerX + distance
        tileY = playerY + distance
        tileZ = playerZ
    elif direction == 'South':
        tileX = playerX
        tileY = playerY + distance
        tileZ = playerZ
    elif direction == 'Left':
        tileX = playerX - distance
        tileY = playerY + distance
        tileZ = playerZ
    elif direction == 'West':
        tileX = playerX - distance
        tileY = playerY
        tileZ = playerZ
    return tileX, tileY, tileZ

# credits to omgarturo https://github.com/GloriousRedLeader/omgarturo/blob/master/fm_core/core_gathering.py
# Gets the tile serial. This isnt a trivial task.
# Searching by cave floor tile id. Then doing an item search.
# The cave floor tile is apparently an item with a serial. That is
# how we get the serial.
# The tile serial is provided to Target execute. We cant just use
# the x,y coords because it doesnt work. It just says you cant mine there.
# Also cant use target relative.
def get_tile_in_front_serial():
    tileX, tileY, tileZ = get_tile_in_front()
    #tileinfo = Statics.GetStaticsLandInfo(tileX, tileY, Player.Map)

    filter = Items.Filter()
    # 0x053B is Cave floor
    # 0x0018 is Sand
    filter.Graphics = List[Int32]((0x053B)) 
    filter.OnGround = True
    filter.RangeMax = 1
    items = Items.ApplyFilter(filter)
    for item in items:
        if item.Position.X == tileX and item.Position.Y == tileY:
            return item.Serial, tileX, tileY, tileZ 
    return None, tileX, tileY, tileZ 
    

    
prospected = False
Journal.Clear()  # There is no metal here to mine
while not Player.IsGhost:

    max_weight = Player.MaxWeight
    smelt_weight = max_weight - 70

    try:
        tool = get_shovels()[0]
    except IndexError:
        Player.HeadMessage(2125, 'Out of tools, making more!!')
        make_tools()
        tool = get_shovels()[0]

    if not prospected:
        land = Statics.GetStaticsTileInfo(Player.Position.X, Player.Position.Y,
                                          Player.Map)
        if land:
            Items.UseItemByID(0x0FB4, 0)
            Target.WaitForTarget(2000)
            Target.TargetExecute(Player.Position.X, Player.Position.Y,
                                 Player.Position.Z, land[0].StaticID)
            prospected = True
    
    acme_mines = False
    
    Target.TargetResource(tool, 'ore')
    Misc.Pause(750)
        

    if Journal.Search('You can\'t mine there'):
        
        #credits to omgarturo https://github.com/GloriousRedLeader/omgarturo/blob/master/fm_core/core_gathering.py
        #for the fix for some of the ACME mines.
        tileSerial, tileX, tileY, tileZ  = get_tile_in_front_serial()
        
        Tool = Items.FindByID(0x0F39,-1,Player.Backpack.Serial)
        Items.UseItem(Tool)
        Target.WaitForTarget(2000, False)
        if tileSerial is not None:
            Target.TargetExecute(tileSerial)
        else:
            Target.TargetExecute(tileX, tileY, tileZ)
        #Target.TargetExecute(playerX, playerY, playerZ)
        #Target.TargetExecuteRelative(Player.Serial, 1)
        Journal.Clear('You can\'t mine there')
        Misc.Pause(250)

    if Journal.Search('There is no metal here to mine'):
        x, y = Player.Position.X, Player.Position.Y 
        Player.HeadMessage(1254, "No ore here!")
        prospected = False
        while Player.Position.X == x and Player.Position.Y == y:
            Misc.Pause(50)
        Journal.Clear('There is no metal here to mine')
        
    if Journal.Search('You have found a'):
        m = Journal.GetLineText('You have found a', False)
        Player.HeadMessage(1266, m)
        Journal.Clear(m)
         
    if Player.Weight >= smelt_weight:
        ores = Items.ApplyFilter(ore_filter)
        Player.HeadMessage(2128, 'Smelting...')
        for ore in ores:
            if ore.ItemID == 0x19B7 and ore.Amount == 1:
                continue
            Items.UseItem(ore)
            Target.WaitForTarget(1000)
            Target.TargetExecute(fire_beetle)
            Misc.Pause(200)

        Misc.Pause(600)

    if Player.Weight > max_weight - 50:
        Player.HeadMessage(2127, 'Moving ingots to beetle...')
        move_ingots()
