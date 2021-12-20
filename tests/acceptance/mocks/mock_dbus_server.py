#!/usr/bin/python
# Copyright 2021 Northern.tech AS
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from gi.repository import GLib
from pydbus import SystemBus
from pydbus.generic import signal


class IoMenderAuthenticationIface:
    """
<node>
	<interface name="io.mender.Authentication1">
		<method name="GetJwtToken">
			<arg type="s" name="token" direction="out"/>
			<arg type="s" name="server_url" direction="out"/>
		</method>
		<method name="FetchJwtToken">
			<arg type="b" name="success" direction="out"/>
		</method>
        <signal name="JwtTokenStateChange">
			<arg type="s" name="token"/>
			<arg type="s" name="server_url"/>
		</signal>
		<method name="MockSetJwtToken">
			<arg type="s" name="token" direction="in"/>
			<arg type="s" name="server_url" direction="in"/>
		</method>
		<method name="MockSetJwtTokenAndEmitSignal">
			<arg type="s" name="token" direction="in"/>
			<arg type="s" name="server_url" direction="in"/>
		</method>
	</interface>
</node>
	"""

    def __init__(self):
        self.token = ""
        self.server_url = ""

    def GetJwtToken(self):
        return self.token, self.server_url

    def FetchJwtToken(self):
        return True

    JwtTokenStateChange = signal()

    def MockSetJwtToken(self, token, server_url):
        self.token = token
        self.server_url = server_url
        return True

    def MockSetJwtTokenAndEmitSignal(self, token, server_url):
        self.token = token
        self.server_url = server_url
        self.JwtTokenStateChange(self.token, self.server_url)
        return True


loop = GLib.MainLoop()
bus = SystemBus()
service = IoMenderAuthenticationIface()
bus.publish("io.mender.AuthenticationManager", service)
print("Mock for D-Bus interface io.mender.Authentication1 ready")
loop.run()
