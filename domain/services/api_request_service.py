import requests


class APIRequest:
    def __init__(self, api_url: str):
        self.api_url = api_url
        if not self.check_health():
            raise Exception(f"API at {api_url} is not reachable.")

    def check_health(self) -> bool:
        health_endpoint = f"{self.api_url}/health"
        response = requests.get(health_endpoint)
        return response.status_code == 200

    def execute(self, method: str, endpoint: str, payload: dict) -> dict:
        api_url = f"{self.api_url}/{endpoint}"
        if method == "POST":
            response = requests.post(api_url, json=payload)
        elif method == "GET":
            response = requests.get(api_url, params=payload)
        elif method == "PUT":
            response = requests.put(api_url, json=payload)
        elif method == "DELETE":
            response = requests.delete(api_url, json=payload)
        else:
            raise Exception(f"Unsupported HTTP method: {method}")

        if response.status_code in [200, 201]:
            return response.json()
        else:
            raise Exception(
                f"API request failed with status code {response.status_code}: {response.text if response.text else 'No response text'}"
            )
