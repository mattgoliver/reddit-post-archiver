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
import urllib.request  # Allows for media downloading
import requests  # Allows for retrieval of media type given URL
import mimetypes  # Allows for retrieval of media type given URL
import progressbar  # Allows for progress bar for downloads
import time

pbar = None


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

        file_name = download(post, log)  # Download file and grab file name

        if file_name is None:  # Continue to next post if there was no file to download
            continue

        print(f"MAIN: Download successful, filename: '{file_name[8:]}'")

        archive(post, file_name, log)


def download(post, log=False):
    """Downloads post at given url.

    Args:
          post: Post to download.
          log (bool): Print log messages, default = False

    Returns:
         tup: File name
    """
    file_name = ""
    url = post.url

    # Retrieve file type
    response = requests.get(url)
    content_type = response.headers['content-type']
    file_type = mimetypes.guess_extension(content_type)

    # Return None if there is no file to download
    if file_type is None:
        print(f"DOWNLOAD: Error with post: '{post.title}', no media to download.")
        return None

    if log:
        print(f"DOWNLOAD: Downloading post: '{post.title}', file type: '{file_type}'.")

    # Loop until unique file name is generated
    post_exists = True
    while post_exists is True:
        file_name = "./media/" + str(uuid.uuid4().hex) + file_type

        if not os.path.isfile(file_name):  # Check if file name already exists
            post_exists = False

    # Download file
    urllib.request.urlretrieve(url, file_name, show_progress)

    return file_name


def archive(post, file_name, log=False):
    """Archives the post at the given url.

    Information archived: ID, title, author, content (text & media), subreddit, url, date, amount and ratio of upvotes

    Args:
        post: Post to archive.
        file_name: Name of downloaded file to associate post information with.
        log (bool): Print log messages, default = False
    """
    # Find the subscriber count of the post's subreddit
    subreddit_size = int(reddit.subreddit(str(post.subreddit)).subscribers)

    if log:
        print(f"ARCHIVE: ID: {post.id}, Title: {post.title}, Author: {post.author}, Text: {post.selftext}, "
              f"Subreddit: {post.subreddit}, Subreddit Size: {subreddit_size}, Upvotes: {post.score}, "
              f"Ratio: {post.upvote_ratio}, File name: {file_name}, URL: {post.url}, Created: {post.created_utc}")

    # Add post data to the database
    cursor.execute(
        f"insert into posts values ('{post.id}', '{post.title}', '{post.author}', '{post.selftext}', "
        f"'{post.subreddit}', {subreddit_size}, {post.score}, {post.upvote_ratio}, '{file_name}', '{post.url}', "
        f"{post.created_utc})"
    )

    print(f"ARCHIVE: '{post.title}' successfully added to the archive.")


def show_progress(block_num, block_size, total_size):
    # Solution from: https://stackoverflow.com/questions/37748105/how-to-use-progressbar-module-with-urlretrieve
    global pbar
    if pbar is None:
        pbar = progressbar.ProgressBar(maxval=total_size)
        pbar.start()

    downloaded = block_num * block_size
    if downloaded < total_size:
        pbar.update(downloaded)
    else:
        pbar.finish()
        pbar = None


def initialize_database_connection(database_name, log=False):
    """Connects to the archive database, creates one if it doesn't exist.

    Args:
        database_name (str): Name of database to connect to.
        log (bool): Print log messages, default = False

    Returns:
        tup: Database connection and cursor
    """
    # If the database exists, then connect to it
    if os.path.isfile(database_name):
        local_connection = sqlite3.connect(database_name)
        local_cursor = local_connection.cursor()
        if log:
            print(f'SQLLite3: Database exists. Successfully connected to {database_name}')

    # If the database does not exist, then create it and connect to it
    else:
        if log:
            print(f'SQLLite3: Database does not exist. Creating {database_name}...')
        local_connection = sqlite3.connect(database_name)
        local_cursor = local_connection.cursor()
        local_cursor.execute("create table posts (id text, title text, author text, content_text text, "
                             "subreddit text, subreddit_size integer, upvotes integer, ratio integer, "
                             "file_name text, url text, created integer)")
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
    connection, cursor = initialize_database_connection("reddit-post-archive.db", log=True)

    archive_saved_posts(limit=3, log=True)

    # Close database connection
    connection.close()
    print("SQLLite3: Database successfully closed.")
