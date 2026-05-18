PRICE_MAP = {
    'plastic': 15,
    'paper': 10,
    'metal': 40,
    'glass': 12,
    'organic': 5,
    'other': 8,
}

def predict_price(waste_type, weight_kg):
    base_price = PRICE_MAP.get(waste_type, 10)
    return round(base_price * weight_kg, 2)
