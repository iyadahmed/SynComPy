# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 16:14:24 2019

@author: Iyad
"""
import time
import comtypes.client as client
try:
    from .syncomdefs import SF_FingerPresent
    from .synerror import *
    from .helper import *
except:
    from syncomdefs import SF_FingerPresent
    from synerror import *
    from helper import *
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
    
class EventSink(object):
    def __init__(self, syndev, synpac):
        self._syndev = syndev
        self._synpac = synpac
        
        #Assume finger is not present at first
        self._stage = bswitch(False)
        
        #Create new empty event
        self._event = Event()
        
    #Empty handler, patched when method bind_all of SynDevice instance is called
    def _onpac(self , event):    
        pass
    
    #This is where events of ISynDeviceCtrl are directed
    def _ISynDeviceCtrlEvents_OnPacket(self, this):
        #Fill self._synpac with current device information packet
        self._syndev.LoadPacket(self._synpac)
        
        #Check presense of a finger on touchpad
        finger_present = self._synpac.FingerState & SF_FingerPresent
        
        #Translate finger_present state to touch begin, progress and end states
        stage = self._stage.update(finger_present)
        
        #Pass the loaded packet to the event
        self._event._pac = self._synpac
        
        #Set the event's touch begin, progress and end states
        if  stage == 1:
            self._event._touchbegin = True #touch begin
        elif stage == -1:
            self._event._touchend = True #touchend
        elif finger_present:
            self._event._touchinprogress = True #touch in progress
            
        #Call the patched handler
        self._onpac(self._event)
        
        #Reset touch begin, progress and end states
        self._event._touchbegin = False
        self._event._touchend = False
        self._event._touchinprogress = False
        
class SynDevice:
    def __init__(self):
        #Create new ISynAPICtrl control object instance for managing SynComAPI for all devices
        self._synapi = client.CreateObject("SynCtrl.SynAPICtrl")
        
        #Create new ISynDeviceCtrl control object for managing a particular device
        self._syndev = client.CreateObject("SynCtrl.SynDeviceCtrl")
        
        #Create new ISynPacketCtrl control object managing a device's packet data
        self._synpac = client.CreateObject("SynCtrl.SynPacketCtrl")
        
        #Initialize device query handle variable
        self._dev = None
        
        #Initialize device selection flag
        self._selected = False

        #Initialize comtypes connection variable
        self._connection = None

    def find(self, eConnectionType = 0, eDeviceType = 2, lLastHandle = -1):
        '''Find device using parameters, first touchpad by default (0,2,-1)'''
        #Initialize SynAPICtrl instance, this is required before calling any methods of that instance
        if self._synapi.Initialize() == SYNE_FAIL:
            raise RuntimeError("The Synaptics kernel-mode driver is not present on the target machine or the installed driver version is less than that necessary to support the Synaptics COM API.")
        
        #Obtain a query handle for a particular type of device or for a device connected to the host computer in a particular manner.
        self._dev = self._synapi.FindDevice(eConnectionType, eDeviceType, lLastHandle)
        
        #Detect returned error if any
        if self._dev < 0:
            raise RuntimeError("No appropriate device found.")
        elif self._dev == SYNE_FAIL:
            raise RuntimeError("The ISynAPICtrl object has not been initialized properly.")
        else:
            return self._dev
        
    def select(self, lHandle):
        '''Select a device with hwnd as its query handle'''
        #"Point an ISynDeviceCtrl instance to a particular hardware device."
        if self._syndev.Select(lHandle) == SYNE_HANDLE: 
            raise ValueError("The requested lHandle does not correspond to any known device. ")
        else:
            #Set device selection flag to True
            self._selected = True
        
    def bind_all(self, func):
        if self._selected:
            
            #Create the event sink
            self._sink = EventSink(self._syndev, self._synpac)
            
            #Patch the handler with the callable func
            if callable(func):
                self._sink._onpac = func
            else:
                raise TypeError("func must be callable")
            
            #Redirect events of main message pump to the event sink
            self._connection = client.GetEvents(self._syndev, self._sink)
            
            #Connect ISynDeviceCtrl events to the main message pump
            if self._syndev.Activate() == SYNE_FAIL:
                raise RuntimeError("The Synaptics kernel-mode driver is not present on the target machine.")

            
        else:
            raise RuntimeError("No device selected, call the method select with a valid device query handle before binding")
       
        
    def get_property(self, eProperty, is_string = False):
        if self._selected:
            value = self._syndev.GetStringProperty(eProperty) if is_string else self._syndev.GetLongProperty(eProperty)
            return value
        else:
            raise RuntimeError("No device is selected for this SynDevice instance")
        
    def set_property(self, eProperty, lValue):
        if self._selected:
            self._syndev.SetLongProperty(eProperty, lValue)
        else:
            raise RuntimeError("No device is selected for this SynDevce instance")
        
    def __del__(self):
        if self._connection:
            self._syndev.Deactivate()
            self._connection.disconnect()
            time.sleep(.1)




    
    
        
