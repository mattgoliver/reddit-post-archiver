"""Reddit Post Archiver.

Author: Matthew Oliver
Version: 10/15/2023
"""
import access
import random


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

    Information archived: ID, title, author, content, subreddit, date, amount of upvotes

    Args:
        post (dict): Post to archive.
        file_name: Name of downloaded file to associate post information with.
    """
    pass


if __name__ == "__main__":
    archive_saved_posts("test")
