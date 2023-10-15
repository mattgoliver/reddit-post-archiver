"""Allows access to the archived Reddit posts.

Author: Matthew Oliver
Version: 10/15/2023
"""


def check_duplicate(post_id):
    """Check the database for existing post ID.

    Args:
        post_id (str): Post ID to check for duplicates

    Returns:
        bool: True = duplicate found, False = new post
    """
    pass


def search(keyword, category):
    """Searches the database based on the given keyword.

    Args:
        keyword (str): Keyword to search.
        category (str): Category to search, ex: post title, author, or subreddit.

    Returns:
        list: List of all results in the database, list of dictionaries.
    """
    pass


def stats():
    """Prints a list of statistics of the archived posts.

    Statistics include subreddit distribution, author post counts, dates archived, etc.
    """
    pass