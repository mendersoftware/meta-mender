# python3-asyncio depends on python3-threading. Error trace follows:
#   File "/usr/lib/python3.8/asyncio/base_events.py", line 780, in run_in_executor
#     executor = concurrent.futures.ThreadPoolExecutor()
#   File "/usr/lib/python3.8/concurrent/futures/__init__.py", line 49, in __getattr__
#     from .thread import ThreadPoolExecutor as te
#   File "/usr/lib/python3.8/concurrent/futures/thread.py", line 11, in <module>
#     import queue
# ModuleNotFoundError: No module named 'queue'
#
# However seems to be missing at:
# https://github.com/lgirdk/poky/blob/dunfell/meta/recipes-devtools/python/python3/python3-manifest.json#L117
#
# On top of that, for zeus, websockets complains on missing typing module. Error trace follows:
# Traceback (most recent call last):
#   File "/tmp/mock_websocket_server.py", line 19, in <module>
#     import websockets
#   File "/usr/lib/python3.7/site-packages/websockets/__init__.py", line 3, in <module>
#     from .auth import *
#   File "/usr/lib/python3.7/site-packages/websockets/auth.py", line 10, in <module>
#     from typing import Any, Awaitable, Callable, Iterable, Optional, Tuple, Type, Union
# ModuleNotFoundError: No module named 'typing'
#
# Fix it here for our tests with a .bbappend
#

RDEPENDS_${PN} = "\
    ${PYTHON_PN}-asyncio \
    ${PYTHON_PN}-threading \
    ${PYTHON_PN}-typing \
"
