import pytest

from app.api.products import INT_MAX


async def test_get_known_product_returns_200(client, product):
    response = await client.get(f"/products/{product.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == product.id
    assert body["name"] == product.name
    assert body["price"] == "49.90"


async def test_get_unknown_product_returns_404(client):
    response = await client.get("/products/9999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}


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

async def test_put_existing_product_returns_200_with_new_values(client, product):
    product_data = {
        "name": "Claude Code Agent",
        "price": "59.90",
        "description": "Hi, this is the new update"
    }
    put_response = await client.put(f"/products/{product.id}", json=product_data)

    assert put_response.status_code == 200
    put_body = put_response.json()

    assert put_body["id"] == product.id
    assert put_body["name"] == product_data["name"]
    assert put_body["price"] == product_data["price"]
    assert put_body["description"] == product_data["description"]

    get_response = await client.get(f"/products/{product.id}")

    assert get_response.status_code == 200
    get_body = get_response.json()

    assert get_body["id"] == product.id
    assert get_body["name"] == product_data["name"]
    assert get_body["price"] == product_data["price"]
    assert get_body["description"] == product_data["description"]

async def test_put_unknown_product_returns_404(client):
    product_id = 9999
    product_data = {"name": "Ghost product", "price": "10.00", "description": None}
    put_response = await client.put(f"/products/{product_id}", json=product_data)

    assert put_response.status_code == 404
    assert put_response.json() == {"detail": "Product not found"}

@pytest.mark.parametrize("product_id", [0, -1, INT_MAX + 1, "abc"])
async def test_put_invalid_id_returns_422(client, product_id):
    product_data = {
        "name": "Claude Code Agent",
        "price": "59.90",
        "description": "Hi, this is the new update"
    }

    response = await client.put(f"/products/{product_id}", json=product_data)

    assert response.status_code == 422

@pytest.mark.parametrize(
    "product_data",
    [
        pytest.param({"name": "ok", "price": "abc", "description": None}, id="price_not_a_number"),
        pytest.param({"name": "ok", "description": None}, id="price_missing"),
        pytest.param({"name": "a" * 101, "price": "10.00", "description": None}, id="name_too_long"),
        pytest.param({"name": "", "price": "10.00", "description": None}, id="name_empty"),
        pytest.param({"name": "ok", "price": "0", "description": None}, id="price_zero"),
        pytest.param({"name": "ok", "price": "-5", "description": None}, id="price_negative"),
        pytest.param({"name": "ok", "price": "123456789012.00", "description": None}, id="price_too_many_digits")

    ],
)
async def test_put_invalid_body_returns_422(client, product, product_data):
    response = await client.put(f"/products/{product.id}", json=product_data)

    assert response.status_code == 422