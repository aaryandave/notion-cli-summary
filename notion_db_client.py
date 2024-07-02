"""Module to interact with Notion API."""
from datetime import datetime, timedelta
import logging
from typing import List, Optional, Dict, Any
import requests
from notion_client import Client

logging.basicConfig(level=logging.WARNING)

class NotionClient:
    """Class to create a NotionClient object to interact with the Notion API."""

    def __init__(self, notion_api_key: str, notion_database_id: str) -> None:
        """
        Constructor for the NotionClient class.

        Args:
            notion_api_key (str): API key for the Notion API
            notion_database_id (str): ID of the database to interact with
        """
        self.api_key: str = notion_api_key
        self.database_id: str = notion_database_id
        self.headers: Dict[str, str] = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        self.database = Client(auth=self.api_key)

    def get_name_from_id(self, page_id: str) -> Optional[str]:
        """
        Get the name of the page from the page ID.

        Args:
            page_id (str): ID of the page to retrieve

        Returns:
            Optional[str]: Name of the page or None if an error occurs
        """
        url = f"https://api.notion.com/v1/pages/{page_id}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            json_data = response.json()
            page_name = json_data["properties"]["Class"]["title"][0]["plain_text"]
            return page_name
        except requests.RequestException as e:
            logging.error("Error fetching page name for ID {%s}: %s",page_id, e)
            return None

    def get_recent(self, num_items: int = 100) -> Optional[List[Dict[str, Any]]]:
        """
        Get the most recent items from the database.

        Args:
            num_items (int, optional): Number of items to retrieve. Defaults to 100.

        Returns:
            Optional[List[Dict[str, Any]]]: JSON data from the API response or None if 
            an error occurs
        """
        try:
            response = self.database.databases.query(
                **{
                    "database_id": self.database_id,
                    "page_size": num_items,
                    "filter": {
                        "property": "Complete",
                        "checkbox": {
                            "equals": False
                        }
                    }
                }
            )

            return response.get("results")
        except Exception as e:
            logging.error("Error fetching recent items: {%s}", e)
            return None

    def get_today(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get the items due today or before.

        Returns:
            Optional[List[Dict[str, Any]]]: JSON data from the API response or None 
            if an error occurs
        """
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        tomorrow_iso = tomorrow.date().isoformat()
        try:
            response = self.database.databases.query(
                **{
                    "database_id": self.database_id,
                    "sorts": [
                        {
                            "property": "Date",
                            "direction": "ascending"
                        }
                    ],
                    "filter": {
                        "and": [
                            {
                                "property": "Complete",
                                "checkbox": {
                                    "equals": False
                                }
                            },
                            {
                                "property": "Date",
                                "date": {
                                    "before": tomorrow_iso
                                }
                            }
                        ]
                    }
                }
            )
            return response.get("results")
        except Exception as e:
            logging.error("Error fetching today's items: {%s}", e)
            return None

    def _parse_date(self, date_str: str) -> datetime:
        """
        Parse the date string into a datetime object.

        Args:
            date_str (str): Date string to parse

        Returns:
            datetime: Datetime object
        """
        # Remove the timezone part if it exists
        if date_str.endswith('Z'):
            date_str = date_str[:-1]
        elif '+' in date_str:
            date_str = date_str.split('+')[0]
        elif '-' in date_str and date_str.count('-') > 2:  # Handles timezone offsets like -04:00
            date_str = date_str.rsplit('-', 1)[0]

        try:
            # Try to parse with fractional seconds
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
        except ValueError:
            try:
                # Try to parse without fractional seconds
                return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                # If it fails, parse without time component
                return datetime.strptime(date_str, "%Y-%m-%d")

    def get_page_strings(self, json_data: Optional[List[Dict[str, Any]]]) -> List[str]:
        """
        Get the page names from the JSON data.

        Args:
            json_data (Optional[List[Dict[str, Any]]]): JSON data from the API response

        Returns:
            List[str]: List of the page names
        """
        if not json_data:
            return []

        page_strings = []
        for item in json_data:
            try:
                page_name = item["properties"]["Name"]["title"][0]["plain_text"]
                page_date = self._parse_date(item["properties"]["Date"]["date"]["start"])
                page_type = item["properties"]["Type"]["select"]["name"]
                class_id = item["properties"]["Class"]["relation"][0]["id"]
                class_name = self.get_name_from_id(class_id)
                if class_name:
                    page_string = f"{page_name}, a {page_type} for {class_name} due on {page_date}"
                    page_strings.append(page_string)
            except KeyError as e:
                logging.error("Error processing item: {%s}", e)
                continue

        return page_strings
