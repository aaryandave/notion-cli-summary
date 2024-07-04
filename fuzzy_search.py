"""Module to perform fuzzy search on the database items
"""
from fuzzywuzzy import process

def fuzzy_search(query: str, choices: list[str], k=3) -> list[tuple]:
    """Perform a fuzzy search on the database items to find the top k results

    Args:
        query (str): The query name to search for
        choices (list[str]): List of the page names to search through
        k (int, optional): Number of results to return. Defaults to 3.

    Returns:
        list[tuple]: List of the top k results
    """
    results = process.extract(query, choices, limit=k)
    return results

def main():
    """Main function to test the fuzzy search
    """
    query = "07-03"
    choices = ["Meeting - 2022-07-01 - Event",
               "Meeting - 2022-07-02 - Event",
               "Meeting - 2022-07-03 - Event"]
    k = 3
    results = fuzzy_search(query, choices, k)
    print(results)

if __name__ == "__main__":
    main()
