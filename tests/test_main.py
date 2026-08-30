from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from devops_engineer_from_scratch_project_313.app import create_app


@pytest.fixture
def client(tmp_path, monkeypatch) -> Generator[TestClient, None, None]:
    database_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database_path}")
    monkeypatch.setenv("BASE_URL", "https://short.test")

    with TestClient(create_app()) as test_client:
        yield test_client


def test_ping_returns_pong(client: TestClient) -> None:
    response = client.get("/ping")

    assert response.status_code == 200
    assert response.json() == "pong"


def test_cors_preflight_for_links(client: TestClient) -> None:
    preflight_response = client.options(
        "/api/links",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    response = client.get(
        "/api/links",
        headers={"Origin": "http://localhost:5173"},
    )

    assert preflight_response.status_code == 200
    assert (
        preflight_response.headers["access-control-allow-origin"]
        == "http://localhost:5173"
    )
    assert "Content-Range" in response.headers["access-control-expose-headers"]


def test_create_link(client: TestClient) -> None:
    response = client.post(
        "/api/links",
        json={
            "original_url": "https://example.com/long-url",
            "short_name": "exmpl",
        },
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "original_url": "https://example.com/long-url",
        "short_name": "exmpl",
        "short_url": "https://short.test/r/exmpl",
    }


def test_list_links(client: TestClient) -> None:
    client.post(
        "/api/links",
        json={
            "original_url": "https://example.com/long-url",
            "short_name": "first",
        },
    )
    client.post(
        "/api/links",
        json={
            "original_url": "https://example.com/long-url2",
            "short_name": "second",
        },
    )

    response = client.get("/api/links")

    assert response.status_code == 200
    assert response.headers["content-range"] == "links 0-2/2"
    assert response.json() == [
        {
            "id": 1,
            "original_url": "https://example.com/long-url",
            "short_name": "first",
            "short_url": "https://short.test/r/first",
        },
        {
            "id": 2,
            "original_url": "https://example.com/long-url2",
            "short_name": "second",
            "short_url": "https://short.test/r/second",
        },
    ]


def test_list_links_with_range_returns_first_page(client: TestClient) -> None:
    for index in range(12):
        client.post(
            "/api/links",
            json={
                "original_url": f"https://example.com/{index}",
                "short_name": f"short-{index}",
            },
        )

    response = client.get("/api/links?range=[0,10]")

    assert response.status_code == 200
    assert response.headers["content-range"] == "links 0-10/12"
    assert len(response.json()) == 10
    assert response.json()[0]["short_name"] == "short-0"
    assert response.json()[-1]["short_name"] == "short-9"


def test_list_links_with_range_returns_offset_page(client: TestClient) -> None:
    for index in range(11):
        client.post(
            "/api/links",
            json={
                "original_url": f"https://example.com/{index}",
                "short_name": f"offset-{index}",
            },
        )

    response = client.get("/api/links?range=[5,10]")

    assert response.status_code == 200
    assert response.headers["content-range"] == "links 5-10/11"
    assert len(response.json()) == 5
    assert response.json()[0]["short_name"] == "offset-5"
    assert response.json()[-1]["short_name"] == "offset-9"


def test_get_link_by_id(client: TestClient) -> None:
    create_response = client.post(
        "/api/links",
        json={
            "original_url": "https://example.com/long-url",
            "short_name": "exmpl",
        },
    )

    link_id = create_response.json()["id"]
    response = client.get(f"/api/links/{link_id}")

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "original_url": "https://example.com/long-url",
        "short_name": "exmpl",
        "short_url": "https://short.test/r/exmpl",
    }


def test_update_link(client: TestClient) -> None:
    create_response = client.post(
        "/api/links",
        json={
            "original_url": "https://example.com/long-url",
            "short_name": "exmpl",
        },
    )

    link_id = create_response.json()["id"]
    response = client.put(
        f"/api/links/{link_id}",
        json={
            "original_url": "https://example.org/updated",
            "short_name": "updated",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "original_url": "https://example.org/updated",
        "short_name": "updated",
        "short_url": "https://short.test/r/updated",
    }


def test_delete_link(client: TestClient) -> None:
    create_response = client.post(
        "/api/links",
        json={
            "original_url": "https://example.com/long-url",
            "short_name": "exmpl",
        },
    )

    link_id = create_response.json()["id"]
    delete_response = client.delete(f"/api/links/{link_id}")
    get_response = client.get(f"/api/links/{link_id}")

    assert delete_response.status_code == 204
    assert delete_response.content == b""
    assert get_response.status_code == 404
    assert get_response.json() == {"detail": f"link with id {link_id} not found"}


def test_redirect_by_short_name(client: TestClient) -> None:
    client.post(
        "/api/links",
        json={
            "original_url": "https://example.com/long-url",
            "short_name": "exmpl",
        },
    )

    response = client.get("/r/exmpl", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["location"] == "https://example.com/long-url"


def test_create_link_returns_422_for_invalid_body(client: TestClient) -> None:
    response = client.post(
        "/api/links",
        json={
            "original_url": "not-a-url",
            "short_name": "",
        },
    )

    assert response.status_code == 422
    assert "detail" in response.json()


def test_update_link_returns_422_for_invalid_body(client: TestClient) -> None:
    create_response = client.post(
        "/api/links",
        json={
            "original_url": "https://example.com/long-url",
            "short_name": "exmpl",
        },
    )

    link_id = create_response.json()["id"]
    response = client.put(
        f"/api/links/{link_id}",
        json={
            "original_url": "invalid-url",
            "short_name": "",
        },
    )

    assert response.status_code == 422
    assert "detail" in response.json()


def test_get_missing_link_returns_404(client: TestClient) -> None:
    response = client.get("/api/links/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "link with id 999 not found"}


def test_update_missing_link_returns_404(client: TestClient) -> None:
    response = client.put(
        "/api/links/999",
        json={
            "original_url": "https://example.com/long-url",
            "short_name": "exmpl",
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "link with id 999 not found"}


def test_delete_missing_link_returns_404(client: TestClient) -> None:
    response = client.delete("/api/links/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "link with id 999 not found"}


def test_redirect_missing_short_name_returns_404(client: TestClient) -> None:
    response = client.get("/r/missing", follow_redirects=False)

    assert response.status_code == 404
    assert response.json() == {"detail": "link with short_name 'missing' not found"}


def test_create_link_returns_409_for_duplicate_short_name(client: TestClient) -> None:
    client.post(
        "/api/links",
        json={
            "original_url": "https://example.com/long-url",
            "short_name": "exmpl",
        },
    )
    response = client.post(
        "/api/links",
        json={
            "original_url": "https://example.org/another",
            "short_name": "exmpl",
        },
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "short_name already exists"}
