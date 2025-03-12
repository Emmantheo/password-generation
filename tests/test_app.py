import pytest
from app import app
from bs4 import BeautifulSoup


@pytest.fixture
def client():
    """
    Create a test client for the Flask app.
    """
    with app.test_client() as client:
        yield client


def test_home_route_status(client):
    """
    Test that the home page (GET '/') returns status code 200.
    """
    response = client.get('/')
    assert response.status_code == 200


def test_home_route_content(client):
    """
    Test that the home page contains expected form elements.
    """
    response = client.get('/')
    # Check that 'Password Length:' or something similar appears
    assert b'Password Length' in response.data


def test_create_password_default(client):
    """
    Test POST to '/create_password' with no data (uses default length).
    """
    response = client.post('/create_password', data={})
    assert response.status_code == 200

    # Parse the HTML to find the generated password
    soup = BeautifulSoup(response.data, 'html.parser')
    password_element = soup.find('strong')  # <strong>{{ generated_password }}</strong>
    
    assert password_element is not None
    generated_password = password_element.get_text()
    assert len(generated_password) == 8  # default length is 8 if none provided

def test_create_password_custom_length(client):
    """
    Test POST to '/create_password' with a custom length = 12.
    """
    response = client.post('/create_password', data={
        'length': 12,
        'use_upper': 'on',   # simulate user checking the box
        'use_lower': 'on',
        'use_digits': 'on',
        'use_punct': 'on'
    })
    assert response.status_code == 200

    soup = BeautifulSoup(response.data, 'html.parser')
    password_element = soup.find('strong')
    
    assert password_element is not None
    generated_password = password_element.get_text()
    assert len(generated_password) == 12


def test_no_char_types_selected(client):
    """
    Test what happens if the user does NOT select any character type.
    The code should fall back to letters + digits.
    """
    response = client.post('/create_password', data={
        'length': 10
        # no checkboxes selected
    })
    assert response.status_code == 200

    soup = BeautifulSoup(response.data, 'html.parser')
    password_element = soup.find('strong')
    
    assert password_element is not None
    generated_password = password_element.get_text()
    assert len(generated_password) == 10

    # Check that the password includes only letters/digits
    for char in generated_password:
        assert char.isalnum(), f"Found unexpected character '{char}' in password"


def test_create_password_invalid_length(client):
    """
    Test what happens if an invalid (non-integer) length is supplied.
    The code should fallback to length 8.
    """
    response = client.post('/create_password', data={'length': 'abc'})
    assert response.status_code == 200
    
    soup = BeautifulSoup(response.data, 'html.parser')
    password_element = soup.find('strong')
    
    assert password_element is not None
    generated_password = password_element.get_text()
    assert len(generated_password) == 8
