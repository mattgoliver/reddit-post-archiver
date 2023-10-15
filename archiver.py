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
import uuid  # Allows for generation of unique file names


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


def archive_saved_posts(upvote=False, limit=None, log=False):
    """Retrieves all saved posts from user's profile.

    Args:
        upvote (bool): Upvote post once archived, default=False
        limit (int): Amount of posts to retrieve, default=1000, max=1000
        log (bool): Print log messages, default = False

    Returns:
        dict: Dictionary containing post information.
    """
    for post in reddit.user.me().saved(limit=limit):
        if str(type(post)) == "<class 'praw.models.reddit.comment.Comment'>":  # Ignore saved comments
            continue

        file_name = download_post(post, log)

        archive(post, "test", log)


def download_post(post, log=False):
    """Downloads post at given url.

    Args:
          post: Post to download.
          log (bool): Print log messages, default = False

    Returns:
         tup: File name
    """
    file_name = ""

    post_exists = True
    while post_exists is True:
        file_name = str(uuid.uuid4().hex) + ".txt"

        if not os.path.isfile("./media/" + file_name):  # Check if file name already exists
            post_exists = False
            if log:
                print(f"DOWNLOAD: '{file_name}' is unique.")
        else:
            if log:
                print(f"DOWNLOAD: '{file_name}' already exists, regenerating.")

    return file_name


def archive(post, file_name, log=False):
    """Archives the post at the given url.

    Information archived: ID, title, author, content (text & media), subreddit, url, date, amount of upvotes

    Args:
        post: Post to archive.
        file_name: Name of downloaded file to associate post information with.
        log (bool): Print log messages, default = False
    """
    print(f"ARCHIVE: NOT FINISHED - Post title: {post.title}")


def initialize_database_connection(database_name, log=False):
    """Connects to the archive database, creates one if it doesn't exist.

    Args:
        database_name (str): Name of database to connect to.
        log (bool): Print log messages, default = False

    Returns:
        tup: Database connection and cursor
    """
    if os.path.isfile(database_name):
        local_connection = sqlite3.connect(database_name)
        local_cursor = local_connection.cursor()
        if log:
            print(f'SQLLite3: Database exists. Successfully connected to {database_name}')

    else:
        if log:
            print(f'SQLLite3: Database does not exist. Creating {database_name}...')
        local_connection = sqlite3.connect(database_name)
        local_cursor = local_connection.cursor()
        local_cursor.execute("create table posts (file_name text, id text, title text, author text, content_text text, "
                             "subreddit text, url text, upvotes integer, time integer)")
        if log:
            print(f"SQLLite3: Database successfully created.")

    return local_connection, local_cursor


def initialize_reddit_connection(log=False):
    """Connect to Reddit API via PRAW.

    Args:
        log (bool): Print log messages, default = False

    Returns:
        obj: Authenticated Reddit instance
    """
    secrets = read_secrets("secrets.json")
    reddit = praw.Reddit(
        client_id=secrets["client_id"],
        client_secret=secrets["client_secret"],
        password=secrets["password"],
        user_agent=secrets["user_agent"],
        username=secrets["username"]
    )
    if log:
        print(f"PRAW: Successfully authenticated as user: {reddit.user.me()}")

    return reddit


if __name__ == "__main__":
    # Initialize Reddit instance
    reddit = initialize_reddit_connection(log=True)

    # Initialize database connection
    # connection, cursor = initialize_database_connection("reddit-post-archive.db", log=True)

    # archive_saved_posts(limit=5)

    # Close database connection
    # connection.close()
    # print("SQLLite3: Database successfully closed.")
