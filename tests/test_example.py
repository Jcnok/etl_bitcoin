import pytest
import requests
from unittest.mock import patch, Mock
from src.main import calculate_kpis, get_price


# Fixture for valid price data to avoid repetition
@pytest.fixture
def valid_price_data():
    """Fixture that returns a valid price data dictionary."""
    return {"data": {"amount": "50000.00"}}


# --- Tests for calculate_kpis ---

def test_calculate_kpis_success(valid_price_data):
    """Tests if KPI calculation is correct with valid data."""
    kpis = calculate_kpis(valid_price_data)
    assert kpis is not None
    assert kpis['price_usd'] == 50000.00
    assert kpis['price_real'] == 50000.00 * 5.5
    assert 'timestamp' in kpis


def test_calculate_kpis_with_none_input():
    """Tests if the function handles None as input gracefully."""
    assert calculate_kpis(None) is None


def test_calculate_kpis_with_missing_data_key():
    """Tests if the function handles a dictionary missing the 'data' key."""
    invalid_data = {"amount": "50000.00"}
    assert calculate_kpis(invalid_data) is None


def test_calculate_kpis_with_missing_amount_key():
    """Tests if the function handles a dictionary missing the 'amount' key."""
    invalid_data = {"data": {"price": "50000.00"}}
    assert calculate_kpis(invalid_data) is None


def test_calculate_kpis_with_invalid_amount_value():
    """Tests if the function handles a non-numeric 'amount' value."""
    invalid_data = {"data": {"amount": "invalid-price"}}
    assert calculate_kpis(invalid_data) is None


# --- Tests for get_price (using mock) ---

@patch('src.main.requests.get')
def test_get_price_success(mock_get):
    """Tests the price fetching function on a successful API call."""
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"data": {"amount": "50000.00"}}
    mock_get.return_value = mock_response

    price = get_price()
    assert price == {"data": {"amount": "50000.00"}}
    mock_get.assert_called_once_with(
        "https://api.coinbase.com/v2/prices/spot?currency=USD", timeout=5
    )


@patch('src.main.requests.get')
def test_get_price_connection_error(mock_get):
    """Tests the price fetching function when a ConnectionError occurs."""
    mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
    assert get_price() is None


@patch('src.main.requests.get')
def test_get_price_timeout(mock_get):
    """Tests the price fetching function when a Timeout occurs."""
    mock_get.side_effect = requests.exceptions.Timeout("Request timed out")
    assert get_price() is None


@patch('src.main.requests.get')
def test_get_price_http_error(mock_get):
    """Tests price fetching when the API returns an HTTP error (e.g., 404, 500)."""
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
    mock_get.return_value = mock_response
    assert get_price() is None
