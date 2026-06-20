import time
import requests

BASE_URL = "https://fakestoreapi.com"

# Cache
_cache = {}
CACHE_TTL = 300  # 5 minutes


def _get_cached(url):
    """
    Cached GET request with error handling.
    """

    now = time.time()

    # Return cached data if still valid
    if url in _cache:
        data, expiry = _cache[url]

        if now < expiry:
            print(f"[CACHE HIT] {url}")
            return data

    try:
        print(f"[FETCHING] {url}")

        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        print(f"[STATUS CODE] {response.status_code}")

        response.raise_for_status()

        data = response.json()

        _cache[url] = (
            data,
            now + CACHE_TTL
        )

        return data

    except Exception as e:
        print(f"[API ERROR] {url}")
        print(str(e))

        # Return expired cache if available
        if url in _cache:
            print("[USING EXPIRED CACHE]")
            return _cache[url][0]

        return None


def get_all_products():
    """
    Get all products.
    """

    data = _get_cached(f"{BASE_URL}/products")

    if not data:
        print("[WARNING] No products returned")
        return []

    print(f"[PRODUCT COUNT] {len(data)}")

    return data


def get_product_by_id(product_id):
    """
    Get product by ID.
    """

    if not product_id:
        return None

    return _get_cached(
        f"{BASE_URL}/products/{product_id}"
    )


def get_categories():
    """
    Get all categories.
    """

    data = _get_cached(
        f"{BASE_URL}/products/categories"
    )

    if not data:
        return []

    return data


def get_featured_products(limit=4):
    """
    Get highest rated products.
    """

    products = get_all_products()

    if not products:
        return []

    try:
        sorted_products = sorted(
            products,
            key=lambda p: p.get("rating", {}).get("rate", 0),
            reverse=True
        )

        return sorted_products[:limit]

    except Exception as e:
        print("[FEATURED ERROR]", e)
        return products[:limit]


def get_latest_products(limit=4):
    """
    Get latest products.
    """

    products = get_all_products()

    if not products:
        return []

    try:
        sorted_products = sorted(
            products,
            key=lambda p: p.get("id", 0),
            reverse=True
        )

        return sorted_products[:limit]

    except Exception as e:
        print("[LATEST ERROR]", e)
        return products[:limit]