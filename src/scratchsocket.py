# -*- coding: utf-8 -*-
"""Simplified socket class"""
#  ____                 _       _     ____  _             _
# / ___|  ___ _ __ __ _| |_ ___| |__ / ___|| |_ __ _  ___| | __
# \___ \ / __| '__/ _` | __/ __| '_ \\___ \| __/ _` |/ __| |/ /
#  ___) | (__| | | (_| | || (__| | | |___) | || (_| | (__|   <
# |____/ \___|_|  \__,_|\__\___|_| |_|____/ \__\__,_|\___|_|\_\
#

import socket


class InboundSocket:
    """Provides a simple callback-based API for inbound TCP sockets

    Attributes:
        port (int): The port currently being listened on
    """
    def __init__(self):
        self.port = None
        self._client_socket = None
        self._server_socket = None
        self._running = False

    def listen(self, port, read_callback):
        """Start listening on the given port

        Args:
            port (int): Port to listen on
            read_callback (callable): Called every time a byte is read from
                the socket

        Raises:
            RuntimeError: If socket is already listening
        """
        if self._running:
            raise RuntimeError('Socket already listening')

        self.port = port
        self._running = True

        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind(('0.0.0.0', self.port))
        self._server_socket.listen(1)

        (self._client_socket, _) = self._server_socket.accept()

        while self._running:
            byte = self._client_socket.recv(1)
            if byte == b'':
                # The connection has closed, wait for another one
                (self._client_socket, _) = self._server_socket.accept()
                continue
            read_callback(byte)

    def write(self, bytes_to_write):
        """Write bytes to the currently connected client connection (if any)

        Note:
            An RuntimeError will be thrown if no client is currently connected

        Args:
            bytes_to_write (bytes): Bytes that will be sent to the connected
                client

        Raises:
            RuntimeError: If no clients are currently connected
            RuntimeError: If the current connection is closed by the client
        """
        if self._client_socket is None:
            raise RuntimeError('Cannot write to socket: Not listening on any port')

        bytes_sent = 0
        while bytes_sent < len(bytes_to_write):
            sent = self._client_socket.send(bytes_to_write[bytes_sent:])
            if sent == 0:
                raise RuntimeError('Cannot write to socket: Connection closed')
            bytes_sent += sent

    def close_client_conn(self):
        """Gracefully terminate any inbound client connections"""
        if self._client_socket is not None:
            self._client_socket.shutdown(1)

    def stop(self):
        """Stop listening on the current port"""
        if self._client_socket is not None:
            self._client_socket.shutdown(1)
            self._client_socket.close()
        if self._server_socket is not None:
            self._server_socket.close()

        self.port = None
        self._client_socket = None
        self._server_socket = None
        self._running = False
