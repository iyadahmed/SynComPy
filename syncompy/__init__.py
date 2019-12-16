# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 16:14:24 2019

@author: Iyad
"""
import time
import comtypes.client as client
from .SynComDefs import *
from .hfuncs import *
class Event(object):
    def __init__(self):
        self._touchbegin = False
        self._touchend = False
        self._touchinprogress = False
        self._pac = None
    @property
    def TouchBegin(self):
        return self._touchbegin
    @property
    def TouchEnd(self):
        return self._touchend
    @property
    def TouchInProgress(self):
        return self._touchinprogress
    @property
    def X(self):
        return self._pac.X
    @property
    def Y(self):
        return self._pac.Y
    def __del__(self):
        self._pac = None
        self.begin = None
        self.end = None
        self.inprogess = None
class EventSink(object):
    def __init__(self, syndev, synpac):
        self._syndev = syndev
        self._synpac = synpac
        #Create a new boolean "switch", becomes true when value is changed from false to true and vice versa
        self._state = bswitch(0)
        #Create new event
        self._event = Event()
    #Empty handler, '''Patch this, use pac variable to access Packet data \n example: pac.GetLongProperty(SP_X)'''
    def _onpac(self , event):    
        pass
    #pre-handler, calls necessary code every packet
    def _ISynDeviceCtrlEvents_OnPacket(self, this):
        #Needs to be called on each packet
        self._syndev.LoadPacket(self._synpac) #Load packet into self._synpac
        #Optional but provides TouchBegin-End events
        prestate = self._synpac.FingerState & SF_FingerPresent
        state = self._state.update(prestate)
        #Set event Event packet to the just loaded packet
        self._event._pac = self._synpac
        #TouchBegin-progress-end detection
        if  state == 1:
            self._event._touchbegin = True #touch begin
        elif state == -1:
            self._event._touchend = True #touchend
        elif prestate:
            self._event._touchinprogress = True #touch in progress, cap touchprogress state using prestate
        #Call handler
        self._onpac(self._event)
        #Reset states
        self._event._touchbegin = False
        self._event._touchend = False
        self._event._touchinprogress = False
        return 0
    
    
class SynDevice:
    def __init__(self):
        #Create SynCOM objects
        self._synapi = client.CreateObject("SynCtrl.SynAPICtrl")
        self._syndev = client.CreateObject("SynCtrl.SynDeviceCtrl")
        self._synpac = client.CreateObject("SynCtrl.SynPacketCtrl")
        #Holder for device
        self._dev = None
        #connection flag(required for clean code)
        self._dcon = False 
        
    def Find(self, ConnectionType = 0, DeviceType = 2, lastDev = -1):
        '''Find device with params, First touchpad by default (0,2,-1)'''
        #Init synapictrl (required before first use)
        self._synapi.Initialize()
        self._dev = self._synapi.FindDevice(ConnectionType, DeviceType, lastDev)
        return self._dev
    def Select(self, hwnd = None, handler = None):
        '''Connect to device and receive events, use hwnd as device handle if provided, else use device found using Find'''
        if hwnd == None:
            if self._dev == None:
                raise RuntimeError("No Device Selected Nor Handle Specified")
        else:
            self._dev = hwnd
        if self._syndev.Select(self._dev): #"Point an ISynDeviceCtrl instance to a particular hardware device."
            raise RuntimeError("Selected Device Handle Is Not Valid")
        #Create EventSink object
        self._sink = EventSink(self._syndev, self._synpac)
        #Set Handler
        if handler != None:
            if callable(handler):
                self._sink._onpac = handler
            else:
                raise ValueError("Handler Must Be Callable")
        #"connects an event sink to the COM object"
        self._connection = client.GetEvents(self._syndev, self._sink)
        #"Connect an ISynDeviceCtrl instance to device events."
        self._syndev.Activate()
        #Set connection flag to True
        self._dcon = True
    def GetProperty(self, eProperty, string = False):
        if self._dcon:
            value = self._syndev.GetStringProperty(eProperty) if string else self._syndev.GetLongProperty(eProperty)
            return value
        else:
            raise RuntimeError("No Device is Connected to This SynCom Instance")
    def SetProperty(self, eProperty, lValue):
        if self._dcon:
            self._syndev.SetLongProperty(eProperty, lValue)
        else:
            raise RuntimeError("No Device is Connected to This SynCom Instance")
        
    def __del__(self):
        if self._dcon:
            self._syndev.Deactivate()
            self._connection.disconnect()
            time.sleep(.1)
        self._synapi = None
        self._syndev = None
        self._synpac = None




    
    
        
