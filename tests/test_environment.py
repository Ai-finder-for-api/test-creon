import unittest
from quantum_testbench.core.environment import EnvironmentManager


class TestEnvironmentManager(unittest.TestCase):
    def setUp(self):
        self.mgr = EnvironmentManager({"HOST": "api.test.io", "TOKEN": "secret123"})

    def test_get_and_set(self):
        self.assertEqual(self.mgr.get("HOST"), "api.test.io")
        self.mgr.set("NEW_VAR", "value99")
        self.assertEqual(self.mgr.get("NEW_VAR"), "value99")

    def test_interpolate(self):
        url = "https://{{HOST}}/v1/auth?key={{TOKEN}}"
        resolved = self.mgr.interpolate(url)
        self.assertEqual(resolved, "https://api.test.io/v1/auth?key=secret123")

    def test_interpolate_dict(self):
        headers = {"Authorization": "Bearer {{TOKEN}}", "Host": "{{HOST}}"}
        res = self.mgr.interpolate_dict(headers)
        self.assertEqual(res["Authorization"], "Bearer secret123")
        self.assertEqual(res["Host"], "api.test.io")

    def test_remove(self):
        self.assertTrue(self.mgr.remove("HOST"))
        self.assertIsNone(self.mgr.get("HOST"))
        self.assertFalse(self.mgr.remove("NONEXISTENT"))


if __name__ == "__main__":
    unittest.main()