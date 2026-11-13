import unittest
from quantum_testbench.models.data_models import SuiteRunResult, TestResult, RequestDefinition, HttpMethod, ResponseData
from quantum_testbench.core.reporter import ReportGenerator


class TestReportGenerator(unittest.TestCase):
    def test_report_formats(self):
        req = RequestDefinition(id="r1", name="Sample Test", method=HttpMethod.GET, url="http://127.0.0.1/test")
        resp = ResponseData(status_code=200, status_text="OK", headers={}, body="OK", elapsed_ms=12.5)
        res = TestResult(request=req, response=resp, passed=True)

        run = SuiteRunResult(
            suite_id="s1",
            suite_name="Regression",
            start_time=1700000000.0,
            duration_ms=45.0,
            results=[res],
            total_count=1,
            passed_count=1,
            failed_count=0
        )

        json_out = ReportGenerator.to_json(run)
        self.assertIn('"suite_name": "Regression"', json_out)

        md_out = ReportGenerator.to_markdown(run)
        self.assertIn("# QA Test Execution Report: Regression", md_out)

        html_out = ReportGenerator.to_html(run)
        self.assertIn("<!DOCTYPE html>", html_out)
        self.assertIn("100.0% Passed", html_out)


if __name__ == "__main__":
    unittest.main()