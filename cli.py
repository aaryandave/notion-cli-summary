"""Command line interface for the Notion fuzzy search
"""
import json
import argparse
from notion_client import NotionClient
from fuzzy_search import fuzzy_search

def print_results(results: list[tuple]) -> None:
    """Print the results of the fuzzy search in a nice, colored format

    Args:
        results (list[tuple]): List of the top k results
    """
    print("Search Results:")
    print("---------------")
    for result in results:
        print(f"- {result[0]} (relevance: {result[1]})")

def main() -> None:
    """Main function to run the fuzzy search
    """
    parser = argparse.ArgumentParser(description="Search for items in the Notion database")
    parser.add_argument("query", type=str, help="The query to search for")
    parser.add_argument("--config", type=str, default=".config.json",
                        help="Path to the config file")
    parser.add_argument("--k", type=int, default=3, help="Number of results to return")

    args = parser.parse_args()

    with open(args.config, encoding="utf-8") as f:
        config_items = json.load(f)

    client = NotionClient(config_items["NOTION_API_KEY"], config_items["NOTION_DATABASE_ID"])
    choices = client.get_page_strings()
    search_results = fuzzy_search(args.query, choices, args.k)
    print_results(search_results)

if __name__ == "__main__":
    main()
