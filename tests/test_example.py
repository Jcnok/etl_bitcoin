from unittest.mock import Mock, patch

import pytest
import requests

from src.main import calculate_kpis, get_price, get_usd_to_brl_rate


# Fixture for valid price data to avoid repetition
@pytest.fixture
def valid_price_data() -> dict:
    """Fixture that returns a valid price data dictionary."""
    return {"data": {"amount": "50000.00"}}


# --- Tests for calculate_kpis ---


def test_calculate_kpis_success(valid_price_data: dict) -> None:
    """Tests if KPI calculation is correct with valid data."""
    mock_rate = 5.5
    kpis = calculate_kpis(valid_price_data, mock_rate)
    assert kpis is not None
    assert kpis["price_usd"] == 50000.00
    assert kpis["price_real"] == 50000.00 * mock_rate
    assert "timestamp" in kpis


def test_calculate_kpis_with_none_input() -> None:
    """Tests if the function handles None as input gracefully."""
    assert calculate_kpis(None, 5.5) is None


def test_calculate_kpis_with_missing_data_key() -> None:
    """Tests if the function handles a dictionary missing the 'data' key."""
    invalid_data = {"amount": "50000.00"}
    assert calculate_kpis(invalid_data, 5.5) is None


def test_calculate_kpis_with_missing_amount_key() -> None:
    """Tests if the function handles a dictionary missing the 'amount' key."""
    invalid_data = {"data": {"price": "50000.00"}}
    assert calculate_kpis(invalid_data, 5.5) is None


def test_calculate_kpis_with_invalid_amount_value() -> None:
    """Tests if the function handles a non-numeric 'amount' value."""
    invalid_data = {"data": {"amount": "invalid-price"}}
    assert calculate_kpis(invalid_data, 5.5) is None


# --- Tests for get_price (using mock) ---


@patch("src.main.requests.get")
def test_get_price_success(mock_get: Mock) -> None:
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


@patch("src.main.requests.get")
def test_get_price_connection_error(mock_get: Mock) -> None:
    """Tests the price fetching function when a ConnectionError occurs."""
    mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
    assert get_price() is None


@patch("src.main.requests.get")
def test_get_price_timeout(mock_get: Mock) -> None:
    """Tests the price fetching function when a Timeout occurs."""
    mock_get.side_effect = requests.exceptions.Timeout("Request timed out")
    assert get_price() is None


@patch("src.main.requests.get")
def test_get_price_http_error(mock_get: Mock) -> None:
    """Tests price fetching when the API returns an HTTP error (e.g., 404, 500)."""
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "404 Not Found"
    )
    mock_get.return_value = mock_response
    assert get_price() is None


# --- Tests for get_usd_to_brl_rate (using mock) ---


@patch("src.main.requests.get")
def test_get_usd_to_brl_rate_success(mock_get: Mock) -> None:
    """Tests the currency rate fetching on a successful API call."""
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"rates": {"BRL": 5.15}}
    mock_get.return_value = mock_response

    rate = get_usd_to_brl_rate()
    assert rate == 5.15


@patch("src.main.requests.get")
def test_get_usd_to_brl_rate_api_error(mock_get: Mock) -> None:
    """Tests the currency rate fetching when the API returns an error."""
    mock_get.side_effect = requests.exceptions.RequestException("API Error")
    assert get_usd_to_brl_rate() is None


@patch("src.main.requests.get")
def test_get_usd_to_brl_rate_key_error(mock_get: Mock) -> None:
    """Tests the currency rate fetching with a malformed JSON response."""
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"data": {}}  # Missing 'rates' key
    mock_get.return_value = mock_response

    assert get_usd_to_brl_rate() is None
