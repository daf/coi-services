#!/usr/bin/env python

"""
@package ion.agents.alarms.alarms
@file ion/agents/alarms/alarms.py
@author Edward Hunter
@brief Alarm objects to control construction of valid alarm expressions.
"""

__author__ = 'Edward Hunter'
__license__ = 'Apache 2.0'

# Pyon imports
from pyon.public import IonObject, log

# Standard imports.
import time

# gevent.
import gevent

# Alarm types and events.
from interface.objects import StreamAlertType, AggregateStatusType

# Events.
from pyon.event.event import EventPublisher

# Resource agent.
from pyon.agent.agent import ResourceAgentState


class BaseAlert(object):
    """
    """
    def __init__(self, name=None, stream_name=None, message=None, alert_type=None,
                 value_id=None, resource_id=None, origin_type=None, aggregate_type=None):
        assert isinstance(name, str)
        assert isinstance(stream_name, str)
        assert alert_type in StreamAlertType._str_map.keys()
        
        if alert_type == StreamAlertType.ALL_CLEAR:
            message == 'Alert is cleared.'
        else:
            assert isinstance(message, str)

        if aggregate_type:
            assert aggregate_type in AggregateStatusType._str_map.keys()

        if value_id: assert isinstance(value_id, str)
        assert isinstance(resource_id, str)
        assert isinstance(origin_type, str)
        
        self._name = name
        self._stream_name = stream_name
        self._message = message
        self._alert_type = alert_type
        self._aggregate_type = aggregate_type
        self._value_id = value_id        
        self._resource_id = resource_id
        self._origin_type = origin_type
        
        self._status = None
        self._prev_status = None
        self._current_value = None

    def get_status(self):
        """
        """        
        status = {
            'name' : self._name,
            'stream_name' : self._stream_name,
            'message' : self._message,
            'alert_type' : self._alert_type,
            'aggregate_type' : self._aggregate_type,
            'value_id' : self._value_id,
            'alert_class' : self.__class__.__name__,
            'value' : self._current_value,
            'status' : self._status
        }

        return status

    def make_event_data(self):
        """
        """
        event_data = {
            'name' : self._name,
            'stream_name' : self._stream_name,
            'message' : self._message,
            'value' : self._current_value,
            'event_type' : 'StreamAlertEvent',
            'origin' : self._resource_id,
            'origin_type' : self._origin_type
        }
        
        if self._status:
            event_data['sub_type'] = 'ALL_CLEAR'
            
        elif self._alert_type == StreamAlertType.WARNING:
            event_data['sub_type'] = 'WARNING'
        
        elif self._alert_type == StreamAlertType.ALERT:
            event_data['sub_type'] = 'ALERT'    

        return event_data

    def publish_alert(self):
        """
        """
        event_data = self.make_event_data()
        print '########## publishing: ' + event_data['sub_type']
        print '########## publishing etc: ' + str(event_data)
        pub = EventPublisher()
        pub.publish_event(**event_data)

    def stop(self):
        pass

class IntervalAlert(BaseAlert):
    """
    """
    
    rel_ops = ['<', '<=']
    
    def __init__(self, name=None, stream_name=None, message=None, alert_type=None,
                 value_id=None, resource_id=None, origin_type=None, aggregate_type=None,
                 lower_bound=None, lower_rel_op=None, upper_bound=None,
                 upper_rel_op=None, **kwargs):

        super(IntervalAlert, self).__init__(name, stream_name, message,
                alert_type, value_id, resource_id, origin_type, aggregate_type)
        
        assert isinstance(value_id, str)
        self._value_id = value_id

        self._lower_bound = None
        self._upper_bound = None
        self._upper_rel_op = None
        self._lower_rel_op = None

        assert (isinstance(lower_bound, (int, float)) \
                or isinstance(upper_bound, (int, float)))
        
        if isinstance(lower_bound, (int, float)):
            assert lower_rel_op in IntervalAlert.rel_ops
            self._lower_rel_op = lower_rel_op
            self._lower_bound = lower_bound

        if isinstance(upper_bound, (int, float)):
            assert upper_rel_op in IntervalAlert.rel_ops
            self._upper_rel_op = upper_rel_op
            self._upper_bound= upper_bound

    def get_status(self):
        status = super(IntervalAlert, self).get_status()
        status['lower_bound'] = self._lower_bound
        status['upper_bound'] = self._upper_bound
        status['lower_rel_op'] = self._lower_rel_op
        status['upper_rel_op'] = self._upper_rel_op
        return status

    def eval_alert(self, x):
        self._current_value = x
        self._prev_status = self._status
        
        if self._lower_bound and self._upper_bound:
            if self._lower_rel_op == '<=':
                if self._upper_rel_op == '<=':
                    self._status = (self._lower_bound <= self._current_value <= self._upper_bound)
                
                else:
                    self._status = (self._lower_bound <= self._current_value < self._upper_bound)
                    
            else:
                if self._upper_rel_op == '<=':
                    self._status = (self._lower_bound < self._current_value <= self._upper_bound)
                
                else:
                    self._status = (self._lower_bound < self._current_value < self._upper_bound)
                        
        elif self._lower_bound:
            if self._lower_rel_op == '<=':
                self._status = (self._lower_bound <= self._current_value)
            else:
                self._status = (self._lower_bound < self._current_value)
            
        elif self._upper_bound:
            if self._upper_rel_op == '<=':
                self._status = (self._current_value <= self._upper_bound)
            else:
                self._status = (self._current_value < self._upper_bound)
                
        if self._prev_status != self._status:
            self.publish_alert()


class RSNEventAlert(BaseAlert):
    """
    """

    # value_id represents the name of the monitorable in an RSNAlert
    #

    def __init__(self, name=None, stream_name=None, message=None, alert_type=None,
                 value_id=None, resource_id=None, origin_type=None, aggregate_type=None,
                 **kwargs):

        super(RSNEventAlert, self).__init__(name, '', message,
                alert_type, value_id, resource_id, origin_type, aggregate_type)

        assert isinstance(value_id, str)
        self._value_id = value_id

#        {
#        "group": "power",
#        "name" : "low_voltage_warning",
#        "value_id" : "input_voltage",
#        "value" : "1.2",
#        "alert_type" : "warning",
#        "url": "http://localhost:8000",
#        "timestamp": 3573569514.295556,
#        "ref_id": "44.78",
#        "platform_id": "TODO_some_platform_id_of_type_UPS",
#        "message": "low battery (synthetic event generated from simulator)"
#        }

        self._name = name
        self._stream_name = stream_name
        self._message = message
        self._alert_type = alert_type
        self._aggregate_type = aggregate_type
        self._value_id = value_id
        self._resource_id = resource_id
        self._origin_type = origin_type

        self._status = None
        self._prev_status = None
        self._current_value = None

    def get_status(self):
        status = super(RSNEventAlert, self).get_status()

        return status

    def eval_alert(self, x):

        # x is an RSN event struct TBD
        assert isinstance(x, dict)

        #print 'x: %s',x.keys()
        print 'x: %s',x

        self._current_value = x['value']
        self._prev_status = self._status

        self._message = x['message']

        if x['alert_type'] is "warning":
            self._alert_type = StreamAlertType.WARNING
            self._status = False
        elif x['alert_type'] is "error":
            self._alert_type = StreamAlertType.ALERT
            self._status = False
        else:
            self._alert_type = StreamAlertType.ALL_CLEAR
            self._status = True

        self._resource_id = x['platform_id']

        if self._prev_status != self._status:
            self.publish_alert()

        return


class UserExpressionAlert(BaseAlert):
    """
    """
    pass

class DeltaAlert(BaseAlert):
    """
    """
    pass

class LateDataAlert(BaseAlert):
    """
    """
    def __init__(self, name=None, stream_name=None, message=None, alert_type=None,
                 value_id=None, resource_id=None, origin_type=None, aggregate_type=None,
                 time_delta=None, get_state=None, **kwargs):

        super(LateDataAlert, self).__init__(name, stream_name, message,
                alert_type, value_id, resource_id, origin_type, aggregate_type)

        assert isinstance(time_delta, (int, float))
        assert get_state
        assert callable(get_state)
        
        self._time_delta = time_delta
        self._get_state = get_state
        self._gl = gevent.spawn(self._check_data)

    def get_status(self):
        status = super(LateDataAlert, self).get_status()
        status['time_delta'] = self._time_delta
        return status

    def eval_alert(self):
        """
        if self._get_state() == ResourceAgentState.STREAMING:
            prev_value = self._current_value
            self._current_value = time.time()
            if prev_value:
                self._cur_timestep = self._current_value - prev_value
        else:
            self._current_value = None
            self._cur_timestep = 0.0
        """
        self._current_value = time.time()
        if not self._status:
            self._status = True
            self.publish_alert()
        
    def _check_data(self):
        """
        start = time.time()
        while True:
            if self._get_state() == ResourceAgentState.STREAMING:
                last_data_arrived = self._current_value
                gevent.sleep(self._time_delta)
                if self._get_state() == ResourceAgentState.STREAMING:
                    self._prev_status = self._status
                    if last_data_arrived == self._current_value:
                        #print '########## TIMER %f:    %f  %f  %f:     NO NEW DATA' % ((time.time() - start), last_data_arrived, self._current_value, self._cur_timestep)
                        self._status = False
                    elif self._cur_timestep > self._time_delta:
                        #print '########## TIMER %f:    %f  %f  %f:     TIMESTEP TO LARGE' % ((time.time() - start), last_data_arrived, self._current_value, self._cur_timestep)
                        self._status = False
                    else:
                        #print '########## TIMER %f:    %f  %f  %f:     DATA OK' % ((time.time() - start), last_data_arrived, self._current_value, self._cur_timestep)
                        self._status = True
                    if self._prev_status != self._status:
                        self.publish_alert()
                        
            else:
                gevent.sleep(self._time_delta)
        """
        while True:
            prev_value = self._current_value
            prev_status = self._status
            gevent.sleep(self._time_delta)            
            if self._get_state() == ResourceAgentState.STREAMING:
                if self._current_value == prev_value and self._status:
                    self._status = False
                    self.publish_alert()
        
    def stop(self):
        if self._gl:
            self._gl.kill()
            self._gl.join()
            self._gl = None