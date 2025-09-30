import requests


class GoogleSearch:
    def __init__(self, api_key: str, search_engine_id: str):
        self.api_key = api_key
        self.search_engine_id = search_engine_id

    def search(self, query: str, max_results=5) -> list:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {"key": self.api_key, "cx": self.search_engine_id, "q": query}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            results = response.json().get("items", [])
            formattedResults = []
            for item in results[:max_results]:
                formattedResults.append(
                    {"title": item.get("title", ""), "snippet": item.get("snippet", "")}
                )
            return formattedResults

        except Exception as e:
            print(f"Error during Google Search: {e}")
            return []
