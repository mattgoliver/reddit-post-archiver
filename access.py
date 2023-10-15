"""Allows access to the archived Reddit posts.

Author: Matthew Oliver
Version: 10/15/2023
"""
import sqlite3

import archiver


def check_duplicate(post_id, local_cursor, log=False):
    """Check the database for existing post ID.

    Args:
        post_id (str): Post ID to check for duplicates.
        local_cursor: Database cursor.
        log (bool): Print log messages, default = False.

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


def search(local_cursor):
    searching = True

    # Search until the user signals that they are finished.
    while searching:
        print("Type 'p' to print all saved data, or 'exit' to exit\nAvailable categories: id, title, author, "
              "content_text, subreddit, file_name, etc.")
        category = input("Which category would you like to search? ")

        if category == 'exit':
            print('-' * 80)
            break

        elif category == 'p':
            print("SQLLite3: Printing current database:")
            local_cursor.execute("SELECT * FROM posts")
            rows = local_cursor.fetchall()
            for row in rows:
                print(row)

        else:
            keyword = input(f"What would you like to search in {category}? ")
            print(get_search(category, keyword, local_cursor))

        print('-' * 80)  # Separate main output from closing messages
        print("SEARCH: Finished searching.")


def get_search(category, keyword, local_cursor):
    """Searches the database based on the given keyword.

    Args:
        keyword (str): Keyword to search.
        category (str): Category to search, ex: post title, author, or subreddit.
        local_cursor: Database cursor.

    Returns:
        list: List of all results in the database, list of dictionaries.
    """
    # Try to search for given category, but don't crash if it doesn't exist
    try:
        local_cursor.execute(f"select * from posts where {category}='{keyword}'")
        results = local_cursor.fetchall()

    except sqlite3.OperationalError:
        return f"Category '{category}' does not exist."

    # If there are no results then give a clear message
    if not results:
        return f"No results for keyword '{keyword}' in '{category}'"
    else:
        return results


def stats():
    """Prints a list of statistics of the archived posts.

    Statistics include subreddit distribution, author post counts, dates archived, etc.
    """
    pass


if __name__ == "__main__":
    # Initialize database connection
    connection, cursor = archiver.initialize_database_connection("reddit-post-archive.db")

    print('-' * 80)  # Separate initialization messages from main output

    search(cursor)

    # Close database connection
    connection.close()
    print("SQLLite3: Database successfully closed.")
