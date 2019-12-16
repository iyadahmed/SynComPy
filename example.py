from syncompy import SynDevice, SynComDefs as defs
#packet_handler to print xy position of finger on touchpad
def eventHandler(event):
    x = event.X
    y = event.Y
    if event.TouchEnd: print(f"End {x} {y}")
    elif event.TouchBegin: print(f"Begin {x} {y}")
    elif event.TouchInProgress: print(f"Progress {x} {y}")
#init syncomapi
mypad = SynDevice()
mypad.Find()
#Connect to event handler
mypad.Select(handler = eventHandler)
print(mypad.GetProperty(defs.SP_ModelString, string = True))
