import requests


class SendAPIRequestUseCase:
    def __init__(self, api_url: str):
        self.api_url = api_url
        if not self.check_health():
            raise Exception(f"API at {api_url} is not reachable.")

    def check_health(self) -> bool:
        health_endpoint = f"{self.api_url}/health/"
        response = requests.get(health_endpoint)
        return response.status_code == 200

    def execute(self, endpoint: str, payload: dict) -> dict:
        api_url = f"{self.api_url}/{endpoint}"
        response = requests.post(api_url, json=payload)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"API request failed with status code {response.status_code}: {response.text}"
            )
