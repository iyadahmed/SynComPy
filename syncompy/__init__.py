from comtypes import client
client.GetModule("SynCtrl.dll")
import comtypes.gen.SYNCTRLLib as synctrl
from . import synerror
import time


class SynDevice:
    def __init__(self, connection_type= synctrl.SE_ConnectionAny, device_type= synctrl.SE_DeviceAny):
        self._synapi = client.CreateObject("SynCtrl.SynAPICtrl")
        if self._synapi.Initialize() == synerror.SYNE_FAIL:
            raise RuntimeError("The Synaptics kernel-mode driver is not present on "
                               "the target machine, or the installed driver version "
                               "is less than that necessary to support the Synaptics COM API.")
        self._syndev = client.CreateObject("SynCtrl.SynDeviceCtrl")
        self._synpac = client.CreateObject("SynCtrl.SynPacketCtrl")

        # TODO: catch COMError
        lHandle = self._synapi.FindDevice(connection_type, device_type, -1)
        if lHandle < 0:
            raise RuntimeError("No appropriate device found.")
        elif lHandle == synerror.SYNE_FAIL:
            raise RuntimeError("The ISynAPICtrl object has not been initialized properly.")

        if self._syndev.Select(lHandle) == synerror.SYNE_HANDLE: 
            raise ValueError("The requested lHandle does not correspond to any known device.")

        self._connection = client.GetEvents(self._syndev, self)
        if self._syndev.Activate() == synerror.SYNE_FAIL:
            raise RuntimeError("The Synaptics kernel-mode driver is not present on the target machine.")

    def _ISynDeviceCtrlEvents_OnPacket(self, this):
        self._syndev.LoadPacket(self._synpac)
        self.on_packet(self._synpac)

    def on_packet(self, packet):
        pass
    
    # DO NOT EVER DO THIS, TODO: make a context manager instead
    def __del__(self):
        self._syndev.Deactivate()
        self._connection.disconnect()
        time.sleep(.1)
