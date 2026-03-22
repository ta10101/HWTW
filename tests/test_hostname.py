"""Tests for Wind Tunnel hostname validation (security + Holo guide shape)."""

import pytest

from main import validate_wind_tunnel_hostname


@pytest.mark.parametrize(
    "host",
    [
        "nomad-client-jane-01",
        "nomad-client-yourname-01",
        "a",
        "ab",
        "node-1",
        "host.example.com",
        "NOMAD-CLIENT-TEAM-42",
    ],
)
def test_valid_hostnames(host: str) -> None:
    ok, msg = validate_wind_tunnel_hostname(host)
    assert ok, msg


@pytest.mark.parametrize(
    "host",
    [
        "",
        " ",
        "nomad-client-",  # trailing hyphen in label
        "-bad",
        "bad..dots",
        "has space",
        "semi;evil",
        "pipe|evil",
        "backtick`evil",
        "$(whoami)",
        "unicode–dash",  # en-dash, not ASCII hyphen
        "a" * 300,
    ],
)
def test_invalid_hostnames(host: str) -> None:
    ok, _msg = validate_wind_tunnel_hostname(host)
    assert not ok
