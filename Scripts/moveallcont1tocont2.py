container = Target.PromptTarget('Source container')
containerItem = Items.FindBySerial(container)
container2 = Target.PromptTarget('Target Container')
containerItem2 = Items.FindBySerial(container2)


for item in containerItem.Contains:
    Misc.SendMessage(item)
    Items.Move(item, container2, 0)
    Misc.Pause(600)