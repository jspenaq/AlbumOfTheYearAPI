import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup


class UserMethods:
    """
    A collection of methods to retrieve user profile data from Album of the Year.

    This class provides functionalities to fetch user statistics such as
    rating counts, review counts, list counts, follower counts, user "about"
    information, rating distribution, and lists of perfect scores and liked music
    by scraping the Album of the Year website.
    """

    def __init__(self):
        """
        Initializes the UserMethods class with default attributes.

        Attributes are set up to store user information, URLs, and parsed
        page content for subsequent data extraction.
        """
        self.user: str = ""
        self.url: str = ""
        self.user_url: str = "https://www.albumoftheyear.org/user/"
        self.user_page: BeautifulSoup = None

    def __set_user_page(self, user: str, url: str) -> None:
        """
        Sets up the user page for scraping by fetching and parsing the HTML.

        This private method is responsible for making the HTTP request to the
        user's page URL, reading the content, and parsing it with BeautifulSoup.

        Args:
            user (str): The username of the user.
            url (str): The URL of the user's page on Album of the Year.

        Returns:
            None

        Raises:
            URLError: If there's a problem with the network connection or URL.
            HTTPError: If the server returns an HTTP error status.
        """
        self.user = user
        self.url = url
        self.req = Request(self.url, headers={"User-Agent": "Mozilla/6.0"})
        ugly_user_page = urlopen(self.req).read()
        self.user_page = BeautifulSoup(ugly_user_page, "html.parser")

    def user_rating_count(self, user: str) -> str:
        """
        Retrieves the total number of ratings a user has submitted.

        Args:
            user (str): The username of the user.

        Returns:
            str: The count of user ratings as a string.
        """
        url = self.user_url + user
        if self.url != url or self.user_page is None:
            self.__set_user_page(user, url)

        ratings_section = self.user_page.find(
            href=f"/user/{self.user}/ratings/"
        )
        ratings = ratings_section.find(class_="profileStat").getText()
        return ratings

    def user_rating_count_json(self, user: str) -> str:
        """
        Retrieves a JSON string containing the total number of ratings a user has submitted.

        Args:
            user (str): The username of the user.

        Returns:
            str: A JSON string representing the count of user ratings.
        """
        ratings_JSON = {"ratings": self.user_rating_count(user)}
        return json.dumps(ratings_JSON)

    def user_review_count(self, user: str) -> str:
        """
        Retrieves the total number of reviews a user has written.

        Args:
            user (str): The username of the user.

        Returns:
            str: The count of user reviews as a string.
        """
        url = self.user_url + user
        if self.url != url or self.user_page is None:
            self.__set_user_page(user, url)

        reviews_section = self.user_page.find(
            href=f"/user/{self.user}/reviews/"
        )
        reviews = reviews_section.find(class_="profileStat").getText()
        return reviews

    def user_review_count_json(self, user: str) -> str:
        """
        Retrieves a JSON string containing the total number of reviews a user has written.

        Args:
            user (str): The username of the user.

        Returns:
            str: A JSON string representing the count of user reviews.
        """
        reviews_JSON = {"reviews": self.user_review_count(user)}
        return json.dumps(reviews_JSON)

    def user_list_count(self, user: str) -> str:
        """
        Retrieves the total number of lists a user has created.

        Args:
            user (str): The username of the user.

        Returns:
            str: The count of user lists as a string.
        """
        url = self.user_url + user
        if self.url != url or self.user_page is None:
            self.__set_user_page(user, url)

        lists_section = self.user_page.find(
            href=f"/user/{self.user}/lists/"
        )
        lists = lists_section.find(class_="profileStat").getText()
        return lists

    def user_list_count_json(self, user: str) -> str:
        """
        Retrieves a JSON string containing the total number of lists a user has created.

        Args:
            user (str): The username of the user.

        Returns:
            str: A JSON string representing the count of user lists.
        """
        lists_JSON = {"lists": self.user_list_count(user)}
        return json.dumps(lists_JSON)

    def user_follower_count(self, user: str) -> str:
        """
        Retrieves the total number of followers a user has.

        Args:
            user (str): The username of the user.

        Returns:
            str: The count of user followers as a string.
        """
        url = self.user_url + user
        if self.url != url or self.user_page is None:
            self.__set_user_page(user, url)

        followers_section = self.user_page.find(
            href=f"/user/{self.user}/followers/"
        )
        followers = followers_section.find(class_="profileStat").getText()
        return followers

    def user_follower_count_json(self, user: str) -> str:
        """
        Retrieves a JSON string containing the total number of followers a user has.

        Args:
            user (str): The username of the user.

        Returns:
            str: A JSON string representing the count of user followers.
        """
        followers_JSON = {"followers": self.user_follower_count(user)}
        return json.dumps(followers_JSON)

    def user_about(self, user: str) -> str:
        """
        Retrieves the "About Me" text from a user's profile.

        Args:
            user (str): The username of the user.

        Returns:
            str: The "About Me" text as a string.
        """
        url = self.user_url + user
        if self.url != url or self.user_page is None:
            self.__set_user_page(user, url)

        about = self.user_page.find(class_="aboutUser")
        if about is None:
            return ""
        return about.getText()

    def user_about_json(self, user: str) -> str:
        """
        Retrieves a JSON string containing the "About Me" text from a user's profile.

        Args:
            user (str): The username of the user.

        Returns:
            str: A JSON string representing the "About Me" text.
        """
        about_JSON = {"about_user": self.user_about(user)}
        return json.dumps(about_JSON)

    def user_rating_distribution(self, user: str) -> list[str]:
        """
        Retrieves the distribution of a user's ratings across different score ranges.

        The distribution is returned as a list of strings, where each string
        represents the count of ratings within a specific score range (e.g., 100, 90-99, etc.).

        Args:
            user (str): The username of the user.

        Returns:
            list[str]: A list of strings representing the rating counts for each score range.
        """
        url = self.user_url + user
        if self.url != url or self.user_page is None:
            self.__set_user_page(user, url)

        user_rating_distribution_tags = self.user_page.findAll(class_="distRow")

        user_rating_distribution = []
        for i in range(11):
            tag_content = user_rating_distribution_tags[i].getText()
            # Extract the number, assuming it's the last part after splitting by space
            # and strip any whitespace. If content is empty, default to "0".
            rating = tag_content.split()[-1].strip() if tag_content.strip() else "0"
            user_rating_distribution.append(rating)

        return user_rating_distribution

    def user_rating_distribution_json(self, user: str) -> str:
        """
        Retrieves a JSON string containing the distribution of a user's ratings.

        The JSON object maps score ranges (e.g., "100", "90-99") to the count
        of ratings within that range.

        Args:
            user (str): The username of the user.

        Returns:
            str: A JSON string representing the user's rating distribution.
        """
        user_rating_distribution = self.user_rating_distribution(user)

        user_rating_distribution_JSON = {
            "100": user_rating_distribution[0],
            "90-99": user_rating_distribution[1],
            "80-89": user_rating_distribution[2],
            "70-79": user_rating_distribution[3],
            "60-69": user_rating_distribution[4],
            "50-59": user_rating_distribution[5],
            "40-49": user_rating_distribution[6],
            "30-39": user_rating_distribution[7],
            "20-29": user_rating_distribution[8],
            "10-19": user_rating_distribution[9],
            "0-9": user_rating_distribution[10],
        }

        return json.dumps(user_rating_distribution_JSON)

    def user_ratings(self, user: str) -> str:
        """
        Retrieves a summary of a user's recent ratings.

        Note: This method currently returns the text content of a general
        "albumBlock" which might not be specific enough for individual ratings.
        Further parsing might be needed for detailed rating information.

        Args:
            user (str): The username of the user.

        Returns:
            str: A string containing a summary of user ratings.
        """
        url = self.user_url + user
        if self.url != url or self.user_page is None:
            self.__set_user_page(user, url)

        # This might need more specific parsing if individual ratings are desired.
        # Currently, it returns the text of the first albumBlock found.
        album_block = self.user_page.find(class_="albumBlock")
        if album_block is None:
            return ""
        return album_block.getText()

    def user_ratings_json(self, user: str) -> str:
        """
        Retrieves a JSON string containing a summary of a user's recent ratings.

        Args:
            user (str): The username of the user.

        Returns:
            str: A JSON string representing the summary of user ratings.
        """
        ratings_JSON = {"ratings": self.user_ratings(user)}
        return json.dumps(ratings_JSON)

    def user_perfect_scores(self, user: str) -> str:
        """
        Retrieves a string containing information about the albums a user has given perfect scores (100/100) to.

        If no perfect scores are found, an empty string is returned.

        Args:
            user (str): The username of the user.

        Returns:
            str: A string containing details of perfect scores, or an empty string if none.
        """
        url = self.user_url + user + "/ratings/perfect/"
        if self.url != url or self.user_page is None:
            self.__set_user_page(user, url)

        perfect_scores = self.user_page.find(class_="albumBlock")
        if perfect_scores is None:
            return ""
        return perfect_scores.getText()

    def user_perfect_scores_json(self, user: str) -> str:
        """
        Retrieves a JSON string containing information about the albums a user has given perfect scores to.

        Args:
            user (str): The username of the user.

        Returns:
            str: A JSON string representing the user's perfect scores.
        """
        perfect_sccores_json = {"perfect scores": self.user_perfect_scores(user)}
        return json.dumps(perfect_sccores_json)

    def user_liked_music(self, user: str) -> list[str]:
        """
        Retrieves a list of music (artist: album) that the user has liked.

        Args:
            user (str): The username of the user.

        Returns:
            list[str]: A list of strings, each representing a liked album in "Artist: Album" format.
        """
        url = self.user_url + user + "/liked/albums/"
        if self.url != url or self.user_page is None:
            self.__set_user_page(user, url)

        liked_music = self.user_page.find_all(class_="albumBlock")

        result = []
        for entry in liked_music:
            artist_element = entry.find(class_="artistTitle")
            album_element = entry.find(class_="albumTitle")

            artist = ""
            album = ""

            if artist_element:
                artist = artist_element.getText().encode("ascii", "ignore").decode().strip()
            if album_element:
                album = album_element.getText().encode("ascii", "ignore").decode().strip()
            
            if artist and album:
                combined = f"{artist}: {album}"
                result.append(combined)
            elif album: # If only album title is found
                result.append(album)


        return result

    def user_liked_music_json(self, user: str) -> str:
        """
        Retrieves a JSON string containing a list of music that the user has liked.

        Args:
            user (str): The username of the user.

        Returns:
            str: A JSON string representing the list of liked music.
        """
        liked_music_json = {"liked music": self.user_liked_music(user)}
        return json.dumps(liked_music_json)

