from __future__ import absolute_import, print_function, unicode_literals
import Live, sys, time, json, os, types
from _Framework.ControlSurface import ControlSurface
from .RemoteConsole import RemoteConsole

""" Pretty bare bones Ableton Remote Script Control Surface implementation
    Uses update_display tick for RemoteConsole server socket
"""
class AbletonShellControlSurface(ControlSurface):

    def __init__(self, c_instance):
        self.c_instance = c_instance
        ControlSurface.__init__(self, c_instance)
        self.log("****************** Ableton Shell Control Surface init")
        self.remote_console = RemoteConsole(ctx={'self': self}, welcome=u"Welcome to Ableton Python Shell :) ")
        that = self
        def console_log(self, *args):
            that.log(*args)
        self.remote_console.log = types.MethodType(console_log, self.remote_console)

    def update_display(self):
        u"""Live -> Script
        Aka on_timer. Called every 100 ms and should be used to update display relevant
        parts of the controller
        """
        self.remote_console.tick()

    def disconnect(self):
        u""" Called when unloaded / re-opening """
        self.log('ControlSurface disconnect')
        self.remote_console.shutdown()

    def build_midi_map(self, midi_map_handle):
        u""" Must call forward here to be able to receive midi events """
        self.log('Building midi map')
        script_handle = self.c_instance.handle()
        # Live.MidiMap.forward_midi_cc(script_handle, midi_map_handle, channel, cc)
        # self._send_midi((MIDI_CC + MIDI_STATUS_CHANNEL, int(code), int(value)))

    def receive_midi(self, midi_bytes):
        u""" MIDI messages are only received through this function, when explicitly fwd'd in map """
        self.log('received midi bytes', midi_bytes)

    def log(self, *args, delim=" "):
        def to_str(val):
            try:
                iterator = iter(val)
            except TypeError:
                return val.encode('ascii') if type(val) == bytes else str(val)
            else:
                return val if type(val) == str else delim.join([to_str(item) for item in iterator])
        self.c_instance.log_message(to_str(args))

    def suggest_input_port(self):
        u""" For the Ableton midi device in the Menu """
        return 'IAC' # something

    def suggest_output_port(self):
        u""" For the Ableton midi device in the Menu """
        return 'IAC' # something

    def can_lock_to_devices(self):
        u""" ??? """
        self.log("can lock to devices called.")
        return False

    def connect_script_instances(self, instanciated_scripts):
        u""" Can connect to other script instances? """
        self.log("connect script instances called.")
        pass

    def request_rebuild_midi_map(self):
        u"""Script -> Live
        When the internal MIDI controller has changed in a way that you need to rebuild
        the MIDI mappings, request a rebuild by calling this function
        This is processed as a request, to be sure that its not too often called, because
        its time-critical.
        """
        self.log("request rebuild midi map called.")
        self.c_instance.request_rebuild_midi_map()

    def send_midi(self, midi_event_bytes):
        u"""Script -> Live
        Use this function to send MIDI events through Live to the _real_ MIDI devices
        that this script is assigned to.
        """
        self.log("send midi called", midi_event_bytes)
        self.c_instance.send_midi(midi_event_bytes)

    def refresh_state(self):
        u"""Live -> Script
        Send out MIDI to completely update the attached MIDI controller.
        Will be called when requested by the user, after for example having reconnected
        the MIDI cables...
        """
        self.log('Control Surface state refresh requested')
