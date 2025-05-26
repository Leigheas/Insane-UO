# This script will pull a BOD book from a container, dump all BODs on your character into it, then put
# the book back into the container.
# Perfect for BOD collecting characters.
# From InstaCare/Kitsune/Crafty Kitsune
# Issues? Please report in the IUO discord: https://discord.gg/CjBhM6vJZr
#
# What you need to do:
#  ** get the serial of the container that holds the book you want to use
#  ** get the serial of the bod book you want to use
# These can be obtained thru clicking Inspect Entity in Razor Enhanced and then 
# clicking the container or book. Look in the window that pops up for Serial.

from System.Collections.Generic import List
from System import Byte

# ========================== MISC Settings ================================
drag_delay_milliseconds = 700
wait_for_container_delay = 1000

# ========================== Item IDs, Colors, Serials ====================
BOD_ITEM_ID = 0x2258                # Set to your BOD itemID (SHOULD NOT NEED TO CHANGE)
BOD_BOOK_SERIAL = 0x4015EEE0         # The serial of the bod book you want to use
BOD_BOOK_CONTAINER_SERIAL = 0x4020A5FF  # The serial of the container holding the book

# Get the Item objects
#bod_book = Items.FindBySerial(BOD_BOOK_SERIAL)
bod_book_container = Items.FindBySerial(BOD_BOOK_CONTAINER_SERIAL)

# ============================= Helper Functions ===========================
def find_item(item_id, container, color=-1, ignore_containers=None):
    """
    Recursively searches for items by ID and (optionally) color within a container.
    Returns the first found item, or None if not found.
    """
    if ignore_containers is None:
        ignore_containers = []

    ignore_color = (color == -1)
    if not hasattr(container, "Contains"):
        return None

    for item in container.Contains:
        if (isinstance(item_id, int) and item.ItemID == item_id and (ignore_color or item.Hue == color)) or \
           (isinstance(item_id, list) and item.ItemID in item_id and (ignore_color or item.Hue == color)):
            return item

    # Search subcontainers recursively
    for subcontainer in container.Contains:
        if subcontainer.IsContainer and subcontainer.Serial not in ignore_containers:
            found_item = find_item(item_id, subcontainer, color, ignore_containers)
            if found_item:
                return found_item

    return None

def move_item(item, destination_serial, amount=0):
    """
    Moves an item to the specified destination container.
    """
    Items.Move(item, destination_serial, amount)
    Misc.Pause(drag_delay_milliseconds)

def pull_bod_storage_book():
    try:
        # Pulls the BOD book from its storage container to your backpack.
        Items.UseItem(bod_book_container.Serial)
        Misc.Pause(wait_for_container_delay)
        bod_book = Items.FindBySerial(BOD_BOOK_SERIAL) #scan now that container is opened
        if bod_book is None:
            Misc.SendMessage("Error: BOD book not found!", 33)
            return
        # Only move if not already in backpack
        if bod_book.Container != Player.Backpack.Serial:
            move_item(bod_book, Player.Backpack.Serial)
            # Check if move was successful
            Misc.Pause(500)
            bod_book = Items.FindBySerial(BOD_BOOK_SERIAL) #scan again for redundancy
            if bod_book.Container != Player.Backpack.Serial:
                Misc.SendMessage("Error: Failed to move BOD book to backpack.", 33)
            else:
                Misc.SendMessage("Moved BOD book to backpack.", 34)
        else:
            Misc.SendMessage("BOD book is already in your backpack.", 34)
    except Exception as e:
        Misc.SendMessage(f"Exception in pull_bod_storage_book: {e}", 33)

def put_bod_book_back():
    try:
        # Puts the BOD book back into its container.
        Items.UseItem(bod_book_container.Serial)
        Misc.Pause(wait_for_container_delay)
        bod_book = Items.FindBySerial(BOD_BOOK_SERIAL) #scan now that container is opened
        if bod_book is None:
            Misc.SendMessage("Error: BOD book not found!", 33)
            return
        # Only move if in backpack
        if bod_book.Container == Player.Backpack.Serial:
            move_item(bod_book, bod_book_container.Serial)
            # Check if move was successful
            Misc.Pause(500)
            bod_book = Items.FindBySerial(BOD_BOOK_SERIAL) #scan again for redundancy
            if bod_book.Container != bod_book_container.Serial:
                Misc.SendMessage("Error: Failed to move BOD book back to container.", 33)
            else:
                Misc.SendMessage("Moved BOD book back to container.", 34)
        else:
            Misc.SendMessage("BOD book is not in your backpack; cannot move it back to container.", 33)
    except Exception as e:
        Misc.SendMessage(f"Exception in put_bod_book_back: {e}", 33)

def dump_to_central_book():
    # Dumps all BODs on character into the specified BOD book.
    
    # Pull the BOD book to backpack
    pull_bod_storage_book()
    
    bod_book = Items.FindBySerial(BOD_BOOK_SERIAL)
    
    # Find and move all BODs in backpack into the book
    while True:
        bod = find_item(BOD_ITEM_ID, Player.Backpack)
        if not bod:
            break
        move_item(bod, bod_book.Serial)

    # close book gump and put the book back
    Misc.Pause(2000)
    Gumps.CloseGump(0x54f555df)
    put_bod_book_back()


dump_to_central_book()
