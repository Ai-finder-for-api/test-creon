import unittest
import time
from quantum_testbench.models.data_models import LoadTestConfig, HttpMethod
from quantum_testbench.core.load_tester import LoadTestRunner
from quantum_testbench.core.mock_server import MockServerController


class TestLoadRunner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.controller = MockServerController(host="127.0.0.1", port=8993)
        cls.controller.start()
        time.sleep(0.1)

    @classmethod
    def tearDownClass(cls):
        cls.controller.stop()

    def test_load_bench_execution(self):
        runner = LoadTestRunner()
        config = LoadTestConfig(
            url="http://127.0.0.1:8993/health",
            method=HttpMethod.GET,
            concurrency=4,
            total_requests=20
        )
        res = runner.run(config)
        self.assertEqual(res.total_requests, 20)
        self.assertEqual(res.successful_requests, 20)
        self.assertEqual(res.failed_requests, 0)
        self.assertTrue(res.rps > 0)
        self.assertTrue(res.avg_latency_ms >= 0)


if __name__ == "__main__":
    unittest.main()