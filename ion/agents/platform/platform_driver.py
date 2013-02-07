#!/usr/bin/env python

"""
@package ion.agents.platform.platform_driver
@file    ion/agents/platform/platform_driver.py
@author  Carlos Rueda
@brief   Base class for platform drivers
         PRELIMINARY
"""

__author__ = 'Carlos Rueda'
__license__ = 'Apache 2.0'


from pyon.public import log
import logging

from ion.agents.platform.platform_driver_event import DriverEvent


class PlatformDriver(object):
    """
    A platform driver handles a particular platform in a platform network.
    """

    def __init__(self, platform_id, driver_config, parent_platform_id=None):
        """
        @param platform_id ID of my associated platform.
        @param driver_config Driver configuration.
        @param parent_platform_id Platform ID of my parent, if any.
                    This is mainly used for diagnostic purposes
        """

        log.debug("%r: PlatformDriver constructor called", platform_id)

        self._platform_id = platform_id
        self._driver_config = driver_config
        self._parent_platform_id = parent_platform_id

        self._send_event = None

        # The root NNode defining the platform network rooted at the platform
        # identified by self._platform_id.
        self._nnode = None

    def set_nnode(self, nnode):
        """
        Sets the node definition for this driver.
        """
        self._nnode = nnode
        if log.isEnabledFor(logging.DEBUG):
            log.debug("%r: set_nnode:\n%s",
                     self._platform_id, self._nnode.dump(include_subplatforms=False))

    def set_event_listener(self, evt_recv):
        """
        (to support similar setting in instrument-agent:
          driver_client.start_messaging(self.evt_recv)
        )
        Sets the listener of events generated by this driver.
        """
        self._send_event = evt_recv

    def ping(self):
        """
        To be implemented by subclass.
        Verifies communication with external platform returning "PONG" if
        this verification completes OK.

        @retval "PONG"
        @raise PlatformConnectionException
        """
        raise NotImplementedError()  #pragma: no cover

    def go_active(self):
        """
        Activates the driver.

        @raise PlatformDriverException set_nnode must have been called prior to this call.
        """
        raise NotImplementedError()  #pragma: no cover

    def get_metadata(self):
        """
        To be implemented by subclass.
        Returns the metadata associated to the platform.

        @raise PlatformConnectionException
        """
        raise NotImplementedError()  #pragma: no cover

    def get_attribute_values(self, attr_names, from_time):
        """
        To be implemented by subclass.
        Returns the values for specific attributes since a given time.

        @param attr_names [attrName, ...] desired attributes
        @param from_time time from which the values are requested.
                         Assummed to be in the format basically described by
                         pyon's get_ion_ts function, "a str representing an
                         integer number, the millis in UNIX epoch."

        @retval {attrName : [(attrValue, timestamp), ...], ...}
                dict indexed by attribute name with list of (value, timestamp)
                pairs. Timestamps in same format as from_time.
        """
        raise NotImplementedError()  #pragma: no cover

    def set_attribute_values(self, attrs):
        """
        To be implemented by subclass.
        Sets values for writable attributes in this platform.

        @param attrs 	[(attrName, attrValue), ...] 	List of attribute values

        @retval {platform_id: {attrName : [(attrValue, timestamp), ...], ...}}
                dict with a single entry for the requested platform ID and value
                as a list of (value,timestamp) pairs for each attribute indicated
                in the input. Returned timestamps indicate the time when the
                value was set. Each timestamp is "a str representing an
                integer number, the millis in UNIX epoch;" this is to be
                aligned with description of pyon's get_ion_ts function.
        """
        raise NotImplementedError()  #pragma: no cover

    def get_ports(self):
        """
        To be implemented by subclass.
        Returns information about the ports associated to the platform.

        @raise PlatformConnectionException
        """
        raise NotImplementedError()  #pragma: no cover

    def connect_instrument(self, port_id, instrument_id, attributes):
        """
        To be implemented by subclass.
        Connects an instrument to a port in this platform.

        @param port_id      Port ID
        @param instrument_id Instrument ID
        @param attributes   Attribute dictionary

        @retval The resulting configuration for the instrument.

        @raise PlatformConnectionException
        """
        raise NotImplementedError()  #pragma: no cover

    def disconnect_instrument(self, port_id, instrument_id):
        """
        To be implemented by subclass.
        Disconnects an instrument from a port in this platform.

        @param port_id      Port ID
        @param instrument_id Instrument ID

        @retval

        @raise PlatformConnectionException
        """
        raise NotImplementedError()  #pragma: no cover

    def get_connected_instruments(self, port_id):
        """
        To be implemented by subclass.
        Retrieves the IDs of the instruments connected to a port.

        @param port_id      Port ID

        @retval

        @raise PlatformConnectionException
        """
        raise NotImplementedError()  #pragma: no cover

    def turn_on_port(self, port_id):
        """
        To be implemented by subclass.
        Turns on a port in this platform.

        @param port_id      Port ID

        @retval The resulting on/off of the port.

        @raise PlatformConnectionException
        """
        raise NotImplementedError()  #pragma: no cover

    def turn_off_port(self, port_id):
        """
        To be implemented by subclass.
        Turns off a port in this platform.

        @param port_id      Port ID

        @retval The resulting on/off of the port.

        @raise PlatformConnectionException
        """
        raise NotImplementedError()  #pragma: no cover

    def get_subplatform_ids(self):
        """
        Gets the IDs of the subplatforms of this driver's associated
        platform. This is based on self._nnode, which should have been
        assigned by a call to go_active.
        """
        assert self._nnode is not None, "go_active should have been called first"
        return self._nnode.subplatforms.keys()

    def destroy(self):
        """
        Stops all activity done by the driver. Nothing done in this class.
        (previously it stopped resource monitoring).
        """
        pass

    def _notify_driver_event(self, driver_event):
        """
        Convenience method for subclasses to send a driver event to
        corresponding platform agent.

        @param driver_event a DriverEvent object.
        """
        log.debug("platform driver=%r: notify driver_event=%s",
            self._platform_id, driver_event)

        assert isinstance(driver_event, DriverEvent)

        if self._send_event:
            self._send_event(driver_event)
        else:
            log.warn("self._send_event not set to notify driver_event=%s",
                     str(driver_event))

    def start_event_dispatch(self, params):
        """
        To be implemented by subclass.
        Starts the dispatch of events received from the platform network to do
        corresponding event notifications.
        """
        raise NotImplementedError()  #pragma: no cover

    def stop_event_dispatch(self):
        """
        To be implemented by subclass.
        Stops the dispatch of events received from the platform network.
        """
        raise NotImplementedError()  #pragma: no cover
