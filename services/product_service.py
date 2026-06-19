import time
import requests

BASE_URL = "https://fakestoreapi.com"

# Simple in-memory cache to speed up website performance and survive external API downtime
_cache = {}
CACHE_TTL = 300  # Cache duration: 5 minutes

def _get_cached(url):
    """
    Helper function to perform cached GET requests with timeout and error handling.
    """
    now = time.time()
    if url in _cache:
        val, expiry = _cache[url]
        if now < expiry:
            return val
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            _cache[url] = (data, now + CACHE_TTL)
            return data
    except Exception as e:
        print(f"Error fetching from FakeStore API ({url}): {e}")
        # If cache exists but has expired, return the expired version as a fallback
        if url in _cache:
            return _cache[url][0]
    return None

def get_all_products():
    """
    Fetch all products from the FakeStore API.
    """
    return _get_cached(f"{BASE_URL}/products") or []

def get_product_by_id(product_id):
    """
    Fetch details of a single product by its ID.
    """
    if not product_id:
        return None
    return _get_cached(f"{BASE_URL}/products/{product_id}")

def get_categories():
    """
    Fetch all product categories from the FakeStore API.
    """
    return _get_cached(f"{BASE_URL}/products/categories") or []

def get_featured_products(limit=4):
    """
    Get the top rated products as featured products.
    """
    products = get_all_products()
    if not products:
        return []
    try:
        # Sort products by rating rate in descending order
        sorted_products = sorted(
            products,
            key=lambda x: x.get('rating', {}).get('rate', 0.0),
            reverse=True
        )
        return sorted_products[:limit]
    except Exception as e:
        print(f"Error sorting featured products: {e}")
        return products[:limit]

def get_latest_products(limit=4):
    """
    Get the latest products (defined as products with the highest IDs).
    """
    products = get_all_products()
    if not products:
        return []
    try:
        # Sort products by ID in descending order
        sorted_products = sorted(
            products,
            key=lambda x: x.get('id', 0),
            reverse=True
        )
        return sorted_products[:limit]
    except Exception as e:
        print(f"Error sorting latest products: {e}")
        return products[-limit:] if len(products) >= limit else products
