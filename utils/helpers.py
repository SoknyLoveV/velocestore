import re

def is_valid_email(email):
    """
    Validate email address format using regular expressions.
    """
    if not email:
        return False
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def get_cart_item_count(cart):
    """
    Compute total number of items in the cart (sum of quantities).
    """
    if not cart or 'items' not in cart:
        return 0
    return sum(cart['items'].values())
