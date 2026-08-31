import hashlib
import os
import subprocess
import sys
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HASH_BIN = ROOT / "tests" / "hash_check"
SERVER_BIN = ROOT / "Servidor_Cliente" / "servidor"
CLIENT_BIN = ROOT / "Servidor_Cliente" / "cliente"


class Sha256CompatTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        src = ROOT / "tests" / "hash_check.c"
        subprocess.run(
            ["gcc", "-Wall", "-Wextra", "-o", str(HASH_BIN), str(src)],
            check=True,
            cwd=ROOT,
        )

    def test_matches_python_hashlib(self):
        payload = "demo:demo123"
        expected = hashlib.sha256(payload.encode()).hexdigest()
        got = subprocess.check_output([str(HASH_BIN), payload], text=True).strip()
        self.assertEqual(got, expected)


@unittest.skipUnless(os.environ.get("TTT_TEST_SOCKETS") == "1", "set TTT_TEST_SOCKETS=1 to run live socket tests")
class AuthServerTests(unittest.TestCase):
    def test_demo_login_over_tcp(self):
        sys.path.insert(0, str(ROOT / "client"))
        import users

        users.USERS_FILE = ROOT / "data" / "users.txt"
        users.ensure_demo_user()

        subprocess.run(["make", "server", "client-c"], check=True, cwd=ROOT)
        proc = subprocess.Popen(
            [str(SERVER_BIN)],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            time.sleep(0.2)
            out = subprocess.check_output(
                [str(CLIENT_BIN), "127.0.0.1", "demo", "demo123"],
                cwd=ROOT,
                text=True,
            )
            self.assertIn("Auth successful", out)
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=2)


if __name__ == "__main__":
    unittest.main()
