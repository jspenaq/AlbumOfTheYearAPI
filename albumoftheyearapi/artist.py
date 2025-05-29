import json
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup


class ArtistMethods:
    """
    A collection of methods to retrieve artist-related data from Album of the Year.

    This class provides functionalities to fetch discographies, community scores,
    top songs, and other details for a given artist by scraping the
    Album of the Year website.
    """

    def __init__(self):
        """
        Initializes the ArtistMethods class with default attributes.

        Attributes are set up to store artist information, URLs, and parsed
        page content for subsequent data extraction.
        """
        self.artist = ""
        self.url = ""
        self.artist_url = "https://www.albumoftheyear.org/artist/"
        
        self.albums = []

    def __set_artist_page(self, artist: str, url: str) -> None:
        """
        Sets up the artist page for scraping by fetching and parsing the HTML.

        This private method is responsible for making the HTTP request to the
        artist's page URL, reading the content, and parsing it with BeautifulSoup.
        It also triggers the discography and community data extraction.

        Args:
            artist (str): The name of the artist.
            url (str): The URL of the artist's page on Album of the Year.

        Returns:
            None

        Raises:
            URLError: If there's a problem with the network connection or URL.
            HTTPError: If the server returns an HTTP error status.
        """
        self.artist = artist
        self.url = url
        self.req = Request(self.url, headers={"User-Agent": "Mozilla/6.0"})
        ugly_artist_page = urlopen(self.req).read()
        self.artist_page = BeautifulSoup(ugly_artist_page, "html.parser")
        self.__get_discography(artist)
        self.__get_community_data(artist)

    def __class_text(self, artist: str, class_name: str, url: str) -> str:
        """
        Extracts text content from a specific HTML element identified by its class name.

        This private helper method ensures the correct artist page is loaded
        before attempting to find and extract text from an element.

        Args:
            artist (str): The name of the artist.
            class_name (str): The CSS class name of the HTML element to find.
            url (str): The URL of the artist's page.

        Returns:
            str: The extracted text content from the specified element.
        """
        if self.url != url:
            self.__set_artist_page(artist, url)

        return self.artist_page.find(class_=class_name).getText()

    def __get_discography(self, artist: str) -> None:
        """
        Parses the artist's page to extract and categorize their discography.

        This private method identifies different types of releases (albums, mixtapes,
        EPs, singles) and similar artists by traversing the parsed HTML.
        The extracted data is stored in instance attributes.

        Args:
            artist (str): The name of the artist.

        Returns:
            None
        """
        url = self.artist_url + artist + "/"
        if self.url != url:
            self.__set_artist_page(artist, url)

        # Dictionary to store albums under their respective categories
        categorized_albums = {}

        # Find all h2 and div elements inside the artist page
        elements = self.artist_page.find_all(["h2", "div"])
        current_category = None  # To track which category the divs belong to

        for element in elements:
            if element.name == "h2":
                # New category found, update current_category
                current_category = element.get_text(strip=True)
                categorized_albums[current_category] = []  # Initialize list for this category
            elif element.name == "div" and current_category == "Similar Artists":
                # Similar Artists is structured differently
                album_title_div = element.find("div", class_="name")
                if album_title_div:
                    album_name = album_title_div.get_text().encode("ascii", "ignore").decode().strip()
                    categorized_albums[current_category].append(album_name)
            elif element.name == "div" and current_category:
                # For each category, loop through all divs to find the album title
                album_title_div = element.find("div", class_="albumTitle")
                if album_title_div:
                    album_name = album_title_div.get_text().encode("ascii", "ignore").decode().strip()
                    categorized_albums[current_category].append(album_name)
                
        self.albums = categorized_albums['Albums']
        self.mixtapes = categorized_albums['Mixtapes']
        self.eps = categorized_albums['EPs']
        # self.live_albums = categorized_albums['Live Albums'] # UNUSED
        # self.compilations = categorized_albums['Compilations'] # UNUSED
        self.singles = categorized_albums['SinglesView All']
        # self.appears_on = categorized_albums['Appears OnView All'] # UNUSED
        self.similar_artists_cat = categorized_albums['Similar Artists']

    def __get_community_data(self, artist: str) -> None:
        """
        Extracts community-related data, specifically top songs, from the artist's page.

        This private method iterates through table rows to find and store
        the titles of top songs as listed on the artist's page.

        Args:
            artist (str): The name of the artist.

        Returns:
            None
        """
        url = self.artist_url + artist + "/"
        if self.url != url:
            self.__set_artist_page(artist, url)

        # Find all <tr> elements
        rows = self.artist_page.find_all("tr")

        extracted_texts = []  # Store extracted text from <a> elements

        for row in rows:
            # Find the div with class "songAlbum" inside this row
            song_album_div = row.find("td", class_="songAlbum")
        
            if song_album_div:
                # Find the <a> tag inside this div
                link = song_album_div.find("a")
                if link:
                    text = link.get_text().strip()
                    extracted_texts.append(text)

        self.top_songs = extracted_texts

    def artist_albums(self, artist: str) -> list[str]:
        """
        Retrieves a list of studio albums by the specified artist.

        Args:
            artist (str): The name of the artist.

        Returns:
            list[str]: A list of album titles.
        """
        url = self.artist_url + artist + "/"
        if self.url != url:
            self.__set_artist_page(artist, url)
            
        return self.albums

    def artist_albums_json(self, artist: str) -> str:
        """
        Retrieves a JSON string containing a list of studio albums by the specified artist.

        Args:
            artist (str): The name of the artist.

        Returns:
            str: A JSON string representing the list of album titles.
        """
        albums_JSON = {"albums": self.artist_albums(artist)}
        return json.dumps(albums_JSON)

    def artist_mixtapes(self, artist: str) -> list[str]:
        """
        Retrieves a list of mixtapes by the specified artist.

        Args:
            artist (str): The name of the artist.

        Returns:
            list[str]: A list of mixtape titles.
        """
        url = self.artist_url + artist + "/"
        if self.url != url:
            self.__set_artist_page(artist, url)
            
        return self.mixtapes

    def artist_mixtapes_json(self, artist: str) -> str:
        """
        Retrieves a JSON string containing a list of mixtapes by the specified artist.

        Args:
            artist (str): The name of the artist.

        Returns:
            str: A JSON string representing the list of mixtape titles.
        """
        mixtapes_JSON = {"mixtapes": self.artist_mixtapes(artist)}
        return json.dumps(mixtapes_JSON)

    def artist_eps(self, artist: str) -> list[str]:
        """
        Retrieves a list of EPs (Extended Plays) by the specified artist.

        Args:
            artist (str): The name of the artist.

        Returns:
            list[str]: A list of EP titles.
        """
        url = self.artist_url + artist + "/"
        if self.url != url:
            self.__set_artist_page(artist, url)
            
        return self.eps

    def artist_eps_json(self, artist: str) -> str:
        """
        Retrieves a JSON string containing a list of EPs by the specified artist.

        Args:
            artist (str): The name of the artist.

        Returns:
            str: A JSON string representing the list of EP titles.
        """
        eps_JSON = {"eps": self.artist_eps(artist)}
        return json.dumps(eps_JSON)

    def artist_singles(self, artist: str) -> list[str]:
        """
        Retrieves a list of singles by the specified artist.

        Args:
            artist (str): The name of the artist.

        Returns:
            list[str]: A list of single titles.
        """
        url = self.artist_url + artist + "/"
        if self.url != url:
            self.__set_artist_page(artist, url)
        
        return self.singles

    def artist_singles_json(self, artist: str) -> str:
        """
        Retrieves a JSON string containing a list of singles by the specified artist.

        Args:
            artist (str): The name of the artist.

        Returns:
            str: A JSON string representing the list of single titles.
        """
        singles_JSON = {"singles": self.artist_singles(artist)}
        return json.dumps(singles_JSON)

    def artist_name(self, artist: str) -> str:
        """
        Retrieves the official name of the artist as displayed on the page.

        Args:
            artist (str): The name of the artist.

        Returns:
            str: The official artist name.
        """
        return self.__class_text(
            artist, "artistHeadline", self.artist_url + artist + "/"
        )

    def artist_name_json(self, artist: str) -> str:
        """
        Retrieves a JSON string containing the official name of the artist.

        Args:
            artist (str): The name of the artist.

        Returns:
            str: A JSON string representing the artist's name.
        """
        name_JSON = {"name": self.artist_name(artist)}
        return json.dumps(name_JSON)

    def artist_critic_score(self, artist: str) -> str:
        """
        Retrieves the average critic score for the artist.

        Args:
            artist (str): The name of the artist.

        Returns:
            str: The critic score as a string.
        """
        return self.__class_text(
            artist, "artistCriticScore", self.artist_url + artist + "/"
        )

    def artist_critic_score_json(self, artist: str) -> str:
        """
        Retrieves a JSON string containing the average critic score for the artist.

        Args:
            artist (str): The name of the artist.

        Returns:
            str: A JSON string representing the critic score.
        """
        critic_score_JSON = {"critic score": self.artist_critic_score(artist)}
        return json.dumps(critic_score_JSON)

    def artist_user_score(self, artist: str) -> str:
        """
        Retrieves the average user score for the artist.

        Args:
            artist (str): The name of the artist.

        Returns:
            str: The user score as a string.
        """
        return self.__class_text(
            artist, "artistUserScore", self.artist_url + artist + "/"
        )

    def artist_user_score_json(self, artist: str) -> str:
        """
        Retrieves a JSON string containing the average user score for the artist.

        Args:
            artist (str): The name of the artist.

        Returns:
            str: A JSON string representing the user score.
        """
        user_score_JSON = {"user score": self.artist_user_score(artist)}
        return json.dumps(user_score_JSON)

    def artist_total_score(self, artist: str) -> float:
        """
        Calculates the total average score for the artist (average of critic and user scores).

        Args:
            artist (str): The name of the artist.

        Returns:
            float: The calculated total average score.
        """
        return (
            int(self.artist_critic_score(artist)) + int(self.artist_user_score(artist))
        ) / 2

    def artist_total_score_json(self, artist: str) -> str:
        """
        Retrieves a JSON string containing the total average score for the artist.

        Args:
            artist (str): The name of the artist.

        Returns:
            str: A JSON string representing the total score.
        """
        total_score_JSON = {"total score": self.artist_total_score(artist)}
        return json.dumps(total_score_JSON)

    def artist_follower_count(self, artist: str) -> str:
        """
        Retrieves the number of followers the artist has on Album of the Year.

        Args:
            artist (str): The name of the artist.

        Returns:
            str: The follower count as a string.
        """
        return self.__class_text(artist, "followCount", self.artist_url + artist + "/")

    def artist_follower_count_json(self, artist: str) -> str:
        """
        Retrieves a JSON string containing the number of followers for the artist.

        Args:
            artist (str): The name of the artist.

        Returns:
            str: A JSON string representing the follower count.
        """
        follower_count_JSON = {"follower count": self.artist_follower_count(artist)}
        return json.dumps(follower_count_JSON)

    def artist_details(self, artist: str) -> str:
        """
        Retrieves general details or a summary about the artist.

        Args:
            artist (str): The name of the artist.

        Returns:
            str: A string containing general artist details.
        """
        return self.__class_text(
            artist, "artistTopBox info", self.artist_url + artist + "/"
        )

    def artist_details_json(self, artist: str) -> str:
        """
        Retrieves a JSON string containing general details about the artist.

        Args:
            artist (str): The name of the artist.

        Returns:
            str: A JSON string representing the artist's details.
        """
        artist_details_JSON = {"artist details": self.artist_details(artist)}
        return json.dumps(artist_details_JSON)

    def artist_top_songs(self, artist: str) -> list[str]:
        """
        Retrieves a list of top songs by the specified artist.

        Args:
            artist (str): The name of the artist.

        Returns:
            list[str]: A list of top song titles.
        """
        url = self.artist_url + artist + "/"
        if self.url != url:
            self.__set_artist_page(artist, url)
            
        return self.top_songs

    def artist_top_songs_json(self, artist: str) -> str:
        """
        Retrieves a JSON string containing a list of top songs by the specified artist.

        Args:
            artist (str): The name of the artist.

        Returns:
            str: A JSON string representing the list of top song titles.
        """
        artist_top_songs_JSON = {"top songs": self.artist_top_songs(artist)}
        return json.dumps(artist_top_songs_JSON)

    def similar_artists(self, artist: str) -> list[str]:
        """
        Retrieves a list of artists similar to the specified artist.

        Args:
            artist (str): The name of the artist.

        Returns:
            list[str]: A list of similar artist names.
        """
        url = self.artist_url + artist + "/"
        if self.url != url:
            self.__set_artist_page(artist, url)
            
        return self.similar_artists_cat

    def similar_artists_json(self, artist: str) -> str:
        """
        Retrieves a JSON string containing a list of artists similar to the specified artist.

        Args:
            artist (str): The name of the artist.

        Returns:
            str: A JSON string representing the list of similar artist names.
        """
        similar_artists_JSON = {"similar artists": self.similar_artists(artist)}
        return json.dumps(similar_artists_JSON)
