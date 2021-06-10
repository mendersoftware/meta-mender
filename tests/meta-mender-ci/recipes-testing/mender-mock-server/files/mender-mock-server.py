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

import os
import re
import shutil
import ssl

from http.server import HTTPServer, BaseHTTPRequestHandler


BASE_PATH = os.path.dirname(__file__)
DEMO_CRT_PATH = "/usr/local/share/ca-certificates/mender/server-1.crt"
JWT_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJkNjA2ZjYxNC03NWFkLTQ4M2MtOTAyNS0xMzA5NWQ2ZTNjN2MiLCJzdWIiOiIyOTYyNmYwNi03NjFiLTQ4NzEtYmQ4Ny1kMTg1YjgzZWZhM2UiLCJpc3MiOiJNZW5kZXIiLCJtZW5kZXIudGVuYW50IjoiNWRjOTBiZmQ3MGQ2OTAwMDAxZDI3YWZjIiwiZXhwIjoxNjA2NzU2NDYyLCJpYXQiOjE2MDYxNTE2NjIsIm5iZiI6LTYyMTM1NTk2ODAwLCJtZW5kZXIuZGV2aWNlIjp0cnVlLCJtZW5kZXIucGxhbiI6ImVudGVycHJpc2UifQ.onLYZ1_AhYj96g-8Ozke_dzyvPNW4FHu2h7hxRmKzUDPpEBbUvsS5dc3IEni7Ch7olhxbLnV4S9SmPQdDZyouehd4dWNm-1ZPCFTan74buicgSE3WOU_NaGB_KSFjll2nwFkw5TMykwe6dFrdqs_gfMl8nTgG27K1cnBcNca0_s3t5zYXFlBTn0rKhhikx5wCnR2NR74QgjaL-GLcIaWlHlJg5bC-OVuNasd6rAiTdin1I2Xy9uQmMt6PtFYIUQ7PJcYXM1EOZnrWW8XAMoES8pYCnFVIHW-DJe8TtyZCkPGcWcJ0tqfoml97UGr5eT2ZeO0kQ6rjxPgZcB1DoEDt2dBvRaBwqAZKnkI5lCI6gLcAX5cQmHxfR2MbHe-lXyhCmtXhsw7znAk9JVAYyjCPZAXebKRM01TneAHdv8yg-xGvgDsQXjEbaxcWSO_efqP5P4kiQFJsNWd803StGt1hzo8pEPRJ27Zvq1tgSoummmJ1qVIUSZuBOw9Hm6jugCX"


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.read_body()

        if self.path == "/api/devices/v1/deployments/device/deployments/next":
            return self.do_GET_or_POST_deployments_next()
        elif self.path.startswith("/data/"):
            with open(self.path, "rb") as body:
                self.send_response(200)
                self.send_header("Content-Type", "application/octet-stream")
                self.send_header("Content-Length", str(os.fstat(body.fileno()).st_size))
                self.end_headers()

                shutil.copyfileobj(body, self.wfile)
        else:
            self.send_empty_response(404)

    def do_POST(self):
        self.read_body()

        if self.path == "/api/devices/v1/authentication/auth_requests":
            return self.do_POST_auth_requests()
        elif self.path == "/api/devices/v1/deployments/device/deployments/next":
            return self.do_GET_or_POST_deployments_next()
        self.send_empty_response(404)

    def do_PATCH(self):
        self.read_body()

        if self.path == "/api/devices/v1/inventory/device/attributes":
            return self.do_PATCH_or_PUT_device_attributes()
        self.send_empty_response(404)

    def do_PUT(self):
        self.read_body()

        if self.path == "/api/devices/v1/inventory/device/attributes":
            return self.do_PATCH_or_PUT_device_attributes()
        elif (
            re.match(
                "/api/devices/v1/deployments/device/deployments/[^/]*/status", self.path
            )
            is not None
        ):
            self.send_empty_response(204)
        else:
            self.send_empty_response(404)

    def do_POST_auth_requests(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/jwt")
        self.send_header("Content-Length", len(JWT_TOKEN.encode("utf-8")))
        self.end_headers()
        self.wfile.write(JWT_TOKEN.encode("utf-8"))

    def do_PATCH_or_PUT_device_attributes(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", 0)
        self.end_headers()

    def do_GET_or_POST_deployments_next(self):
        if os.path.exists("/data/mender-mock-server-deployment-header.json"):
            with open("/data/mender-mock-server-deployment-header.json", "rb") as body:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", os.fstat(body.fileno()).st_size)
                self.end_headers()

                shutil.copyfileobj(body, self.wfile)

            # Only serve the request once.
            os.remove("/data/mender-mock-server-deployment-header.json")

        else:
            self.send_empty_response(204)

    def send_empty_response(self, status_code):
        self.send_response(status_code)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def read_body(self):
        if self.headers.get(
            "Transfer-Encoding"
        ) is not None and "chunked" in self.headers.get("Transfer-Encoding"):
            size = self.rfile.readline().strip()
            size = int(size, 16)
        elif self.headers.get("Content-Length") is not None:
            size = int(self.headers.get("Content-Length"))
        else:
            return ""

        data = self.rfile.read(size)

        if self.headers.get(
            "Transfer-Encoding"
        ) is not None and "chunked" in self.headers.get("Transfer-Encoding"):
            # We only support one chunk.
            lineend = self.rfile.readline().strip()
            assert lineend == b""
            size = self.rfile.readline().strip()
            assert size == b"0"
            lineend = self.rfile.readline().strip()
            assert lineend == b""

        return data


def main():
    httpd = HTTPServer(("localhost", 8443), SimpleHTTPRequestHandler)
    httpd.socket = ssl.wrap_socket(
        httpd.socket,
        keyfile=os.path.join(BASE_PATH, "private.key"),
        certfile=DEMO_CRT_PATH,
        server_side=True,
    )
    httpd.serve_forever()


if __name__ == "__main__":
    main()
