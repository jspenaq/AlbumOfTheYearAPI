import json
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup


class Album:
    """
    Represents an album with its name, artist, and release date.
    """

    def __init__(self, name: str, artist: str, date: str):
        """
        Initializes an Album object.

        Args:
            name (str): The name of the album.
            artist (str): The artist of the album.
            date (str): The release date of the album (e.g., "Jan 1").
        """
        self.name = name
        self.artist = artist
        self.release_date = date

    def to_JSON(self) -> str:
        """
        Converts the Album object into a JSON string.

        Returns:
            str: A JSON string representation of the Album object.
        """
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=0)


class AlbumMethods:
    """
    Provides methods to fetch and parse album data from the Album of the Year website.
    This class handles web scraping logic to retrieve upcoming album releases.
    """

    def __init__(self):
        """
        Initializes the AlbumMethods class with configuration for web scraping.
        Sets the CSS class for identifying album blocks, the number of albums per page,
        and a hardcoded page limit to prevent excessive scraping.
        """
        self.upcoming_album_class = "albumBlock five small"
        self.aoty_albums_per_page = 60
        self.page_limit = 21

    def upcoming_releases_by_limit(self, total: int) -> str:
        """
        Fetches a specified total number of upcoming album releases.
        It calculates the number of pages needed and scrapes them sequentially
        until the desired total is met or the page limit is reached.

        Args:
            total (int): The total number of upcoming albums to retrieve.

        Returns:
            str: A JSON string containing a list of Album objects, or an error message
                 if the requested total exceeds the scraping page limit or an error occurs.
        """
        min_page_number = 1
        max_page_number = total // self.aoty_albums_per_page
        if total % self.aoty_albums_per_page != 0:
            max_page_number += 1
        upcoming_albums = {}
        albums = []
        counter = total
        for page_number in range(min_page_number, max_page_number + 1):
            try:
                if counter < self.aoty_albums_per_page:
                    albums += self._get_upcoming_releases_by_page(page_number)[:counter]
                else:
                    albums += self._get_upcoming_releases_by_page(page_number)
                    counter -= self.aoty_albums_per_page
            except Exception as e:
                return json.dumps(
                    self._build_error_response(
                        "Page Limit Error",
                        "Number of albums exceeded page limit. Exception raise: ." + str(e),
                    )
                )
        json_albums = [album.to_JSON() for album in albums]
        upcoming_albums["albums"] = json_albums
        return json.dumps(upcoming_albums)

    def upcoming_releases_by_page(self, page_number: int) -> str:
        """
        Fetches upcoming album releases for a specific page number.

        Args:
            page_number (int): The page number to retrieve.

        Returns:
            str: A JSON string containing a list of Album objects for the specified page,
                 or an error message if the page number is out of range.
        """
        upcoming_albums = {}
        try:
            parsed_albums = self._get_upcoming_releases_by_page(page_number)
        except:
            return json.dumps(
                self._build_error_response(
                    "Page Limit Error", "The page number requested is out of range."
                )
            )
        json_albums = [album.to_JSON() for album in parsed_albums]
        upcoming_albums["albums"] = json_albums
        return json.dumps(upcoming_albums)

    def upcoming_releases_by_date(self, month: int, day: int) -> str:
        """
        Fetches upcoming album releases for a specific date.
        It scrapes pages until all albums for the target date are found,
        and stops when an album from the next day is encountered.

        Args:
            month (int): The month number (1-12).
            day (int): The day of the month.

        Returns:
            str: A JSON string containing a list of Album objects for the specified date,
                 or an error message if an issue occurs during scraping or date mapping.
        
        Raises:
            
        """
        upcoming_albums = {}
        try:
            parsed_albums = self._get_upcoming_releases_by_date(month, day)
        except Exception as e:
            return json.dumps(
                self._build_error_response("Releases by date Error: ", str(e))
            )
        json_albums = [album.to_JSON() for album in parsed_albums]
        upcoming_albums["albums"] = json_albums
        return json.dumps(upcoming_albums)

    def _get_upcoming_releases_by_date(self, month: int, day: int) -> list[Album]:
        """
        Internal method to scrape upcoming releases for a specific date.
        It iterates through pages, collecting albums until it finds an album
        from the day after the target date, indicating all relevant albums have been found.

        Args:
            month (int): The month number (1-12).
            day (int): The day of the month.

        Returns:
            list[Album]: A list of Album objects released on the target date.

        Raises:
            Exception: If the month number is invalid or a scraping error occurs.
        """
        month_name = self._map_month_number_to_name(month)
        target_date = (month_name + " " + str(day)).strip()
        next_date = (month_name + " " + str(day + 1)).strip()
        page_number = 1
        result_albums = []

        complete = False
        while not complete:
            albums = self._get_upcoming_releases_by_page(page_number)
            for album in albums:
                if album.release_date == target_date:
                    result_albums.append(album)

                if album.release_date == next_date:
                    complete = True
            page_number += 1
        return result_albums

    def _build_error_response(self, error_type: str, msg: str) -> dict:
        """
        Internal method to build a standardized error response dictionary.

        Args:
            error_type (str): The type of error (e.g., "Page Limit Error").
            msg (str): A detailed error message.

        Returns:
            dict: A dictionary containing error type and message.
        """
        error_dict = {"error": error_type, "message": msg}
        return error_dict

    def _map_month_number_to_name(self, month_number: int) -> str:
        """
        Internal method to convert a month number to its three-letter abbreviation.

        Args:
            month_number (int): The month number (1-12).

        Returns:
            str: The three-letter abbreviation of the month (e.g., "Jan", "Feb").

        Raises:
            Exception: If the month number is invalid (not between 1 and 12).
        """
        month_names = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]
        if not 1 <= month_number <= 12:
            raise Exception("Invalid month number")
        return month_names[month_number - 1]

    def _get_upcoming_releases_by_page(self, page_number: int) -> list[Album]:
        """
        Internal method to scrape upcoming releases from a specific page on Album of the Year.
        Constructs the URL for the given page number and then fetches and parses its content.

        Args:
            page_number (int): The page number to scrape.

        Returns:
            list[Album]: A list of Album objects found on the specified page.

        Raises:
            Exception: If the page number exceeds the defined page limit.
        """
        if page_number > self.page_limit:
            raise Exception("Page number out of range")
        url = "https://www.albumoftheyear.org/upcoming/" + (str(page_number) + "/" if page_number > 1 else "")
        page = self._get_release_page_from_request(url)
        albums = page.find_all("div", {"class": self.upcoming_album_class})
        parsed_albums = self._parse_albums(albums)
        return parsed_albums

    def _get_release_page_from_request(self, url: str) -> BeautifulSoup:
        """
        Internal method to fetch and parse an HTML page from a given URL.
        It uses urllib.request to make the HTTP request and BeautifulSoup to parse the HTML.

        Args:
            url (str): The URL of the page to fetch.

        Returns:
            BeautifulSoup: A BeautifulSoup object representing the parsed HTML content.

        Raises:
            URLError: If there's an issue with the network request (e.g., invalid URL, connection error).
        """
        request = Request(url, headers={"User-Agent": "Mozilla/6.0"})
        unparsed_page = urlopen(request).read()
        release_page = BeautifulSoup(unparsed_page, "html.parser")
        return release_page

    def _parse_albums(self, unparsed_albums: list) -> list[Album]:
        """
        Parses a list of BeautifulSoup tag objects (representing raw album HTML blocks)
        into a list of Album objects. Extracts artist, title, and date from each block.

        Args:
            unparsed_albums (list): A list of BeautifulSoup tag objects, each containing
                                    the HTML structure for an album.

        Returns:
            list[Album]: A list of Album objects, each populated with extracted data.
        """
        parsed_albums = []
        for album in unparsed_albums:
            artist = str(album.find("div", {"class": "artistTitle"}).getText())
            title = str(album.find("div", {"class": "albumTitle"}).getText())
            date = str(album.find("div", {"class": "type"}).getText())
            parsed_albums.append(Album(title, artist, date))
        return parsed_albums
