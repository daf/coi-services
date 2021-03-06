#!/usr/bin/env python

"""
@package ion.services.mi.exceptions Exception classes for MI work
@file ion/services/mi/exceptions.py
@author Steve Foley
@brief Common exceptions used in the MI work. Specific ones can be subclassed
in the driver code
"""

__author__ = 'Steve Foley'
__license__ = 'Apache 2.0'

from ion.services.mi.common import InstErrorCode

class InstrumentException(Exception):
    """Base class for an exception related to physical instruments or their
    representation in ION.
    """
    
    def __init__ (self, error_code=None, msg=None):
        self.args = (error_code, msg)
        self.error_code = error_code
        self.msg = msg
    
class InstrumentConnectionException(InstrumentException):
    """Exception related to connection with a physical instrument"""
    
class InstrumentProtocolException(InstrumentException):
    """Exception related to an instrument protocol problem
    
    These are generally related to parsing or scripting of what is supposed
    to happen when talking at the lowest layer protocol to a device.
    @todo Add partial result property?
    """
    
class InstrumentStateException(InstrumentException):
    """Exception related to an instrument state of any sort"""
    
class InstrumentTimeoutException(InstrumentException):
    """Exception related to a command, request, or communication timing out"""
    def __init__(self, error_code=InstErrorCode.TIMEOUT, msg=None):
        InstrumentException.__init__(self, error_code, msg)
    
class InstrumentDataException(InstrumentException):
    """Exception related to the data returned by an instrument or developed
    along the path of handling that data"""
    
class CommsException(InstrumentException):
    """Exception related to upstream communications trouble"""
    
class RequiredParameterException(InstrumentException):
    """A required parameter is not supplied"""
    
    