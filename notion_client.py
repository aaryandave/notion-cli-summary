"""Module to interact with Notion API
"""
import requests

class NotionClient:
    """Class create a NotionClient object to interact with the Notion API
    """
    def __init__(self, notion_api_key: str, notion_database_id: str) -> None:
        """Constructor for the NotionClient class

        Args:
            notion_api_key (str): API key for the Notion API
            notion_database_id (str): ID of the database to interact with
        """
        self.api_key: str = notion_api_key
        self.database_id: str = notion_database_id
        self.headers: dict[str, str] = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

    def get_name_from_id(self, page_id: str) -> str:
        """Get the name of the page from the page ID

        Args:
            page_id (str): ID of the page to retrieve

        Returns:
            str: Name of the page
        """
        url = f"https://api.notion.com/v1/pages/{page_id}"
        response = requests.get(url, headers=self.headers, timeout=10)
        json_data = response.json()
        page_name = json_data["properties"]["Class"]["title"][0]["plain_text"]
        return page_name

    def get_recent(self, num_items: int=100) -> dict[str, str]:
        """Get the most recent items from the database

        Args:
            num_items (int, optional): Number of items to retrieve. Defaults to 5.

        Returns:
            dict[str, str]: JSON data from the API response
        """
        url = f"https://api.notion.com/v1/databases/{self.database_id}/query"

        db_filter = {
            "property": "Complete",
            "checkbox": {
                "equals": False
            }
        }
        payload = {"page_size": num_items, "filter": db_filter}
        response = requests.post(url, headers=self.headers, json=payload, timeout=100)
        json_data = response.json()

        return json_data

    def get_page_strings(self) -> list[str]:
        """Get the names of the pages in the database

        Returns:
            list[str]: List of the page names
        """
        json_data: dict = self.get_recent()

        database_items: dict = json_data["results"]
        page_names: list = [item["properties"]["Name"]["title"][0]["plain_text"]
                            for item in database_items]
        page_dates: list = [item["properties"]["Date"]["date"]["start"] for item in database_items]
        page_types: list = [item["properties"]["Type"]["select"]["name"] for item in database_items]
        class_ids: list = [item["properties"]["Class"]["relation"][0]["id"]
                           for item in database_items]
        class_names: list = [self.get_name_from_id(class_id) for class_id in class_ids]
        zipped = list(zip(page_names, page_dates, page_types, class_names))
        strings = [f"{name}, a {p_type} for {c_name} due on {date}"
                   for name, date, p_type, c_name in zipped]
        return strings
