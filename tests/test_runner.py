import unittest
import time
from quantum_testbench.models.data_models import TestSuite, RequestDefinition, HttpMethod, Assertion, AssertionType
from quantum_testbench.core.runner import SuiteRunner
from quantum_testbench.core.mock_server import MockServerController
from quantum_testbench.core.environment import EnvironmentManager


class TestSuiteRunner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.controller = MockServerController(host="127.0.0.1", port=8992)
        cls.controller.start()
        time.sleep(0.1)

    @classmethod
    def tearDownClass(cls):
        cls.controller.stop()

    def test_run_suite_success(self):
        env = EnvironmentManager({"BASE_URL": "http://127.0.0.1:8992"})
        runner = SuiteRunner(env_manager=env)

        suite = TestSuite(
            id="s_test",
            name="Unit Test Suite",
            requests=[
                RequestDefinition(
                    id="r1",
                    name="Check Health",
                    method=HttpMethod.GET,
                    url="{{BASE_URL}}/health",
                    assertions=[Assertion(AssertionType.STATUS_EQUALS, 200)]
                ),
                RequestDefinition(
                    id="r2",
                    name="Fetch Users",
                    method=HttpMethod.GET,
                    url="{{BASE_URL}}/api/v1/users",
                    assertions=[Assertion(AssertionType.STATUS_EQUALS, 200)]
                )
            ]
        )

        res = runner.run_suite(suite)
        self.assertEqual(res.total_count, 2)
        self.assertEqual(res.passed_count, 2)
        self.assertEqual(res.failed_count, 0)
        self.assertEqual(res.pass_percentage, 100.0)


if __name__ == "__main__":
    unittest.main()