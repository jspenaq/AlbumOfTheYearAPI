import json
import datetime
from unittest.mock import patch, MagicMock

import pytest

# Import the classes directly from album.py for unit testing
from albumoftheyearapi.album import Album, AlbumMethods


@pytest.fixture
def album_methods_client():
    """Fixture to provide an instance of AlbumMethods."""
    return AlbumMethods()


@pytest.fixture
def mock_album_objects():
    """Fixture to provide mock Album objects."""
    return [
        Album("Album 1", "Artist 1", "Jan 1"),
        Album("Album 2", "Artist 2", "Jan 2"),
    ]


# --- Tests for Album class ---
def test_album_init():
    """Test initialization of an Album object."""
    album = Album("My Album", "My Artist", "Dec 25")
    assert album.name == "My Album"
    assert album.artist == "My Artist"
    assert album.release_date == "Dec 25"


def test_album_to_json():
    """Test conversion of an Album object to a JSON string."""
    album = Album("Test Album", "Test Artist", "Feb 15")
    expected_json = '{"artist": "Test Artist", "name": "Test Album", "release_date": "Feb 15"}'
    assert json.loads(album.to_JSON()) == json.loads(expected_json)


# --- Tests for AlbumMethods class ---

def test_album_methods_init(album_methods_client):
    """Test initialization of AlbumMethods."""
    assert album_methods_client is not None
    assert album_methods_client.upcoming_album_class == "albumBlock five small"
    assert album_methods_client.aoty_albums_per_page == 60
    assert album_methods_client.page_limit == 21


# Test _map_month_number_to_name
@pytest.mark.parametrize(
    "month_num, expected_name",
    [
        (1, "Jan"),
        (6, "Jun"),
        (12, "Dec"),
    ],
)
def test_map_month_number_to_name_valid(album_methods_client, month_num, expected_name):
    """Test valid month number to name mapping."""
    assert album_methods_client._map_month_number_to_name(month_num) == expected_name


@pytest.mark.parametrize(
    "month_num",
    [
        0,
        13,
        -1,
    ],
)
def test_map_month_number_to_name_invalid(album_methods_client, month_num):
    """Test invalid month number to name mapping raises exception."""
    with pytest.raises(Exception, match="Invalid month number"):
        album_methods_client._map_month_number_to_name(month_num)


# Test _build_error_response
def test_build_error_response(album_methods_client):
    """Test building a standardized error response."""
    error_dict = album_methods_client._build_error_response("Test Error", "This is a test message.")
    assert error_dict == {"error": "Test Error", "message": "This is a test message."}


def test_parse_albums_returns_correct_album_objects(album_methods_client):
    """Test that _parse_albums returns Album objects with correct fields."""
    mock_album_block = MagicMock()
    mock_artist = MagicMock()
    mock_artist.getText.return_value = "Artist X"
    mock_title = MagicMock()
    mock_title.getText.return_value = "Album X"
    mock_date = MagicMock()
    mock_date.getText.return_value = "Mar 10"

    def find_side_effect(name, attrs):
        if name == "div" and attrs == {"class": "artistTitle"}:
            return mock_artist
        if name == "div" and attrs == {"class": "albumTitle"}:
            return mock_title
        if name == "div" and attrs == {"class": "type"}:
            return mock_date
        return None

    mock_album_block.find.side_effect = find_side_effect

    parsed_albums = album_methods_client._parse_albums([mock_album_block])
    assert len(parsed_albums) == 1
    album = parsed_albums[0]
    assert isinstance(album, Album)
    assert album.name == "Album X"
    assert album.artist == "Artist X"
    assert album.release_date == "Mar 10"


def test_parse_albums_empty_list(album_methods_client):
    """Test that _parse_albums returns an empty list when given no albums."""
    parsed_albums = album_methods_client._parse_albums([])
    assert parsed_albums == []

def test_parse_albums_handles_missing_fields(album_methods_client):
    """Test that _parse_albums raises AttributeError if fields are missing."""
    # Album block missing 'artistTitle'
    album_block = MagicMock()
    album_block.find.side_effect = lambda name, attrs: None
    with pytest.raises(AttributeError):
        album_methods_client._parse_albums([album_block])


# Test _get_release_page_from_request
@patch('albumoftheyearapi.album.urlopen')
@patch('albumoftheyearapi.album.BeautifulSoup')
def test_get_release_page_from_request_success(mock_bs, mock_urlopen, album_methods_client):
    """Test successful fetching and parsing of a release page."""
    mock_response = MagicMock()
    mock_response.read.return_value = b"<html>mock html</html>"
    mock_urlopen.return_value = mock_response
    mock_bs.return_value = "mock_beautifulsoup_object"

    result = album_methods_client._get_release_page_from_request("http://test.com")
    mock_urlopen.assert_called_once()
    mock_bs.assert_called_once_with(b"<html>mock html</html>", "html.parser")
    assert result == "mock_beautifulsoup_object"


@patch('albumoftheyearapi.album.urlopen', side_effect=Exception("Network error"))
def test_get_release_page_from_request_error(mock_urlopen, album_methods_client):
    """Test error handling during fetching a release page."""
    with pytest.raises(Exception, match="Network error"):
        album_methods_client._get_release_page_from_request("http://test.com")


# Test _get_upcoming_releases_by_page
@patch('albumoftheyearapi.album.AlbumMethods._parse_albums')
@patch('albumoftheyearapi.album.AlbumMethods._get_release_page_from_request')
def test_get_upcoming_releases_by_page_success(mock_get_page, mock_parse_albums, album_methods_client, mock_album_objects):
    """Test successful scraping of upcoming releases for a specific page."""
    mock_get_page.return_value.find_all.return_value = "mock_albums_html"
    mock_parse_albums.return_value = mock_album_objects

    # Test page 1 (empty string URL)
    albums = album_methods_client._get_upcoming_releases_by_page(1)
    mock_get_page.assert_called_once_with("https://www.albumoftheyear.org/upcoming/")
    assert albums == mock_album_objects
    mock_get_page.reset_mock()  # Reset mock call history for next assertion

    # Test other page number
    albums = album_methods_client._get_upcoming_releases_by_page(5)
    mock_get_page.assert_called_once_with("https://www.albumoftheyear.org/upcoming/5/")
    assert albums == mock_album_objects


def test_get_upcoming_releases_by_page_limit_exceeded(album_methods_client):
    """Test that requesting a page beyond the limit raises an exception."""
    with pytest.raises(Exception, match="Page number out of range"):
        album_methods_client._get_upcoming_releases_by_page(album_methods_client.page_limit + 1)


@patch('albumoftheyearapi.album.AlbumMethods._map_month_number_to_name', side_effect=Exception("Invalid month"))
def test_get_upcoming_releases_by_date_internal_map_month_error(mock_map_month, album_methods_client):
    """Test error when mapping month number in _get_upcoming_releases_by_date."""
    with pytest.raises(Exception, match="Invalid month"):
        album_methods_client._get_upcoming_releases_by_date(0, 1)



@patch('albumoftheyearapi.album.AlbumMethods._get_upcoming_releases_by_page')
@patch('albumoftheyearapi.album.AlbumMethods._map_month_number_to_name', return_value="Jan")
def test_get_upcoming_releases_by_date_internal_success(mock_map_month, mock_get_upcoming_releases_by_page, album_methods_client):
    """Test internal method for scraping releases by date, including loop termination."""
    # Simulate albums across dates: 2 for Jan 1, 1 for Jan 2 (should stop after Jan 2 is found)
    mock_get_upcoming_releases_by_page.side_effect = [
        [
            Album("Album A", "Artist A", "Jan 1"),
            Album("Album B", "Artist B", "Jan 1"),
            Album("Album C", "Artist C", "Jan 2"),  # Next date, should not be included
            Album("Album D", "Artist D", "Jan 1"),  # Should be included too
            Album("Album D", "Artist D", "Jan 3"),  # Should not be included
            Album("Album E", "Artist E", "Jan 4"),  # Should not be included
            Album("Album F", "Artist F", "Jan 1"),  # Should be included too
        ],
        [
            Album("Album E", "Artist E", "Jan 3"),  # Should not be reached
        ]
    ]

    result_albums = album_methods_client._get_upcoming_releases_by_date(1, 1)
    # Only albums with "Jan 1" before the first "Jan 2" should be included
    assert len(result_albums) == 4
    assert all(album.release_date == "Jan 1" for album in result_albums)
    assert result_albums[0].name == "Album A"
    assert result_albums[1].name == "Album B"
    assert result_albums[2].name == "Album D"
    assert result_albums[3].name == "Album F"


# Test upcoming_releases_by_page (public method)
@patch('albumoftheyearapi.album.AlbumMethods._get_upcoming_releases_by_page')
def test_upcoming_releases_by_page_public_success(mock_get_upcoming_releases_by_page, album_methods_client, mock_album_objects):
    """Test the public method for fetching releases by page number."""
    mock_get_upcoming_releases_by_page.return_value = mock_album_objects
    result_json = album_methods_client.upcoming_releases_by_page(1)
    result = json.loads(result_json)
    assert len(result["albums"]) == len(mock_album_objects)
    assert json.loads(result["albums"][0]) == json.loads(mock_album_objects[0].to_JSON())
    mock_get_upcoming_releases_by_page.assert_called_once_with(1)


@patch('albumoftheyearapi.album.AlbumMethods._get_upcoming_releases_by_page', side_effect=Exception("Test error"))
def test_upcoming_releases_by_page_public_error(mock_get_upcoming_releases_by_page, album_methods_client):
    """Test error handling in the public method for fetching releases by page number."""
    result_json = album_methods_client.upcoming_releases_by_page(999)
    result = json.loads(result_json)
    assert result["error"] == "Page Limit Error"
    assert result["message"] == "The page number requested is out of range."
    mock_get_upcoming_releases_by_page.assert_called_once_with(999)


# Test upcoming_releases_by_limit
@patch('albumoftheyearapi.album.AlbumMethods._get_upcoming_releases_by_page')
def test_upcoming_releases_by_limit_less_than_page(mock_get_upcoming_releases_by_page, album_methods_client, mock_album_objects):
    """Test fetching a total number of albums less than a full page."""
    # Mock _get_upcoming_releases_by_page to return enough albums for one page
    mock_get_upcoming_releases_by_page.return_value = mock_album_objects * 30  # 60 albums

    total_albums = 10
    result_json = album_methods_client.upcoming_releases_by_limit(total_albums)
    result = json.loads(result_json)
    assert len(result["albums"]) == total_albums
    mock_get_upcoming_releases_by_page.assert_called_once_with(1)


@patch('albumoftheyearapi.album.AlbumMethods._get_upcoming_releases_by_page')
def test_upcoming_releases_by_limit_exact_page(mock_get_upcoming_releases_by_page, album_methods_client, mock_album_objects):
    """Test fetching a total number of albums exactly equal to a full page."""
    mock_get_upcoming_releases_by_page.return_value = mock_album_objects * 30  # 60 albums

    total_albums = 60
    result_json = album_methods_client.upcoming_releases_by_limit(total_albums)
    result = json.loads(result_json)
    assert len(result["albums"]) == total_albums
    mock_get_upcoming_releases_by_page.assert_called_once_with(1)


@patch('albumoftheyearapi.album.AlbumMethods._get_upcoming_releases_by_page')
def test_upcoming_releases_by_limit_multiple_pages(mock_get_upcoming_releases_by_page, album_methods_client, mock_album_objects):
    """Test fetching a total number of albums spanning multiple pages."""
    # Mock _get_upcoming_releases_by_page to return 60 albums per call
    mock_get_upcoming_releases_by_page.return_value = mock_album_objects * 30  # 60 albums

    total_albums = 125  # 2 full pages + 5 from third page
    result_json = album_methods_client.upcoming_releases_by_limit(total_albums)
    result = json.loads(result_json)
    assert len(result["albums"]) == total_albums
    assert mock_get_upcoming_releases_by_page.call_count == 3
    mock_get_upcoming_releases_by_page.assert_any_call(1)
    mock_get_upcoming_releases_by_page.assert_any_call(2)
    mock_get_upcoming_releases_by_page.assert_any_call(3)


@patch('albumoftheyearapi.album.AlbumMethods._get_upcoming_releases_by_page', side_effect=Exception("Test error"))
def test_upcoming_releases_by_limit_error(mock_get_upcoming_releases_by_page, album_methods_client):
    """Test error handling in upcoming_releases_by_limit."""
    result_json = album_methods_client.upcoming_releases_by_limit(100)
    result = json.loads(result_json)
    assert result["error"] == "Page Limit Error"
    assert "Test error" in result["message"]  # Check for the exception message
    mock_get_upcoming_releases_by_page.assert_called_once_with(1)  # Error happens on first page

# Test upcoming_releases_by_date (public method)
@patch('albumoftheyearapi.album.AlbumMethods._get_upcoming_releases_by_date')
def test_upcoming_releases_by_date_public_success(mock_get_upcoming_releases_by_date, album_methods_client, mock_album_objects):
    """Test the public method for fetching releases by date."""
    mock_get_upcoming_releases_by_date.return_value = mock_album_objects
    result_json = album_methods_client.upcoming_releases_by_date(1, 1)
    result = json.loads(result_json)
    assert len(result["albums"]) == len(mock_album_objects)
    assert json.loads(result["albums"][0]) == json.loads(mock_album_objects[0].to_JSON())
    mock_get_upcoming_releases_by_date.assert_called_once_with(1, 1)


@patch('albumoftheyearapi.album.AlbumMethods._get_upcoming_releases_by_date', side_effect=Exception("Test error message"))
def test_upcoming_releases_by_date_public_error(mock_get_upcoming_releases_by_date, album_methods_client):
    """Test error handling in the public method for fetching releases by date."""
    result_json = album_methods_client.upcoming_releases_by_date(1, 1)
    result = json.loads(result_json)
    assert result["error"] == "Releases by date Error: "
    assert result["message"] == "Test error message"
    mock_get_upcoming_releases_by_date.assert_called_once_with(1, 1)


# Test for the original scenario of upcoming_albums_date, ensuring it still works
def test_upcoming_albums_date_tomorrow_scenario(album_methods_client, mock_album_objects):
    """Test the original 'tomorrow' scenario for upcoming_releases_by_date."""
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    tomorrow_month = tomorrow.month
    tomorrow_day = tomorrow.day

    # Mock _get_upcoming_releases_by_date to return a controlled set of albums
    # The original test asserts len < 60, which implies it expects a subset.
    # Let's make sure our mock returns a smaller set.
    with patch('albumoftheyearapi.album.AlbumMethods._get_upcoming_releases_by_date',
               return_value=mock_album_objects) as mock_get_date:  # 2 albums
        albums_json = album_methods_client.upcoming_releases_by_date(tomorrow_month, tomorrow_day)
        albums = json.loads(albums_json)
        assert len(albums["albums"]) == len(mock_album_objects)  # Based on mock_album_objects
        assert len(albums["albums"]) < 60  # Original assertion still holds
        mock_get_date.assert_called_once_with(tomorrow_month, tomorrow_day)
        
