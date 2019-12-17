from syncompy import SynDevice, syncomdefs as defs


#Simple event handler to print x,y position of finger throughout a three-stage touch
def eventHandler(event):
    x = event.X
    y = event.Y
    
    if event.TouchEnd: print(f"End {x} {y}")
    elif event.TouchBegin: print(f"Begin {x} {y}")
    elif event.TouchInProgress: print(f"Progress {x} {y}")
    
#Create new SynDevice instance
mypad = SynDevice()

#Find query handle for a touchpad on any known port
query_handle = mypad.find(eConnectionType = defs.SE_ConnectionAny, eDeviceType = defs.SE_DeviceTouchPad, lLastHandle = -1)

#Select the touchpad
mypad.select(0)

#Bind all events to the event handler
mypad.bind_all(eventHandler)
