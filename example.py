from syncompy import syn
#packet_handler to print xy position of finger on touchpad
def packet_handler(packet):
    print(packet.X, packet.Y)

#init syncomapi
mypad = syn()
#connect to first available device and catch its events
mypad.Connect(0)
#set event handler for touch begin and end to packet_handler
mypad.trigger(begin = packet_handler, end = packet_handler)
