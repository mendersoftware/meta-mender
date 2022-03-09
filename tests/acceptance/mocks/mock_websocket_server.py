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

import argparse

import asyncio
import websockets


parser = argparse.ArgumentParser()
parser.add_argument("port", type=int, help="port")

args = parser.parse_args()

server_host = "localhost"


async def hello(websocket, path):
    await websocket.recv()


start_server = websockets.serve(hello, server_host, args.port)
serverws = asyncio.get_event_loop().run_until_complete(start_server)

port = serverws.server.sockets[0].getsockname()[1]
server_url = f"http://{server_host}:{port}"

print("Listening on %s" % server_url)
asyncio.get_event_loop().run_forever()
