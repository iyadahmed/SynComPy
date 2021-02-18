from syncompy import SynDevice


# Subclass SynDevice, override on_packet to get info
class Touchpad(SynDevice):
    def on_packet(self, packet):
        print(packet.X, packet.Y)

tpad = Touchpad()
