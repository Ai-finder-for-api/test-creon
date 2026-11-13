import unittest
from quantum_testbench.models.data_models import Assertion, AssertionType, ResponseData
from quantum_testbench.core.assertions import AssertionEngine


class TestAssertionEngine(unittest.TestCase):
    def setUp(self):
        self.resp = ResponseData(
            status_code=200,
            status_text="OK",
            headers={"Content-Type": "application/json", "X-Server": "Quantum"},
            body='{"status": "ok", "user": {"id": 101, "name": "Alice"}}',
            elapsed_ms=45.2
        )

    def test_status_equals_pass(self):
        ast = Assertion(AssertionType.STATUS_EQUALS, 200)
        res = AssertionEngine.evaluate(ast, self.resp)
        self.assertTrue(res.passed)

    def test_status_equals_fail(self):
        ast = Assertion(AssertionType.STATUS_EQUALS, 404)
        res = AssertionEngine.evaluate(ast, self.resp)
        self.assertFalse(res.passed)

    def test_latency_less_than(self):
        ast = Assertion(AssertionType.LATENCY_LESS_THAN, 100.0)
        res = AssertionEngine.evaluate(ast, self.resp)
        self.assertTrue(res.passed)

        ast_fail = Assertion(AssertionType.LATENCY_LESS_THAN, 20.0)
        res_fail = AssertionEngine.evaluate(ast_fail, self.resp)
        self.assertFalse(res_fail.passed)

    def test_body_contains(self):
        ast = Assertion(AssertionType.BODY_CONTAINS, "Alice")
        res = AssertionEngine.evaluate(ast, self.resp)
        self.assertTrue(res.passed)

    def test_header_exists(self):
        ast = Assertion(AssertionType.HEADER_EXISTS, "x-server")
        res = AssertionEngine.evaluate(ast, self.resp)
        self.assertTrue(res.passed)

    def test_json_path_equals(self):
        ast = Assertion(AssertionType.JSON_PATH_EQUALS, "user.name:Alice")
        res = AssertionEngine.evaluate(ast, self.resp)
        self.assertTrue(res.passed)

        ast2 = Assertion(AssertionType.JSON_PATH_EQUALS, "user.id:101")
        res2 = AssertionEngine.evaluate(ast2, self.resp)
        self.assertTrue(res2.passed)


if __name__ == "__main__":
    unittest.main()