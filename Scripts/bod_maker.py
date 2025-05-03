#Bod making script!
#original credits to thomasthorun from UOA
#modified to work with IUO by InstaCare/Kitsune/Crafty Kitsune

import sys
from System.Collections.Generic import List
from System import Int32
from AutoComplete import *



class Bod:
    def __init__(self, skill, serial):
        self.skill = skill
        self.serial = serial
        self.material = ''
        self.exceptional = False
        self.type = 'small'
        self.item = {'name': '', 'done_amount': 0}
        self.items = []
        self.total_amount = 0
        self.filled = False
        self.refresh(True)

    def refresh(self, create_list=False):
        if not self.serial:
            return
        for _ in range(10):
            try:
                txt_list = str(self.serial.Properties).replace("[", "|").replace("]", "|").lower()
                if "exceptional" in txt_list:
                    self.exceptional = True
                if "large bulk" in txt_list:
                    self.type = "large"
                    Misc.IgnoreObject(self.serial)
                if self.skill in ["Blacksmithing", "Tinkering"]:
                    self.material = "Iron"
                    for ingot in skill_info[self.skill]['material']:
                        if "all items must be made with " + ingot.lower() + " ingots." in txt_list:
                            self.material = ingot
                if self.skill == "Tailoring":
                    self.material = "Leather/Hides"
                    for leather in skill_info[self.skill]['material']:
                        if "all items must be made with " + leather.lower().replace("hides", "leather.") in txt_list:
                            self.material = leather
                if self.skill in ["Bowcraft and Fletching", "Carpentry"]:
                    self.material = "Wood"
                    for wood in skill_info[self.skill]['material']:
                        if "|" + wood.lower() + "|" in txt_list:
                            self.material = wood
                for prop in txt_list.split("|"):
                    if ":" in prop and "weight" not in prop:
                        if "amount to make:" in prop:
                            self.total_amount = int(prop.split("amount to make:")[1])
                        else:
                            item_data = prop.split(":")
                            if create_list:
                                self.items.append({'name': item_data[0], 'done_amount': int(item_data[1])})
                                self.item = self.items[0]
                            else:
                                self.item = {'name': item_data[0], 'done_amount': int(item_data[1])}
                return
            except Exception:
                Misc.Pause(10)
        error("Failed to retrieve data from " + self.skill + " BOD.")

    def to_make_quantity(self):
        return self.total_amount - self.item['done_amount']

    def use(self):
        bod_gump_id = 0
        if self.type == "large":
            cont_list = get_root_containers_from_id([0x2258], skill_info[self.skill]['bod_color'])
        else:
            cont_list = get_root_containers_from_id([self.item['name']])
        Journal.Clear()
        for container in cont_list:
            for i in range(10):
                Items.UseItem(self.serial)
                bod_gump_id = get_gump_num(["A bulk order", "A large bulk order"])
                if bod_gump_id > 0 and Gumps.WaitForGump(bod_gump_id, 4000) > 0:
                    Gumps.SendAction(bod_gump_id, 4)
                    if Target.WaitForTarget(4000, False) > 0:
                        Target.TargetExecute(container)
                        break
            Misc.Pause(500)
            Gumps.CloseGump(Gumps.CurrentGump())
            Misc.Pause(500)
            Gumps.CloseGump(bod_gump_id)
            if bod_gump_id == 0:
                error("Failed to open " + self.skill + " BOD gump.")

    def start(self):
        Misc.SendMessage("\r\n\r\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",
                         skill_info[self.skill]['bod_color'])
        Misc.SendMessage(self.skill + " Small BOD | " + self.item['name'].title() +
                         "\r\n*** Starting ***\r\n\r\n", 48)

    def finished(self):
        if (self.type == "small" and self.to_make_quantity() <= 0) or (self.type == "large" and self.filled):
            Misc.IgnoreObject(self.serial)
            Misc.SendMessage("\r\n\r\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",
                             skill_info[self.skill]['bod_color'])
            if self.type == "small" and self.to_make_quantity() <= 0:
                Misc.SendMessage(self.skill + " Small BOD | " + self.item['name'].title() +
                                 "\r\n*** Finished ***\r\n\r\n", 68)
            else:
                Misc.SendMessage(self.skill + " Large BOD | Items: \r\n" +
                                 "\r\n".join([item['name'].title() for item in self.items]) +
                                 "\r\n*** Finished ***\r\n\r\n", 68)
            return True
        return False


alchemy_gump = {
    "categories": [
        ("Exit", 0),
        ("Cancel Make", 84),
        ("Non Quest Item", 77),
        ("Make Last", 21),
        ("Last Ten", 28),
        ("Healing And Curative", 1),
        ("Enhancement", 8),
        ("Toxic", 15),
        ("Explosive", 22),
        ("Strange Brew", 29),
        ("Ingredients", 36),],
    ("Healing And Curative", 1): {
        "Refresh": {
            "btn": 2,
            "stack": False,
            "mats": [("Black Pearl", 1), ("Empty Bottles", 1)],
        },
        "Greater Refreshment": {
            "btn": 9,
            "stack": False,
            "mats": [("Black Pearl", 5), ("Empty Bottles", 1)],
        },
        "Lesser Heal": {
            "btn": 16,
            "stack": False,
            "mats": [("Ginseng", 1), ("Empty Bottles", 1)],
        },
        "Heal": {
            "btn": 23,
            "stack": False,
            "mats": [("Ginseng", 3), ("Empty Bottles", 1)],
        },
        "Greater Heal": {
            "btn": 30,
            "stack": False,
            "mats": [("Ginseng", 7), ("Empty Bottles", 1)],
        },
        "Lesser Cure": {
            "btn": 37,
            "stack": False,
            "mats": [("Garlic", 1), ("Empty Bottles", 1)],
        },
        "Cure": {
            "btn": 44,
            "stack": False,
            "mats": [("Garlic", 3), ("Empty Bottles", 1)],
        },
        "Greater Cure": {
            "btn": 51,
            "stack": False,
            "mats": [("Garlic", 6), ("Empty Bottles", 1)],
        },
        "Elixir Of Rebirth": {
            "btn": 58,
            "stack": False,
            "mats": [
                ("Medusa Blood", 1), ("Spiders' Silk", 3),
                ("Empty Bottles", 1),
            ],
        },
        "Barrab Hemolymph Concentrate": {
            "btn": 65,
            "stack": False,
            "mats": [
                ("Empty Bottles", 1), ("Ginseng", 20),
                ("Plant Clippings", 5), ("Myrmidex Eggsac", 5),
            ],
        },
    },
    ("Enhancement", 8): {
        "Agility": {
            "btn": 2,
            "stack": False,
            "mats": [("Blood Moss", 1), ("Empty Bottles", 1)],
        },
        "Greater Agility": {
            "btn": 9,
            "stack": False,
            "mats": [("Blood Moss", 3), ("Empty Bottles", 1)],
        },
        "Night Sight": {
            "btn": 16,
            "stack": False,
            "mats": [("Spiders' Silk", 1), ("Empty Bottles", 1)],
        },
        "Strength": {
            "btn": 23,
            "stack": False,
            "mats": [("Mandrake Root", 2), ("Empty Bottles", 1)],
        },
        "Greater Strength": {
            "btn": 30,
            "stack": False,
            "mats": [("Mandrake Root", 5), ("Empty Bottles", 1)],
        },
        "Invisibility": {
            "btn": 37,
            "stack": False,
            "mats": [
                ("Empty Bottles", 1), ("Blood Moss", 4),
                ("Nightshade", 3),
            ],
        },
        "Jukari Burn Poultice": {
            "btn": 44,
            "stack": False,
            "mats": [
                ("Empty Bottles", 1), ("Black Pearl", 20),
                ("vanilla", 10), ("Lava Berry", 5),
            ],
        },
        "Kurak Ambusher'S Essence": {
            "btn": 51,
            "stack": False,
            "mats": [
                ("Empty Bottles", 1), ("Blood Moss", 20),
                ("Blue Diamond", 1), ("Lava Berry", 10),
            ],
        },
        "Barako Draft Of Might": {
            "btn": 58,
            "stack": False,
            "mats": [
                ("Empty Bottles", 1), ("Spiders' Silk", 20),
                ("bottle of liquor", 10), ("Perfect Bananas", 5),
            ],
        },
        "Urali Trance Tonic": {
            "btn": 65,
            "stack": False,
            "mats": [
                ("Empty Bottles", 1), ("Mandrake Root", 20),
                ("Sea Serpent or Dragon Scales", 10),
                ("River Moss", 5),
            ],
        },
        "Sakkhra Prophylaxis Potion": {
            "btn":72,
            "stack": False,
            "mats": [
                ("Empty Bottles", 1), ("Nightshade", 20),
                ("bottle of wine", 10), ("Blue Corn", 5),
            ],
        },
    },
    ("Toxic", 15): {
        "Lesser Poison": {
            "btn": 2,
            "stack": False,
            "mats": [("Nightshade", 1), ("Empty Bottles", 1)],
        },
        "Poison": {
            "btn": 9,
            "stack": False,
            "mats": [("Nightshade", 2), ("Empty Bottles", 1)],
        },
        "Greater Poison": {
            "btn": 16,
            "stack": False,
            "mats": [("Nightshade", 4), ("Empty Bottles", 1)],
        },
        "Deadly Poison": {
            "btn": 23,
            "stack": False,
            "mats": [("Nightshade", 8), ("Empty Bottles", 1)],
        },
        "Parasitic": {
            "btn": 30,
            "stack": False,
            "mats": [("Empty Bottles", 1), ("parasitic plant", 5)],
        },
        "Darkglow": {
            "btn": 37,
            "stack": False,
            "mats": [("Empty Bottles", 1), ("luminescent fungi", 5)],
        },
        "Scouring Toxin": {
            "btn": 44,
            "stack": False,
            "mats": [("toxic venom sac", 1), ("Empty Bottles", 1)],
        },
    },
    ("Explosive", 22): {
        "Lesser Explosion": {
            "btn": 2,
            "stack": False,
            "mats": [("Sulfurous Ash", 3), ("Empty Bottles", 1)],
        },
        "Explosion": {
            "btn": 9,
            "stack": False,
            "mats": [("Sulfurous Ash", 5), ("Empty Bottles", 1)],
        },
        "Greater Explosion": {
            "btn": 16,
            "stack": False,
            "mats": [("Sulfurous Ash", 10), ("Empty Bottles", 1)],
        },
        "Conflagration": {
            "btn": 23,
            "stack": False,
            "mats": [("Empty Bottles", 1), ("Grave Dust", 5)],
        },
        "Greater Conflagration": {
            "btn": 30,
            "stack": False,
            "mats": [("Empty Bottles", 1), ("Grave Dust", 10)],
        },
        "Confusion Blast": {
            "btn": 37,
            "stack": False,
            "mats": [("Empty Bottles", 1), ("Pig Iron", 5)],
        },
        "Greater Confusion Blast": {
            "btn": 44,
            "stack": False,
            "mats": [("Empty Bottles", 1), ("Pig Iron", 10)],
        },
        "Black Powder": {
            "btn": 51,
            "stack": True,
            "mats": [
                ("Sulfurous Ash", 1), ("saltpeter", 6), 
                ("charcoal", 1)],
        },
        "Fuse Cord": {
            "btn": 58,
            "stack": False,
            "mats": [
                ("ball of yarn", 1), ("black powder", 1), 
                ("potash", 1)],
        },
    },
    ("Strange Brew", 29): {
        "Smoke Bomb": {
            "btn": 2,
            "stack": False,
            "mats": [("Eggs", 1), ("Ginseng", 3)],
        },
        "Hovering Wisp": {
            "btn": 9,
            "stack": False,
            "mats": [("Captured Essence", 4)],
        },
        "Natural Dye": {
            "btn": 16,
            "stack": False,
            "mats": [("plant pigment", 1), ("color fixative", 1)],
        },
        "Nexus Core ": {
            "btn":23,
            "stack": False,
            "mats": [
                ("Mandrake", 10), ("Spider's Silk", 10),
                ("Dark Sapphire", 5), ("crushed glass", 5),
            ],
        },
    },
    ("Ingredients", 36): {
        "Plant Pigment": {
            "btn": 2,
            "stack": False,
            "mats": [("Plant Clippings", 1), ("empty bottle", 1)],
        },
        "Color Fixative": {
            "btn": 9,
            "stack": False,
            "mats": [("silver serpent venom", 1), ("bottle of wine", 1)],
        },
        "Crystal Granules": {
            "btn": 16,
            "stack": False,
            "mats": [("Shimmering Crystals", 1)],
        },
        "Crystal Dust": {
            "btn": 23,
            "stack": False,
            "mats": [("broken crystals", 4)],
        },
        "Softened Reeds": {
            "btn": 30,
            "stack": False,
            "mats": [("dry reeds", 1), ("scouring toxin", 2)],
        },
        "Vial Of Vitriol": {
            "btn": 37,
            "stack": False,
            "mats": [("Parasitic Poison", 1), ("Nightshade", 30)],
        },
        "Bottle Of Ichor": {
            "btn": 44,
            "stack": False,
            "mats": [("Darkglow Poison", 1), ("Spiders' Silk", 1)],
        },
        "Potash": {
            "btn": 51, 
            "stack": True, 
            "mats": [("Boards or Logs", 1)]
        },
        "Gold Dust": {
            "btn": 58, 
            "stack": False, 
            "mats": [("Gold", 1000)]
        },
    },
}

blacksmithing_gump = {
    'categories': [
        ('Exit', 0), 
        ('Cancel Make', 84), 
        ('Repair Item', 42), 
        ('Mark Item', 49), 
        ('Enhance Item', 63), 
        ('Non Quest Item', 77), 
        ('Make Last', 21), 
        ('Smelt Item', 14), 
        ('Last Ten', 28), 
        ('Metal Armor', 1),
        ('Helmets', 8), 
        ('Shields', 15), 
        ('Bladed', 22), 
        ('Axes', 28), 
        ('Polearms', 36), 
        ('Bashing', 43),
        ('Cannons', 50), 
        ('Throwing', 57), 
        ('Miscellaneous', 64),
    ],
    ("Metal Armor", 1): {
        "Ringmail Gloves": {"btn": 2, "stack": False, "mats": [("Ingots", 10)]},
        "Ringmail Leggings": {"btn": 9, "stack": False, "mats": [("Ingots", 16)]},
        "Ringmail Sleeves": {"btn": 16, "stack": False, "mats": [("Ingots", 14)]},
        "Ringmail Tunic": {"btn": 23, "stack": False, "mats": [("Ingots", 18)]},
        "Chainmail Coif": {"btn": 30, "stack": False, "mats": [("Ingots", 10)]},
        "Chainmail Leggings": {"btn": 37, "stack": False, "mats": [("Ingots", 18)]},
        "Chainmail Tunic": {"btn": 44, "stack": False, "mats": [("Ingots", 20)]},
        "Platemail Arms": {"btn": 51, "stack": False, "mats": [("Ingots", 18)]},
        "Platemail Gloves": {"btn": 58, "stack": False, "mats": [("Ingots", 12)]},
        "Platemail Gorget": {"btn": 65, "stack": False, "mats": [("Ingots", 10)]},
        "Platemail Legs": {"btn": 72, "stack": False, "mats": [("Ingots", 20)]},
        "Platemail (Tunic)": {"btn": 79, "stack": False, "mats": [("Ingots", 25)]},
        "Platemail (Female) Plate": {"btn": 56, "stack": False, "mats": [("Ingots", 20)]},
        "Platemail Mempo": {"btn": 93, "stack": False, "mats": [("Ingots", 18)]},
        "Platemail Do": {"btn": 100, "stack": False, "mats": [("Ingots", 28)]},
        "Platemail Hiro Sode": {"btn": 107, "stack": False, "mats": [("Ingots", 16)]},
        "Platemail Suneate": {"btn": 114, "stack": False, "mats": [("Ingots", 20)]},
        "Platemail Haidate": {"btn": 121, "stack": False, "mats": [("Ingots", 20)]},
        "Gargish Platemail Arms": {"btn": 142, "stack": False, "mats": [("Ingots", 18)]},
        "Gargish Platemail Chest": {"btn": 149, "stack": False, "mats": [("Ingots", 25)]},
        "Gargish Platemail Leggings": {"btn": 156, "stack": False, "mats": [("Ingots", 20)]},
        "Gargish Platemail Kilt": {"btn": 163, "stack": False, "mats": [("Ingots", 12)]},
        "Gargish Platemail Arms 2": {"btn": 170, "stack": False, "mats": [("Ingots", 18)]},
        "Gargish Platemail Chest 2": {"btn": 177, "stack": False, "mats": [("Ingots", 25)]},
        "Gargish Platemail Leggings 2": {"btn": 184, "stack": False, "mats": [("Ingots", 20)]},
        "Gargish Platemail Kilt 2": {"btn": 191, "stack": False, "mats": [("Ingots", 12)]},
        "Gargish Amulet": {"btn": 198, "stack": False, "mats": [("Ingots", 3)]},
        "Britches Of Warding": {"btn": 205, "stack": False, "mats": [
             ("Ingots", 18), ("Leggings of Bane", 1),
             ("Turquoise", 4), ("Blood of the Dark Father", 5)]},
    },
    ('Helmets', 8):
        {"Bascinet": {'btn': 2, 'stack': False, 'mats': [("Ingots", 15)]},
         "Close Helmet": {'btn': 9, 'stack': False, 'mats': [("Ingots", 15)]},
         "Helmet": {'btn': 16, 'stack': False, 'mats': [("Ingots", 15)]},
         "Norse Helm": {'btn': 23, 'stack': False, 'mats': [("Ingots", 15)]},
         "Plate Helm": {'btn': 30, 'stack': False, 'mats': [("Ingots", 15)]},
         "Chainmail Hatsuburi": {'btn': 37, 'stack': False, 'mats': [("Ingots", 20)]},
         "Platemail Hatsuburi": {'btn': 44, 'stack': False, 'mats': [("Ingots", 20)]},
         "Heavy Platemail Jingasa": {'btn': 51, 'stack': False, 'mats': [("Ingots", 20)]},
         "Light Platemail Jingasa": {'btn': 58, 'stack': False, 'mats': [("Ingots", 20)]},
         "Small Platemail Jingasa": {'btn': 65, 'stack': False, 'mats': [("Ingots", 20)]},
         "Decorative Platemail Kabuto": {'btn': 72, 'stack': False, 'mats': [("Ingots", 25)]},
         "Platemail Battle Kabuto": {'btn': 79, 'stack': False, 'mats': [("Ingots", 25)]},
         "Standard Platemail Kabuto": {'btn': 86, 'stack': False, 'mats': [("Ingots", 25)]},
         "Circlet": {'btn': 93, 'stack': False, 'mats': [("Ingots", 6)]},
         "Royal Circlet": {'btn': 100, 'stack': False, 'mats': [("Ingots", 6)]},
         "Gemmed Circlet": {'btn': 107, 'stack': False, 'mats':
             [("Ingots", 6), ("Tourmalines", 1), ("Amethysts", 1), ("Blue Diamond", 1)]},
    },
    ('Shields', 15):
        {"Buckler ": {'btn': 2, 'stack': False, 'mats': [("Ingots", 10)]},
         "Bronze Shield": {'btn': 9, 'stack': False, 'mats': [("Ingots", 12)]},
         "Heater Shield": {'btn': 16, 'stack': False, 'mats': [("Ingots", 18)]},
         "Metal Shield": {'btn': 23, 'stack': False, 'mats':  [("Ingots", 14)]},
         "Metal Kite Shield": {'btn': 30, 'stack': False, 'mats': [("Ingots", 16)]},
         "Tear Kite Shield": {'btn': 37, 'stack': False, 'mats': [("Ingots", 8)]},
         "Chaos Shield": {'btn': 44, 'stack': False, 'mats': [("Ingots", 25)]},
         "Order Shield": {'btn': 51, 'stack': False, 'mats': [("Ingots", 25)]},
         "Small Plate Shield": {'btn': 58, 'stack': False, 'mats': [("Ingots", 12)]},
         "Gargish Kite Shield": {'btn': 65, 'stack': False, 'mats': [("Ingots", 16)]},
         "Large Plate Shield": {'btn': 72, 'stack': False, 'mats': [("Ingots", 18)]},
         "Medium Plate Shield": {'btn': 79, 'stack': False, 'mats': [("Ingots", 14)]},
         "Gargish Chaos Shield": {'btn': 86, 'stack': False, 'mats': [("Ingots", 25)]},
         "Gargish Order Shield": {'btn': 93, 'stack': False, 'mats': [("Ingots", 25)]}
        },
    ('Bladed', 22):
        {"Bone Harvester": {'btn': 2, 'stack': False, 'mats': [("Ingots", 10)]},
         "Broadsword": {'btn': 9, 'stack': False, 'mats': [("Ingots", 10)]},
         "Crescent Blade": {'btn': 16, 'stack': False, 'mats': [("Ingots", 14)]},
         "Cutlass": {'btn': 23, 'stack': False, 'mats': [("Ingots", 8)]},
         "Dagger": {'btn': 30, 'stack': False, 'mats': [("Ingots", 3)]},
         "Katana": {'btn': 37, 'stack': False, 'mats': [("Ingots", 8)]},
         "Kryss": {'btn': 44, 'stack': False, 'mats': [("Ingots", 8)]},
         "Longsword": {'btn': 51, 'stack': False, 'mats': [("Ingots", 12)]},
         "Scimitar": {'btn': 58, 'stack': False, 'mats': [("Ingots", 10)]},
         "Viking Sword": {'btn': 65, 'stack': False, 'mats': [("Ingots", 14)]},
         "No-Dachi": {'btn': 72, 'stack': False, 'mats': [("Ingots", 18)]},
         "Wakizashi": {'btn': 79, 'stack': False, 'mats': [("Ingots", 8)]},
         "Lajatang": {'btn': 86, 'stack': False, 'mats': [("Ingots", 25)]},
         "Daisho": {'btn': 93, 'stack': False, 'mats': [("Ingots", 15)]},
         "Tekagi": {'btn': 100, 'stack': False, 'mats': [("Ingots", 12)]},
         "Shuriken": {'btn': 107, 'stack': False, 'mats': [("Ingots", 5)]},
         "Kama": {'btn': 114, 'stack': False, 'mats': [("Ingots", 14)]},
         "Sai": {'btn': 121, 'stack': False, 'mats': [("Ingots", 12)]},
         "Radiant Scimitar": {'btn': 128, 'stack': False, 'mats': [("Ingots", 15)]},
         "War Cleaver": {'btn': 135, 'stack': False, 'mats': [("Ingots", 18)]},
         "Elven Spellblade": {'btn': 142, 'stack': False, 'mats': [("Ingots", 14)]},
         "Assassin Spike": {'btn': 149, 'stack': False, 'mats': [("Ingots", 9)]},
         "Leafblade": {'btn': 156, 'stack': False, 'mats': [("Ingots", 12)]},
         "Rune Blade": {'btn': 163, 'stack': False, 'mats': [("Ingots", 15)]},
         "Elven Machete": {'btn': 170, 'stack': False, 'mats': [("Ingots", 14)]},
         "Rune Carving Knife": {'btn': 177, 'stack': False, 'mats': 
             [("Ingots", 9), ("Dread Horn Mane", 1), ("Putrefaction", 10), ("Muculent", 10)]},
         "Cold Forged Blade": {'btn': 184, 'stack': False, 'mats':
             [("Ingots", 18), ("Grizzled Bones", 1), ("Grizzled Bones", 10), ("Blight", 10)]},
         "Overseer Sundered Blade": {'btn': 191, 'stack': False, 'mats':
             [("Ingots", 15), ("Grizzled Bones", 1), ("Blight", 10), ("Scourge", 10)]},
         "Luminous Rune Blade": {'btn': 198, 'stack': False, 'mats':
             [("Ingots", 15), ("Grizzled Bones", 1), ("Corruption", 10), ("Putrefaction", 10)]},
         "True Spellblade": {'btn': 205, 'stack': False, 'mats':
             [("Ingots", 14), ("Blue Diamond", 1)]},
         "Icy Spellblade": {'btn': 212, 'stack': False, 'mats':
             [("Ingots", 14), ("Turquoise", 1)]},
         "Fiery Spellblade": {'btn': 219, 'stack': False, 'mats':
             [("Ingots", 14), ("Fire Ruby", 1)]},
         "Spellblade Of Defense": {'btn': 226, 'stack': False, 'mats':
             [("Ingots", 18), ("White Pearl", 1)]},
         "True Assassin Spike": {'btn': 233, 'stack': False, 'mats':
             [("Ingots", 9), ("Dark Sapphire", 1)]},
         "Charged Assassin Spike": {'btn': 240, 'stack': False, 'mats':
             [("Ingots", 9), ("Ecru Citrine", 1)]},
         "Magekiller Assassin Spike": {'btn': 247, 'stack': False, 'mats':
             [("Ingots", 9), ("Brilliant Amber", 1)]},
         "Wounding Assassin Spike": {'btn': 254, 'stack': False, 'mats':
             [("Ingots", 9), ("Perfect Emerald", 1)]},
         "True Leafblade": {'btn': 261, 'stack': False, 'mats':
             [("Ingots", 12), ("Blue Diamond", 1)]},
         "Luckblade": {'btn': 268, 'stack': False, 'mats':
             [("Ingots", 12), ("White Pearl", 1)]},
         "Magekiller Leafblade": {'btn': 275, 'stack': False, 'mats':
             [("Ingots", 12), ("Fire Ruby", 1)]},
         "Leafblade Of Ease": {'btn': 282, 'stack': False, 'mats':
             [("Ingots", 12), ("Perfect Emerald", 1)]},
         "Knight'S War Cleaver": {'btn': 289, 'stack': False, 'mats':
             [("Ingots", 18), ("Perfect Emerald", 1)]},
         "Butcher'S War Cleaver": {'btn': 296, 'stack': False, 'mats':
             [("Ingots", 18), ("Turquoise", 1)]},
         "Serrated War Cleaver": {'btn': 303, 'stack': False, 'mats':
             [("Ingots", 18), ("Ecru Citrine", 1)]},
         "True War Cleaver": {'btn': 310, 'stack': False, 'mats':
             [("Ingots", 18), ("Brilliant Amber", 1)]},
         "Adventurer'S Machete": {'btn': 317, 'stack': False, 'mats':
             [("Ingots", 14), ("White Pearl", 1)]},
         "Orcish Machete": {'btn': 324, 'stack': False, 'mats':
             [("Ingots", 14), ("Scourge", 1)]},
         "Machete Of Defense": {'btn': 331, 'stack': False, 'mats':
             [("Ingots", 14), ("Brilliant Amber", 1)]},
         "Diseased Machete": {'btn': 338, 'stack': False, 'mats':
             [("Ingots", 14), ("Blight", 1)]},
         "Runesabre": {'btn': 345, 'stack': False, 'mats':
             [("Ingots", 15), ("Turquoise", 1)]},
         "Mage'S Rune Blade": {'btn': 352, 'stack': False, 'mats':
             [("Ingots", 15), ("Blue Diamond", 1)]},
         "Rune Blade Of Knowledge": {'btn': 359, 'stack': False, 'mats':
             [("Ingots", 15), ("Ecru Citrine", 1)]},
         "Corrupted Rune Blade": {'btn': 366, 'stack': False, 'mats':
             [("Ingots", 15), ("Corruption", 1)]},
         "True Radiant Scimitar": {'btn': 373, 'stack': False, 'mats':
             [("Ingots", 15), ("Brilliant Amber", 1)]},
         "Darkglow Scimitar": {'btn': 380, 'stack': False, 'mats':
             [("Ingots", 15), ("Dark Sapphire", 1)]},
         "Icy Scimitar": {'btn': 387, 'stack': False, 'mats':
             [("Ingots", 15), ("Dark Sapphire", 1)]},
         "Twinkling Scimitar": {'btn': 394, 'stack': False, 'mats':
             [("Ingots", 15), ("Dark Sapphire", 1)]},
         "Bone Machete": {'btn': 401, 'stack': False, 'mats':
             [("Ingots", 20), ("Bones", 6)]},
         "Gargish Katana": {'btn': 408, 'stack': False, 'mats': [("Ingots", 8)]},
         "Gargish Kryss": {'btn': 415, 'stack': False, 'mats': [("Ingots", 8)]},
         "Gargish Bone Harvester": {'btn': 422, 'stack': False, 'mats': [("Ingots", 10)]},
         "Gargish Tekagi": {'btn': 429, 'stack': False, 'mats': [("Ingots", 12)]},
         "Gargish Daisho": {'btn': 436, 'stack': False, 'mats': [("Ingots", 15)]},
         "Dread Sword": {'btn': 443, 'stack': False, 'mats': [("Ingots", 14)]},
         "Gargish Talwar": {'btn': 450, 'stack': False, 'mats': [("Ingots", 18)]},
         "Gargish Dagger": {'btn': 457, 'stack': False, 'mats': [("Ingots", 3)]},
         "Bloodblade": {'btn': 464, 'stack': False, 'mats': [("Ingots", 8)]},
         "Shortblade": {'btn': 471, 'stack': False, 'mats': [("Ingots", 12)]}
        },
    ('Axes', 29):
        {"Axe": {'btn': 2, 'stack': False, 'mats': [("Ingots", 14)]},
         "Battle Axe": {'btn': 9, 'stack': False, 'mats': [("Ingots", 14)]},
         "Double Axe": {'btn': 16, 'stack': False, 'mats': [("Ingots", 12)]},
         "Executioner'S Axe": {'btn': 23, 'stack': False, 'mats': [("Ingots", 14)]},
         "Large Battle Axe": {'btn': 30, 'stack': False, 'mats': [("Ingots", 12)]},
         "Two Handed Axe": {'btn': 37, 'stack': False, 'mats': [("Ingots", 16)]},
         "War Axe": {'btn': 44, 'stack': False, 'mats': [("Ingots", 16)]},
         "Ornate Axe": {'btn': 51, 'stack': False, 'mats': [("Ingots", 18)]},
         "Guardian Axe": {'btn': 58, 'stack': False, 'mats':
             [("Ingots", 15), ("Blue Diamond", 1)]},
         "Singing Axe": {'btn': 65, 'stack': False, 'mats':
             [("Ingots", 15), ("Brilliant Amber", 1)]},
         "Thundering Axe": {'btn': 72, 'stack': False, 'mats':
             [("Ingots", 15), ("Ecru Citrine", 1)]},
         "Heavy Ornate Axe": {'btn': 79, 'stack': False, 'mats':
             [("Ingots", 15), ("Turquoise", 1)]},
         "Gargish Battle Axe": {'btn': 86, 'stack': False, 'mats': [("Ingots", 14)]},
         "Gargish Axe": {'btn': 93, 'stack': False, 'mats': [("Ingots", 14)]},
         "Dual Short Axes": {'btn': 100, 'stack': False, 'mats': [("Ingots", 24)]}
        },
    ('Polearms', 36):
        {"Bardiche": {'btn': 2, 'stack': False, 'mats': [("Ingots", 18)]},
         "Bladed Staff": {'btn': 9, 'stack': False, 'mats': [("Ingots", 12)]},
         "Double Bladed Staff": {'btn': 16, 'stack': False, 'mats': [("Ingots", 16)]},
         "Halberd": {'btn': 23, 'stack': False, 'mats': [("Ingots", 20)]},
         "Lance": {'btn': 30, 'stack': False, 'mats': [("Ingots", 20)]},
         "Pike": {'btn': 37, 'stack': False, 'mats': [("Ingots", 12)]},
         "Short Spear": {'btn': 44, 'stack': False, 'mats': [("Ingots", 6)]},
         "Scythe": {'btn': 51, 'stack': False, 'mats': [("Ingots", 14)]},
         "Spear": {'btn': 58, 'stack': False, 'mats':  [("Ingots", 12)]},
         "War Fork": {'btn': 65, 'stack': False, 'mats': [("Ingots", 12)]},
         "Gargish Bardiche": {'btn': 72, 'stack': False, 'mats': [("Ingots", 18)]},
         "Gargish War Fork": {'btn': 79, 'stack': False, 'mats': [("Ingots", 12)]},
         "Gargish Scythe": {'btn': 86, 'stack': False, 'mats': [("Ingots", 14)]},
         "Gargish Pike": {'btn': 93, 'stack': False, 'mats': [("Ingots", 12)]},
         "Gargish Lance": {'btn': 100, 'stack': False, 'mats': [("Ingots", 20)]},
         "Dual Pointed Spear": {'btn': 107, 'stack': False, 'mats': [("Ingots", 16)]}
        },
    ('Bashing', 43):
        {"Hammer Pick": {'btn': 2, 'stack': False, 'mats': [("Ingots", 16)]},
         "Mace": {'btn': 9, 'stack': False, 'mats': [("Ingots", 6)]},
         "Maul": {'btn': 16, 'stack': False, 'mats': [("Ingots", 10)]},
         "Scepter": {'btn': 23, 'stack': False, 'mats': [("Ingots", 10)]},
         "War Mace": {'btn': 30, 'stack': False, 'mats': [("Ingots", 14)]},
         "War Hammer": {'btn': 37, 'stack': False, 'mats': [("Ingots", 16)]},
         "Tessen": {'btn': 44, 'stack': False, 'mats':
             [("Ingots", 16), ("Cloth", 10)]},
         "Diamond Mace": {'btn': 51, 'stack': False, 'mats': [("Ingots", 20)]},
         "Shard Thrasher": {'btn': 58, 'stack': False, 'mats':
             [("Ingots", 20), ("Eye of the Travesty", 1), ("Muculent", 10), ("Corruption", 10)]},
         "Ruby Mace": {'btn': 65, 'stack': False, 'mats':
             [("Ingots", 20), ("Fire Ruby", 1)]},
         "Emerald Mace": {'btn': 72, 'stack': False, 'mats':
             [("Ingots", 20), ("Perfect Emerald", 1)]},
         "Sapphire Mace": {'btn': 79, 'stack': False, 'mats':
             [("Ingots", 20), ("Dark Sapphire", 1)]},
         "Silver-Etched Mace": {'btn': 86, 'stack': False, 'mats':
             [("Ingots", 20), ("Blue Diamond", 1)]},
         "Gargish War Hammer": {'btn': 93, 'stack': False, 'mats': [("Ingots", 16)]},
         "Gargish Maul": {'btn': 100, 'stack': False, 'mats': [("Ingots", 10)]},
         "Gargish Tessen": {'btn': 107, 'stack': False, 'mats':
             [("Ingots", 16), ("Cloth", 10)]},
         "Disc Mace": {'btn': 114, 'stack': False, 'mats': [("Ingots", 20)]}
        },
    ('Cannons', 50):
        {"Cannonball": {'btn': 2, 'stack': True, 'mats': [("Ingots", 12)]},
         "Grapeshot": {'btn': 9, 'stack': True, 'mats':
             [("Ingots", 12), ("Cloth", 2)]},
         "Culverin": {'btn': 16, 'stack': False, 'mats':
             [("Ingots", 900), ("Boards or Logs", 50)]},
         "Carronade": {'btn': 23, 'stack': False, 'mats':
             [("Ingots", 1800), ("Boards or Logs", 75)]}
        },
    ('Throwing', 57):
        {"Boomerang": {'btn': 2, 'stack': False, 'mats': [("Ingots", 5)]},
         "Cyclone": {'btn': 9, 'stack': False, 'mats': [("Ingots", 9)]},
         "Soul Glaive": {'btn': 16, 'stack': False, 'mats': [("Ingots", 9)]}
        },
    ('Miscellaneous', 64):
        {"Dragon Gloves": {'btn': 2, 'stack': False, 'mats': [("Dragon Scales", 16)]},
         "Dragon Helm": {'btn': 9, 'stack': False, 'mats': [("Dragon Scales", 20)]},
         "Dragon Leggings": {'btn': 16, 'stack': False, 'mats': [("Dragon Scales", 28)]},
         "Dragon Sleeves": {'btn': 23, 'stack': False, 'mats': [("Dragon Scales", 24)]},
         "Dragon Breastplate": {'btn': 30, 'stack': False, 'mats': [("Dragon Scales", 36)]},
         "Crushed Glass": {'btn': 37, 'stack': False, 'mats':
             [("Blue Diamond", 1), ("glass sword", 5)]},
         "Powdered Iron": {'btn': 44, 'stack': False, 'mats':
             [("white pearl", 1), ("Ingots", 20)]},
         "Metal Keg": {'btn': 51, 'stack': False, 'mats': [("Ingots", 25)]},
         "Exodus Sacrificial Dagger": {'btn': 58, 'stack': False, 'mats':
             [("Ingots", 12), ("Blue Diamond", 2), ("Fire Ruby", 2), ("a small piece of blackrock", 10)]},
         "Gloves Of Feudal Grip": {'btn': 65, 'stack': False, 'mats':
             [("Dragon Scales", 18), ("Blue Diamond", 4), ("Gauntlets of Nobility", 1),
             ("Blood of the Dark Father", 5)]}
        }
    }

bowcraft_gump = {
    'categories': [
        ('Exit', 0), 
        ('Cancel Make', 84), 
        ('Repair Item', 42), 
        ('Mark Item', 49), 
        ('Enhance Item', 63), 
        ('Non Quest Item', 77), 
        ('Make Last', 21), 
        ('Last Ten', 28), 
        ('Materials', 1), 
        ('Ammunition', 8), 
        ('Weapons', 15)
    ],
    ('Materials', 1):
        {"Elven Fletching": {'btn': 2, 'stack': False, 'mats':
             [("Feathers", 20), ("faery dust", 1)]},
         "Kindling": {'btn': 9, 'stack': False, 'mats': [("Boards or Logs", 1)]},
         "Shaft": {'btn': 16, 'stack': True, 'mats': [("Boards or Logs", 1)]}
        },
    ('Ammunition', 8):
        {"Arrow": {'btn': 2, 'stack': True, 'mats':
             [("Arrow Shafts", 1), ("Feathers", 1)]},
         "Crossbow Bolt": {'btn': 9, 'stack': True, 'mats':
             [("Arrow Shafts", 1), ("Feathers", 1)]},
         "Fukiya Dart": {'btn': 16, 'stack': True, 'mats': [("Boards or Logs", 1)]}
        },
    ('Weapons', 15):
        {"Bow": {'btn': 2, 'stack': False, 'mats': [("Boards or Logs", 7)]},
         "Crossbow": {'btn': 9, 'stack': False, 'mats': [("Boards or Logs", 7)]},
         "Heavy Crossbow": {'btn': 16, 'stack': False, 'mats': [("Boards or Logs", 10)]},
         "Composite Bow": {'btn': 23, 'stack': False, 'mats': [("Boards or Logs", 7)]},
         "Repeating Crossbow": {'btn': 30, 'stack': False, 'mats': [("Boards or Logs", 10)]},
         "Yumi": {'btn': 37, 'stack': False, 'mats': [("Boards or Logs", 10)]},
         "Elven Composite Longbow": {'btn': 44, 'stack': False, 'mats': [("Boards or Logs", 20)]},
         "Magical Shortbow": {'btn': 51, 'stack': False, 'mats': [("Boards or Logs", 15)]},
         "Blight Gripped Longbow": {'btn': 58, 'stack': False, 'mats':
             [("Boards or Logs", 20), ("Lard of Paroxysmus", 1), ("Blight", 10), ("Corruption", 10)]},
         "Faerie Fire": {'btn': 65, 'stack': False, 'mats':
             [("Boards or Logs", 20), ("Lard of Paroxysmus", 1), ("Putrefaction", 10), ("Taint", 10)]},
         "Silvani'S Feywood Bow": {'btn': 72, 'stack': False, 'mats':
             [("Boards or Logs", 20), ("Lard of Paroxysmus", 1), ("Scourge", 10), ("Muculent", 10)]},
         "Mischief Maker": {'btn': 79, 'stack': False, 'mats':
             [("Boards or Logs", 15), ("Dread Horn Mane", 1), ("Corruption", 10), ("Putrefaction", 10)]},
         "The Night Reaper": {'btn': 86, 'stack': False, 'mats':
             [("Boards or Logs", 10), ("Dread Horn Mane", 1), ("Blight", 10), ("Scourge", 10)]},
         "Barbed Longbow": {'btn': 93, 'stack': False, 'mats':
             [("Boards or Logs", 20), ("fire ruby", 1)]},
         "Slayer Longbow": {'btn': 100, 'stack': False, 'mats':
             [("Boards or Logs", 20), ("brilliant amber", 1)]},
         "Frozen Longbow": {'btn': 107, 'stack': False, 'mats':
             [("Boards or Logs", 20), ("turquoise", 1)]},
         "Longbow Of Might": {'btn': 114, 'stack': False, 'mats':
             [("Boards or Logs", 10), ("blue diamond", 1)]},
         "Ranger'S Shortbow": {'btn': 121, 'stack': False, 'mats':
             [("Boards or Logs", 15), ("perfect emerald", 1)]},
         "Lightweight Shortbow": {'btn': 128, 'stack': False, 'mats':
             [("Boards or Logs", 15), ("white pearl", 1)]},
         "Mystical Shortbow": {'btn': 135, 'stack': False, 'mats':
             [("Boards or Logs", 15), ("ecru citrine", 1)]},
         "Assassin'S Shortbow": {'btn': 142, 'stack': False, 'mats':
             [("Boards or Logs", 15), ("dark sapphire", 1)]}
        }
    }

carpentry_gump = {
    'categories': [
        ('Exit', 0), 
        ('Cancel Make', 84), 
        ('Repair Item', 42), 
        ('Mark Item', 49), 
        ('Enhance Item', 63), 
        ('Non Quest Item', 77), 
        ('Make Last', 21), 
        ('Last Ten', 28), 
        ('Other', 1), 
        ('Furniture', 8), 
        ('Containers', 15), 
        ('Weapons', 22), 
        ('Armor', 29), 
        ('Instruments', 36), 
        ('Misc. Add-Ons', 43), 
        ('Tailoring And Cooking', 50), 
        ('Anvils And Forges', 57), 
        ('Training', 64)
    ], 
    ('Other', 1):
        {"Barrel Staves": {'btn': 2, 'stack': False, 'mats': [("Boards or Logs", 5)]},
         "Barrel Lid": {'btn': 9, 'stack': False, 'mats': [("Boards or Logs", 4)]},
         "Short Music Stand (Left)": {'btn': 16, 'stack': False, 'mats': [("Boards or Logs", 15)]},
         "Short Music Stand (Right)": {'btn': 23, 'stack': False, 'mats': [("Boards or Logs", 15)]},
         "Tall Music Stand (Left)": {'btn': 30, 'stack': False, 'mats': [("Boards or Logs", 20)]},
         "Tall Music Stand (Right)": {'btn': 37, 'stack': False, 'mats': [("Boards or Logs", 20)]},
         "Easel (South)": {'btn': 44, 'stack': False, 'mats': [("Boards or Logs", 20)]},
         "Easel (East)": {'btn': 51, 'stack': False, 'mats': [("Boards or Logs", 20)]},
         "Easel (North)": {'btn': 58, 'stack': False, 'mats': [("Boards or Logs", 20)]},
         "Red Hanging Lantern": {'btn': 65, 'stack': False, 'mats':
             [("Boards or Logs", 5), ("Blank Scrolls", 10)]},
         "White Hanging Lantern": {'btn': 72, 'stack': False, 'mats':
             [("Boards or Logs", 5), ("Blank Scrolls", 10)]},
         "Shoji Screen": {'btn': 79, 'stack': False, 'mats':
             [("Boards or Logs", 75), ("Cloth", 60)]},
         "Bamboo Screen": {'btn': 86, 'stack': False, 'mats':
             [("Boards or Logs", 75), ("Cloth", 60)]},
         "Fishing Pole": {'btn': 93, 'stack': False, 'mats':
             [("Boards or Logs", 5), ("Cloth", 5)]},
         "Wooden Container Engraving Tool": {'btn': 100, 'stack': False, 'mats':
             [("Boards or Logs", 4), ("Ingots", 2)]},
         "Runed Switch": {'btn': 107, 'stack': False, 'mats':
             [("Boards or Logs", 2), ("Enchanted Switch", 1), ("Runed Prism", 1), ("jeweled filigree", 1)]},
         "Arcanist Statue (South)": {'btn': 114, 'stack': False, 'mats': [("Boards or Logs", 250)]},
         "Arcanist Statue (East)": {'btn': 121, 'stack': False, 'mats': [("Boards or Logs", 250)]},
         "Warrior Statue (South)": {'btn': 128, 'stack': False, 'mats': [("Boards or Logs", 250)]},
         "Warrior Statue (East)": {'btn': 135, 'stack': False, 'mats': [("Boards or Logs", 250)]},
         "Squirrel Statue (South)": {'btn': 142, 'stack': False, 'mats': [("Boards or Logs", 250)]},
         "Squirrel Statue (East)": {'btn': 149, 'stack': False, 'mats': [("Boards or Logs", 250)]},
         "Giant Replica Acorn": {'btn': 156, 'stack': False, 'mats': [("Boards or Logs", 35)]},
         "Mounted Dread Horn": {'btn': 163, 'stack': False, 'mats':
             [("Boards or Logs", 50), ("Pristine Dread Horn", 1)]},
         "Acid Proof Rope": {'btn': 170, 'stack': False, 'mats':
             [("Greater Strength Potion", 2), ("Protection", 1), ("switch", 1)]},
         "Gargish Banner": {'btn': 177, 'stack': False, 'mats':
             [("Boards or Logs", 50), ("Cloth", 50)]},
         "An Incubator": {'btn': 184, 'stack': False, 'mats': [("Boards or Logs", 100)]},
         "A Chicken Coop": {'btn': 191, 'stack': False, 'mats': [("Boards or Logs", 150)]},
         "Exodus Summoning Altar": {'btn': 198, 'stack': False, 'mats':
             [("Boards or Logs", 100), ("high quality granite", 10), ("a small piece of blackrock", 10),
              ("nexus core ", 1)]},
         "Dark Wooden Sign Hanger": {'btn': 205, 'stack': False, 'mats': [("Boards or Logs", 5)]},
         "Light Wooden Sign Hanger": {'btn': 212, 'stack': False, 'mats': [("Boards or Logs", 5)]}},
    ('Furniture', 8):
        {"Foot Stool": {'btn': 2, 'stack': False, 'mats': [("Boards or Logs", 9)]},
         "Stool": {'btn': 9, 'stack': False, 'mats': [("Boards or Logs", 9)]},
         "Straw Chair": {'btn': 16, 'stack': False, 'mats': [("Boards or Logs", 13)]},
         "Wooden Chair": {'btn': 23, 'stack': False, 'mats': [("Boards or Logs", 13)]},
         "Vesper-Style Chair": {'btn': 30, 'stack': False, 'mats': [("Boards or Logs", 15)]},
         "Trinsic-Style Chair": {'btn': 37, 'stack': False, 'mats': [("Boards or Logs", 13)]},
         "Wooden Bench": {'btn': 44, 'stack': False, 'mats': [("Boards or Logs", 17)]},
         "Wooden Throne": {'btn': 51, 'stack': False, 'mats': [("Boards or Logs", 17)]},
         "Magincia-Style Throne": {'btn': 58, 'stack': False, 'mats': [("Boards or Logs", 19)]},
         "Small Table": {'btn': 65, 'stack': False, 'mats': [("Boards or Logs", 17)]},
         "Writing Table": {'btn': 72, 'stack': False, 'mats': [("Boards or Logs", 17)]},
         "Yew-Wood Table": {'btn': 79, 'stack': False, 'mats': [("Boards or Logs", 27)]},
         "Large Table": {'btn': 86, 'stack': False, 'mats': [("Boards or Logs", 23)]},
         "Elegant Low Table": {'btn': 93, 'stack': False, 'mats': [("Boards or Logs", 35)]},
         "Plain Low Table": {'btn': 100, 'stack': False, 'mats': [("Boards or Logs", 35)]},
         "Ornate Table (South)": {'btn': 128, 'stack': False, 'mats': [("Boards or Logs", 60)]},
         "Ornate Table (East)": {'btn': 135, 'stack': False, 'mats': [("Boards or Logs", 60)]},
         "Hardwood Table (South)": {'btn': 142, 'stack': False, 'mats': [("Boards or Logs", 50)]},
         "Hardwood Table (East)": {'btn': 149, 'stack': False, 'mats': [("Boards or Logs", 50)]},
         "Elven Podium": {'btn': 156, 'stack': False, 'mats': [("Boards or Logs", 20)]},
         "Ornate Elven Chair": {'btn': 163, 'stack': False, 'mats': [("Boards or Logs", 30)]},
         "Cozy Elven Chair": {'btn': 170, 'stack': False, 'mats': [("Boards or Logs", 40)]},
         "Reading Chair": {'btn': 177, 'stack': False, 'mats': [("Boards or Logs", 30)]},
         "Ter-Mur Style Chair": {'btn': 184, 'stack': False, 'mats': [("Boards or Logs", 40)]},
         "Ter-Mur Style Table": {'btn': 191, 'stack': False, 'mats': [("Boards or Logs", 50)]},
         "Upholstered Chair": {'btn': 198, 'stack': False, 'mats':
             [("Boards or Logs", 40), ("Cloth", 12)]}
        },
    ('Containers', 15):
        {"Wooden Box": {'btn': 2, 'stack': False, 'mats': [("Boards or Logs", 10)]},
         "Small Crate": {'btn': 9, 'stack': False, 'mats': [("Boards or Logs", 8)]},
         "Medium Crate": {'btn': 16, 'stack': False, 'mats': [("Boards or Logs", 15)]},
         "Large Crate": {'btn': 23, 'stack': False, 'mats': [("Boards or Logs", 18)]},
         "Wooden Chest": {'btn': 30, 'stack': False, 'mats': [("Boards or Logs", 20)]},
         "Wooden Shelf": {'btn': 37, 'stack': False, 'mats': [("Boards or Logs", 25)]},
         "Armoire (Red)": {'btn': 44, 'stack': False, 'mats': [("Boards or Logs", 35)]},
         "Armoire": {'btn': 51, 'stack': False, 'mats': [("Boards or Logs", 35)]},
         "Plain Wooden Chest": {'btn': 58, 'stack': False, 'mats': [("Boards or Logs", 30)]},
         "Ornate Wooden Chest": {'btn': 65, 'stack': False, 'mats': [("Boards or Logs", 30)]},
         "Gilded Wooden Chest": {'btn': 72, 'stack': False, 'mats': [("Boards or Logs", 30)]},
         "Wooden Footlocker": {'btn': 79, 'stack': False, 'mats': [("Boards or Logs", 30)]},
         "Finished Wooden Chest": {'btn': 86, 'stack': False, 'mats': [("Boards or Logs", 30)]},
         "Tall Cabinet": {'btn': 93, 'stack': False, 'mats': [("Boards or Logs", 35)]},
         "Short Cabinet": {'btn': 100, 'stack': False, 'mats': [("Boards or Logs", 35)]},
         "Red Armoire": {'btn': 107, 'stack': False, 'mats': [("Boards or Logs", 40)]},
         "Elegant Armoire": {'btn': 114, 'stack': False, 'mats': [("Boards or Logs", 40)]},
         "Maple Armoire": {'btn': 121, 'stack': False, 'mats': [("Boards or Logs", 40)]},
         "Cherry Armoire": {'btn': 128, 'stack': False, 'mats': [("Boards or Logs", 40)]},
         "Keg": {'btn': 135, 'stack': False, 'mats':
             [("Barrel Staves", 3), ("Barrel Hoops", 1), ("Barrel Lids", 1)]},
         "Arcane Bookshelf (South)": {'btn': 142, 'stack': False, 'mats': [("Boards or Logs", 80)]},
         "Arcane Bookshelf (East)": {'btn': 149, 'stack': False, 'mats': [("Boards or Logs", 80)]},
         "Ornate Elven Chest (South)": {'btn': 156, 'stack': False, 'mats': [("Boards or Logs", 40)]},
         "Ornate Elven Chest (East)": {'btn': 163, 'stack': False, 'mats': [("Boards or Logs", 40)]},
         "Elven Wash Basin (South)": {'btn': 170, 'stack': False, 'mats': [("Boards or Logs", 40)]},
         "Elven Wash Basin (East)": {'btn': 177, 'stack': False, 'mats': [("Boards or Logs", 40)]},
         "Elven Dresser (South)": {'btn': 184, 'stack': False, 'mats': [("Boards or Logs", 45)]},
         "Elven Dresser (East)": {'btn': 191, 'stack': False, 'mats': [("Boards or Logs", 45)]},
         "Elven Armoire (Fancy)": {'btn': 198, 'stack': False, 'mats': [("Boards or Logs", 60)]},
         "Elven Armoire (Simple)": {'btn': 205, 'stack': False, 'mats': [("Boards or Logs", 60)]},
         "Rarewood Chest": {'btn': 212, 'stack': False, 'mats': [("Boards or Logs", 30)]},
         "Decorative Box": {'btn': 219, 'stack': False, 'mats': [("Boards or Logs", 25)]},
         "Academic Bookcase": {'btn': 226, 'stack': False, 'mats':
             [("Boards or Logs", 25), ("academic books", 1)]},
         "Gargish Chest": {'btn': 233, 'stack': False, 'mats': [("Boards or Logs", 30)]},
         "Empty Liquor Barrel": {'btn': 240, 'stack': False, 'mats': [("Boards or Logs", 50)]}
        },
    ('Weapons', 22):
        {"Shepherd'S Crook": {'btn': 2, 'stack': False, 'mats': [("Boards or Logs", 7)]},
         "Quarter Staff": {'btn': 9, 'stack': False, 'mats': [("Boards or Logs", 6)]},
         "Gnarled Staff": {'btn': 16, 'stack': False, 'mats': [("Boards or Logs", 7)]},
         "Bokuto": {'btn': 23, 'stack': False, 'mats': [("Boards or Logs", 6)]},
         "Fukiya": {'btn': 30, 'stack': False, 'mats': [("Boards or Logs", 6)]},
         "Tetsubo": {'btn': 37, 'stack': False, 'mats': [("Boards or Logs", 10)]},
         "Wild Staff": {'btn': 44, 'stack': False, 'mats': [("Boards or Logs", 16)]},
         "Phantom Staff": {'btn': 51, 'stack': False, 'mats':
             [("Boards or Logs", 16), ("Diseased Bark", 1), ("Putrefaction", 10), ("Taint", 10)]},
         "Arcanist'S Wild Staff": {'btn': 58, 'stack': False, 'mats':
             [("Boards or Logs", 16), ("white pearl", 1)]},
         "Ancient Wild Staff": {'btn': 65, 'stack': False, 'mats':
             [("Boards or Logs", 16), ("perfect emerald", 1)]},
         "Thorned Wild Staff": {'btn': 72, 'stack': False, 'mats':
             [("Boards or Logs", 16), ("fire ruby", 1)]},
         "Hardened Wild Staff": {'btn': 79, 'stack': False, 'mats':
             [("Boards or Logs", 16), ("turquoise", 1)]},
         "Serpentstone Staff": {'btn': 86, 'stack': False, 'mats':
             [("Boards or Logs", 16), ("ecru citrine", 1)]},
         "Gargish Gnarled Staff": {'btn': 93, 'stack': False, 'mats':
             [("Boards or Logs", 16), ("ecru citrine", 1)]},
         "Club": {'btn': 100, 'stack': False, 'mats': [("Boards or Logs", 9)]},
         "Black Staff": {'btn': 107, 'stack': False, 'mats': [("Boards or Logs", 9)]},
         "Kotl Black Rod": {'btn': 114, 'stack': False, 'mats':
             [("Boards or Logs", 20), ("Black Moonstone", 1), ("Staff of the Magi", 1)]}
        },
    ('Armor', 29):
        {"Wooden Shield": {'btn': 2, 'stack': False, 'mats': [("Boards or Logs", 9)]},
         "Woodland Chest": {'btn': 9, 'stack': False, 'mats':
             [("Boards or Logs", 20), ("Bark Fragment", 6)]},
         "Woodland Arms": {'btn': 16, 'stack': False, 'mats':
             [("Boards or Logs", 15), ("Bark Fragment", 4)]},
         "Woodland Gauntlets": {'btn': 23, 'stack': False, 'mats':
             [("Boards or Logs", 15), ("Bark Fragment", 4)]},
         "Woodland Leggings": {'btn': 30, 'stack': False, 'mats':
             [("Boards or Logs", 15), ("Bark Fragment", 4)]},
         "Woodland Gorget": {'btn': 37, 'stack': False, 'mats':
             [("Boards or Logs", 15), ("Bark Fragment", 4)]},
         "Raven Helm": {'btn': 44, 'stack': False, 'mats':
             [("Boards or Logs", 10), ("Bark Fragment", 4), ("feathers", 25)]},
         "Vulture Helm": {'btn': 51, 'stack': False, 'mats':
             [("Boards or Logs", 10), ("Bark Fragment", 4), ("feathers", 25)]},
         "Winged Helm": {'btn': 58, 'stack': False, 'mats':
             [("Boards or Logs", 10), ("Bark Fragment", 4), ("feathers", 60)]},
         "Ironwood Crown": {'btn': 65, 'stack': False, 'mats':
             [("Boards or Logs", 10), ("Diseased Bark", 1), ("Corruption", 10), ("Putrefaction", 10)]},
         "Bramble Coat": {'btn': 72, 'stack': False, 'mats':
             [("Boards or Logs", 10), ("Diseased Bark", 1), ("Taint", 10), ("Scourge", 10)]},
         "Darkwood Crown": {'btn': 79, 'stack': False, 'mats':
             [("Boards or Logs", 10), ("Lard of Paroxysmus", 1), ("Blight", 10), ("Taint", 10)]},
         "Darkwood Chest": {'btn': 86, 'stack': False, 'mats':
             [("Boards or Logs", 20), ("Dread Horn Mane", 1), ("Corruption", 10), ("Muculent", 10)]},
         "Darkwood Gorget": {'btn': 93, 'stack': False, 'mats':
             [("Boards or Logs", 15), ("Diseased Bark", 1), ("Blight", 10), ("Scourge", 10)]},
         "Darkwood Leggings": {'btn': 100, 'stack': False, 'mats':
             [("Boards or Logs", 15), ("Grizzled Bones", 1), ("Corruption", 10), ("Putrefaction", 10)]},
         "Darkwood Pauldrons": {'btn': 107, 'stack': False, 'mats':
             [("Boards or Logs", 15), ("Eye of the Travesty", 1), ("Scourge", 10), ("Taint", 10)]},
         "Darkwood Gauntlets": {'btn': 114, 'stack': False, 'mats':
             [("Boards or Logs", 15), ("Captured Essence", 1), ("Putrefaction", 10), ("Muculent", 10)]},
         "Gargish Wooden Shield": {'btn': 121, 'stack': False, 'mats': [("Boards or Logs", 9)]},
         "Pirate Shield": {'btn': 128, 'stack': False, 'mats':
             [("Boards or Logs", 12), ("Ingots", 8)]}
        },
    ('Instruments', 36):
        {"Lap Harp": {'btn': 2, 'stack': False, 'mats':
             [("Boards or Logs", 20), ("Cloth", 10)]},
         "Standing Harp": {'btn': 9, 'stack': False, 'mats':
             [("Boards or Logs", 35), ("Cloth", 15)]},
         "Drum": {'btn': 16, 'stack': False, 'mats':
             [("Boards or Logs", 20), ("Cloth", 10)]},
         "Lute": {'btn': 23, 'stack': False, 'mats':
             [("Boards or Logs", 25), ("Cloth", 10)]},
         "Tambourine": {'btn': 30, 'stack': False, 'mats':
             [("Boards or Logs", 15), ("Cloth", 10)]},
         "Tambourine (Tassel)": {'btn': 37, 'stack': False, 'mats':
             [("Boards or Logs", 15), ("Cloth", 15)]},
         "Bamboo Flute": {'btn': 44, 'stack': False, 'mats': [("Boards or Logs", 15)]},
         "Aud-Char": {'btn': 51, 'stack': False, 'mats':
             [("Boards or Logs", 35), ("Stones", 3)]},
         "Snake Charmer Flute": {'btn': 58, 'stack': False, 'mats':
             [("Boards or Logs", 15), ("luminescent fungi", 3)]},
         "Cello": {'btn': 65, 'stack': False, 'mats':
             [("Boards or Logs", 15), ("Cloth", 5)]},
         "Wall Mounted Bell (South)": {'btn': 72, 'stack': False, 'mats':
             [("Boards or Logs", 50), ("Ingots", 50)]},
         "Wall Mounted Bell (East)": {'btn': 79, 'stack': False, 'mats':
             [("Boards or Logs", 50), ("Ingots", 50)]},
         "Trumpet": {'btn': 86, 'stack': False, 'mats':
             [("Boards or Logs", 10), ("Ingots", 15)]},
         "Cowbell": {'btn': 93, 'stack': False, 'mats':
             [("Boards or Logs", 10), ("Ingots", 15)]}
        },
    ('Misc. Add-Ons', 43):
        {"Bulletin Board": {'btn': 2, 'stack': False, 'mats': [("Boards or Logs", 50)]},
         "Bulletin Board 2": {'btn': 9, 'stack': False, 'mats': [("Boards or Logs", 50)]},
         "Parrot Perch": {'btn': 16, 'stack': False, 'mats': [("Boards or Logs", 100)]},
         "Arcane Circle": {'btn': 23, 'stack': False, 'mats':
             [("Boards or Logs", 100), ("blue diamond", 2), ("perfect emerald", 2), ("fire ruby", 2)]},
         "Tall Elven Bed (South)": {'btn': 30, 'stack': False, 'mats':
             [("Boards or Logs", 200), ("Cloth", 100)]},
         "Tall Elven Bed (East)": {'btn': 37, 'stack': False, 'mats':
             [("Boards or Logs", 200), ("Cloth", 100)]},
         "Elven Bed (South)": {'btn': 44, 'stack': False, 'mats':
             [("Boards or Logs", 100), ("Cloth", 100)]},
         "Elven Bed (East)": {'btn': 51, 'stack': False, 'mats':
             [("Boards or Logs", 100), ("Cloth", 100)]},
         "Elven Loveseat (East)": {'btn': 58, 'stack': False, 'mats': [("Boards or Logs", 50)]},
         "Elven Loveseat (South)": {'btn': 65, 'stack': False, 'mats': [("Boards or Logs", 50)]},
         "Alchemist Table (South)": {'btn': 72, 'stack': False, 'mats': [("Boards or Logs", 70)]},
         "Alchemist Table (East)": {'btn': 79, 'stack': False, 'mats': [("Boards or Logs", 70)]},
         "Small Bed (South)": {'btn': 86, 'stack': False, 'mats':
             [("Boards or Logs", 100), ("Cloth", 100)]},
         "Small Bed (East)": {'btn': 93, 'stack': False, 'mats':
             [("Boards or Logs", 100), ("Cloth", 100)]},
         "Large Bed (South)": {'btn': 100, 'stack': False, 'mats':
             [("Boards or Logs", 150), ("Cloth", 150)]},
         "Large Bed (East)": {'btn': 107, 'stack': False, 'mats':
             [("Boards or Logs", 150), ("Cloth", 150)]},
         "Dartboard (South)": {'btn': 114, 'stack': False, 'mats': [("Boards or Logs", 5)]},
         "Dartboard (East)": {'btn': 121, 'stack': False, 'mats': [("Boards or Logs", 5)]},
         "Ballot Box": {'btn': 128, 'stack': False, 'mats': [("Boards or Logs", 5)]},
         "Pentagram": {'btn': 135, 'stack': False, 'mats':
             [("Boards or Logs", 100), ("Ingots", 40)]},
         "Abbatoir": {'btn': 142, 'stack': False, 'mats':
             [("Boards or Logs", 100), ("Ingots", 40)]},
         "Gargish Couch (East)": {'btn': 149, 'stack': False, 'mats': [("Boards or Logs", 75)]},
         "Gargish Couch (South)": {'btn': 156, 'stack': False, 'mats': [("Boards or Logs", 75)]},
         "Long Table (South)": {'btn': 163, 'stack': False, 'mats': [("Boards or Logs", 80)]},
         "Long Table (East)": {'btn': 170, 'stack': False, 'mats': [("Boards or Logs", 80)]},
         "Ter-Mur Style Dresser (East)": {'btn': 177, 'stack': False, 'mats': [("Boards or Logs", 60)]},
         "Ter-Mur Style Dresser (South)": {'btn': 184, 'stack': False, 'mats': [("Boards or Logs", 60)]},
         "Rustic Bench (South)": {'btn': 191, 'stack': False, 'mats': [("Boards or Logs", 35)]},
         "Rustic Bench (East)": {'btn': 198, 'stack': False, 'mats': [("Boards or Logs", 35)]},
         "Plain Wooden Shelf (South)": {'btn': 205, 'stack': False, 'mats': [("Boards or Logs", 15)]},
         "Plain Wooden Shelf (East)": {'btn': 212, 'stack': False, 'mats': [("Boards or Logs", 15)]},
         "Fancy Wooden Shelf (South)": {'btn': 219, 'stack': False, 'mats': [("Boards or Logs", 15)]},
         "Fancy Wooden Shelf (East)": {'btn': 226, 'stack': False, 'mats': [("Boards or Logs", 15)]},
         "Fancy Loveseat (South)": {'btn': 233, 'stack': False, 'mats':
             [("Boards or Logs", 80), ("Cloth", 24)]},
         "Fancy Loveseat (East)": {'btn': 240, 'stack': False, 'mats':
             [("Boards or Logs", 80), ("Cloth", 24)]},
         "Plush Loveseat (South)": {'btn': 247, 'stack': False, 'mats':
             [("Boards or Logs", 80), ("Cloth", 24)]},
         "Plush Loveseat (East)": {'btn': 254, 'stack': False, 'mats':
             [("Boards or Logs", 80), ("Cloth", 24)]},
         "Plant Tapestry (South)": {'btn': 261, 'stack': False, 'mats':
             [("Boards or Logs", 12), ("Cloth", 50)]},
         "Plant Tapestry (East)": {'btn': 268, 'stack': False, 'mats':
             [("Boards or Logs", 12), ("Cloth", 50)]},
         "Metal Table (South)": {'btn': 275, 'stack': False, 'mats':
             [("Boards or Logs", 20), ("Ingots", 15)]},
         "Metal Table (East)": {'btn': 282, 'stack': False, 'mats':
             [("Boards or Logs", 20), ("Ingots", 15)]},
         "Long Metal Table (South)": {'btn': 289, 'stack': False, 'mats':
             [("Boards or Logs", 40), ("Ingots", 30)]},
         "Long Metal Table (East)": {'btn': 296, 'stack': False, 'mats':
             [("Boards or Logs", 40), ("Ingots", 30)]},
         "Wooden Table (South)": {'btn': 303, 'stack': False, 'mats': [("Boards or Logs", 20)]},
         "Wooden Table (East)": {'btn': 310, 'stack': False, 'mats': [("Boards or Logs", 20)]},
         "Long Wooden Table (South)": {'btn': 317, 'stack': False, 'mats': [("Boards or Logs", 80)]},
         "Long Wooden Table (East)": {'btn': 324, 'stack': False, 'mats': [("Boards or Logs", 80)]},
         "Small Display Case (South)": {'btn': 331, 'stack': False, 'mats':
             [("Boards or Logs", 40), ("Ingots", 10)]},
         "Small Display Case (East)": {'btn': 338, 'stack': False, 'mats':
             [("Boards or Logs", 40), ("Ingots", 10)]},
         "Fancy Loveseat (North)": {'btn': 345, 'stack': False, 'mats':
             [("Boards or Logs", 80), ("Cloth", 48)]},
         "Fancy Loveseat (West)": {'btn': 352, 'stack': False, 'mats':
             [("Boards or Logs", 80), ("Cloth", 48)]},
         "Fancy Couch (North)": {'btn': 373, 'stack': False, 'mats':
             [("Boards or Logs", 80), ("Cloth", 48)]},
         "Fancy Couch (West)": {'btn': 380, 'stack': False, 'mats':
             [("Boards or Logs", 80), ("Cloth", 48)]},
         "Fancy Couch (South)": {'btn': 387, 'stack': False, 'mats':
             [("Boards or Logs", 80), ("Cloth", 48)]},
         "Fancy Couch (East)": {'btn': 394, 'stack': False, 'mats':
             [("Boards or Logs", 80), ("Cloth", 48)]},
         "Small Elegant Aquarium": {'btn': 401, 'stack': False, 'mats':
             [("Boards or Logs", 20), ("workable glass", 2), ("Sand", 5), ("Live Rock", 1)]},
         "Wall Mounted Aquarium": {'btn': 408, 'stack': False, 'mats':
             [("Boards or Logs", 50), ("workable glass", 4), ("Sand", 10), ("Live Rock", 3)]},
         "Large Elegant Aquarium": {'btn': 415, 'stack': False, 'mats':
             [("Boards or Logs", 100), ("workable glass", 8), ("Sand", 20), ("Live Rock", 5)]}
        },
    ('Tailoring And Cooking', 50):
        {"Dressform (Front)": {'btn': 2, 'stack': False, 'mats':
            [("Boards or Logs", 25), ("Cloth", 10)]},
         "Dressform (Side)": {'btn': 9, 'stack': False, 'mats':
             [("Boards or Logs", 25), ("Cloth", 10)]},
         "Elven Spinning Wheel (East)": {'btn': 16, 'stack': False, 'mats':
             [("Boards or Logs", 60), ("Cloth", 40)]},
         "Elven Spinning Wheel (South)": {'btn': 23, 'stack': False, 'mats':
             [("Boards or Logs", 60), ("Cloth", 40)]},
         "Elven Oven (South)": {'btn': 30, 'stack': False, 'mats': [("Boards or Logs", 80)]},
         "Elven Oven (East)": {'btn': 37, 'stack': False, 'mats': [("Boards or Logs", 80)]},
         "Spinning Wheel (East)": {'btn': 44, 'stack': False, 'mats':
             [("Boards or Logs", 75), ("Cloth", 25)]},
         "Spinning Wheel (South)": {'btn': 51, 'stack': False, 'mats':
             [("Boards or Logs", 75), ("Cloth", 25)]},
         "Loom (East)": {'btn': 58, 'stack': False, 'mats':
             [("Boards or Logs", 85), ("Cloth", 25)]},
         "Loom (South)": {'btn': 65, 'stack': False, 'mats':
             [("Boards or Logs", 85), ("Cloth", 25)]},
         "Stone Oven (East)": {'btn': 72, 'stack': False, 'mats':
             [("Boards or Logs", 85), ("Ingots", 125)]},
         "Stone Oven (South)": {'btn': 79, 'stack': False, 'mats':
             [("Boards or Logs", 85), ("Ingots", 125)]},
         "Flour Mill (East)": {'btn': 86, 'stack': False, 'mats':
             [("Boards or Logs", 100), ("Ingots", 50)]},
         "Flour Mill (South)": {'btn': 93, 'stack': False, 'mats':
             [("Boards or Logs", 100), ("Ingots", 50)]},
         "Water Trough (East)": {'btn': 100, 'stack': False, 'mats': [("Boards or Logs", 150)]},
         "Water Trough (South)": {'btn': 107, 'stack': False, 'mats': [("Boards or Logs", 150)]}
        },
    ('Anvils And Forges', 57):
        {"Elven Forge": {'btn': 2, 'stack': False, 'mats': [("Boards or Logs", 200)]},
         "Soulforge": {'btn': 9, 'stack': False, 'mats':
             [("Boards or Logs", 150), ("Ingots", 150), ("Relic Fragment", 1)]},
         "Small Forge": {'btn': 16, 'stack': False, 'mats':
             [("Boards or Logs", 5), ("Ingots", 75)]},
         "Large Forge (East)": {'btn': 23, 'stack': False, 'mats':
             [("Boards or Logs", 5), ("Ingots", 100)]},
         "Large Forge (South)": {'btn': 30, 'stack': False, 'mats':
             [("Boards or Logs", 5), ("Ingots", 100)]},
         "Anvil (East)": {'btn': 37, 'stack': False, 'mats':
             [("Boards or Logs", 5), ("Ingots", 150)]},
         "Anvil (South)": {'btn': 44, 'stack': False, 'mats':
             [("Boards or Logs", 5), ("Ingots", 150)]}
        },
    ('Training', 64):
        {"Training Dummy (East)": {'btn': 2, 'stack': False, 'mats':
            [("Boards or Logs", 55), ("Cloth", 60)]},
         "Training Dummy (South)": {'btn': 9, 'stack': False, 'mats':
             [("Boards or Logs", 55), ("Cloth", 60)]},
         "Pickpocket Dip (East)": {'btn': 16, 'stack': False, 'mats':
             [("Boards or Logs", 65), ("Cloth", 60)]},
         "Pickpocket Dip (South)": {'btn': 23, 'stack': False, 'mats':
             [("Boards or Logs", 65), ("Cloth", 60)]}
        }
    }

cartography_gump = {
    'categories': [
        ('Exit', 0), 
        ('Cancel Make', 84), 
        ('Non Quest Item', 77), 
        ('Make Last', 21), 
        ('Last Ten', 28), 
        ('Maps', 1)
    ],
    ('Maps', 1):
        {"Local Map": {'btn': 2, 'stack': False, 'mats': [("Blank Maps or Scrolls", 1)]},
         "City Map": {'btn': 9, 'stack': False, 'mats': [("Blank Maps or Scrolls", 1)]},
         "Sea Chart": {'btn': 16, 'stack': False, 'mats': [("Blank Maps or Scrolls", 1)]},
         "World Map": {'btn': 23, 'stack': False, 'mats': [("Blank Maps or Scrolls", 1)]},
         "Tattered Wall Map (South)": {'btn': 30, 'stack': False, 'mats':
             [("Level 1 Treasure Maps", 10), ("Level 3 Treasure Maps", 5), 
             ("Level 4 Treasure Maps", 3), ("Level 5 Treasure Maps", 1)]},
         "Tattered Wall Map (East)": {'btn': 37, 'stack': False, 'mats':
             [("Level 1 Treasure Maps", 10), ("Level 3 Treasure Maps", 5), 
             ("Level 4 Treasure Maps", 3), ("Level 5 Treasure Maps", 1)]},
         "Wall Map Of Eodon": {'btn': 44, 'stack': False, 'mats':
             [("Blank Maps or Scrolls", 50), ("Unabridged Atlas of Eodon", 1)]},
         "Star Chart": {'btn': 51, 'stack': False, 'mats': [("Blank Maps or Scrolls", 1)]}
        }
    }

cooking_gump = {
    'categories': [
        ('Exit', 0), 
        ('Cancel Make', 84), 
        ('Mark Item', 49), 
        ('Non Quest Item', 77), 
        ('Make Last', 21), 
        ('Last Ten', 28), 
        ('Ingredients', 1), 
        ('Preparations', 8), 
        ('Baking', 15), 
        ('Barbecue', 22), 
        ('Enchanted', 29), 
        ('Chocolatiering', 36), 
        ('Magical Fish Pies', 43), 
        ('Beverages', 50)
    ],
    ('Ingredients', 1):
        {"Sack Of Flour": {'btn': 2, 'stack': False, 'mats': [("Wheat", 2)]},
         "Dough": {'btn': 9, 'stack': False, 'mats':
             [("Flour", 1), ("Water", 1)]},
         "Sweet Dough": {'btn': 16, 'stack': False, 'mats':
             [("Dough", 1), ("Honey", 1)]},
         "Cake Mix": {'btn': 23, 'stack': False, 'mats':
             [("Flour", 1), ("Sweet Dough", 1)]},
         "Cookie Mix": {'btn': 30, 'stack': False, 'mats':
             [("Honey", 1), ("Sweet Dough", 1)]},
         "Cocoa Butter": {'btn': 37, 'stack': False, 'mats': [("cocoa pulp", 1)]},
         "Cocoa Liquor": {'btn': 44, 'stack': False, 'mats':
             [("cocoa pulp", 1), ("pewter bowl", 1)]},
         "Wheat Wort": {'btn': 51, 'stack': False, 'mats':
             [("empty bottle", 1), ("Water", 1), ("Flour", 1)]},
         "Fish Oil Flask": {'btn': 58, 'stack': True, 'mats':
             [("Coffee Grounds", 1), ("Raw Fish Steaks", 8)]},
         "Fresh Seasoning": {'btn': 65, 'stack': False, 'mats': [("salt", 4)]}
        },
    ('Preparations', 8):
        {"Unbaked Quiche": {'btn': 2, 'stack': False, 'mats':
             [("Dough", 1), ("Eggs", 1)]},
         "Unbaked Meat Pie": {'btn': 9, 'stack': False, 'mats':
             [("Dough", 1), ("Raw Meat", 1)]},
         "Uncooked Sausage Pizza": {'btn': 16, 'stack': False, 'mats':
             [("Dough", 1), ("Sausage", 1)]},
         "Uncooked Cheese Pizza": {'btn': 23, 'stack': False, 'mats':
             [("Dough", 1), ("Cheese", 1)]},
         "Unbaked Fruit Pie": {'btn': 30, 'stack': False, 'mats':
             [("Dough", 1), ("Pears", 1)]},
         "Unbaked Peach Cobbler": {'btn': 37, 'stack': False, 'mats':
             [("Dough", 1), ("Peaches", 1)]},
         "Unbaked Apple Pie": {'btn': 44, 'stack': False, 'mats':
             [("Dough", 1), ("Apples", 1)]},
         "Unbaked Pumpkin Pie": {'btn': 51, 'stack': False, 'mats':
             [("Dough", 1), ("Pumpkin", 1)]},
         "Green Tea": {'btn': 58, 'stack': False, 'mats':
             [("Green Tea", 1), ("Water", 1)]},
         "Wasabi Clumps": {'btn': 65, 'stack': False, 'mats':
             [("Water", 1), ("bowl of peas", 3)]},
         "Sushi Rolls": {'btn': 72, 'stack': False, 'mats':
             [("Water", 1), ("Raw Fish Steaks", 10)]},
         "Sushi Platter": {'btn': 79, 'stack': False, 'mats':
             [("Water", 1), ("Raw Fish Steaks", 10)]},
         "Savage Kin Paint": {'btn': 86, 'stack': False, 'mats':
             [("Flour", 1), ("Tribal Berries", 1)]},
         "Egg Bomb": {'btn': 93, 'stack': False, 'mats':
             [("Eggs", 1), ("Flour", 3)]},
         "Parrot Wafer": {'btn': 100, 'stack': False, 'mats':
             [("Dough", 1), ("Honey", 1), ("Raw Fish Steaks", 10)]},
         "Plant Pigment": {'btn': 107, 'stack': False, 'mats':
             [("Plant Clippings", 1), ("empty bottle", 1)]},
         "Natural Dye": {'btn': 114, 'stack': False, 'mats':
             [("plant pigment", 1), ("color fixative", 1)]},
         "Color Fixative": {'btn': 121, 'stack': False, 'mats':
             [("bottle of wine", 1), ("silver serpent venom", 1)]},
         "Wood Pulp": {'btn': 128, 'stack': False, 'mats':
             [("Bark Fragment", 1), ("Water", 1)]},
         "Charcoal": {'btn': 135, 'stack': True, 'mats':
             [("Boards or Logs", 1)]},
         "Charybdis Bait": {'btn': 142, 'stack': False, 'mats':
             [("Samuel's Secret Sauce", 1), ("Raw Fish Steaks", 50),
             ("salted serpent steak", 3)]}
        },
    ('Baking', 15):
        {"Bread Loaf": {'btn': 2, 'stack': False, 'mats': [("Dough", 1)]},
         "Pan Of Cookies": {'btn': 9, 'stack': False, 'mats': [("Cookie Mix", 1)]},
         "Cake": {'btn': 16, 'stack': False, 'mats': [("Cake Mix", 1)]},
         "Muffins": {'btn': 23, 'stack': False, 'mats': [("Sweet Dough", 1)]},
         "Baked Quiche": {'btn': 30, 'stack': False, 'mats': [("Uncooked Quiches", 1)]},
         "Baked Meat Pie": {'btn': 37, 'stack': False, 'mats': [("Uncooked Meat Pies", 1)]},
         "Sausage Pizza": {'btn': 44, 'stack': False, 'mats': [("Uncooked Sausage Pizzas", 1)]},
         "Cheese Pizza": {'btn': 51, 'stack': False, 'mats': [("Uncooked Cheese Pizzas", 1)]},
         "Baked Fruit Pie": {'btn': 58, 'stack': False, 'mats': [("Uncooked Fruit Pies", 1)]},
         "Baked Peach Cobbler": {'btn': 65, 'stack': False, 'mats': [("Uncooked Peach Cobblers", 1)]},
         "Baked Apple Pie": {'btn': 72, 'stack': False, 'mats': [("Uncooked Apple Pies", 1)]},
         "Baked Pumpkin Pie": {'btn': 79, 'stack': False, 'mats': [("Unbaked Pumpkin Pies", 1)]},
         "Miso Soup": {'btn': 86, 'stack': False, 'mats':
             [("Raw Fish Steaks", 1), ("Water", 1)]},
         "White Miso Soup": {'btn': 93, 'stack': False, 'mats':
             [("Raw Fish Steaks", 1), ("Water", 1)]},
         "Red Miso Soup": {'btn': 100, 'stack': False, 'mats':
             [("Raw Fish Steaks", 1), ("Water", 1)]},
         "Awase Miso Soup": {'btn': 107, 'stack': False, 'mats':
             [("Raw Fish Steaks", 1), ("Water", 1)]},
         "Gingerbread Cookie": {'btn': 114, 'stack': False, 'mats':
             [("Cookie Mix", 1), ("Fresh Ginger", 1)]},
         "Three Tiered Cake": {'btn': 121, 'stack': False, 'mats': [("Cake Mix", 3)]}
        },
    ('Barbecue', 22):
        {"Cooked Bird": {'btn': 2, 'stack': True, 'mats': [("Raw Birds", 1)]},
         "Chicken Leg": {'btn': 9, 'stack': True, 'mats': [("Raw Chicken Legs", 1)]},
         "Fish Steak": {'btn': 16, 'stack': True, 'mats': [("Raw Fish Steaks", 1)]},
         "Fried Eggs": {'btn': 23, 'stack': True, 'mats': [("Eggs", 1)]},
         "Leg Of Lamb": {'btn': 30, 'stack': True, 'mats': [("Raw Legs of Lamb", 1)]},
         "Cut Of Ribs": {'btn': 37, 'stack': True, 'mats': [("Raw Ribs", 1)]},
         "Bowl Of Rotworm Stew": {'btn': 44, 'stack': True, 'mats': [("raw rotworm meat", 1)]},
         "Blackrock Stew": {'btn': 51, 'stack': False, 'mats':
             [("bowl of rotworm stew", 1), ("a piece of blackrock", 1)]},
         "Khaldun Tasty Treat": {'btn': 58, 'stack': True, 'mats': [("Raw Fish Steaks", 40)]},
         "Hamburger": {'btn': 65, 'stack': False, 'mats':
             [("bread loaf", 1), ("Raw Ribs", 1), 
             ("head of lettuce", 1)]},
         "Hot Dog": {'btn': 72, 'stack': False, 'mats':
             [("bread loaf", 1), ("sausage", 1)]},
         "Sausage": {'btn': 79, 'stack': False, 'mats':
             [("ham", 1), ("dried herbs", 1)]},
         "Grilled Serpent Steak": {'btn': 86, 'stack': True, 'mats':
             [("raw serpent steak", 1), ("fresh seasoning", 1)]},
         "Bbq Dino Ribs": {'btn': 93, 'stack': True, 'mats':
             [("raw dino ribs", 1), ("fresh seasoning", 1), 
             ("sack of sugar", 1), ("Samuel's Secret Sauce", 1)]},
         "Waku Chicken": {'btn': 100, 'stack': True, 'mats':
             [("Raw Birds", 1), ("dried herbs", 1), 
             ("Samuel's Secret Sauce", 1)]}
        },
    ('Enchanted', 29):
        {"Food Decoration Tool": {'btn': 2, 'stack': False, 'mats':
             [("Dough", 1), ("Honey", 1)]},
         "Enchanted Apple": {'btn': 9, 'stack': False, 'mats':
             [("Apples", 1), ("Greater Heal Potion", 1)]},
         "Grapes Of Wrath": {'btn': 16, 'stack': False, 'mats':
             [("Grapes", 1), ("Greater Strength Potion", 1)]},
         "Fruit Bowl": {'btn': 23, 'stack': False, 'mats':
             [("Wooden Bowl", 1), ("Pears", 3), 
             ("Apples", 3), ("Bananas", 3)]}
        },
    ('Chocolatiering', 36):
        {"Sweet Cocoa Butter": {'btn': 2, 'stack': False, 'mats':
             [("sack of sugar", 1), ("cocoa butter", 1)]},
         "Dark Chocolate": {'btn': 9, 'stack': False, 'mats':
             [("sack of sugar", 1), ("cocoa butter", 1), 
             ("cocoa liquor", 1)]},
         "Milk Chocolate": {'btn': 16, 'stack': False, 'mats':
             [("sack of sugar", 1), ("cocoa butter", 1), 
             ("cocoa liquor", 1), ("milk", 1)]},
         "White Chocolate": {'btn': 23, 'stack': False, 'mats':
             [("sack of sugar", 1), ("cocoa butter", 1), 
             ("vanilla", 1), ("milk", 1)]},
         "Dark Chocolate Nutcracker": {'btn': 30, 'stack': False, 'mats':
             [("sweet cocoa butter", 1), ("foil sheet", 1), 
             ("cocoa liquor", 1)]},
         "Milk Chocolate Nutcracker": {'btn': 37, 'stack': False, 'mats':
             [("sweet cocoa butter", 1), ("foil sheet", 1), 
             ("cocoa liquor", 1)]},
         "White Chocolate Nutcracker": {'btn': 44, 'stack': False, 'mats':
             [("sweet cocoa butter", 1), ("foil sheet", 1), 
             ("cocoa liquor", 1)]}
        },
    ('Magical Fish Pies', 43):
        {"Great Barracuda Pie": {'btn': 2, 'stack': False, 'mats':
             [("great barracuda steak", 1), ("Mento Seasoning", 1), 
             ("zoogi fungus", 1)]},
         "Giant Koi Pie": {'btn': 9, 'stack': False, 'mats':
             [("Giant Koi Steak.", 1), ("Mento Seasoning", 1), 
             ("bowl of peas", 1), ("dough", 1)]},
         "Fire Fish Pie": {'btn': 16, 'stack': False, 'mats':
             [("fire fish steak", 1), ("dough", 1), 
             ("carrot", 1), ("Samuel's Secret Sauce", 1)]},
         "Stone Crab Pie": {'btn': 23, 'stack': False, 'mats':
             [("stone crab meat", 1), ("dough", 1), 
             ("head of cabbage", 1), ("Samuel's Secret Sauce", 1)]},
         "Blue Lobster Pie": {'btn': 30, 'stack': False, 'mats':
             [("blue lobster meat", 1), ("dough", 1), 
             ("tribal berry", 1), ("Samuel's Secret Sauce", 1)]},
         "Reaper Fish Pie": {'btn': 37, 'stack': False, 'mats':
             [("reaper fish steak", 1), ("dough", 1), 
             ("pumpkin", 1), ("Samuel's Secret Sauce", 1)]},
         "Crystal Fish Pie": {'btn': 44, 'stack': False, 'mats':
             [("crystal fish steak", 1), ("dough", 1), 
             ("apple", 1), ("Samuel's Secret Sauce", 1)]},
         "Bull Fish Pie": {'btn': 52, 'stack': False, 'mats':
             [("bull fish steak", 1), ("dough", 1), 
             ("squash", 1), ("Mento Seasoning", 1)]},
         "Summer Dragonfish Pie": {'btn': 58, 'stack': False, 'mats':
             [("summer dragonfish steak", 1), ("dough", 1), 
             ("onion", 1), ("Mento Seasoning", 1)]},
         "Fairy Salmon Pie": {'btn': 65, 'stack': False, 'mats':
             [("fairy salmon steak", 1), ("dough", 1), 
             ("ear of corn", 1), ("dark truffle", 1)]},
         "Lava Fish Pie": {'btn': 72, 'stack': False, 'mats':
             [("lava fish steak", 1), ("dough", 1), 
             ("Cheese", 1), ("dark truffle", 1)]},
         "Autumn Dragonfish Pie": {'btn': 79, 'stack': False, 'mats':
             [("autumn dragonfish steak", 1), ("dough", 1), 
             ("pear", 1), ("Mento Seasoning", 1)]},
         "Spider Crab Pie": {'btn': 86, 'stack': False, 'mats':
             [("spider crab meat", 1), ("dough", 1), 
             ("head of lettuce", 1), ("Mento Seasoning", 1)]},
         "Yellowtail Barracuda": {'btn': 93, 'stack': False, 'mats':
             [("yellowtail barracuda steak", 1), ("dough", 1), 
             ("bottle of wine", 1), ("Mento Seasoning", 1)]},
         "Holy Mackerel Pie": {'btn': 100, 'stack': False, 'mats':
             [("holy mackerel steak", 1), ("dough", 1), 
             ("jar of honey", 1), ("Mento Seasoning", 1)]},
         "Unicorn Fish Pie": {'btn': 107, 'stack': False, 'mats':
             [("unicorn fish steak", 1), ("dough", 1), 
             ("Fresh Ginger", 1), ("Mento Seasoning", 1)]}},
    ('Beverages', 50):
        {"Coffee": {'btn': 2, 'stack': False, 'mats':
             [("Coffee Grounds", 1), ("Water", 1)]},
         "Green Tea": {'btn': 9, 'stack': False, 'mats':
             [("Basket of Green Tea", 1), ("Water", 1)]},
         "Hot Cocoa": {'btn': 16, 'stack': False, 'mats':
             [("Cocoa liquor", 1), ("Sack of sugar", 1), 
             ("Pitcher of Milk", 1)]}
        }
    }

inscription_gump = {
    'categories':
        [('Exit', 0), 
        ('Cancel Make', 84), 
        ('Mark Item', 49), 
        ('Non Quest Item', 77), 
        ('Make Last', 21), 
        ('Last Ten', 28), 
        ('First - Second Circle', 1), 
        ('Third - Fourth Circle', 8), 
        ('Fifth - Sixth Circle', 15), 
        ('Seventh - Eighth Circle', 22), 
        ('Spells Of Necromancy', 29), 
        ('Other', 36), 
        ('Spells Of Mysticism', 43)
    ],
    ('First - Second Circle', 1):
        {"Reactive Armor": {'btn': 2, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Garlic", 1), 
             ("Spiders' Silk", 1), ("Sulfurous Ash", 1)]},
         "Clumsy": {'btn': 9, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Blood Moss", 1), 
             ("Nightshade", 1)]},
         "Create Food": {'btn': 16, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Garlic", 1), 
             ("Ginseng", 1), ("Mandrake Root", 1)]},
         "Feeblemind": {'btn': 23, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Nightshade", 1), 
             ("Ginseng", 1)]},
         "Heal": {'btn': 30, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Garlic", 1), 
             ("Ginseng", 1), ("Spiders' Silk", 1)]},
         "Magic Arrow": {'btn': 37, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Sulfurous Ash", 1)]},
         "Night Sight": {'btn': 44, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Spiders' Silk", 1), 
             ("Sulfurous Ash", 1)]},
         "Weaken": {'btn': 51, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Garlic", 1), 
             ("Nightshade", 1)]},
         "Agility": {'btn': 58, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Blood Moss", 1), 
             ("Mandrake Root", 1)]},
         "Cunning": {'btn': 65, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Nightshade", 1), 
             ("Mandrake Root", 1)]},
         "Cure": {'btn': 72, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Garlic", 1), 
             ("Ginseng", 1)]},
         "Harm": {'btn': 79, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Nightshade", 1), 
             ("Spiders' Silk", 1)]},
         "Magic Trap": {'btn': 86, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Garlic", 1), 
             ("Spiders' Silk", 1), ("Sulfurous Ash", 1)]},
         "Magic Untrap": {'btn': 93, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Blood Moss", 1), 
             ("Sulfurous Ash", 1)]},
         "Protection": {'btn': 100, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Garlic", 1), 
             ("Ginseng", 1), ("Sulfurous Ash", 1)]},
         "Strength": {'btn': 107, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Nightshade", 1), 
             ("Mandrake Root", 1)]}
        },
    ('Third - Fourth Circle', 8):
        {"Bless": {'btn': 2, 'stack': False, 'mats':
            [("Blank Scroll", 1), ("Garlic", 1), 
            ("Mandrake Root", 1)]},
         "Fireball": {'btn': 9, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Black Pearl", 1)]},
         "Magic Lock": {'btn': 16, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Blood Moss", 1), 
             ("Garlic", 1), ("Sulfurous Ash", 1)]},
         "Poison": {'btn': 23, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Nightshade", 1)]},
         "Telekinesis": {'btn': 30, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Blood Moss", 1), 
             ("Mandrake Root", 1)]},
         "Teleport": {'btn': 37, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Blood Moss", 1), 
             ("Mandrake Root", 1)]},
         "Unlock": {'btn': 44, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Blood Moss", 1), 
             ("Sulfurous Ash", 1)]},
         "Wall Of Stone": {'btn': 51, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Blood Moss", 1), 
             ("Garlic", 1)]},
         "Arch Cure": {'btn': 58, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Garlic", 1), 
             ("Ginseng", 1), ("Mandrake Root", 1)]},
         "Arch Protection": {'btn': 65, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Garlic", 1), 
             ("Ginseng", 1), ("Mandrake Root", 1), 
             ("Sulfurous Ash", 1)]},
         "Curse": {'btn': 72, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Garlic", 1), 
             ("Nightshade", 1), ("Sulfurous Ash", 1)]},
         "Fire Field": {'btn': 79, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Black Pearl", 1), 
             ("Spiders' Silk", 1), ("Sulfurous Ash", 1)]},
         "Greater Heal": {'btn': 86, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Garlic", 1), 
             ("Spiders' Silk", 1), ("Mandrake Root", 1), 
             ("Ginseng", 1)]},
         "Lightning": {'btn': 93, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Mandrake Root", 1), 
             ("Sulfurous Ash", 1)]},
         "Mana Drain": {'btn': 100, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Black Pearl", 1), 
             ("Spiders' Silk", 1), ("Mandrake Root", 1)]},
         "Recall": {'btn': 107, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Black Pearl", 1), 
             ("Blood Moss", 1), ("Mandrake Root", 1)]}
        },
    ('Fifth - Sixth Circle', 15):
        {"Blade Spirits": {'btn': 2, 'stack': False, 'mats':
            [("Blank Scroll", 1), ("Black Pearl", 1), 
            ("Nightshade", 1), ("Mandrake Root", 1)]},
         "Dispel Field": {'btn': 9, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Black Pearl", 1), 
             ("Garlic", 1), ("Spiders' Silk", 1), ("Sulfurous Ash", 1)]},
         "Incognito": {'btn': 16, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Blood Moss", 1), 
             ("Garlic", 1), ("Nightshade", 1)]},
         "Magic Reflection": {'btn': 23, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Garlic", 1), (
             "Mandrake Root", 1), ("Spiders' Silk", 1)]},
         "Mind Blast": {'btn': 30, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Black Pearl", 1), 
             ("Mandrake Root", 1), ("Nightshade", 1), 
             ("Sulfurous Ash", 1)]},
         "Paralyze": {'btn': 37, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Garlic", 1), 
             ("Mandrake Root", 1), ("Spiders' Silk", 1)]},
         "Poison Field": {'btn': 44, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Black Pearl", 1), 
             ("Nightshade", 1), ("Spiders' Silk", 1)]},
         "Summon Creature": {'btn': 51, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Blood Moss", 1), 
             ("Mandrake Root", 1), ("Spiders' Silk", 1)]},
         "Dispel": {'btn': 58, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Garlic", 1), 
             ("Mandrake Root", 1), ("Sulfurous Ash", 1)]},
         "Energy Bolt": {'btn': 65, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Black Pearl", 1), 
             ("Nightshade", 1)]},
         "Explosion": {'btn': 72, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Blood Moss", 1), 
             ("Mandrake Root", 1)]},
         "Invisibility": {'btn': 79, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Blood Moss", 1), 
             ("Nightshade", 1)]},
         "Mark": {'btn': 86, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Blood Moss", 1), 
             ("Black Pearl", 1), ("Mandrake Root", 1)]},
         "Mass Curse": {'btn': 93, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Garlic", 1), 
             ("Mandrake Root", 1), ("Nightshade", 1), 
             ("Sulfurous Ash", 1)]},
         "Paralyze Field": {'btn': 100, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Black Pearl", 1), 
             ("Ginseng", 1), ("Spiders' Silk", 1)]},
         "Reveal": {'btn': 107, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Blood Moss", 1), 
             ("Sulfurous Ash", 1)]}
        },
    ('Seventh - Eighth Circle', 22):
        {"Chain Lightning": {'btn': 2, 'stack': False, 'mats':
            [("Blank Scroll", 1), ("Black Pearl", 1), 
            ("Blood Moss", 1), ("Mandrake Root", 1), 
            ("Sulfurous Ash", 1)]},
         "Energy Field": {'btn': 9, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Black Pearl", 1), 
             ("Mandrake Root", 1), ("Spiders' Silk", 1),
              ("Sulfurous Ash", 1)]},
         "Flamestrike": {'btn': 16, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Spiders' Silk", 1), 
             ("Sulfurous Ash", 1)]},
         "Gate Travel": {'btn': 23, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Black Pearl", 1), 
             ("Mandrake Root", 1), ("Sulfurous Ash", 1)]},
         "Mana Vampire": {'btn': 30, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Black Pearl", 1), 
             ("Blood Moss", 1), ("Mandrake Root", 1), 
             ("Spiders' Silk", 1)]},
         "Mass Dispel": {'btn': 37, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Black Pearl", 1), 
             ("Garlic", 1), ("Mandrake Root", 1), 
             ("Sulfurous Ash", 1)]},
         "Meteor Swarm": {'btn': 44, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Blood Moss", 1), 
             ("Mandrake Root", 1), ("Sulfurous Ash", 1),
              ("Spiders' Silk", 1)]},
         "Polymorph": {'btn': 52, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Blood Moss", 1), 
             ("Mandrake Root", 1), ("Spiders' Silk", 1)]},
         "Earthquake": {'btn': 58, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Blood Moss", 1), 
             ("Mandrake Root", 1), ("Ginseng", 1), 
             ("Sulfurous Ash", 1)]},
         "Energy Vortex": {'btn': 65, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Black Pearl", 1), 
             ("Blood Moss", 1), ("Mandrake Root", 1), 
             ("Nightshade", 1)]},
         "Resurrection": {'btn': 72, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Blood Moss", 1), 
             ("Garlic", 1), ("Ginseng", 1)]},
         "Summon Air Elemental": {'btn': 79, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Blood Moss", 1), 
             ("Mandrake Root", 1), ("Spiders' Silk", 1)]},
         "Summon Daemon": {'btn': 86, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Blood Moss", 1), 
             ("Mandrake Root", 1), ("Spiders' Silk", 1), 
             ("Sulfurous Ash", 1)]},
         "Summon Earth Elemental": {'btn': 93, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Blood Moss", 1), 
             ("Mandrake Root", 1), ("Spiders' Silk", 1)]},
         "Summon Fire Elemental": {'btn': 100, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Blood Moss", 1), 
             ("Mandrake Root", 1), ("Spiders' Silk", 1), 
             ("Sulfurous Ash", 1)]},
         "Summon Water Elemental": {'btn': 207, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Blood Moss", 1), 
             ("Mandrake Root", 1), ("Spiders' Silk", 1)]}
        },
    ('Spells Of Necromancy', 29):
        {"Animate Dead": {'btn': 2, 'stack': False, 'mats':
            [("Blank Scroll", 1), ("Grave Dust", 1), 
            ("Daemon Blood", 1)]},
         "Blood Oath": {'btn': 9, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Daemon Blood", 1)]},
         "Corpse Skin": {'btn': 16, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Batwing", 1), 
             ("Grave Dust", 1)]},
         "Curse Weapon": {'btn': 23, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Pig Iron", 1)]},
         "Evil Omen": {'btn': 30, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Batwing", 1), 
             ("Nox Crystal", 1)]},
         "Horrific Beast": {'btn': 37, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Batwing", 1), 
             ("Daemon Blood", 1)]},
         "Lich Form": {'btn': 44, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Grave Dust", 1), 
             ("Daemon Blood", 1), ("Nox Crystal", 1)]},
         "Mind Rot": {'btn': 51, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Batwing", 1), 
             ("Daemon Blood", 1), ("Pig Iron", 1)]},
         "Pain Spike": {'btn': 58, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Grave Dust", 1), 
             ("Pig Iron", 1)]},
         "Poison Strike": {'btn': 65, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Nox Crystal", 1)]},
         "Strangle": {'btn': 72, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Daemon Blood", 1), 
             ("Nox Crystal", 1)]},
         "Summon Familiar": {'btn': 79, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Batwing", 1), 
             ("Grave Dust", 1), ("Daemon Blood", 1)]},
         "Vampiric Embrace": {'btn': 86, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Batwing", 1), 
             ("Nox Crystal", 1), ("Pig Iron", 1)]},
         "Vengeful Spirit": {'btn': 93, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Batwing", 1), 
             ("Grave Dust", 1), ("Pig Iron", 1)]},
         "Wither": {'btn': 100, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Grave Dust", 1), 
             ("Nox Crystal", 1), ("Pig Iron", 1)]},
         "Wraith Form": {'btn': 107, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Nox Crystal", 1), 
             ("Pig Iron", 1)]},
         "Exorcism": {'btn': 114, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Nox Crystal", 1), 
             ("Grave Dust", 1)]}
        },
    ('Other', 36):
        {"Enchanted Switch": {'btn': 2, 'stack': False, 'mats':
            [("Blank Scrolls", 1), ("Spiders' Silk", 1), 
            ("Black Pearl", 1), ("Switch", 1)]},
         "Runed Prism": {'btn': 9, 'stack': False, 'mats':
             [("Blank Scrolls", 1), ("Spiders' Silk", 1), 
             ("Black Pearl", 1), ("hollow prism", 1)]},
         "Runebook": {'btn': 16, 'stack': False, 'mats':
             [("Blank Scrolls", 8), ("Recall Scrolls", 1), 
             ("Gate Scrolls", 1), ("Unmarked Runes", 1)]},
         "Bulk Order Book": {'btn': 23, 'stack': False, 'mats': [("Blank Scrolls", 10)]},
         "Spellbook": {'btn': 30, 'stack': False, 'mats': [("Blank Scrolls", 10)]},
         "Scrapper'S Compendium": {'btn': 37, 'stack': False, 'mats':
             [("Blank Scrolls", 100), ("Dread Horn Mane", 1), 
             ("Taint", 10), ("Corruption", 10)]},
         "Spellbook Engraving Tool": {'btn': 44, 'stack': False, 'mats':
             [("Feathers", 1), ("Black Pearl", 7)]},
         "Mysticism Spellbook": {'btn': 51, 'stack': False, 'mats': [("Blank Scrolls", 10)]},
         "Necromancer Spellbook": {'btn': 58, 'stack': False, 'mats': [("Blank Scrolls", 10)]},
         "Exodus Summoning Rite ": {'btn': 65, 'stack': False, 'mats':
             [("Daemon Blood", 5), ("Taint", 1), (
             "Daemon Bone", 5), ("A Daemon Summoning Scroll", 1)]},
         "Prophetic Manuscript": {'btn': 72, 'stack': False, 'mats':
             [("Ancient Parchment", 10), ("Antique Documents Kit", 1), 
             ("wood pulp", 10), ("Beeswax", 5)]},
         "Blank Scroll": {'btn': 79, 'stack': False, 'mats': [("wood pulp", 1)]},
         "Scroll Binder": {'btn': 86, 'stack': False, 'mats': [("wood pulp", 1)]},
         "Book (100 Pages)": {'btn': 93, 'stack': False, 'mats':
             [("Blank Scrolls", 40), ("Beeswax", 2)]},
         "Book (200 Pages)": {'btn': 100, 'stack': False, 'mats':
             [("Blank Scrolls", 40), ("Beeswax", 2)]},
         "Runic Atlas": {'btn': 107, 'stack': False, 'mats':
             [("Blank Scrolls", 24), ("Recall Scrolls", 3), 
             ("Gate Scrolls", 3)]}
        },
    ('Spells Of Mysticism', 43):
        {"Nether Bolt": {'btn': 2, 'stack': False, 'mats':
            [("Blank Scroll", 1), ("Sulfurous Ash", 1), 
            ("Black Pearl", 1)]},
         "Healing Stone": {'btn': 9, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Bone", 1), 
             ("Garlic", 1), ("Ginseng", 1), 
             ("Spiders' Silk", 1)]},
         "Purge Magic": {'btn': 16, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Fertile Dirt", 1), 
             ("Garlic", 1), ("Mandrake Root", 1), 
             ("Sulfurous Ash", 1)]},
         "Enchant": {'btn': 23, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Spiders' Silk", 1), 
             ("Mandrake Root", 1), ("Sulfurous Ash", 1)]},
         "Sleep": {'btn': 30, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Spiders' Silk", 1), 
             ("Black Pearl", 1), ("Nightshade", 1)]},
         "Eagle Strike": {'btn': 37, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Spiders' Silk", 1), 
             ("Blood Moss", 1), ("Mandrake Root", 1), 
             ("Bone", 1)]},
         "Animated Weapon": {'btn': 44, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Bone", 1), 
             ("Black Pearl", 1), ("Mandrake Root", 1), 
             ("Nightshade", 1)]},
         "Stone Form": {'btn': 51, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Blood Moss", 1), 
             ("Fertile Dirt", 1), ("Garlic", 1)]},
         "Spell Trigger": {'btn': 58, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Spiders' Silk", 1), 
             ("Mandrake Root", 1), ("Garlic", 1), 
             ("Dragon's Blood", 1)]},
         "Mass Sleep": {'btn': 65, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Spiders' Silk", 1), 
             ("Nightshade", 1), ("Ginseng", 1)]},
         "Cleansing Winds": {'btn': 72, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Ginseng", 1), (
             "Garlic", 1), ("Dragon's Blood", 1), 
             ("Mandrake Root", 1)]},
         "Bombard": {'btn': 79, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Garlic", 1), 
             ("Dragon's Blood", 1), ("Sulfurous Ash", 1), 
             ("Blood Moss", 1)]},
         "Spell Plague": {'btn': 86, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Daemon Bone", 1), 
             ("Dragon's Blood", 1), ("Nightshade", 1), 
             ("Sulfurous Ash", 1)]},
         "Hail Storm": {'btn': 93, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Dragon's Blood", 1), 
             ("Black Pearl", 1), ("Mandrake Root", 1), 
             ("Blood Moss", 1)]},
         "Nether Cyclone": {'btn': 100, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Blood Moss", 1), 
             ("Nightshade", 1), ("Sulfurous Ash", 1), 
             ("Mandrake Root", 1)]},
         "Rising Colossus": {'btn': 107, 'stack': False, 'mats':
             [("Blank Scroll", 1), ("Daemon Bone", 1), 
             ("Fertile Dirt", 1), ("Dragon's Blood", 1), 
             ("Nightshade", 1)]}
        }
    }

tailoring_gump = {
    'categories':
        [('Exit', 0), 
        ('Cancel Make', 84), 
        ('Repair Item', 42), 
        ('Mark Item', 49), 
        ('Enhance Item', 63), 
        ('Non Quest Item', 77), 
        ('Make Last', 21), 
        ('Last Ten', 28), 
        ('Materials', 1), 
        ('Hats', 8), 
        ('Shirts And Pants', 15), 
        ('Miscellaneous', 22), 
        ('Footwear', 29), 
        ('Leather Armor', 36), 
        ('Cloth Armor', 43), 
        ('Studded Armor', 50), 
        ('Female Armor', 57), 
        ('Bone Armor', 64)
    ],
    ('Materials', 1):
        {"Cut-Up Cloth": {'btn': 2, 'stack': False, 'mats': [("Bolts of Cloth", 1)]},
         "Combine Cloth": {'btn': 9, 'stack': False, 'mats': [("Yards of Cloth", 1)]},
         "Powder Charge": {'btn': 16, 'stack': True, 'mats':
             [("Yards of Cloth", 1), ("black powder", 4)]},
         "Abyssal Cloth": {'btn': 23, 'stack': False, 'mats':
             [("Yards of Cloth", 50), ("Crystalline Blackrock", 1)]}
        },
    ('Hats', 8):
        {"Skullcap": {'btn': 2, 'stack': False, 'mats': [("Yards of Cloth", 2)]},
         "Bandana": {'btn': 9, 'stack': False, 'mats': [("Yards of Cloth", 2)]},
         "Floppy Hat": {'btn': 16, 'stack': False, 'mats': [("Yards of Cloth", 11)]},
         "Cap": {'btn': 23, 'stack': False, 'mats': [("Yards of Cloth", 11)]},
         "Wide-Brim Hat": {'btn': 30, 'stack': False, 'mats': [("Yards of Cloth", 12)]},
         "Straw Hat": {'btn': 37, 'stack': False, 'mats': [("Yards of Cloth", 10)]},
         "Tall Straw Hat": {'btn': 44, 'stack': False, 'mats': [("Yards of Cloth", 13)]},
         "Wizard'S Hat": {'btn': 51, 'stack': False, 'mats': [("Yards of Cloth", 15)]},
         "Bonnet": {'btn': 58, 'stack': False, 'mats': [("Yards of Cloth", 11)]},
         "Feathered Hat": {'btn': 65, 'stack': False, 'mats': [("Yards of Cloth", 12)]},
         "Tricorne Hat": {'btn': 72, 'stack': False, 'mats': [("Yards of Cloth", 12)]},
         "Jester Hat": {'btn': 79, 'stack': False, 'mats': [("Yards of Cloth", 15)]},
         "Flower Garland": {'btn': 86, 'stack': False, 'mats': [("Yards of Cloth", 5)]},
         "Cloth Ninja Hood": {'btn': 93, 'stack': False, 'mats': [("Yards of Cloth", 13)]},
         "Kasa": {'btn': 100, 'stack': False, 'mats': [("Yards of Cloth", 12)]},
         "Orc Mask": {'btn': 107, 'stack': False, 'mats': [("Yards of Cloth", 12)]},
         "Bear Mask": {'btn': 114, 'stack': False, 'mats': [("Yards of Cloth", 15)]},
         "Deer Mask": {'btn': 121, 'stack': False, 'mats': [("Yards of Cloth", 15)]},
         "Tribal Mask": {'btn': 128, 'stack': False, 'mats': [("Yards of Cloth", 12)]},
         "Tribal Mask 2": {'btn': 135, 'stack': False, 'mats': [("Yards of Cloth", 12)]},
         "Chef'S Toque": {'btn': 142, 'stack': False, 'mats': [("Yards of Cloth", 11)]},
         "Krampus Minion Hat": {'btn': 149, 'stack': False, 'mats': [("Yards of Cloth", 8)]},
         "Assassin'S Cowl": {'btn': 156, 'stack': False, 'mats':
             [("Yards of Cloth", 5), ("Leather or Hides", 5), 
             ("vile tentacles", 5)]},
         "Mage'S Hood": {'btn': 163, 'stack': False, 'mats':
             [("Yards of Cloth", 5), ("Leather or Hides", 5), 
             ("void core", 5)]},
         "Cowl Of The Mace & Shield": {'btn': 170, 'stack': False, 'mats':
             [("Yards of Cloth", 5), ("Leather or Hides", 5), 
             ("Mace and Shield Reading Glasses", 1), ("vile tentacles", 10)]},
         "Mage'S Hood Of Scholarly Insight": {'btn': 177, 'stack': False, 'mats':
             [("Yards of Cloth", 5), ("Leather or Hides", 5), 
             ("the scholar's halo", 1), ("void core", 10)]}
        },
    ('Shirts And Pants', 15):
        {"Doublet": {'btn': 2, 'stack': False, 'mats': [("Yards of Cloth", 8)]},
         "Shirt": {'btn': 9, 'stack': False, 'mats': [("Yards of Cloth", 8)]},
         "Fancy Shirt": {'btn': 16, 'stack': False, 'mats': [("Yards of Cloth", 8)]},
         "Tunic": {'btn': 23, 'stack': False, 'mats': [("Yards of Cloth", 12)]},
         "Surcoat": {'btn': 30, 'stack': False, 'mats': [("Yards of Cloth", 14)]},
         "Plain Dress": {'btn': 37, 'stack': False, 'mats': [("Yards of Cloth", 10)]},
         "Fancy Dress": {'btn': 44, 'stack': False, 'mats': [("Yards of Cloth", 12)]},
         "Cloak": {'btn': 51, 'stack': False, 'mats': [("Yards of Cloth", 14)]},
         "Robe": {'btn': 58, 'stack': False, 'mats': [("Yards of Cloth", 16)]},
         "Jester Suit": {'btn': 65, 'stack': False, 'mats': [("Yards of Cloth", 24)]},
         "Fur Cape": {'btn': 72, 'stack': False, 'mats': [("Yards of Cloth", 13)]},
         "Gilded Dress": {'btn': 79, 'stack': False, 'mats': [("Yards of Cloth", 16)]},
         "Formal Shirt": {'btn': 86, 'stack': False, 'mats': [("Yards of Cloth", 16)]},
         "Cloth Ninja Jacket": {'btn': 93, 'stack': False, 'mats': [("Yards of Cloth", 12)]},
         "Kamishimo": {'btn': 100, 'stack': False, 'mats': [("Yards of Cloth", 15)]},
         "Hakama-Shita": {'btn': 107, 'stack': False, 'mats': [("Yards of Cloth", 14)]},
         "Male Kimono": {'btn': 114, 'stack': False, 'mats': [("Yards of Cloth", 16)]},
         "Female Kimono": {'btn': 121, 'stack': False, 'mats': [("Yards of Cloth", 16)]},
         "Jin-Baori": {'btn': 128, 'stack': False, 'mats': [("Yards of Cloth", 12)]},
         "Short Pants": {'btn': 135, 'stack': False, 'mats': [("Yards of Cloth", 6)]},
         "Long Pants": {'btn': 142, 'stack': False, 'mats': [("Yards of Cloth", 8)]},
         "Kilt": {'btn': 149, 'stack': False, 'mats': [("Yards of Cloth", 8)]},
         "Skirt": {'btn': 156, 'stack': False, 'mats': [("Yards of Cloth", 10)]},
         "Fur Sarong": {'btn': 163, 'stack': False, 'mats': [("Yards of Cloth", 12)]},
         "Hakama": {'btn': 170, 'stack': False, 'mats': [("Yards of Cloth", 16)]},
         "Tattsuke-Hakama": {'btn': 177, 'stack': False, 'mats': [("Yards of Cloth", 16)]},
         "Elven Shirt": {'btn': 184, 'stack': False, 'mats': [("Yards of Cloth", 10)]},
         "Elven Shirt 2": {'btn': 191, 'stack': False, 'mats': [("Yards of Cloth", 10)]},
         "Elven Pants": {'btn': 198, 'stack': False, 'mats': [("Yards of Cloth", 12)]},
         "Elven Robe": {'btn': 205, 'stack': False, 'mats': [("Yards of Cloth", 30)]},
         "Female Elven Robe": {'btn': 212, 'stack': False, 'mats': [("Yards of Cloth", 30)]},
         "Woodland Belt": {'btn': 219, 'stack': False, 'mats': [("Yards of Cloth", 10)]},
         "Gargish Robe": {'btn': 226, 'stack': False, 'mats': [("Yards of Cloth", 16)]},
         "Gargish Fancy Robe": {'btn': 233, 'stack': False, 'mats': [("Yards of Cloth", 16)]},
         "Robe Of Rite": {'btn': 240, 'stack': False, 'mats':
             [("Leather or Hides", 6), ("Fire Ruby", 1), 
             ("Gold Dust ", 5), ("abyssal cloth", 6)]},
         "Gilded Kilt": {'btn': 247, 'stack': False, 'mats': [("Yards of Cloth", 8)]},
         "Checkered Kilt": {'btn': 254, 'stack': False, 'mats': [("Yards of Cloth", 8)]},
         "Fancy Kilt": {'btn': 261, 'stack': False, 'mats': [("Yards of Cloth", 8)]},
         "Flowered Dress": {'btn': 268, 'stack': False, 'mats': [("Yards of Cloth", 18)]},
         "Evening Gown": {'btn': 275, 'stack': False, 'mats': [("Yards of Cloth", 18)]}
        },
    ('Miscellaneous', 11):
        {"Body Sash": {'btn': 2, 'stack': False, 'mats': [("Yards of Cloth", 4)]},
         "Half Apron": {'btn': 9, 'stack': False, 'mats': [("Yards of Cloth", 6)]},
         "Full Apron": {'btn': 16, 'stack': False, 'mats': [("Yards of Cloth", 10)]},
         #" A Bag": {'btn': 23, 'stack': False, 'mats': [("Yards of Cloth", 6)]},
         #"Pouch": {'btn': 30, 'stack': False, 'mats': [("Yards of Cloth", 8)]},
         #"Backpack": {'btn': 37, 'stack': False, 'mats': [("Leather or Hides", 15)]},
         "Obi": {'btn': 23, 'stack': False, 'mats': [("Yards of Cloth", 6)]},
         "Elven Quiver": {'btn': 30, 'stack': False, 'mats': [("Leather or Hides", 28)]},
         "Quiver Of Fire": {'btn': 37, 'stack': False, 'mats':
             [("Leather or Hides", 28), ("Fire Ruby", 15)]},
         "Quiver Of Ice": {'btn': 44, 'stack': False, 'mats':
             [("Leather or Hides", 28), ("White Pearl", 15)]},
         "Quiver Of Blight": {'btn': 51, 'stack': False, 'mats':
             [("Leather or Hides", 28), ("Blight", 10)]},
         "Quiver Of Lightning": {'btn': 58, 'stack': False, 'mats':
             [("Leather or Hides", 28), ("Corruption", 10)]},
         "Leather Container Engraving Tool": {'btn': 65, 'stack': False, 'mats':
             [("Bones", 1), ("Leather or Hides", 6), 
             ("Spools of Thread", 2), ("dyes", 1)]},
         "Gargish Half Apron": {'btn': 72, 'stack': False, 'mats': [("Yards of Cloth", 6)]},
         "Gargish Sash": {'btn': 79, 'stack': False, 'mats': [("Yards of Cloth", 4)]},
         "Oil Cloth": {'btn': 86, 'stack': False, 'mats': [("Yards of Cloth", 1)]},
         "Goza (East)": {'btn': 93, 'stack': False, 'mats': [("Yards of Cloth", 25)]},
         "Goza (South)": {'btn': 100, 'stack': False, 'mats': [("Yards of Cloth", 25)]},
         "Square Goza (East)": {'btn': 107, 'stack': False, 'mats': [("Yards of Cloth", 25)]},
         "Square Goza (South)": {'btn': 114, 'stack': False, 'mats': [("Yards of Cloth", 25)]},
         "Brocade Goza (East)": {'btn': 121, 'stack': False, 'mats': [("Yards of Cloth", 25)]},
         "Brocade Goza (South)": {'btn': 128, 'stack': False, 'mats': [("Yards of Cloth", 25)]},
         "Square Brocade Goza (East)": {'btn': 135, 'stack': False, 'mats': [("Yards of Cloth", 25)]},
         "Square Brocade Goza (South)": {'btn': 142, 'stack': False, 'mats': [("Yards of Cloth", 25)]},
         "Square Goza": {'btn': 149, 'stack': False, 'mats': [("Yards of Cloth", 25)]},
         "Mace Belt": {'btn': 156, 'stack': False, 'mats':
             [("Yards of Cloth", 5), ("Leather or Hides", 5), 
             ("lodestone", 5)]},
         "Sword Belt": {'btn': 163, 'stack': False, 'mats':
             [("Yards of Cloth", 5), ("Leather or Hides", 5), 
             ("lodestone", 5)]},
         "Dagger Belt": {'btn': 170, 'stack': False, 'mats':
             [("Yards of Cloth", 5), ("Leather or Hides", 5), 
             ("lodestone", 5)]},
         "Elegant Collar": {'btn': 177, 'stack': False, 'mats':
             [("Yards of Cloth", 5), ("Leather or Hides", 5), 
             ("fey wings", 5)]},
         "Crimson Mace Belt": {'btn': 184, 'stack': False, 'mats':
             [("Yards of Cloth", 5), ("Leather or Hides", 5), 
             ("Crimson Cincture", 1), ("lodestone", 10)]},
         "Crimson Sword Belt": {'btn': 191, 'stack': False, 'mats':
             [("Yards of Cloth", 5), ("Leather or Hides", 5), 
             ("Crimson Cincture", 1), ("lodestone", 10)]},
         "Crimson Dagger Belt": {'btn': 198, 'stack': False, 'mats':
             [("Yards of Cloth", 5), ("Leather or Hides", 5), 
             ("Crimson Cincture", 1), ("lodestone", 10)]},
         "Elegant Collar Of Fortune": {'btn': 205, 'stack': False, 'mats':
             [("Yards of Cloth", 5), ("Leather or Hides", 5), 
             ("Leurocian's Mempo of Fortune", 1), ("fey wings", 10)]}
        },
    ('Footwear', 29):
        {"Elven Boots": {'btn': 2, 'stack': False, 'mats': [("Leather or Hides", 15)]},
         "Fur Boots": {'btn': 9, 'stack': False, 'mats': [("Yards of Cloth", 12)]},
         "Ninja Tabi": {'btn': 16, 'stack': False, 'mats': [("Yards of Cloth", 10)]},
         "Waraji And Tabi": {'btn': 23, 'stack': False, 'mats': [("Yards of Cloth", 6)]},
         "Sandals": {'btn': 30, 'stack': False, 'mats': [("Leather or Hides", 4)]},
         "Shoes": {'btn': 37, 'stack': False, 'mats': [("Leather or Hides", 6)]},
         "Boots": {'btn': 44, 'stack': False, 'mats': [("Leather or Hides", 8)]},
         "Thigh Boots": {'btn': 51, 'stack': False, 'mats': [("Leather or Hides", 10)]},
         "Gargish Leather Talons": {'btn': 58, 'stack': False, 'mats': [("Leather or Hides", 6)]},
         "Jester Shoes": {'btn': 65, 'stack': False, 'mats': [("Yards of Cloth", 6)]},
         "Krampus Minion Boots": {'btn': 72, 'stack': False, 'mats':
             [("Leather or Hides", 6), ("Yards of Cloth", 4)]},
         "Krampus Minion Talons": {'btn': 79, 'stack': False, 'mats':
             [("Leather or Hides", 6), ("Yards of Cloth", 4)]}
        },
    ('Leather Armor', 36):
        {"Spell Woven Britches": {'btn': 2, 'stack': False, 'mats':
            [("Leather or Hides", 15), ("Eye of the Travesty", 1), 
            ("Putrefaction", 10), ("Scourge", 10)]},
         "Song Woven Mantle": {'btn': 9, 'stack': False, 'mats':
             [("Leather or Hides", 15), ("Eye of the Travesty", 1), 
             ("Blight", 10), ("Muculent", 10)]},
         "Stitcher'S Mittens": {'btn': 16, 'stack': False, 'mats':
             [("Leather or Hides", 15), ("Captured Essence", 1), 
             ("Corruption", 10), ("Taint", 10)]},
         "Leather Gorget": {'btn': 23, 'stack': False, 'mats':
             [("Leather or Hides", 4)]},
         "Leather Cap": {'btn': 30, 'stack': False, 'mats': [("Leather or Hides", 2)]},
         "Leather Gloves": {'btn': 37, 'stack': False, 'mats': [("Leather or Hides", 3)]},
         "Leather Sleeves": {'btn': 44, 'stack': False, 'mats': [("Leather or Hides", 4)]},
         "Leather Leggings": {'btn': 51, 'stack': False, 'mats': [("Leather or Hides", 10)]},
         "Leather Tunic": {'btn': 58, 'stack': False, 'mats': [("Leather or Hides", 12)]},
         "Leather Jingasa": {'btn': 65, 'stack': False, 'mats': [("Leather or Hides", 4)]},
         "Leather Mempo": {'btn': 72, 'stack': False, 'mats': [("Leather or Hides", 8)]},
         "Leather Do": {'btn': 79, 'stack': False, 'mats': [("Leather or Hides", 12)]},
         "Leather Hiro Sode": {'btn': 86, 'stack': False, 'mats': [("Leather or Hides", 5)]},
         "Leather Suneate": {'btn': 93, 'stack': False, 'mats': [("Leather or Hides", 12)]},
         "Leather Haidate": {'btn': 100, 'stack': False, 'mats': [("Leather or Hides", 12)]},
         "Leather Ninja Pants": {'btn': 107, 'stack': False, 'mats': [("Leather or Hides", 13)]},
         "Leather Ninja Jacket": {'btn': 114, 'stack': False, 'mats': [("Leather or Hides", 13)]},
         "Leather Ninja Belt": {'btn': 121, 'stack': False, 'mats': [("Leather or Hides", 5)]},
         "Leather Ninja Mitts": {'btn': 128, 'stack': False, 'mats': [("Leather or Hides", 12)]},
         "Leather Ninja Hood": {'btn': 135, 'stack': False, 'mats': [("Leather or Hides", 14)]},
         "Leaf Tunic": {'btn': 142, 'stack': False, 'mats': [("Leather or Hides", 15)]},
         "Leaf Arms": {'btn': 149, 'stack': False, 'mats': [("Leather or Hides", 12)]},
         "Leaf Gloves": {'btn': 156, 'stack': False, 'mats': [("Leather or Hides", 10)]},
         "Leaf Leggings": {'btn': 163, 'stack': False, 'mats': [("Leather or Hides", 15)]},
         "Leaf Gorget": {'btn': 170, 'stack': False, 'mats': [("Leather or Hides", 12)]},
         "Leaf Tonlet": {'btn': 177, 'stack': False, 'mats': [("Leather or Hides", 12)]},
         "Gargish Leather Arms": {'btn': 184, 'stack': False, 'mats': [("Leather or Hides", 8)]},
         "Gargish Leather Chest": {'btn': 191, 'stack': False, 'mats': [("Leather or Hides", 8)]},
         "Gargish Leather Leggings": {'btn': 198, 'stack': False, 'mats': [("Leather or Hides", 10)]},
         "Gargish Leather Kilt": {'btn': 205, 'stack': False, 'mats': [("Leather or Hides", 6)]},
         "Gargish Leather Arms 2": {'btn': 212, 'stack': False, 'mats': [("Leather or Hides", 8)]},
         "Gargish Leather Chest 2": {'btn': 219, 'stack': False, 'mats': [("Leather or Hides", 8)]},
         "Gargish Leather Leggings 2": {'btn': 226, 'stack': False, 'mats': [("Leather or Hides", 10)]},
         "Gargish Leather Kilt 2": {'btn': 233, 'stack': False, 'mats': [("Leather or Hides", 6)]},
         "Gargish Leather Wing Armor": {'btn': 240, 'stack': False, 'mats': [("Leather or Hides", 12)]},
         "Tiger Pelt Chest": {'btn': 247, 'stack': False, 'mats':
             [("Tiger Pelt", 4), ("Leather or Hides", 8)]},
         "Tiger Pelt Leggings": {'btn': 254, 'stack': False, 'mats':
             [("Tiger Pelt", 8), ("Leather or Hides", 4)]},
         "Tiger Pelt Shorts": {'btn': 261, 'stack': False, 'mats':
             [("Tiger Pelt", 4), ("Leather or Hides", 2)]},
         "Tiger Pelt Helm": {'btn': 268, 'stack': False, 'mats':
             [("Tiger Pelt", 2), ("Leather or Hides", 2)]},
         "Tiger Pelt Collar": {'btn': 275, 'stack': False, 'mats':
             [("Tiger Pelt", 2), ("Leather or Hides", 1)]},
         "Dragon Turtle Hide Chest": {'btn': 282, 'stack': False, 'mats':
             [("Leather or Hides", 8), ("Dragon Turtle Scute", 2)]},
         "Dragon Turtle Hide Leggings": {'btn': 289, 'stack': False, 'mats':
             [("Leather or Hides", 8), ("Dragon Turtle Scute", 4)]},
         "Dragon Turtle Hide Helm": {'btn': 296, 'stack': False, 'mats':
             [("Leather or Hides", 2), ("Dragon Turtle Scute", 1)]},
         "Dragon Turtle Hide Arms": {'btn': 303, 'stack': False, 'mats':
             [("Leather or Hides", 4), ("Dragon Turtle Scute", 2)]}
        },
    ('Cloth Armor', 43):
        {"Gargish Cloth Arms": {'btn': 2, 'stack': False, 'mats': [("Yards of Cloth", 8)]},
         "Gargish Cloth Chest": {'btn': 9, 'stack': False, 'mats': [("Yards of Cloth", 8)]},
         "Gargish Cloth Leggings": {'btn': 16, 'stack': False, 'mats': [("Yards of Cloth", 10)]},
         "Gargish Cloth Kilt": {'btn': 23, 'stack': False, 'mats': [("Yards of Cloth", 6)]},
         "Gargish Cloth Arms 2": {'btn': 30, 'stack': False, 'mats': [("Yards of Cloth", 8)]},
         "Gargish Cloth Chest 2": {'btn': 37, 'stack': False, 'mats': [("Yards of Cloth", 8)]},
         "Gargish Cloth Leggings 2": {'btn': 44, 'stack': False, 'mats': [("Yards of Cloth", 10)]},
         "Gargish Cloth Kilt 2": {'btn': 51, 'stack': False, 'mats': [("Yards of Cloth", 6)]},
         "Gargish Cloth Wing Armor": {'btn': 58, 'stack': False, 'mats': [("Yards of Cloth", 12)]}
        },
    ('Studded Armor', 50):
        {"Studded Gorget": {'btn': 2, 'stack': False, 'mats': [("Leather or Hides", 6)]},
         "Studded Gloves": {'btn': 9, 'stack': False, 'mats': [("Leather or Hides", 8)]},
         "Studded Sleeves": {'btn': 16, 'stack': False, 'mats': [("Leather or Hides", 10)]},
         "Studded Leggings": {'btn': 23, 'stack': False, 'mats': [("Leather or Hides", 12)]},
         "Studded Tunic": {'btn': 30, 'stack': False, 'mats': [("Leather or Hides", 14)]},
         "Studded Mempo": {'btn': 37, 'stack': False, 'mats': [("Leather or Hides", 8)]},
         "Studded Do": {'btn': 44, 'stack': False, 'mats': [("Leather or Hides", 14)]},
         "Studded Hiro Sode": {'btn': 51, 'stack': False, 'mats': [("Leather or Hides", 8)]},
         "Studded Suneate": {'btn': 58, 'stack': False, 'mats': [("Leather or Hides", 14)]},
         "Studded Haidate": {'btn': 65, 'stack': False, 'mats': [("Leather or Hides", 14)]},
         "Hide Tunic": {'btn': 72, 'stack': False, 'mats': [("Leather or Hides", 15)]},
         "Hide Pauldrons": {'btn': 79, 'stack': False, 'mats': [("Leather or Hides", 12)]},
         "Hide Gloves": {'btn': 86, 'stack': False, 'mats': [("Leather or Hides", 10)]},
         "Hide Pants": {'btn': 93, 'stack': False, 'mats': [("Leather or Hides", 15)]},
         "Hide Gorget": {'btn': 100, 'stack': False, 'mats': [("Leather or Hides", 12)]}
        },
    ('Female Armor', 57):
        {"Leather Shorts": {'btn': 2, 'stack': False, 'mats': [("Leather or Hides", 8)]},
         "Leather Skirt": {'btn': 9, 'stack': False, 'mats': [("Leather or Hides", 6)]},
         "Leather Bustier": {'btn': 16, 'stack': False, 'mats': [("Leather or Hides", 6)]},
         "Studded Bustier": {'btn': 23, 'stack': False, 'mats': [("Leather or Hides", 8)]},
         "Female Leather Armor": {'btn': 30, 'stack': False, 'mats': [("Leather or Hides", 8)]},
         "Studded Armor": {'btn': 37, 'stack': False, 'mats': [("Leather or Hides", 10)]},
         "Tiger Pelt Bustier": {'btn': 44, 'stack': False, 'mats':
             [("Tiger Pelt", 3), ("Leather or Hides", 6)]},
         "Tiger Pelt Long Skirt": {'btn': 51, 'stack': False, 'mats':
             [("Tiger Pelt", 2), ("Leather or Hides", 4)]},
         "Tiger Pelt Skirt": {'btn': 58, 'stack': False, 'mats':
             [("Tiger Pelt", 2), ("Leather or Hides", 4)]},
         "Dragon Turtle Hide Bustier": {'btn': 65, 'stack': False, 'mats':
             [("Leather or Hides", 6), ("Dragon Turtle Scute", 3)]}
        },
    ('Bone Armor', 64):
        {"Bone Helmet": {'btn': 2, 'stack': False, 'mats':
            [("Leather or Hides", 4), ("Bones", 2)]},
         "Bone Gloves": {'btn': 9, 'stack': False, 'mats':
             [("Leather or Hides", 6), ("Bones", 2)]},
         "Bone Arms": {'btn': 16, 'stack': False, 'mats':
             [("Leather or Hides", 8), ("Bones", 4)]},
         "Bone Leggings": {'btn': 23, 'stack': False, 'mats':
             [("Leather or Hides", 10), ("Bones", 6)]},
         "Bone Armor": {'btn': 30, 'stack': False, 'mats':
             [("Leather or Hides", 12), ("Bones", 10)]},
         "Orc Helm": {'btn': 37, 'stack': False, 'mats':
             [("Leather or Hides", 6), ("Bones", 4)]},
         "Cuffs Of The Archmage": {'btn': 44, 'stack': False, 'mats':
             [("Yards of Cloth", 8), ("Midnight Bracers", 1), 
             ("Blood of the Dark Father", 5), ("Dark Sapphire", 4)]}
        }
    }

tinkering_gump = {
    'categories': [
        ('Exit', 0), 
        ('Cancel Make', 84), 
        ('Repair Item', 42), 
        ('Mark Item', 49), 
        ('Enhance Item', 63), 
        ('Non Quest Item', 77), 
        ('Make Last', 21), 
        ('Last Ten', 21), 
        ('Jewelry', 1), 
        ('Wooden Items', 8), 
        ('Tools', 15), 
        ('Parts', 22), 
        ('Utensils', 29), 
        ('Miscellaneous', 36), 
        ('Assemblies', 43), 
        ('Traps', 50), 
        ('Magic Jewelry', 57)
    ],
    ('Jewelry', 1):
        {"Ring": {'btn': 2, 'stack': False, 'mats': [("Ingots", 3)]},
         "Bracelet": {'btn': 9, 'stack': False, 'mats': [("Ingots", 3)]},
         "Gargish Necklace": {'btn': 16, 'stack': False, 'mats': [("Ingots", 3)]},
         "Gargish Bracelet": {'btn': 23, 'stack': False, 'mats': [("Ingots", 3)]},
         "Gargish Ring": {'btn': 30, 'stack': False, 'mats': [("Ingots", 3)]},
         "Gargish Earrings": {'btn': 37, 'stack': False, 'mats': [("Ingots", 3)]},
         "Star Sapphire Ring": {'btn': 44, 'stack': False, 'mats':
             [("Ingots", 2), ("Star Sapphires", 1)]},
         "Star Sapphire Necklace (Silver)": {'btn': 51, 'stack': False, 'mats':
             [("Ingots", 2), ("Star Sapphires", 1)]},
         "Star Sapphire Necklace (Jewelled)": {'btn': 58, 'stack': False, 'mats':
             [("Ingots", 2), ("Star Sapphires", 1)]},
         "Star Sapphire Earrings": {'btn': 65, 'stack': False, 'mats':
             [("Ingots", 2), ("Star Sapphires", 1)]},
         "Star Sapphire Necklace (Golden)": {'btn': 72, 'stack': False, 'mats':
             [("Ingots", 2), ("Star Sapphires", 1)]},
         "Star Sapphire Bracelet": {'btn': 79, 'stack': False, 'mats':
             [("Ingots", 2), ("Star Sapphires", 1)]},
         "Emerald Ring": {'btn': 86, 'stack': False, 'mats':
             [("Ingots", 2), ("Emeralds", 1)]},
         "Emerald Necklace (Silver)": {'btn': 93, 'stack': False, 'mats':
             [("Ingots", 2), ("Emeralds", 1)]},
         "Emerald Necklace (Jewelled)": {'btn': 100, 'stack': False, 'mats':
             [("Ingots", 2), ("Emeralds", 1)]},
         "Emerald Earrings": {'btn': 107, 'stack': False, 'mats':
             [("Ingots", 2), ("Emeralds", 1)]},
         "Emerald Necklace (Golden)": {'btn': 114, 'stack': False, 'mats':
             [("Ingots", 2), ("Emeralds", 1)]},
         "Emerald Bracelet": {'btn': 121, 'stack': False, 'mats':
             [("Ingots", 2), ("Emeralds", 1)]},
         "Sapphire Ring": {'btn': 128, 'stack': False, 'mats':
             [("Ingots", 2), ("Sapphires", 1)]},
         "Sapphire Necklace (Silver)": {'btn': 135, 'stack': False, 'mats':
             [("Ingots", 2), ("Sapphires", 1)]},
         "Sapphire Necklace (Jewelled)": {'btn': 142, 'stack': False, 'mats':
             [("Ingots", 2), ("Sapphires", 1)]},
         "Sapphire Earrings": {'btn': 149, 'stack': False, 'mats':
             [("Ingots", 2), ("Sapphires", 1)]},
         "Sapphire Necklace (Golden)": {'btn': 156, 'stack': False, 'mats':
             [("Ingots", 2), ("Sapphires", 1)]},
         "Sapphire Bracelet": {'btn': 163, 'stack': False, 'mats':
             [("Ingots", 2), ("Sapphires", 1)]},
         "Ruby Ring": {'btn': 170, 'stack': False, 'mats':
             [("Ingots", 2), ("Rubies", 1)]},
         "Ruby Necklace (Silver)": {'btn': 177, 'stack': False, 'mats':
             [("Ingots", 2), ("Rubies", 1)]},
         "Ruby Necklace (Jewelled)": {'btn': 184, 'stack': False, 'mats':
             [("Ingots", 2), ("Rubies", 1)]},
         "Ruby Earrings": {'btn': 191, 'stack': False, 'mats':
             [("Ingots", 2), ("Rubies", 1)]},
         "Ruby Necklace (Golden)": {'btn': 198, 'stack': False, 'mats':
             [("Ingots", 2), ("Rubies", 1)]},
         "Ruby Bracelet": {'btn': 205, 'stack': False, 'mats':
             [("Ingots", 2), ("Rubies", 1)]},
         "Citrine Ring": {'btn': 212, 'stack': False, 'mats':
             [("Ingots", 2), ("Citrines", 1)]},
         "Citrine Necklace (Silver)": {'btn': 219, 'stack': False, 'mats':
             [("Ingots", 2), ("Citrines", 1)]},
         "Citrine Necklace (Jewelled)": {'btn': 226, 'stack': False, 'mats':
             [("Ingots", 2), ("Citrines", 1)]},
         "Citrine Earrings": {'btn': 233, 'stack': False, 'mats':
             [("Ingots", 2), ("Citrines", 1)]},
         "Citrine Necklace (Golden)": {'btn': 240, 'stack': False, 'mats':
             [("Ingots", 2), ("Citrines", 1)]},
         "Citrine Bracelet": {'btn': 247, 'stack': False, 'mats':
             [("Ingots", 2), ("Citrines", 1)]},
         "Amethyst Ring": {'btn': 254, 'stack': False, 'mats':
             [("Ingots", 2), ("Amethysts", 1)]},
         "Amethyst Necklace (Silver)": {'btn': 261, 'stack': False, 'mats':
             [("Ingots", 2), ("Amethysts", 1)]},
         "Amethyst Necklace (Jewelled)": {'btn': 268, 'stack': False, 'mats':
             [("Ingots", 2), ("Amethysts", 1)]},
         "Amethyst Earrings": {'btn': 275, 'stack': False, 'mats':
             [("Ingots", 2), ("Amethysts", 1)]},
         "Amethyst Necklace (Golden)": {'btn': 282, 'stack': False, 'mats':
             [("Ingots", 2), ("Amethysts", 1)]},
         "Amethyst Bracelet": {'btn': 289, 'stack': False, 'mats':
             [("Ingots", 2), ("Amethysts", 1)]},
         "Tourmaline Ring": {'btn': 296, 'stack': False, 'mats':
             [("Ingots", 2), ("Tourmalines", 1)]},
         "Tourmaline Necklace (Silver)": {'btn': 303, 'stack': False, 'mats':
             [("Ingots", 2), ("Tourmalines", 1)]},
         "Tourmaline Necklace (Jewelled)": {'btn': 310, 'stack': False, 'mats':
             [("Ingots", 2), ("Tourmalines", 1)]},
         "Tourmaline Earrings": {'btn': 317, 'stack': False, 'mats':
             [("Ingots", 2), ("Tourmalines", 1)]},
         "Tourmaline Necklace (Golden)": {'btn': 324, 'stack': False, 'mats':
             [("Ingots", 2), ("Tourmalines", 1)]},
         "Tourmaline Bracelet": {'btn': 331, 'stack': False, 'mats':
             [("Ingots", 2), ("Tourmalines", 1)]},
         "Amber Ring": {'btn': 338, 'stack': False, 'mats':
             [("Ingots", 2), ("Amber", 1)]},
         "Amber Necklace (Silver)": {'btn': 345, 'stack': False, 'mats':
             [("Ingots", 2), ("Amber", 1)]},
         "Amber Necklace (Jewelled)": {'btn': 352, 'stack': False, 'mats':
             [("Ingots", 2), ("Amber", 1)]},
         "Amber Earrings": {'btn': 359, 'stack': False, 'mats':
             [("Ingots", 2), ("Amber", 1)]},
         "Amber Necklace (Golden)": {'btn': 366, 'stack': False, 'mats':
             [("Ingots", 2), ("Amber", 1)]},
         "Amber Bracelet": {'btn': 373, 'stack': False, 'mats':
             [("Ingots", 2), ("Amber", 1)]},
         "Diamond Ring": {'btn': 380, 'stack': False, 'mats':
             [("Ingots", 2), ("Diamonds", 1)]},
         "Diamond Necklace (Silver)": {'btn': 387, 'stack': False, 'mats':
             [("Ingots", 2), ("Diamonds", 1)]},
         "Diamond Necklace (Jewelled)": {'btn': 394, 'stack': False, 'mats':
             [("Ingots", 2), ("Diamonds", 1)]},
         "Diamond Earrings": {'btn': 401, 'stack': False, 'mats':
             [("Ingots", 2), ("Diamonds", 1)]},
         "Diamond Necklace (Golden)": {'btn': 408, 'stack': False, 'mats':
             [("Ingots", 2), ("Diamonds", 1)]},
         "Diamond Bracelet": {'btn': 415, 'stack': False, 'mats':
             [("Ingots", 2), ("Diamonds", 1)]},
         "Krampus Minion Earrings": {'btn': 422, 'stack': False, 'mats':
             [("Ingots", 3)]}
        },
    ('Wooden Items', 8):
        {"Nunchaku": {'btn': 2, 'stack': False, 'mats':
            [("Ingots", 3), ("Boards or Logs", 8)]},
         "Jointing Plane": {'btn': 9, 'stack': False, 'mats': [("Boards or Logs", 4)]},
         "Moulding Planes": {'btn': 16, 'stack': False, 'mats': [("Boards or Logs", 4)]},
         "Smoothing Plane": {'btn': 23, 'stack': False, 'mats': [("Boards or Logs", 4)]},
         "Clock Frame": {'btn': 30, 'stack': False, 'mats': [("Boards or Logs", 6)]},
         "Axle": {'btn': 37, 'stack': False, 'mats': [("Boards or Logs", 2)]},
         "Rolling Pin": {'btn': 44, 'stack': False, 'mats': [("Boards or Logs", 5)]},
         "Ramrod": {'btn': 51, 'stack': False, 'mats': [("Boards or Logs", 8)]},
         "Swab": {'btn': 58, 'stack': False, 'mats':
             [("Cloth", 1), ("Boards or Logs", 4)]},
         "Softened Reeds": {'btn': 65, 'stack': False, 'mats':
             [("dry reeds", 1), ("scouring toxin", 2)]},
         "Round Basket": {'btn': 72, 'stack': False, 'mats':
             [("softened reeds", 2), ("shafts", 3)]},
         "Bushel": {'btn': 79, 'stack': False, 'mats':
             [("softened reeds", 2), ("shafts", 3)]},
         "Small Bushel": {'btn': 86, 'stack': False, 'mats':
             [("softened reeds", 1), ("shafts", 2)]},
         "Picnic Basket": {'btn': 93, 'stack': False, 'mats':
             [("softened reeds", 1), ("shafts", 2)]},
         "Winnowing Basket": {'btn': 100, 'stack': False, 'mats':
             [("softened reeds", 2), ("shafts", 3)]},
         "Square Basket": {'btn': 107, 'stack': False, 'mats':
             [("softened reeds", 2), ("shafts", 3)]},
         "Basket": {'btn': 114, 'stack': False, 'mats':
             [("softened reeds", 2), ("shafts", 3)]},
         "Tall Round Basket": {'btn': 121, 'stack': False, 'mats':
             [("softened reeds", 3), ("shafts", 4)]},
         "Small Square Basket": {'btn': 128, 'stack': False, 'mats':
             [("softened reeds", 1), ("shafts", 2)]},
         "Tall Basket": {'btn': 135, 'stack': False, 'mats':
             [("softened reeds", 3), ("shafts", 4)]},
         "Small Round Basket": {'btn': 142, 'stack': False, 'mats':
             [("softened reeds", 1), ("shafts", 2)]},
         "Enchanted Picnic Basket": {'btn': 149, 'stack': False, 'mats':
             [("softened reeds", 2), ("shafts", 3)]}
        },
    ('Tools', 15):
        {"Scissors": {'btn': 2, 'stack': False, 'mats': [("Ingots", 2)]},
         "Mortar And Pestle": {'btn': 9, 'stack': False, 'mats': [("Ingots", 3)]},
         "Scorp": {'btn': 16, 'stack': False, 'mats': [("Ingots", 2)]},
         "Tinker'S Tools": {'btn': 23, 'stack': False, 'mats': [("Ingots", 2)]},
         "Hatchet": {'btn': 30, 'stack': False, 'mats': [("Ingots", 4)]},
         "Draw Knife": {'btn': 37, 'stack': False, 'mats': [("Ingots", 2)]},
         "Sewing Kit": {'btn': 44, 'stack': False, 'mats': [("Ingots", 2)]},
         "Saw": {'btn': 51, 'stack': False, 'mats': [("Ingots", 4)]},
         "Dovetail Saw": {'btn': 58, 'stack': False, 'mats': [("Ingots", 4)]},
         "Froe": {'btn': 65, 'stack': False, 'mats': [("Ingots", 2)]},
         "Shovel": {'btn': 72, 'stack': False, 'mats': [("Ingots", 4)]},
         "Hammer": {'btn': 79, 'stack': False, 'mats': [("Ingots", 1)]},
         "Tongs": {'btn': 86, 'stack': False, 'mats': [("Ingots", 1)]},
         "Smith'S Hammer": {'btn': 93, 'stack': False, 'mats': [("Ingots", 4)]},
         "Sledge Hammer": {'btn': 100, 'stack': False, 'mats': [("Ingots", 4)]},
         "Inshave": {'btn': 107, 'stack': False, 'mats': [("Ingots", 2)]},
         "Pickaxe": {'btn': 114, 'stack': False, 'mats': [("Ingots", 4)]},
         "Lockpick": {'btn': 121, 'stack': False, 'mats': [("Ingots", 1)]},
         "Skillet": {'btn': 128, 'stack': False, 'mats':  [("Ingots", 4)]},
         "Flour Sifter": {'btn': 135, 'stack': False, 'mats': [("Ingots", 3)]},
         "Fletcher'S Tools": {'btn': 142, 'stack': False, 'mats': [("Ingots", 3)]},
         "Mapmaker'S Pen": {'btn': 149, 'stack': False, 'mats': [("Ingots", 1)]},
         "Scribe'S Pen": {'btn': 156, 'stack': False, 'mats': [("Ingots", 1)]},
         "Clippers": {'btn': 163, 'stack': False, 'mats': [("Ingots", 4)]},
         "Metal Container Engraving Tool": {'btn': 170, 'stack': False, 'mats':
             [("Ingots", 4), ("Springs", 1), 
             ("Gears", 2), ("diamond", 1)]},
         "Pitchfork": {'btn': 177, 'stack': False, 'mats': [("Ingots", 4)]}
        },
    ('Parts', 22):
        {"Gears": {'btn': 2, 'stack': False, 'mats': [("Ingots", 2)]},
         "Clock Parts": {'btn': 9, 'stack': False, 'mats': [("Ingots", 1)]},
         "Barrel Tap": {'btn': 16, 'stack': False, 'mats': [("Ingots", 2)]},
         "Springs": {'btn': 23, 'stack': False, 'mats': [("Ingots", 2)]},
         "Sextant Parts": {'btn': 30, 'stack': False, 'mats': [("Ingots", 4)]},
         "Barrel Hoops": {'btn': 37, 'stack': False, 'mats': [("Ingots", 5)]},
         "Hinge": {'btn': 44, 'stack': False, 'mats': [("Ingots", 2)]},
         "Bola Balls": {'btn': 51, 'stack': False, 'mats': [("Ingots", 10)]},
         "Jeweled Filigree": {'btn': 58, 'stack': False, 'mats':
             [("Ingots", 2), ("Star Sapphires", 1), 
             ("Rubies", 1)]}},
    ('Utensils', 29):
        {"Butcher Knife": {'btn': 2, 'stack': False, 'mats': [("Ingots", 2)]},
         "Spoon (Left)": {'btn': 9, 'stack': False, 'mats': [("Ingots", 1)]},
         "Spoon (Right)": {'btn': 16, 'stack': False, 'mats': [("Ingots", 1)]},
         "Plate": {'btn': 23, 'stack': False, 'mats': [("Ingots", 2)]},
         "Fork (Left)": {'btn': 30, 'stack': False, 'mats': [("Ingots", 1)]},
         "Fork (Right)": {'btn': 37, 'stack': False, 'mats': [("Ingots", 1)]},
         "Cleaver": {'btn': 44, 'stack': False, 'mats': [("Ingots", 3)]},
         "Knife (Left)": {'btn': 51, 'stack': False, 'mats': [("Ingots", 1)]},
         "Knife (Right)": {'btn': 58, 'stack': False, 'mats': [("Ingots", 1)]},
         "Goblet": {'btn': 65, 'stack': False, 'mats': [("Ingots", 2)]},
         "Pewter Mug": {'btn': 72, 'stack': False, 'mats': [("Ingots", 2)]},
         "Skinning Knife": {'btn': 79, 'stack': False, 'mats': [("Ingots", 2)]},
         "Gargish Cleaver": {'btn': 86, 'stack': False, 'mats': [("Ingots", 3)]},
         "Gargish Butcher'S Knife": {'btn': 93, 'stack': False, 'mats': [("Ingots", 2)]}
        },
    ('Miscellaneous', 36):
        {"Key Ring": {'btn': 2, 'stack': False, 'mats': [("Ingots", 2)]},
         "Candelabra": {'btn': 9, 'stack': False, 'mats': [("Ingots", 4)]},
         "Scales": {'btn': 16, 'stack': False, 'mats': [("Ingots", 4)]},
         "Iron Key": {'btn': 23, 'stack': False, 'mats': [("Ingots", 3)]},
         "Globe": {'btn': 30, 'stack': False, 'mats': [("Ingots", 4)]},
         "Spyglass": {'btn': 37, 'stack': False, 'mats': [("Ingots", 4)]},
         "Lantern": {'btn': 44, 'stack': False, 'mats': [("Ingots", 2)]},
         "Heating Stand": {'btn': 51, 'stack': False, 'mats': [("Ingots", 4)]},
         "Shoji Lantern": {'btn': 58, 'stack': False, 'mats': 
             [("Ingots", 10), ("Boards or Logs", 5)]},
         "Paper Lantern": {'btn': 65, 'stack': False, 'mats':
             [("Ingots", 10), ("Boards or Logs", 5)]},
         "Round Paper Lantern": {'btn': 72, 'stack': False, 'mats':
             [("Ingots", 10), ("Boards or Logs", 5)]},
         "Wind Chimes": {'btn': 79, 'stack': False, 'mats': [("Ingots", 15)]},
         "Fancy Wind Chimes": {'btn': 86, 'stack': False, 'mats': [("Ingots", 15)]},
         "Ter-Mur Style Candelabra": {'btn': 93, 'stack': False, 'mats': [("Ingots", 4)]},
         "Farspeaker": {'btn': 100, 'stack': False, 'mats':
             [("Ingots", 20), ("emerald", 10), 
             ("ruby", 10), ("copper wire", 1)]},
         "Gorgon Lens": {'btn': 107, 'stack': False, 'mats':
             [("Medusa scales", 2), ("crystal dust", 3)]},
         "A Scale Collar": {'btn': 114, 'stack': False, 'mats':
             [("Medusa scales", 4), ("Scourge", 1)]},
         "Dragon Lamp": {'btn': 121, 'stack': False, 'mats':
             [("Ingots", 8), ("candelabra", 1), 
             ("workable glass", 1)]},
         "Stained Glass Lamp": {'btn': 128, 'stack': False, 'mats':
             [("Ingots", 8), ("candelabra", 1), 
             ("workable glass", 1)]},
         "Tall Double Lamp": {'btn': 135, 'stack': False, 'mats':
             [("Ingots", 8), ("candelabra", 1), 
             ("workable glass", 1)]},
         "Curled Metal Sign Hanger": {'btn': 142, 'stack': False, 'mats': [("Ingots", 8)]},
         "Flourished Metal Sign Hanger": {'btn': 149, 'stack': False, 'mats': [("Ingots", 8)]},
         "Inward Curled Metal Sign Hanger": {'btn': 156, 'stack': False, 'mats': [("Ingots", 8)]},
         "End Curled Metal Sign Hanger": {'btn': 163, 'stack': False, 'mats': [("Ingots", 8)]},
         "Left Metal Door (S In)": {'btn': 170, 'stack': False, 'mats': [("Ingots", 50)]},
         "Right Metal Door (S In)": {'btn': 177, 'stack': False, 'mats': [("Ingots", 50)]},
         "Left Metal Door (E Out)": {'btn': 184, 'stack': False, 'mats': [("Ingots", 50)]},
         "Right Metal Door (E Out)": {'btn': 191, 'stack': False, 'mats': [("Ingots", 50)]},
         "Currency Wall Safe": {'btn': 198, 'stack': False, 'mats': [("Ingots", 20)]},
         "Left Metal Door (E In)": {'btn': 205, 'stack': False, 'mats': [("Ingots", 50)]},
         "Right Metal Door (E In)": {'btn': 212, 'stack': False, 'mats': [("Ingots", 50)]},
         "Left Metal Door (S Out)": {'btn': 219, 'stack': False, 'mats': [("Ingots", 50)]},
         "Right Metal Door (S Out)": {'btn': 226, 'stack': False, 'mats': [("Ingots", 50)]},
         "Kotl Power Core": {'btn': 233, 'stack': False, 'mats':
             [("workable glass", 5), ("copper wire", 5), 
             ("Ingots", 100), ("Moonstone Crystal Shards", 5)]},
         "Weathered Bronze Globe Sculpture": {'btn': 240, 'stack': False, 'mats': [("bronze ingots: ", 200)]},
         "Weathered Bronze Man On A Bench Sculpture": {'btn': 247, 'stack': False, 'mats': [("bronze ingots: ", 200)]},
         "Weathered Bronze Fairy Sculpture": {'btn': 254, 'stack': False, 'mats': [("bronze ingots: ", 200)]},
         "Weathered Bronze Archer Sculpture": {'btn': 261, 'stack': False, 'mats': [("bronze ingots: ", 200)]},
         "Barbed Whip": {'btn': 268, 'stack': False, 'mats':
             [("Ingots", 5), ("Leather or Hides", 10)]},
         "Spiked Whip": {'btn': 275, 'stack': False, 'mats':
             [("Ingots", 5), ("Leather or Hides", 10)]},
         "Bladed Whip": {'btn': 282, 'stack': False, 'mats':
             [("Ingots", 5), ("Leather or Hides", 10)]}
        },
    ('Assemblies', 43):
        {"Axle With Gears": {'btn': 2, 'stack': False, 'mats':
             [("Axles", 1), ("Gears", 1)]},
         "Clock Parts": {'btn': 9, 'stack': False, 'mats':
             [("Axles with Gears", 1), ("Springs", 1)]},
         "Sextant Parts": {'btn': 16, 'stack': False, 'mats':
             [("Axles with Gears", 1), ("Hinges", 1)]},
         "Clock (Right)": {'btn': 23, 'stack': False, 'mats':
             [("Clock Frames", 1), ("Clock Parts", 1)]},
         "Clock (Left)": {'btn': 30, 'stack': False, 'mats':
             [("Clock Frames", 1), ("Clock Parts", 1)]},
         "Sextant": {'btn': 37, 'stack': False, 'mats': [("Sextant Parts", 1)]},
         "Bola": {'btn': 44, 'stack': False, 'mats':
             [("Bola Balls", 4), ("Leather or Hides", 3)]},
         "Potion Keg": {'btn': 51, 'stack': False, 'mats':
             [("Empty Kegs", 1), ("Empty Bottles", 10), 
             ("Barrel Lids", 1), ("Keg Taps", 1)]},
         "Leather Wolf Assembly": {'btn': 58, 'stack': False, 'mats':
             [("Clockwork Assembly", 1), ("power crystal", 1), 
             ("Void Essence", 1)]},
         "Clockwork Scorpion Assembly": {'btn': 65, 'stack': False, 'mats':
             [("Clockwork Assembly", 1), ("power crystal", 1), 
             ("Void Essence", 2)]},
         "Vollem Assembly": {'btn': 72, 'stack': False, 'mats':
             [("Clockwork Assembly", 1), ("power crystal", 1), 
             ("Void Essence", 3)]},
         "Hitching Rope": {'btn': 79, 'stack': False, 'mats':
             [("rope", 1), ("Resolve's Bridle", 1)]},
         "Hitching Post (Replica)": {'btn': 86, 'stack': False, 'mats':
             [("Ingots", 50), ("animal pheromone", 1), 
             ("hitching rope", 2), ("Phillip's Wooden Steed", 1)]},
         "Arcanic Rune Stone": {'btn': 93, 'stack': False, 'mats':
             [("Crystal Shards", 1), ("power crystal", 5)]},
         "Void Orb": {'btn': 100, 'stack': False, 'mats':
             [("Dark Sapphire", 1), ("Black Pearl", 50)]},
         "Advanced Training Dummy (South)": {'btn': 107, 'stack': False, 'mats':
             [("training dummy (south)", 1), ("platemail tunic", 1), 
             ("close helmet", 1), ("broadsword", 1)]},
         "Advanced Training Dummy (East)": {'btn': 114, 'stack': False, 'mats':
             [("training dummy (east)", 1), ("platemail tunic", 1), 
             ("close helmet", 1), ("broadsword", 1)]},
         "Distillery (South)": {'btn': 121, 'stack': False, 'mats':
             [("metal keg", 2), ("heating stand", 4), 
             ("copper wire", 1)]},
         "Distillery (East)": {'btn': 128, 'stack': False, 'mats':
             [("metal keg", 2), ("heating stand", 4), 
             ("copper wire", 1)]},
         "Kotl Automaton": {'btn': 135, 'stack': False, 'mats':
             [("Ingots", 300), ("Automaton Actuator", 1), 
             ("Stasis Chamber Power Core", 1), ("Inoperative Automaton Head", 1)]},
         "Telescope": {'btn': 142, 'stack': False, 'mats':
             [("Ingots", 25), ("workable glass", 1), 
             ("Sextant Parts", 1)]},
         "Oracle Of The Sea": {'btn': 149, 'stack': False, 'mats':
             [("Ingots", 3), ("workable glass", 2), 
             ("ocean sapphire", 3)]}
        },
    ('Traps', 50):
        {"Dart Trap": {'btn': 2, 'stack': False, 'mats':
             [("Ingots", 1), ("Crossbow Bolts", 1)]},
         "Poison Trap": {'btn': 9, 'stack': False, 'mats':
             [("Ingots", 1), ("Green Potions", 1)]},
         "Explosion Trap": {'btn': 16, 'stack': False, 'mats':
             [("Ingots", 1), ("Purple Potions", 1)]}
        },
    ('Magic Jewelry', 57):
        {"Brilliant Amber Bracelet": {'btn': 2, 'stack': False, 'mats':
             [("Ingots", 5), ("amber", 20), 
             ("Brilliant Amber", 10)]},
         "Fire Ruby Bracelet": {'btn': 9, 'stack': False, 'mats':
             [("Ingots", 5), ("ruby", 20), 
             ("Fire Ruby", 10)]},
         "Dark Sapphire Bracelet": {'btn': 16, 'stack': False, 'mats':
             [("Ingots", 5), ("sapphire", 20), 
             ("Dark Sapphire", 10)]},
         "White Pearl Bracelet": {'btn': 23, 'stack': False, 'mats':
             [("Ingots", 5), ("tourmaline", 20), 
             ("White Pearl", 10)]},
         "Ecru Citrine Ring": {'btn': 30, 'stack': False, 'mats':
             [("Ingots", 5), ("citrine", 20), 
             ("Ecru Citrine", 10)]},
         "Blue Diamond Ring": {'btn': 37, 'stack': False, 'mats':
             [("Ingots", 5), ("diamond", 20), 
             ("Blue Diamond", 10)]},
         "Perfect Emerald Ring": {'btn': 44, 'stack': False, 'mats':
             [("Ingots", 5), ("emerald", 20), 
             ("Perfect Emerald", 10)]},
         "Turquoise Ring": {'btn': 51, 'stack': False, 'mats':
             [("Ingots", 5), ("amethyst", 20), 
             ("Turquoise", 10)]},
         "Resilient Bracer": {'btn': 58, 'stack': False, 'mats':
             [("Ingots", 2), ("Captured Essence", 1), 
             ("Blue Diamond", 10), ("diamond", 50)]},
         "Essence Of Battle": {'btn': 65, 'stack': False, 'mats':
             [("Ingots", 2), ("Captured Essence", 1), 
             ("Fire Ruby", 10), ("ruby", 50)]},
         "Pendant Of The Magi": {'btn': 72, 'stack': False, 'mats':
             [("Ingots", 2), ("Eye of the Travesty", 1), 
             ("White Pearl", 5), ("star-saphire", 50)]},
         "Dr. Spector'S Lenses": {'btn': 79, 'stack': False, 'mats':
             [("Ingots", 20), ("Black Moonstone", 1), 
             ("Hat of the Magi", 1)]},
         "Bracelet Of Primal Consumption": {'btn': 86, 'stack': False, 'mats':
             [("Ingots", 3), ("Ring of the Elements", 1), 
             ("Blood of the Dark Father", 5), ("White Pearl", 4)]}
        }
    }

material_info = {
    "Ingots": {
        'Iron': {'btn': 6, 'id': [0x1BF2], 'color': 0x0000},
        'Dull Copper': {'btn': 13, 'id': [0x1BF2], 'color': 0x0973},
        'Shadow Iron': {'btn': 20, 'id': [0x1BF2], 'color': 0x0966},
        'Copper': {'btn': 27, 'id': [0x1BF2], 'color': 0x096D},
        'Bronze': {'btn': 34, 'id': [0x1BF2], 'color': 0x0972},
        'Gold': {'btn': 41, 'id': [0x1BF2], 'color': 0x08A5},
        'Agapite': {'btn': 48, 'id': [0x1BF2], 'color': 0x0979},
        'Verite': {'btn': 55, 'id': [0x1BF2], 'color': 0x089F},
        'Valorite': {'btn': 62, 'id': [0x1BF2], 'color': 0x08AB}
    },
    "Boards or Logs": {
        'Wood': {'btn': 6, 'id': [0x1BD7, 0x1BDD], 'color': 0x0000},
        'Oak': {'btn': 13, 'id': [0x1BD7, 0x1BDD], 'color': 0x07DA},
        'Ash': {'btn': 20, 'id': [0x1BD7, 0x1BDD], 'color': 0x04A7},
        'Yew': {'btn': 27, 'id': [0x1BD7, 0x1BDD], 'color': 0x04A8},
        'Heartwood': {'btn': 34, 'id': [0x1BD7, 0x1BDD], 'color': 0x04A9},
        'Bloodwood': {'btn': 41, 'id': [0x1BD7, 0x1BDD], 'color': 0x04AA},
        'Frostwood': {'btn': 48, 'id': [0x1BD7, 0x1BDD], 'color': 0x047F}
    },
    "Leather or Hides": {
        'Leather/Hides': {'btn': 6, 'id': [0x1081, 0x1079], 'color': 0x0000},
        'Spined Hides': {'btn': 13, 'id': [0x1081, 0x1079], 'color': 0x08AC},
        'Horned Hides': {'btn': 20, 'id': [0x1081, 0x1079], 'color': 0x0845},
        'Barbed Hides': {'btn': 27, 'id': [0x1081, 0x1079], 'color': 0x0851}
    }
}

skill_info = {
    "Alchemy": {
        'gump': alchemy_gump, 'bod_color': 0x09C9, 'tools':
            {'mortar and pestle': 0x0E9B}},
    "Blacksmithing": {
        'gump': blacksmithing_gump, 'material': material_info['Ingots'], 'bod_color': 0x044E, 'tools':
            {'smith hammer': 0x13E3, 'sledge hammer': 0x0FB5, 'tongs': 0x0FBB}},
    "Bowcraft and Fletching": {
        'gump': bowcraft_gump, 'bod_color': 0x0591, 'tools':
            {'fletcher tools': 0x1022}},
    "Carpentry": {
        'gump': carpentry_gump, 'material': material_info['Boards or Logs'], 'bod_color': 0x05E8, 'tools':
            {'saw': 0x1034, 'draw_knife': 0x10E4, 'froe': 0x10E5, 'inshave': 0x10E6, 'scorp': 0x10E7,
             'dovetail_saw': 0x1028, 'hammer': 0x102A}},
    "Cartography": {
        'gump': cartography_gump, 'bod_color': 0x0000, 'tools':
            {"mapmaker's pen": 0x0FBF}},
    "Cooking": {
        'gump': cooking_gump, 'bod_color': 0x0491, 'tools':
            {'skillet': 0x097F, 'flour sifter': 0x103E, 'rolling pin': 0x1043}},
    "Inscription": {
        'gump': inscription_gump, 'bod_color': 0x0A26, 'tools':
            {"scribe's pen": 0x0FBF}},
    "Tailoring": {
        'gump': tailoring_gump, 'material': material_info['Leather or Hides'], 'bod_color': 0x0483, 'tools':
            {'sewing kit': 0x0F9D}},
    "Tinkering": {
        'gump': tinkering_gump, 'material': material_info['Ingots'], 'bod_color': 0x0455, 'tools':
            {'tinker tools': 0x1EBC, 'tool kit': 0x1EB8}}}


def get_first(item_list):
    if item_list:
        return item_list[0]
    return None


def dist(pos1, pos2=Player):
    pos = [pos1, pos2]
    for i, _ in enumerate(pos):
        if type(pos[i]) is not dict:
            try:
                _ = pos[i].Serial
            except Exception:
                pos[i] = Items.FindBySerial(pos[i])
        try:
            if pos[i].Serial == Player.Backpack.Serial:
                pos[i] = Player
            if pos[i].Container > 0:
                pos[i] = pos[i].Container
                return dist(pos[0], pos[1])
        except Exception:
            pass
        if type(pos[i]) is not dict:
            try:
                pos[i] = {'X': pos[i].Position.X, 'Y': pos[i].Position.Y, 'Map': pos[i].Map}
            except Exception:
                pos[i] = {'X': pos[i].Position.X, 'Y': pos[i].Position.Y, 'Map': Player.Map}
    try:
        if pos[0]['Map'] != pos[1]['Map']:
            return 10000
    except Exception:
        pass
    return max(abs(pos[0]['X'] - pos[1]['X']), abs(pos[0]['Y'] - pos[1]['Y']))


def find_items_list(item_id_list, container, color=-1, recursive=True):
    found_items = []
    try:
        _ = container.Serial
    except Exception:
        container = Items.FindBySerial(container)
    try:
        for item_id in item_id_list:
            while True:
                item = Items.FindByID(item_id, color, container.Serial, recursive, True)
                if not item:
                    break
                found_items.append(item)
                Misc.IgnoreObject(item)
    except Exception:
        for item_name in item_id_list:
            for item in container.Contains:
                try:
                    idx = item.Name.index(" ") + 1
                except Exception:
                    idx = 0
                alt_name = item.Name[idx:].lower()
                if item_name.lower() in [item.Name.lower(), alt_name]:
                    if color > 0:
                        if int(color) == int(item.Hue):
                            found_items.append(item)
                            Misc.IgnoreObject(item)
                    else:
                        found_items.append(item)
                        Misc.IgnoreObject(item)
                if item.IsContainer and recursive:
                    found_items.extend(find_items_list(item_id_list, item, color, True))
    Misc.ClearIgnore()
    return found_items


def get_root_containers_from_id(item_id_list, color=-1):
    found_countainers_serial = []
    for item in find_items_list(item_id_list, Player.Backpack, color, True):
        if dot_container(item).Serial not in found_countainers_serial:
            found_countainers_serial.append(dot_container(item).Serial)
    return [Items.FindBySerial(container_serial) for container_serial in found_countainers_serial]


def get_items_by_filter(item_id_list=None, name=None, radius=2, ground=False, only_containers=False):
    id_list = []
    selected_list = []
    item = None

    item_filter = Items.Filter()
    if ground:
        item_filter.OnGround = 1
        item_filter.RangeMax = radius
    if item_id_list:
        for item_id in item_id_list:
            item = Items.FindBySerial(item_id)
            if item and item.ItemID not in id_list:
                id_list.append(item.ItemID)
        if not id_list:
            id_list = item_id_list
        item_filter.Graphics = List[Int32](id_list)
    if name:
        item_filter.Name = name
    if only_containers:
        item_filter.IsContainer = 1
    item_list = Items.ApplyFilter(item_filter)
    if item_list:
        for it in item_list:
            if dist(it) <= radius:
                if item:
                    if it.Serial in item_id_list:
                        selected_list.append(it)
                else:
                    selected_list.append(it)
    return selected_list


def dot_container(search_item):
    if type(search_item) is Player:
        return None
    ground_containers = get_items_by_filter(None, None, 2, True, True)
    for container in [Player.Backpack] + ground_containers:
        cont = in_container(search_item, container, True)
        if cont:
            return cont
    return None


def in_container(item, container, recursive=False):
    for i in container.Contains:
        if i.Serial == item.Serial:
            return container
        if recursive and i.IsContainer:
            cont = in_container(item, i, True)
            if cont:
                return cont
    return None


def throw_items(item_list, container):
    try:
        c = container.Serial
    except Exception:
        container = Items.FindBySerial(container)
    for item in item_list:
        try:
            c = item.Serial
        except Exception:
            item = Items.FindBySerial(item)
        while True:
            if in_container(item, container):
                break
            Items.Move(item, container, 0)
            Misc.Pause(2000)


def get_shared_item(name):
    return Items.FindBySerial(Misc.ReadSharedValue(name))


def get_shared(name):
    return int(Misc.ReadSharedValue(name))


def set_shared_item(name, _msg):
    Misc.SendMessage(_msg, 68)
    item = Items.FindBySerial(Target.PromptTarget(""))
    if item:
        Misc.SetSharedValue(name, item.Serial)
    return item


def set_shared_gump(name, gump_num):
    if gump_num != get_shared(name):
        Misc.SetSharedValue(name, gump_num)
    return gump_num


def get_and_set_shared_container(name, var_name):
    container = get_shared_item(var_name)
    while not container or not container.IsContainer or container == Player.Backpack:
        container = set_shared_item(var_name, "Target " + name +
                                    ".\r\n (Or ESC to craft items without one.)")
        if not container or container.IsContainer:
            break
        error("Is that a container?")
    return container


def in_cap(skill):
    if Player.GetSkillValue(skill) >= Player.GetSkillCap(skill):
        Misc.SendMessage(skill + " is in it's cap. Finishing.", 68)
        return True
    return False


def error(text, skill='', item_name='', finish=True):
    msg = ""
    if skill:
        Misc.SendMessage("\r\n\r\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",
                         skill_info[skill]['bod_color'])
        msg = msg + skill
    if item_name:
        msg = msg + " | item: " + item_name
    msg = msg + "\r\n" + text + "\r\n"
    if finish:
        msg = msg + "FINISHING." + "\r\n\r\n"
    Misc.SendMessage(msg, 28)
    if finish:
        sys.exit()


def get_containers():
    global trash_barrel
    for skill in skill_info:
        if Items.FindByID(0x2258, skill_info[skill]['bod_color'], Player.Backpack.Serial, False, True):
            if skill not in ["Blacksmithing", "Tailoring", "Tinkering"]:
                trash_barrel = get_and_set_shared_container("a trash barrel", "trash_barrel")
                break


def search_button(gump, item_name):
    for menu_button in gump:
        if menu_button == 'categories':
            continue
        for gump_item in gump[menu_button]:
            if item_name.title() in [gump_item, gump_item.replace("(", "").replace(")", "")]:
                return menu_button[1], gump[menu_button][gump_item]
    for menu_button in gump:
        if menu_button == 'categories':
            continue
        for gump_item in gump[menu_button]:
            if item_name.title() in gump_item or item_name.title() in gump_item.replace("(", "").replace(")", ""):
                return menu_button[1], gump[menu_button][gump_item]
    error("Failed to retrieve data. Item name didn't match.")


def meditate():
    while Player.Mana != Player.ManaMax:
        Player.UseSkill("Meditation")
        Misc.Pause(1000)
        while Player.BuffsExist('Meditation') and Player.Mana != Player.ManaMax:
            Misc.Pause(1000)


def check_craft_messages():
    msg_list = [("You failed ", 40), ("You create an exceptional", 68), ("You create the", 48),
                ("You do not have ", 28), ("You must be near ", 28)]
    for msg in msg_list:
        for line in Gumps.LastGumpGetLineList():
            if msg[0] in line:
                if msg[1] != 28:
                    Misc.SendMessage(line, msg[1])
                return line
    return ''


def wait_craft_gump(gump_num, timeout):
    for _ in range(int(timeout / 100)):
        if Journal.Search("You have worn out"):
            Journal.Clear()
            return "worn"
        if Journal.Search("You must wait to perform another action."):
            Misc.Pause(2000)
            Journal.Clear()
            return "wait"
        if Gumps.WaitForGump(gump_num, 100) > 0:
            return "success"
    return "timeout"


def get_gump_num(text_list):
    for _ in range(100):
        for text in text_list:
            if Gumps.LastGumpTextExist(text):
                return Gumps.CurrentGump()
        Misc.Pause(100)
        if Journal.Search("You must wait to perform another action."):
            Misc.Pause(2000)
            Journal.Clear()
            return 0
    return 0


def get_bod_resources(bod):
    _, item_data = search_button(skill_info[bod.skill]['gump'], bod.item['name'])
    grabbing_results = []

    common_names = {"Cloth": ["Cloth", "Cut Cloth"],
                    "Yards of Cloth": ["Cloth", "Cut Cloth"],
                    "Blank Maps or Scrolls": ["Blank Scroll", "Blank Map"],
                    "Sea Serpent or Dragon Scales": ["Sea Serpent Scales", "Dragon Scales"]}
    for resource in item_data['mats']:
        resource_data = {}
        for name_list in material_info:
            if resource[0] == name_list:
                resource_data = material_info[name_list][bod.material]
                break
        if not resource_data:
            for name in common_names:
                if resource[0] == name:
                    resource_data = {'id': common_names[name], 'color': -1}
                    break
        if not resource_data:
            resource_data = {'id': [resource[0]], 'color': -1}
        grabbing_results.append(get_resource(resource_data['id'], resource_data['color'],
                                             resource[1], bod.to_make_quantity(), item_data['stack']))
    return False not in grabbing_results


def get_resource(resource_id_list, color=-1, resource_needed=1, to_make_amount=1, stack=False):
    total_amount_found = 0
    for resource_id in resource_id_list:
        amount_found = 0
        escape = False
        container_list = [Player.Backpack] + get_items_by_filter(None, None, 2, True, True)
        for _ in range(5):
            for container in container_list:
                resource = get_first(find_items_list([resource_id], container, color, True))
                if not resource and resource_id is str:
                    resource = get_first(find_items_list([resource_id.rstrip(resource_id[-1])],
                                                         container, color, True))
                if resource:
                    if container.Serial != Player.Backpack.Serial:
                        Items.Move(resource, Player.Backpack,
                                   get_quantity_to_grab(resource, resource_needed, to_make_amount, amount_found, stack))
                        Misc.Pause(600)
                        break
                    else:
                        amount_found = resource.Amount
                        escape = get_quantity_to_grab(resource, resource_needed, to_make_amount, amount_found, stack) <= 0
                        if escape:
                            break
            if escape:
                break
        total_amount_found += amount_found
        if escape:
            break
    return total_amount_found >= resource_needed


def get_quantity_to_grab(resource, resource_needed=1, to_make_amount=1, amount_found=0, stack=False):
    weight_available = (Player.MaxWeight - 70) - Player.Weight
    weight_per_piece = resource.Weight/resource.Amount
    if stack:
        mult = 1
    else:
        mult = 1.5
    return min(int(weight_available/weight_per_piece), int(mult * resource_needed * to_make_amount)) - amount_found


def trash(item_id_list, color=-1, recursive=True):
    if item_id_list:
        if trash_barrel and get_items_by_filter([trash_barrel]):
            Misc.SendMessage("Throwing items away.")
            throw_items(find_items_list(item_id_list, Player.Backpack, color, recursive), trash_barrel)
        return True
    return False


def recycle(skill, item_name):
    def to_recycle():
        return [i.Serial for i in find_items_list([item_name], Player.Backpack)
                if "exceptional" not in str(i.Properties).lower()]
    if not to_recycle():
        return False
    tool = get_tool("Blacksmithing")
    tool_container = dot_container(tool)
    salvage_bag = get_first(find_items_list(["Salvage Bag"], Player.Backpack))
    if salvage_bag and skill in ["Blacksmithing", "Tailoring"]:
        throw_items([tool.Serial], Player.Backpack)
        Misc.SendMessage("\r\nSalvaging remaining pieces\r\n", 78)
        throw_items(to_recycle(), salvage_bag)
        Misc.WaitForContext(salvage_bag.Serial, 10000)
        if skill == "Blacksmithing":
            Misc.ContextReply(salvage_bag.Serial, 0)
        else:
            Misc.ContextReply(salvage_bag.Serial, 1)
        Misc.Pause(1000)
    scissors = get_first(find_items_list([0x0F9F], Player.Backpack))
    if to_recycle() and ((tool and skill == "Blacksmithing") or (scissors and skill == "Tailoring")):
        Misc.SendMessage("\r\nRecycling remaining pieces\r\n", 78)
        while True:
            if not to_recycle():
                break
            for item in to_recycle():
                if tool and skill == "Blacksmithing":
                    if open_craft_gump(skill):
                        if Gumps.WaitForGump(crafting_gump_id, 100) > 0:
                            answer_craft_gump(('Smelt Item', 27)[1])
                            Target.WaitForTarget(5000, False)
                            Target.TargetExecute(item)
                            Gumps.WaitForGump(crafting_gump_id, 8000)
                else:
                    Items.UseItem(scissors)
                    Target.WaitForTarget(5000, False)
                    Target.TargetExecute(item)
                    Misc.Pause(600)
            Gumps.CloseGump(crafting_gump_id)
    throw_items([tool], tool_container)
    trash(to_recycle())


def get_tool(skill):
    global to_container
    container_list = []
    salvage_bag = get_first(find_items_list(["Salvage Bag"], Player.Backpack))
    tool_cod_list = skill_info[skill]['tools'].values()
    if skill in ["Cartography", "Inscription"]:
        tool_cod_list = skill_info[skill]['tools'].keys()
    if salvage_bag and skill in ["Blacksmithing", "Tailoring", "Tinkering"]:
        container_list.append(salvage_bag.Serial)
        to_container = salvage_bag.Serial
    container_list.append(Player.Backpack.Serial)
    container_list.extend([item.Serial for item in get_items_by_filter(None, None, 2, True, True)])
    for _ in range(10):
        for i, container in enumerate(container_list):
            tool_list = find_items_list(tool_cod_list, container, -1, True)
            # Filter out special tools
            filtered_tools = [tool for tool in tool_list if not is_special_tool(tool)]
            if filtered_tools:
                if i > 0:
                    Items.Move(get_first(filtered_tools), to_container, 1)
                    Misc.Pause(600)
                    break
                else:
                    tool = get_first(filtered_tools)
                    to_container = dot_container(tool)
                    return tool
	 # Error reporting if no tool is found
    error_message = f"Error: No tool found for skill '{skill}' after searching all containers and retries."
    Misc.SendMessage(error_message, 33)  
    
	return None

def is_special_tool(tool):
    # Logic to identify special tools
    # Example: Check tool name or specific properties
    special_tool_names = ["Runic Hammer"]  # Add names of special tools to ignore
    if tool.Name in special_tool_names:
        return True
    # Check if "runic" is in the item's name (case-insensitive)
    if "runic" in tool.Name.lower():
        return True
    # Example: Check tool properties or other criteria
    #if "exceptional" in str(tool.Properties).lower():
    #    return True
    return False


def open_craft_gump(skill):
    global crafting_gump_id
    if crafting_gump_id > 0 and Gumps.WaitForGump(crafting_gump_id, 100) > 0:
        return True
    Journal.Clear()
    tool = get_tool(skill)
    if tool:
        while True:
            Items.UseItem(tool)
            crafting_gump_new_id = get_gump_num([skill.upper() + " MENU"])
            if crafting_gump_new_id > 0:
                crafting_gump_id = set_shared_gump("crafting_gump_id", crafting_gump_new_id)
                return True
    return False


def answer_craft_gump(menu_button, item_button=None):
    if crafting_gump_id > 0 and Gumps.WaitForGump(crafting_gump_id, 100) > 0:
        Gumps.SendAction(crafting_gump_id, menu_button)
        if item_button:
            Gumps.WaitForGump(crafting_gump_id, 4000)
            Gumps.SendAction(crafting_gump_id, item_button)
        return True
    return False


def make_one_item(skill, menu_button, item_button):
    if open_craft_gump(skill):
        if answer_craft_gump(menu_button, item_button):
            result = wait_craft_gump(crafting_gump_id, 8000)
            if result == "success":
                return check_craft_messages()
            else:
                return result
    else:
        return "OUT OF TOOLS."
    return "timeout"


def make_item(item_name, skill, quantity=1, exceptional=False):
    global crafting_gump_id
    menu_button, item_data = search_button(skill_info[skill]['gump'], item_name)
    while not Player.IsGhost:
        if Player.Weight >= Player.MaxWeight - 50:
            Misc.SendMessage("Dealing with overweight.", 78)
            return ''
        if quantity <= 0:
            Gumps.CloseGump(crafting_gump_id)
            return ''
        if skill == "INSCRIPTION" and Player.Mana <= 40:
            meditate()
        craft_result = make_one_item(skill, menu_button, item_data['btn'])
        if "You must be near " in craft_result or "You do not have " in craft_result:
            Gumps.CloseGump(crafting_gump_id)
            return craft_result
        if "create" in craft_result:
            if exceptional:
                if "exceptional" in craft_result:
                    quantity -= 1
            else:
                quantity -= 1
        if craft_result == "worn":
            quantity -= 1
        if craft_result == "timeout" or item_data['stack']:
            return ''


def return_gump_to_default(skill, last_material):
    if last_material:
        if skill in ["Blacksmithing", "Tinkering"] and last_material != "Iron":
            choose_gump_material(skill, "Iron")
        if skill == "Tailoring" and last_material != "Leather/Hides":
            choose_gump_material(skill, "Leather/Hides")
        if skill in ["Carpentry", "Bowcraft and Fletching"] and last_material != "Wood":
            choose_gump_material(skill, "Wood")


def choose_gump_material(skill, material_name):
    if not material_name:
        return ""
    global crafting_gump_id
    try:
        material_data = skill_info[skill]['material'][material_name]
        if open_craft_gump(skill):
            if "|" + material_name.upper() not in "|".join(Gumps.LastGumpGetLineList()):
                answer_craft_gump(7, material_data['btn'])
                Gumps.WaitForGump(crafting_gump_id, 4000)
            else:
                Gumps.CloseGump(crafting_gump_id)
                return material_name
        else:
            return "OUT OF TOOLS."
    except Exception:
        return ""


def combine_bods(lbods, sbods):
    if lbods:
        sbod_item_list = [sbod.item for sbod in sbods]
        for lbod in lbods:
            ready = True
            for item in lbod.items:
                if (item['done_amount'] == 0 and
                        {'name': item['name'], 'done_amount': lbod.total_amount} not in sbod_item_list):
                    ready = False
                    break
            if ready:
                Misc.ClearIgnore()
                lbod.use()
                lbod.filled = True
                lbod.finished()


def make_bod():
    get_containers()
    for skill in skill_info:
        sbods = lbods = []
        material = problem = ''
        while not Player.IsGhost:
            bod = Bod(skill, Items.FindByID(0x2258, skill_info[skill]['bod_color'], Player.Backpack.Serial,
                                            True, True))
            if not bod.serial or problem == "OUT OF TOOLS.":
                return_gump_to_default(skill, material)
                break
            problem = ''
            if bod.type == "large":
                lbods.append(bod)
                continue
            if bod.finished():
                sbods.append(bod)
                continue
            bod.start()
            material = choose_gump_material(skill, bod.material)
            while not Player.IsGhost:
                bod.use()
                Target.Cancel()
                if "You do not have " in problem:
                    recycle(skill, bod.item['name'])
                    if get_bod_resources(bod):
                        problem = ''
                if problem:
                    error(problem, skill, bod.item['name'], False)
                    Misc.IgnoreObject(bod.serial)
                    break
                bod.refresh()
                if bod.finished():
                    sbods.append(bod)
                    break
                problem = make_item(bod.item['name'], skill, bod.to_make_quantity(), bod.exceptional)
        combine_bods(lbods, sbods)
    Gumps.CloseGump(crafting_gump_id)
    Gumps.CloseGump(get_gump_num(["A bulk order", "A large bulk order"]))


crafting_gump_id = get_shared("crafting_gump_id")
trash_barrel = get_shared_item("trash_barrel")
to_container = Player.Backpack.Serial
Misc.ClearIgnore()
make_bod()