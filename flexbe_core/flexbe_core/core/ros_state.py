#!/usr/bin/env python

# Copyright 2023 Philipp Schillinger, Team ViGIR, Christopher Newport University
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#
#    * Neither the name of the Philipp Schillinger, Team ViGIR, Christopher Newport University nor the names of its
#      contributors may be used to endorse or promote products derived from
#      this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


"""A state to interface with ROS."""

from rclpy.exceptions import ParameterNotDeclaredException
from flexbe_core.proxy import ProxyPublisher, ProxySubscriberCached

from flexbe_core.core.state import State
from flexbe_core.logger import Logger
from flexbe_core.state_logger import StateLogger


class RosState(State):
    """A state to interface with ROS."""

    _node = None
    _breakpoints = None

    @staticmethod
    def initialize_ros(node):
        """Initialize the ROS interfaces."""
        RosState._node = node
        ProxyPublisher.initialize(RosState._node)
        ProxySubscriberCached.initialize(RosState._node)
        StateLogger.initialize_ros(RosState._node)
        Logger.initialize(RosState._node)
        if RosState._breakpoints is None:
            try:
                RosState._breakpoints = node.get_parameter('breakpoints').get_parameter_value().string_array_value
                Logger.localinfo(f"RosState:  using breakpoints={RosState._breakpoints}")
            except ParameterNotDeclaredException:
                Logger.localinfo("RosState: No 'breakpoints' parameter is defined")
                RosState._breakpoints = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._desired_period_ns = (1 / 10) * 1e9

        if "desired_rate" in kwargs:
            Logger.localinfo('RosState: Set desired state update '
                             f'rate to {kwargs["desired_rate"]} Hz.')
            self._desired_period_ns = (1 / kwargs["desired_rate"]) * 1e9

        self._is_controlled = False

        self._pub = ProxyPublisher()
        self._sub = ProxySubscriberCached()

        self._last_execution = None

    @property
    def sleep_duration(self):
        """Return desired sleep duration in seconds."""
        if self._last_execution is None:
            return -1  # No sleep if not executed since last entry

        elapsed = RosState._node.get_clock().now() - self._last_execution

        # Take how long the timer should sleep for and subtract elapsed time
        return (self._desired_period_ns - elapsed.nanoseconds) * 1e-9

    def set_rate(self, desired_rate):
        """
        Set the execution rate of this state.

        i.e., the rate with which the execute method is being called.

        Note: The rate is best-effort, real-time support is not yet available.

        @type desired_rate: float
        @param desired_rate: The desired rate in Hz.
        """
        self._desired_period_ns = (1 / desired_rate) * 1e9

    def _enable_ros_control(self):
        self._is_controlled = True

    def _disable_ros_control(self):
        self._is_controlled = False

    @property
    def is_breakpoint(self):
        """Check if this state defined as a breakpoint."""
        return self.path in RosState._breakpoints
