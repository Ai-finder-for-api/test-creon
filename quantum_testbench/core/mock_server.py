import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any, List, Optional, Callable


class MockEndpoint:
    def __init__(self, method: str, path: str, status_code: int = 200, response_body: str = "", content_type: str = "application/json"):
        self.method = method.upper()
        self.path = path
        self.status_code = status_code
        self.response_body = response_body
        self.content_type = content_type


class MockServerHandler(BaseHTTPRequestHandler):
    server: "MockHttpServer"

    def log_message(self, format, *args):
        pass

    def do_request(self, method: str):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8", errors="replace") if content_length > 0 else ""

        record = {
            "timestamp": time.strftime("%H:%M:%S"),
            "client_ip": self.client_address[0],
            "method": method,
            "path": self.path,
            "headers": dict(self.headers),
            "body": body
        }
        self.server.record_request(record)

        endpoint = self.server.match_endpoint(method, self.path)
        if endpoint:
            status = endpoint.status_code
            c_type = endpoint.content_type
            resp_bytes = endpoint.response_body.encode("utf-8")
        else:
            status = 200
            c_type = "application/json"
            fallback = {
                "system": "Quantum Mock QA Server",
                "status": "healthy",
                "method": method,
                "path": self.path,
                "timestamp": time.time()
            }
            resp_bytes = json.dumps(fallback, indent=2).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", c_type)
        self.send_header("Content-Length", str(len(resp_bytes)))
        self.send_header("Server", "Quantum-Mock-QA/1.0")
        self.end_headers()
        self.wfile.write(resp_bytes)

    def do_GET(self): self.do_request("GET")
    def do_POST(self): self.do_request("POST")
    def do_PUT(self): self.do_request("PUT")
    def do_DELETE(self): self.do_request("DELETE")
    def do_PATCH(self): self.do_request("PATCH")
    def do_HEAD(self): self.do_request("HEAD")


class MockHttpServer(HTTPServer):
    def __init__(self, host: str = "127.0.0.1", port: int = 8765):
        super().__init__((host, port), MockServerHandler)
        self.endpoints: List[MockEndpoint] = []
        self.request_logs: List[Dict[str, Any]] = []
        self.lock = threading.Lock()
        self.on_request_callback: Optional[Callable[[Dict[str, Any]], None]] = None
        self._init_default_endpoints()

    def _init_default_endpoints(self):
        self.add_endpoint("GET", "/health", 200, json.dumps({"status": "healthy", "version": "1.0.0", "uptime_sec": 420}))
        self.add_endpoint("GET", "/api/v1/users", 200, json.dumps([
            {"id": "usr_101", "name": "Alice Vance", "role": "QA Engineer", "active": True},
            {"id": "usr_102", "name": "Bob Stone", "role": "DevOps", "active": True}
        ]))
        self.add_endpoint("POST", "/api/v1/auth/login", 200, json.dumps({
            "token": "bearer-quantum-test-jwt-token-xyz",
            "expires_in": 3600,
            "user": {"id": "usr_101", "name": "Alice Vance"}
        }))
        self.add_endpoint("GET", "/api/v1/orders/101", 200, json.dumps({
            "order_id": 101,
            "amount": 149.99,
            "currency": "USD",
            "status": "COMPLETED"
        }))

    def add_endpoint(self, method: str, path: str, status_code: int = 200, body: str = "", content_type: str = "application/json"):
        with self.lock:
            self.endpoints = [e for e in self.endpoints if not (e.method == method.upper() and e.path == path)]
            self.endpoints.append(MockEndpoint(method, path, status_code, body, content_type))

    def match_endpoint(self, method: str, path: str) -> Optional[MockEndpoint]:
        pure_path = path.split("?")[0]
        with self.lock:
            for e in self.endpoints:
                if e.method == method.upper() and e.path == pure_path:
                    return e
        return None

    def record_request(self, record: Dict[str, Any]):
        with self.lock:
            self.request_logs.append(record)
            if len(self.request_logs) > 500:
                self.request_logs.pop(0)

        if self.on_request_callback:
            try:
                self.on_request_callback(record)
            except Exception:
                pass

    def get_logs(self) -> List[Dict[str, Any]]:
        with self.lock:
            return list(self.request_logs)

    def clear_logs(self):
        with self.lock:
            self.request_logs.clear()


class MockServerController:
    def __init__(self, host: str = "127.0.0.1", port: int = 8765):
        self.host = host
        self.port = port
        self.server: Optional[MockHttpServer] = None
        self.thread: Optional[threading.Thread] = None
        self._is_running = False

    @property
    def is_running(self) -> bool:
        return self._is_running

    def start(self, on_request: Optional[Callable[[Dict[str, Any]], None]] = None) -> bool:
        if self._is_running:
            return True

        try:
            self.server = MockHttpServer(self.host, self.port)
            self.server.on_request_callback = on_request
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            self._is_running = True
            return True
        except Exception:
            self._is_running = False
            return False

    def stop(self):
        if not self._is_running or not self.server:
            return
        self.server.shutdown()
        self.server.server_close()
        self._is_running = False
        self.server = None
        self.thread = None