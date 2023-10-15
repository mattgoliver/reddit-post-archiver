"""Allows access to the archived Reddit posts.

Author: Matthew Oliver
Version: 10/15/2023
"""
import archiver


def check_duplicate(post_id, local_cursor, log=False):
    """Check the database for existing post ID.

    Args:
        post_id (str): Post ID to check for duplicates
        local_cursor: Database connection
        log (bool): Print log messages, default = False

    Returns:
        bool: True = duplicate found, False = new post
    """
    # Search database for the given post id
    local_cursor.execute(f"select * from posts where id='{post_id}'")
    results = local_cursor.fetchall()

    # If there are any results, then it is a duplicate
    if results:
        if log:
            print(f"CHECK: Duplicate found: {results}.")
        return True

    # If there are no results, then the post has not been archived yet
    else:
        if log:
            print("CHECK: No duplicates found.")
        return False


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