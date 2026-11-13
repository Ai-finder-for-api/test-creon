import unittest
import time
import requests
from quantum_testbench.core.mock_server import MockServerController


class TestMockServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.controller = MockServerController(host="127.0.0.1", port=8991)
        started = cls.controller.start()
        assert started, "Mock server failed to start on port 8991"
        time.sleep(0.1)

    @classmethod
    def tearDownClass(cls):
        cls.controller.stop()

    def test_health_endpoint(self):
        res = requests.get("http://127.0.0.1:8991/health", timeout=3)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data.get("status"), "healthy")

    def test_users_endpoint(self):
        res = requests.get("http://127.0.0.1:8991/api/v1/users", timeout=3)
        self.assertEqual(res.status_code, 200)
        users = res.json()
        self.assertTrue(len(users) >= 2)

    def test_inbound_logging(self):
        requests.post("http://127.0.0.1:8991/custom/webhook", json={"event": "deploy"}, timeout=3)
        logs = self.controller.server.get_logs()
        self.assertTrue(any(log.get("path") == "/custom/webhook" for log in logs))


if __name__ == "__main__":
    unittest.main()