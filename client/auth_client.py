"""Tiny TCP client used to talk to the C authentication server."""

from __future__ import annotations

import socket

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8080


def server_is_up(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, timeout: float = 0.25) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def authenticate_remote(
    username: str,
    password: str,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    timeout: float = 1.0,
) -> tuple[bool, str]:
    """Send `username\\npassword\\n` and return (ok, message)."""
    payload = f"{username}\n{password}\n".encode("utf-8")
    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            sock.sendall(payload)
            sock.shutdown(socket.SHUT_WR)
            chunks = []
            while True:
                data = sock.recv(256)
                if not data:
                    break
                chunks.append(data)
    except OSError as exc:
        return False, f"Could not reach auth server ({exc})"

    reply = b"".join(chunks).decode("utf-8", errors="replace").strip()
    ok = reply.lower().startswith("auth successful")
    return ok, reply or "Empty reply from server"
