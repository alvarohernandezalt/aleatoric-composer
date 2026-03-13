"""
Runtime hook that blocks ALL outbound network connections.
Monkey-patches socket.socket.connect to raise an error,
ensuring the app cannot communicate over the network.
"""
import socket as _socket

_original_connect = _socket.socket.connect


def _blocked_connect(self, *args, **kwargs):
    raise OSError("Network access is disabled in this application")


_socket.socket.connect = _blocked_connect
