import os
import requests

def send_telegram(message):
    """
    Sends a formatted message to a configured Telegram group or chat.
    Fails silently (returns False) on network exceptions or missing environment variables.
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("Telegram service warning: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is not configured in .env")
        return False
        
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    
    try:
        response = requests.post(url, json=payload, timeout=8)
        if response.status_code != 200:
            print(f"Telegram API returned non-200 response: Status {response.status_code}, Body {response.text}")
            return False
        return True
    except Exception as e:
        print(f"Failed to send Telegram notification due to connection error: {e}")
        return False

def send_order_notification(customer_name, phone, address, cart_items, total):
    """
    Sends a formatted e-commerce order notification to a configured Telegram group or chat.
    Fails silently (returns False) on network exceptions or missing environment variables
    to prevent checkout disruption.
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("Telegram service warning: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is not configured in .env")
        return False
        
    # Build product list string
    items_list_str = ""
    for item in cart_items:
        # Resolve product title from item structure
        title = item.get('title')
        if not title and 'product' in item:
            title = item['product'].get('title')
        title = title or "Unknown Product"
        quantity = item.get('quantity', 1)
        items_list_str += f"\n* {title} x{quantity}"
        
    # Format message body
    message = (
        f"🛒 New Order\n\n"
        f"Customer: {customer_name}\n"
        f"Phone: {phone}\n"
        f"Address: {address}\n\n"
        f"Items:{items_list_str}\n\n"
        f"Total: ${total}"
    )
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    
    try:
        response = requests.post(url, json=payload, timeout=8)
        if response.status_code != 200:
            print(f"Telegram API returned non-200 response: Status {response.status_code}, Body {response.text}")
            return False
        return True
    except Exception as e:
        print(f"Failed to send Telegram notification due to connection error: {e}")
        return False
