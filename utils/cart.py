import json
from flask import request

def get_cart():
    """
    Retrieve the cart dictionary from browser cookies.
    Expected cookie format: {"items": {"product_id_string": quantity_int}}
    """
    cart_cookie = request.cookies.get('cart')
    if cart_cookie:
        try:
            cart_data = json.loads(cart_cookie)
            if isinstance(cart_data, dict) and "items" in cart_data:
                # Ensure product IDs are strings and quantities are integers
                cleaned_items = {}
                for k, v in cart_data["items"].items():
                    try:
                        cleaned_items[str(k)] = int(v)
                    except (ValueError, TypeError):
                        continue
                return {"items": cleaned_items}
        except json.JSONDecodeError:
            pass
    return {"items": {}}

def save_cart(response, cart):
    """
    Save the cart dictionary to browser cookies.
    Applies to the provided response object. Expiry set to 30 days.
    """
    response.set_cookie(
        'cart',
        json.dumps(cart),
        max_age=30 * 24 * 60 * 60,
        path='/',
        httponly=True,
        samesite='Lax'
    )

def calculate_total(cart_items_details):
    """
    Calculate the subtotal, tax (8%), and grand total based on list of cart item details.
    Each item detail must contain 'subtotal' (price * quantity).
    """
    subtotal = sum(item['subtotal'] for item in cart_items_details)
    tax = round(subtotal * 0.08, 2)
    grand_total = round(subtotal + tax, 2)
    return {
        'subtotal': round(subtotal, 2),
        'tax': tax,
        'grand_total': grand_total
    }
