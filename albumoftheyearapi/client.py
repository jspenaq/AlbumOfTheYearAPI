""" All methods used to get site data """

from albumoftheyearapi.user import UserMethods
from albumoftheyearapi.artist import ArtistMethods
from albumoftheyearapi.album import AlbumMethods


class AOTY(UserMethods, ArtistMethods, AlbumMethods):
    """
    A lightweight Python library that acts as an API for https://www.albumoftheyear.org.

    This class inherits methods from UserMethods, ArtistMethods, and AlbumMethods
    to provide a comprehensive interface for interacting with the Album of the Year website.
    """

    def __init__(self) -> None:
        """
        Initializes the AOTY client with default attributes.

        These attributes store base URLs and other configuration details
        required for scraping and data retrieval from the Album of the Year website.
        They are also set up to facilitate easier caching of page content.
        """
        self.user: str = ""
        self.artist: str = ""
        self.url: str = ""
        self.user_url: str = "https://www.albumoftheyear.org/user/"
        self.artist_url: str = "https://www.albumoftheyear.org/artist/"
        self.upcoming_album_class: str = "albumBlock five small"
        self.aoty_albums_per_page: int = 60
        self.page_limit: int = 21
