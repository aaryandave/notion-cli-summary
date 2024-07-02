"""Command line interface for the Notion fuzzy search
"""
import json
import argparse
from notion_db_client import NotionClient
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

def print_today(tasks: list[str]) -> None:
    """Print the tasks due today

    Args:
        tasks (list[str]): List of the items due today
    """
    print("Tasks to get done today:")
    print("---------------")
    for task in tasks:
        print(f"- {task}")

def main() -> None:
    """Main function to run the fuzzy search
    """
    parser = argparse.ArgumentParser(description="Search for items in the Notion database")
    # optional argument query, can be --query or -q
    parser.add_argument("--query", "-q", type=str, help="Query to search for")
    parser.add_argument("--config", type=str, default=".config.json",
                        help="Path to the config file")
    parser.add_argument("--k", type=int, default=3, help="Number of results to return")
    parser.add_argument("--today", action="store_true", help="Get the items due today")

    args = parser.parse_args()

    with open(args.config, encoding="utf-8") as f:
        config_items = json.load(f)

    client = NotionClient(config_items["NOTION_API_KEY"], config_items["NOTION_DATABASE_ID"])

    if args.query:
        choices = client.get_page_strings(client.get_recent())
        search_results = fuzzy_search(args.query, choices, args.k)
        print_results(search_results)

    if args.today:
        tasks = client.get_today()
        task_strings = client.get_page_strings(tasks)
        print_today(task_strings)

if __name__ == "__main__":
    main()
