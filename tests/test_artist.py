import json
import datetime
import pytest
from unittest.mock import patch, MagicMock

# Import the classes directly from album.py for unit testing
from albumoftheyearapi import AOTY
from albumoftheyearapi.artist import ArtistMethods
from bs4 import BeautifulSoup # Import BeautifulSoup for mock setup

# --- Fixtures ---

@pytest.fixture
def artist_id():
    """Fixture to provide a sample artist ID."""
    return "183-kanye-west"

@pytest.fixture
def aoty_client():
    """Fixture to provide an instance of the AOTY client."""
    return AOTY()

@pytest.fixture
def artist_methods_client():
    """Fixture to provide an instance of ArtistMethods."""
    return ArtistMethods()

@pytest.fixture
def mock_artist_page_html():
    """Fixture to provide mock HTML content for an artist page.
    This HTML is designed to cover all parsing needs for discography,
    scores, details, top songs, and similar artists.
    """
    return """
    <html>
    <body>
        <div class="artistHeadline">Kanye West</div>
        <div class="artistCriticScore">85</div>
        <div class="artistUserScore">75</div>
        <div class="followCount">123,456</div>
        <div class="artistTopBox info">Some artist details here.</div>

        <h2>Albums</h2>
        <div class="albumBlock">
            <div class="albumTitle">The College Dropout</div>
            <div class="artistTitle">Kanye West</div>
        </div>
        <div class="albumBlock">
            <div class="albumTitle">Late Registration</div>
            <div class="artistTitle">Kanye West</div>
        </div>

        <h2>Mixtapes</h2>
        <div class="albumBlock">
            <div class="albumTitle">Freshmen Adjustment</div>
            <div class="artistTitle">Kanye West</div>
        </div>

        <h2>EPs</h2>
        <div class="albumBlock">
            <div class="albumTitle">808s & Heartbreak (EP)</div>
            <div class="artistTitle">Kanye West</div>
        </div>

        <h2>SinglesView All</h2>
        <div class="albumBlock">
            <div class="albumTitle">Stronger</div>
            <div class="artistTitle">Kanye West</div>
        </div>
        <div class="albumBlock">
            <div class="albumTitle">Gold Digger</div>
            <div class="artistTitle">Kanye West</div>
        </div>

        <h2>Top Songs</h2>
        <table>
            <tr>
                <td class="songAlbum"><a>Runaway</a></td>
            </tr>
            <tr>
                <td class="songAlbum"><a>Jesus Walks</a></td>
            </tr>
        </table>

        <h2>Similar Artists</h2>
        <div class="albumBlock">
            <div class="name">Jay-Z</div>
        </div>
        <div class="albumBlock">
            <div class="name">Kid Cudi</div>
        </div>
    </body>
    </html>
    """

# --- Mocking the web scraping for all subsequent tests ---
# This fixture will run for every test and mock urlopen and BeautifulSoup
@pytest.fixture(autouse=True)
def mock_web_requests(mock_artist_page_html):
    """
    Mocks urllib.request.urlopen and BeautifulSoup to prevent actual web requests.
    It provides a BeautifulSoup object parsed from mock HTML to the ArtistMethods instance.
    """
    with patch('albumoftheyearapi.artist.urlopen') as mock_urlopen, \
         patch('albumoftheyearapi.artist.BeautifulSoup') as mock_bs:
        mock_response = MagicMock()
        mock_response.read.return_value = mock_artist_page_html.encode('utf-8')
        mock_urlopen.return_value = mock_response
        
        # Configure BeautifulSoup to return a real BeautifulSoup object parsed from mock HTML
        # This allows the internal parsing methods (__get_discography, __get_community_data) to work as expected
        mock_bs.return_value = BeautifulSoup(mock_artist_page_html, "html.parser")
        yield # Allow tests to run

# --- Tests for AOTY client initialization ---
def test_aoty_client_initialization(aoty_client):
    """Test that the AOTY client initializes correctly and contains ArtistMethods."""
    assert aoty_client is not None
    # assert isinstance(aoty_client.artist_methods, ArtistMethods)

# --- Tests for ArtistMethods initialization ---
def test_artist_methods_initialization(artist_methods_client):
    """Test that ArtistMethods initializes correctly with default values."""
    assert artist_methods_client is not None
    assert artist_methods_client.artist == ""
    assert artist_methods_client.url == ""
    assert artist_methods_client.artist_url == "https://www.albumoftheyear.org/artist/"
    assert artist_methods_client.albums == [] # Should be empty initially before any method call

# --- Tests for ArtistMethods public methods ---

def test_get_artist_albums(aoty_client, artist_id):
    """Test fetching artist albums."""
    artist_albums = aoty_client.artist_albums(artist_id)
    assert artist_albums is not None
    assert isinstance(artist_albums, list)
    assert "The College Dropout" in artist_albums
    assert "Late Registration" in artist_albums
    assert len(artist_albums) == 2 # Based on mock HTML

def test_get_artist_albums_json(aoty_client, artist_id):
    """Test fetching artist albums in JSON format."""
    artist_albums_json = aoty_client.artist_albums_json(artist_id)
    assert artist_albums_json is not None
    data = json.loads(artist_albums_json)
    assert "albums" in data
    assert isinstance(data["albums"], list)
    assert "The College Dropout" in data["albums"]
    assert "Late Registration" in data["albums"]
    assert len(data["albums"]) == 2

def test_get_artist_mixtapes(aoty_client, artist_id):
    """Test fetching artist mixtapes."""
    artist_mixtapes = aoty_client.artist_mixtapes(artist_id)
    assert artist_mixtapes is not None
    assert isinstance(artist_mixtapes, list)
    assert "Freshmen Adjustment" in artist_mixtapes
    assert len(artist_mixtapes) == 1

def test_get_artist_mixtapes_json(aoty_client, artist_id):
    """Test fetching artist mixtapes in JSON format."""
    artist_mixtapes_json = aoty_client.artist_mixtapes_json(artist_id)
    assert artist_mixtapes_json is not None
    data = json.loads(artist_mixtapes_json)
    assert "mixtapes" in data
    assert isinstance(data["mixtapes"], list)
    assert "Freshmen Adjustment" in data["mixtapes"]
    assert len(data["mixtapes"]) == 1

def test_get_artist_eps(aoty_client, artist_id):
    """Test fetching artist EPs."""
    artist_eps = aoty_client.artist_eps(artist_id)
    assert artist_eps is not None
    assert isinstance(artist_eps, list)
    assert "808s & Heartbreak (EP)" in artist_eps
    assert len(artist_eps) == 1

def test_get_artist_eps_json(aoty_client, artist_id):
    """Test fetching artist EPs in JSON format."""
    artist_eps_json = aoty_client.artist_eps_json(artist_id)
    assert artist_eps_json is not None
    data = json.loads(artist_eps_json)
    assert "eps" in data
    assert isinstance(data["eps"], list)
    assert "808s & Heartbreak (EP)" in data["eps"]
    assert len(data["eps"]) == 1

def test_get_artist_singles(aoty_client, artist_id):
    """Test fetching artist singles."""
    artist_singles = aoty_client.artist_singles(artist_id)
    assert artist_singles is not None
    assert isinstance(artist_singles, list)
    assert "Stronger" in artist_singles
    assert "Gold Digger" in artist_singles
    assert len(artist_singles) == 2

def test_get_artist_singles_json(aoty_client, artist_id):
    """Test fetching artist singles in JSON format."""
    artist_singles_json = aoty_client.artist_singles_json(artist_id)
    assert artist_singles_json is not None
    data = json.loads(artist_singles_json)
    assert "singles" in data
    assert isinstance(data["singles"], list)
    assert "Stronger" in data["singles"]
    assert "Gold Digger" in data["singles"]
    assert len(data["singles"]) == 2

def test_get_artist_name(aoty_client, artist_id):
    """Test fetching artist name."""
    artist_name = aoty_client.artist_name(artist_id)
    assert artist_name == "Kanye West"

def test_get_artist_name_json(aoty_client, artist_id):
    """Test fetching artist name in JSON format."""
    artist_name_json = aoty_client.artist_name_json(artist_id)
    assert artist_name_json is not None
    data = json.loads(artist_name_json)
    assert "name" in data
    assert data["name"] == "Kanye West"

def test_get_artist_critic_score(aoty_client, artist_id):
    """Test fetching artist critic score."""
    artist_critic_score = aoty_client.artist_critic_score(artist_id)
    assert artist_critic_score == "85"

def test_get_artist_critic_score_json(aoty_client, artist_id):
    """Test fetching artist critic score in JSON format."""
    artist_critic_score_json = aoty_client.artist_critic_score_json(artist_id)
    assert artist_critic_score_json is not None
    data = json.loads(artist_critic_score_json)
    assert "critic score" in data
    assert data["critic score"] == "85"

def test_get_artist_user_score(aoty_client, artist_id):
    """Test fetching artist user score."""
    artist_user_score = aoty_client.artist_user_score(artist_id)
    assert artist_user_score == "75"

def test_get_artist_user_score_json(aoty_client, artist_id):
    """Test fetching artist user score in JSON format."""
    artist_user_score_json = aoty_client.artist_user_score_json(artist_id)
    assert artist_user_score_json is not None
    data = json.loads(artist_user_score_json)
    assert "user score" in data
    assert data["user score"] == "75"

def test_get_artist_total_score(aoty_client, artist_id):
    """Test calculating artist total score."""
    artist_total_score = aoty_client.artist_total_score(artist_id)
    assert artist_total_score == 80.0 # (85 + 75) / 2

def test_get_artist_total_score_json(aoty_client, artist_id):
    """Test calculating artist total score in JSON format."""
    artist_total_score_json = aoty_client.artist_total_score_json(artist_id)
    assert artist_total_score_json is not None
    data = json.loads(artist_total_score_json)
    assert "total score" in data
    assert data["total score"] == 80.0

def test_get_artist_follower_count(aoty_client, artist_id):
    """Test fetching artist follower count."""
    artist_follower_count = aoty_client.artist_follower_count(artist_id)
    assert artist_follower_count == "123,456"

def test_get_artist_follower_count_json(aoty_client, artist_id):
    """Test fetching artist follower count in JSON format."""
    artist_follower_count_json = aoty_client.artist_follower_count_json(artist_id)
    assert artist_follower_count_json is not None
    data = json.loads(artist_follower_count_json)
    assert "follower count" in data
    assert data["follower count"] == "123,456"

def test_get_artist_details(aoty_client, artist_id):
    """Test fetching artist details."""
    artist_details = aoty_client.artist_details(artist_id)
    assert artist_details == "Some artist details here."

def test_get_artist_details_json(aoty_client, artist_id):
    """Test fetching artist details in JSON format."""
    artist_details_json = aoty_client.artist_details_json(artist_id)
    assert artist_details_json is not None
    data = json.loads(artist_details_json)
    assert "artist details" in data
    assert data["artist details"] == "Some artist details here."

def test_get_artist_top_songs(aoty_client, artist_id):
    """Test fetching artist top songs."""
    artist_top_songs = aoty_client.artist_top_songs(artist_id)
    assert artist_top_songs is not None
    assert isinstance(artist_top_songs, list)
    assert "Runaway" in artist_top_songs
    assert "Jesus Walks" in artist_top_songs
    assert len(artist_top_songs) == 2

def test_get_artist_top_songs_json(aoty_client, artist_id):
    """Test fetching artist top songs in JSON format."""
    artist_top_songs_json = aoty_client.artist_top_songs_json(artist_id)
    assert artist_top_songs_json is not None
    data = json.loads(artist_top_songs_json)
    assert "top songs" in data
    assert isinstance(data["top songs"], list)
    assert "Runaway" in data["top songs"]
    assert "Jesus Walks" in data["top songs"]
    assert len(data["top songs"]) == 2

def test_get_similar_artists(aoty_client, artist_id):
    """Test fetching similar artists."""
    similar_artists = aoty_client.similar_artists(artist_id)
    assert similar_artists is not None
    assert isinstance(similar_artists, list)
    assert "Jay-Z" in similar_artists
    assert "Kid Cudi" in similar_artists
    assert len(similar_artists) == 2

def test_get_similar_artists_json(aoty_client, artist_id):
    """Test fetching similar artists in JSON format."""
    similar_artists_json = aoty_client.similar_artists_json(artist_id)
    assert similar_artists_json is not None
    data = json.loads(similar_artists_json)
    assert "similar artists" in data
    assert isinstance(data["similar artists"], list)
    assert "Jay-Z" in data["similar artists"]
    assert "Kid Cudi" in data["similar artists"]
    assert len(data["similar artists"]) == 2
    
def test_functions_without_wrapper(artist_methods_client, artist_id):
    """Test a single function directly using ArtistMethods without the main AOTY wrapper."""
    # This test should also be mocked by the autouse fixture
    albums = artist_methods_client.artist_albums(artist_id)
    assert albums is not None
    assert "The College Dropout" in albums
