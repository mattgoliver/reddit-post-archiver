"""Reddit Post Archiver.

Author: Matthew Oliver
Version: 10/15/2023
"""
import access  # Allows for accessing the post/archive database
import random  # Allows for random file names
import json  # Allows access to the .json login information file
import praw  # Allows access to Reddit's API
import sqlite3  # Allows for database management
import os  # Allows for checking if database exists


def read_secrets(filename):
    """Read login information from .json file.

    Args:
        filename (str): Name of file containing login information

    Returns:
        dict: Login information.
    """
    try:
        with open(filename, mode='r') as f:
            return json.loads(f.read())
    except FileNotFoundError:
        print(f"ERROR: No .json file found for login information with the name '{filename}'")


def archive_saved_posts(user, upvote=False):
    """Retrieves all saved posts from a user's profile.

    Args:
        user (str): User to get saved posts from.
        upvote (bool): Upvote post once archived, default=False

    Returns:
        dict: Dictionary containing post information.
    """
    saved_posts = []

    for post in saved_posts:  # Loop through user's saved posts
        if access.check_duplicate(post.id):  # Skip to next post if duplicate
            continue

        file_name = random.name()  # Create a random name to save the content as

        if download_post(post.url, file_name):  # Download post content, if download successful then archive
            archive(post, file_name)  # Archive post content

        if upvote:  # Upvote after archive if enabled
            post.upvote()


def download_post(url, file_name):
    """Downloads post at given url.

    Args:
          url (str): URL of post to download.
          file_name (str): Name to save file as.

    Returns:
         bool: Download success
    """
    pass


def archive(post, file_name):
    """Archives the post at the given url.

    Information archived: ID, title, author, content (text & media), subreddit, url, date, amount of upvotes

    Args:
        post (dict): Post to archive.
        file_name: Name of downloaded file to associate post information with.
    """
    pass


def initialize_database_connection(database_name):
    """Connects to the archive database, creates one if it doesn't exist

    Args:
        database_name (str): Name of database to connect to.

    Returns:
        tup: Database connection and cursor
    """
    if os.path.isfile(database_name):
        local_connection = sqlite3.connect(database_name)
        local_cursor = local_connection.cursor()
        print(f'Database exists. Successfully connected to {database_name}')

    else:
        print(f'Database does not exist. Creating {database_name}...')
        local_connection = sqlite3.connect(database_name)
        local_cursor = local_connection.cursor()
        local_cursor.execute("create table posts (file_name text, id text, title text, author text, content_text text, "
                             "subreddit text, url text, upvotes integer, time integer)")
        print(f"Database successfully created.")

    return local_connection, local_cursor


if __name__ == "__main__":
    # Initialize Reddit instance
    secrets = read_secrets("secrets.json")
    reddit = praw.Reddit(
        client_id=secrets["client_id"],
        client_secret=secrets["client_secret"],
        password=secrets["password"],
        user_agent=secrets["user_agent"],
        username=secrets["username"]
    )
    reddit.read_only = True

    # Initialize database connection
    connection, cursor = initialize_database_connection("reddit-post-archive.db")
