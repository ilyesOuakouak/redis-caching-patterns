import pytest

INT_MAX = 2_147_483_647


async def test_get_unknown_product_returns_404(client):
    response = await client.get("/products/9999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}


async def test_get_known_product_returns_200(client):
    product_id = 1
    response = await client.get(f"/products/{product_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == 1
    assert body["name"] == "Claude AI"


@pytest.mark.parametrize("product_id", [0, -1])
async def test_get_zero_or_negative_id_returns_422(client, product_id):
    response = await client.get(f"/products/{product_id}")

    assert response.status_code == 422


async def test_get_id_above_int_max_returns_422(client):
    response = await client.get(f"/products/{INT_MAX + 1}")

    assert response.status_code == 422


async def test_get_non_integer_id_returns_422(client):
    response = await client.get("/products/abc")

    assert response.status_code == 422
