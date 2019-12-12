# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 16:14:24 2019

@author: Iyad
"""

import comtypes.client as client
from .SynComDefs import *
from .hfuncs import *
class EventSink(object):
    def __init__(self, syndev, synpac):
        self._syndev = syndev
        self._synpac = synpac
        self._state = bswitch(0)
    def _Pac(self, pac):
        '''Patch this, use pac variable to access Packet data \n example: pac.GetLongProperty(SP_X)'''
        pass
    def _ISynDeviceCtrlEvents_OnPacket(self, this):
        self._syndev.LoadPacket(self._synpac)
        self._Pac(self._synpac)
        prestate = self._synpac.FingerState & SF_FingerPresent
        state = self._state.update(prestate)
        if  state == 1:
            self._TouchBegin(self._synpac)
        elif state == -1:
            self._TouchEnd(self._synpac)
        else:
            if prestate: self._TouchInProgress(self._synpac)
        return 0
    def _TouchBegin(self, pac): pass
    def _TouchEnd(self, pac): pass
    def _TouchInProgress(self, pac): pass
    
class syn:
    def __init__(self):
        #Create SynCOM objects
        self._synapi = client.CreateObject("SynCtrl.SynAPICtrl")
        self._syndev = client.CreateObject("SynCtrl.SynDeviceCtrl")
        self._synpac = client.CreateObject("SynCtrl.SynPacketCtrl")
        #Create EventSink object
        self._sink = EventSink(self._syndev, self._synpac)
        #init connection vars(required for clean code)
        self._dcon = False 
        
    def Find(self, ConnectionType = 0, DeviceType = 2, lastDev = -1):
        '''Find device with params, First touchpad by default (0,2,-1)'''
        #Init synapictrl (required before first use)
        self._synapi.Initialize()
        self._dev = self._synapi.FindDevice(ConnectionType, DeviceType, lastDev)
        return self._dev
    def Connect(self, hwnd = None):
        '''Connect to device and receive events'''
        dev = hwnd if hwnd != None else self._dev
        #"Point an ISynDeviceCtrl instance to a particular hardware device."
        self._syndev.Select(dev)
        #"connects an event sink to the COM object"
        self._connection = client.GetEvents(self._syndev, self._sink)
        #"Connect an ISynDeviceCtrl instance to device events."
        self._syndev.Activate()
        self._dcon = True
    def trigger(self, pac = None, begin = None, end= None, prog = None):
        '''packet, touch begin, touch end, touch in progress'''
        if self._dcon:
            if callable(pac):
                self._sink._Pac = pac
            else:
                if pac: print("pac not callable")
            if callable(begin):
                self._sink._TouchBegin = begin
            else:
                if begin: print("begin not callable")
            if callable(end):
                self._sink._TouchEnd = end
            else:
                if end: print("end not callable")
            if callable(prog):
                self._sink._TouchInProgress = prog
            else:
                if prog: print("prog not callable")
        else:
            print("please use find and connect methods first")
    
    def __del__(self):
        if self._dcon:
            self._syndev.Deactivate()
            self._connection.disconnect()
            time.sleep(.1)
        self._synapi = None
        self._syndev = None
        self._synpac = None


if __name__ == '__main__':
    mypad = syn() #Create new syn object
    #mypad.Find() #Find a device handle, or don't if you know it(probably Zero for first device)
    mypad.Connect(0) #Catch events
    def pacH(packet):
        print(packet.X, packet.Y)
    mypad.trigger(begin = pacH, end = pacH)
    
    
        
