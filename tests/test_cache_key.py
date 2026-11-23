from app.core.cache import product_cache_key

def test_product_cache_key_format():
    assert product_cache_key(42) == "product:42"
