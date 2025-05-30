import json
from unittest.mock import patch, MagicMock

import pytest

from albumoftheyearapi.user import UserMethods, BeautifulSoup


@pytest.fixture
def user():
    return "doublez"


@pytest.fixture
def user_methods_client():
    """Fixture to provide an instance of UserMethods."""
    return UserMethods()


def test_user_methods_init(user_methods_client):
    """Test initialization of UserMethods."""
    assert user_methods_client is not None
    assert user_methods_client.user == ""
    assert user_methods_client.url == ""
    assert user_methods_client.user_url == "https://www.albumoftheyear.org/user/"
    assert user_methods_client.user_page is None


@patch('albumoftheyearapi.user.urlopen')
@patch('albumoftheyearapi.user.BeautifulSoup')
def test_set_user_page_success(mock_bs, mock_urlopen, user_methods_client):
    """Test successful fetching and parsing of a user page."""
    mock_response = MagicMock()
    mock_response.read.return_value = b"<html>mock html</html>"
    mock_urlopen.return_value = mock_response
    mock_bs.return_value = "mock_beautifulsoup_object"

    user = "testuser"
    url = "http://test.com"
    user_methods_client._UserMethods__set_user_page(user, url)  # Call private method

    mock_urlopen.assert_called_once()
    mock_bs.assert_called_once_with(b"<html>mock html</html>", "html.parser")
    assert user_methods_client.user == user
    assert user_methods_client.url == url
    assert user_methods_client.user_page == "mock_beautifulsoup_object"


@patch('albumoftheyearapi.user.urlopen', side_effect=Exception("Network error"))
def test_set_user_page_error(mock_urlopen, user_methods_client):
    """Test error handling during fetching a user page."""
    user = "testuser"
    url = "http://test.com"
    with pytest.raises(Exception, match="Network error"):
        user_methods_client._UserMethods__set_user_page(user, url)


# Parameterized testing for user statistics
@pytest.mark.parametrize(
    "method_name, url_suffix, expected_text",
    [
        ("user_rating_count", "/ratings/", "123 Ratings"),
        ("user_review_count", "/reviews/", "45 Reviews"),
        ("user_list_count", "/lists/", "6 Lists"),
        ("user_follower_count", "/followers/", "789 Followers"),
    ],
)
@patch('albumoftheyearapi.user.UserMethods._UserMethods__set_user_page')
def test_user_statistic_success(mock_set_user_page, user_methods_client, user, method_name, url_suffix, expected_text):
    """Test successful retrieval of user statistics."""
    mock_section = MagicMock()
    mock_section.find.return_value.getText.return_value = expected_text.split(" ")[0]  # Return only the number
    user_methods_client.user_page = MagicMock()
    user_methods_client.user_page.find.return_value = mock_section

    method = getattr(user_methods_client, method_name)
    result = method(user)

    assert result == expected_text.split(" ")[0]
    mock_set_user_page.assert_called_once_with(user, f"https://www.albumoftheyear.org/user/{user}")
    user_methods_client.user_page.find.assert_called_once()


@pytest.mark.parametrize(
    "method_name, url_suffix",
    [
        ("user_rating_count", "/ratings/"),
        ("user_review_count", "/reviews/"),
        ("user_list_count", "/lists/"),
        ("user_follower_count", "/followers/"),
    ],
)
@patch('albumoftheyearapi.user.UserMethods._UserMethods__set_user_page')
def test_user_statistic_error(mock_set_user_page, user_methods_client, user, method_name, url_suffix):
    """Test error handling when statistic is not found."""
    user_methods_client.user_page = MagicMock()
    user_methods_client.user_page.find.return_value = None  # Simulate statistic not found

    method = getattr(user_methods_client, method_name)
    with pytest.raises(AttributeError):  # Expect AttributeError when getText() is called on None
        method(user)
    mock_set_user_page.assert_called_once_with(user, f"https://www.albumoftheyear.org/user/{user}")


# Test user_about
@patch('albumoftheyearapi.user.UserMethods._UserMethods__set_user_page')
def test_user_about_success(mock_set_user_page, user_methods_client, user):
    """Test successful retrieval of user 'about' information."""
    expected_about = "This is a test about me section."
    mock_about_section = MagicMock()
    mock_about_section.getText.return_value = expected_about
    user_methods_client.user_page = MagicMock()
    user_methods_client.user_page.find.return_value = mock_about_section

    result = user_methods_client.user_about(user)

    assert result == expected_about
    mock_set_user_page.assert_called_once_with(user, f"https://www.albumoftheyear.org/user/{user}")
    user_methods_client.user_page.find.assert_called_once()


@patch('albumoftheyearapi.user.UserMethods._UserMethods__set_user_page')
def test_user_about_not_found(mock_set_user_page, user_methods_client, user):
    """Test handling when user 'about' section is not found."""
    user_methods_client.user_page = MagicMock()
    user_methods_client.user_page.find.return_value = None  # Simulate 'about' section not found

    result = user_methods_client.user_about(user)

    assert result == ""  # Expect empty string when not found
    mock_set_user_page.assert_called_once_with(user, f"https://www.albumoftheyear.org/user/{user}")


# Test user_rating_distribution
@patch('albumoftheyearapi.user.UserMethods._UserMethods__set_user_page')
def test_user_rating_distribution_success(mock_set_user_page, user_methods_client, user):
    """Test successful retrieval of user rating distribution."""
    # Mock getText to return strings that simulate the actual page content
    # The parsing logic in user_rating_distribution will extract the number from these.
    mock_dist_rows = [MagicMock(getText=MagicMock(return_value=f"100   {i}")) for i in range(11)]
    user_methods_client.user_page = MagicMock()
    user_methods_client.user_page.findAll.return_value = mock_dist_rows

    result = user_methods_client.user_rating_distribution(user)

    assert len(result) == 11
    assert result[0] == "0" # For "100   0" -> "0"
    assert result[10] == "10" # For "100   10" -> "10"
    mock_set_user_page.assert_called_once_with(user, f"https://www.albumoftheyear.org/user/{user}")
    user_methods_client.user_page.findAll.assert_called_once()


@patch('albumoftheyearapi.user.UserMethods._UserMethods__set_user_page')
def test_user_rating_distribution_empty(mock_set_user_page, user_methods_client, user):
    """Test handling of empty rating distribution."""
    mock_dist_rows = [MagicMock(getText=MagicMock(return_value="")) for _ in range(11)]
    user_methods_client.user_page = MagicMock()
    user_methods_client.user_page.findAll.return_value = mock_dist_rows

    result = user_methods_client.user_rating_distribution(user)

    assert len(result) == 11
    assert all(r == "0" for r in result)  # Expect all values to be "0"
    mock_set_user_page.assert_called_once_with(user, f"https://www.albumoftheyear.org/user/{user}")


# Test user_ratings
@patch('albumoftheyearapi.user.UserMethods._UserMethods__set_user_page')
def test_user_ratings_success(mock_set_user_page, user_methods_client, user):
    """Test successful retrieval of user ratings summary."""
    expected_ratings = "Test Album - Test Artist - 80"
    mock_album_block = MagicMock()
    mock_album_block.getText.return_value = expected_ratings
    user_methods_client.user_page = MagicMock()
    user_methods_client.user_page.find.return_value = mock_album_block

    result = user_methods_client.user_ratings(user)

    assert result == expected_ratings
    mock_set_user_page.assert_called_once_with(user, f"https://www.albumoftheyear.org/user/{user}")
    user_methods_client.user_page.find.assert_called_once()


@patch('albumoftheyearapi.user.UserMethods._UserMethods__set_user_page')
def test_user_ratings_not_found(mock_set_user_page, user_methods_client, user):
    """Test handling when user ratings summary is not found."""
    user_methods_client.user_page = MagicMock()
    user_methods_client.user_page.find.return_value = None  # Simulate ratings not found

    result = user_methods_client.user_ratings(user)

    assert result == ""  # Expect empty string when not found
    mock_set_user_page.assert_called_once_with(user, f"https://www.albumoftheyear.org/user/{user}")


# Test user_perfect_scores
@patch('albumoftheyearapi.user.UserMethods._UserMethods__set_user_page')
def test_user_perfect_scores_success(mock_set_user_page, user_methods_client, user):
    """Test successful retrieval of user perfect scores."""
    expected_scores = "Perfect Album - Perfect Artist - 100"
    mock_album_block = MagicMock()
    mock_album_block.getText.return_value = expected_scores
    user_methods_client.user_page = MagicMock()
    user_methods_client.user_page.find.return_value = mock_album_block

    result = user_methods_client.user_perfect_scores(user)

    assert result == expected_scores
    mock_set_user_page.assert_called_once_with(user, f"https://www.albumoftheyear.org/user/{user}/ratings/perfect/")
    user_methods_client.user_page.find.assert_called_once()


@patch('albumoftheyearapi.user.UserMethods._UserMethods__set_user_page')
def test_user_perfect_scores_not_found(mock_set_user_page, user_methods_client, user):
    """Test handling when user perfect scores are not found."""
    user_methods_client.user_page = MagicMock()
    user_methods_client.user_page.find.return_value = None  # Simulate perfect scores not found

    result = user_methods_client.user_perfect_scores(user)

    assert result == ""  # Expect empty string when not found
    mock_set_user_page.assert_called_once_with(user, f"https://www.albumoftheyear.org/user/{user}/ratings/perfect/")


# Test user_liked_music
@patch('albumoftheyearapi.user.UserMethods._UserMethods__set_user_page')
def test_user_liked_music_success(mock_set_user_page, user_methods_client, user):
    """Test successful retrieval of user liked music."""
    mock_album_block = MagicMock()
    
    # Configure the find method of mock_album_block to return specific mocks
    # based on the class_ argument. This ensures getText() is always called
    # on a MagicMock object.
    mock_album_block.find.side_effect = lambda class_: \
        MagicMock(getText=MagicMock(return_value="Test Artist")) if class_ == "artistTitle" else \
        MagicMock(getText=MagicMock(return_value="Test Album")) if class_ == "albumTitle" else \
        None # Return None if class_ doesn't match

    user_methods_client.user_page = MagicMock()
    user_methods_client.user_page.find_all.return_value = [mock_album_block]

    result = user_methods_client.user_liked_music(user)

    assert len(result) == 1
    assert result[0] == "Test Artist: Test Album"
    mock_set_user_page.assert_called_once_with(user, f"https://www.albumoftheyear.org/user/{user}/liked/albums/")
    user_methods_client.user_page.find_all.assert_called_once()


@patch('albumoftheyearapi.user.UserMethods._UserMethods__set_user_page')
def test_user_liked_music_empty(mock_set_user_page, user_methods_client, user):
    """Test handling when user has no liked music."""
    user_methods_client.user_page = MagicMock()
    user_methods_client.user_page.find_all.return_value = []  # Simulate no liked music

    result = user_methods_client.user_liked_music(user)

    assert len(result) == 0
    mock_set_user_page.assert_called_once_with(user, f"https://www.albumoftheyear.org/user/{user}/liked/albums/")


# Test JSON serialization methods
@pytest.mark.parametrize(
    "method_name, expected_key",
    [
        ("user_rating_count_json", "ratings"),
        ("user_review_count_json", "reviews"),
        ("user_list_count_json", "lists"),
        ("user_follower_count_json", "followers"),
        ("user_about_json", "about_user"),
        ("user_ratings_json", "ratings"),
        ("user_perfect_scores_json", "perfect scores"),
        ("user_liked_music_json", "liked music"),
    ],
)
@patch('albumoftheyearapi.user.UserMethods.user_rating_count')
@patch('albumoftheyearapi.user.UserMethods.user_review_count')
@patch('albumoftheyearapi.user.UserMethods.user_list_count')
@patch('albumoftheyearapi.user.UserMethods.user_follower_count')
@patch('albumoftheyearapi.user.UserMethods.user_about')
@patch('albumoftheyearapi.user.UserMethods.user_ratings')
@patch('albumoftheyearapi.user.UserMethods.user_perfect_scores')
@patch('albumoftheyearapi.user.UserMethods.user_liked_music')
def test_json_serialization_success(
    mock_liked_music,
    mock_perfect_scores,
    mock_ratings,
    mock_about,
    mock_follower_count,
    mock_list_count,
    mock_review_count,
    mock_rating_count,
    user_methods_client,
    user,
    method_name,
    expected_key,
):
    """Test successful JSON serialization of user data."""
    # Set return values for each mock
    mock_rating_count.return_value = "100"
    mock_review_count.return_value = "50"
    mock_list_count.return_value = "10"
    mock_follower_count.return_value = "200"
    mock_about.return_value = "About me"
    mock_ratings.return_value = "Some ratings"
    mock_perfect_scores.return_value = "Perfect scores"
    mock_liked_music.return_value = ["Liked music"]

    method = getattr(user_methods_client, method_name)
    result_json = method(user)
    result = json.loads(result_json)

    assert expected_key in result
    
    # Map method_name to its expected return value for cleaner assertions
    expected_values_map = {
        "user_rating_count_json": "100",
        "user_review_count_json": "50",
        "user_list_count_json": "10",
        "user_follower_count_json": "200",
        "user_about_json": "About me",
        "user_ratings_json": "Some ratings",
        "user_perfect_scores_json": "Perfect scores",
        "user_liked_music_json": ["Liked music"],
    }
    assert result[expected_key] == expected_values_map[method_name]

