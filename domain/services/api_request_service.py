import requests
from typing import Optional


class APIRequest:
    def __init__(
        self,
        api_url: str,
        auth_token: str = None,
        username: str = None,
        password: str = None,
    ):
        self.api_url = api_url.rstrip("/")
        self.auth_token = auth_token
        self.username = username
        self.password = password
        self.login_endpoint = f"{self.api_url}/api/v1/auth/login"

        if not self.check_health():
            print(
                f"[Startup] Warning: API at {self.api_url} is not reachable. "
                "The service will continue and retry on request."
            )
        else:
            # Try to get token from credentials if no token provided
            if not self.auth_token and self.username and self.password:
                self._authenticate()

    def check_health(self) -> bool:
        health_endpoint = f"{self.api_url}/health"
        try:
            response = requests.get(health_endpoint, timeout=3)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def _authenticate(self) -> bool:
        """Login to get JWT token"""
        try:
            response = requests.post(
                self.login_endpoint,
                json={"email": self.username, "password": self.password},
                timeout=5,
            )
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("data", {}).get("token") or data.get("token")
                if self.auth_token:
                    print(f"[APIRequest] Successfully authenticated and obtained token")
                    return True
                else:
                    print(
                        f"[APIRequest] Login successful but no token in response: {data}"
                    )
                    return False
            else:
                print(
                    f"[APIRequest] Authentication failed with status {response.status_code}: {response.text}"
                )
                return False
        except Exception as e:
            print(f"[APIRequest] Error during authentication: {e}")
            return False

    def _get_headers(self) -> dict:
        """Build request headers with authorization token if available"""
        headers = {}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers

    def execute(self, method: str, endpoint: str, payload: dict, retry_count: int = 0) -> dict:
        """Execute API request with automatic token refresh on 401"""
        api_url = f"{self.api_url}/{endpoint}"
        headers = self._get_headers()
        
        if method == "POST":
            response = requests.post(api_url, json=payload, headers=headers)
        elif method == "GET":
            response = requests.get(api_url, params=payload, headers=headers)
        elif method == "PUT":
            response = requests.put(api_url, json=payload, headers=headers)
        elif method == "DELETE":
            response = requests.delete(api_url, json=payload, headers=headers)
        else:
            raise Exception(f"Unsupported HTTP method: {method}")

        # Handle 401 Unauthorized - try to refresh token and retry
        if response.status_code == 401 and retry_count < 1:
            print(f"[APIRequest] Got 401 Unauthorized, attempting to refresh token...")
            if self._authenticate():
                print(f"[APIRequest] Token refreshed, retrying request...")
                return self.execute(method, endpoint, payload, retry_count=retry_count + 1)
            else:
                print(f"[APIRequest] Failed to refresh token")

        if response.status_code in [200, 201]:
            return response.json()
        else:
            error_msg = f"API request failed with status code {response.status_code}: {response.text if response.text else 'No response text'}"
            print(f"[APIRequest] {error_msg}")
            raise Exception(error_msg)
