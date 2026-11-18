"""Product catalogue and shopping-cart operations (quantities are whole units)."""
from decimal import Decimal


def default_products():
    """Return a fresh catalogue; prices are stored as strings for exact money."""
    rows = [
        ('P001', 'Rice 5 kg', '28.50', 30),
        ('P002', 'Milk 1 L', '7.20', 40),
        ('P003', 'Bread loaf', '3.80', 35),
        ('P004', 'Eggs pack of 10', '6.50', 25),
        ('P005', 'Sugar 1 kg', '2.85', 40),
        ('P006', 'Cooking oil 1 kg', '6.90', 30),
        ('P007', 'Apples pack', '8.00', 20),
        ('P008', 'Tea 20 bags', '5.40', 25),
    ]
    return {code: {'name': name, 'price': price, 'stock': stock}
            for code, name, price, stock in rows}


def product_for(products, code):
    code = code.strip().upper()
    if code not in products:
        raise ValueError('Product code not found.')
    return code, products[code]


def validate_quantity(quantity):
    if type(quantity) is not int or not 1 <= quantity <= 999:
        raise ValueError('Quantity must be a whole number from 1 to 999.')


def add_to_cart(products, cart, code, quantity):
    """Repeated additions accumulate; stock changes only after checkout."""
    validate_quantity(quantity)
    code, product = product_for(products, code)
    updated = cart.get(code, 0) + quantity
    if updated > product['stock'] or updated > 999:
        raise ValueError('Requested quantity exceeds available stock or cart limit.')
    cart[code] = updated


def update_cart(products, cart, code, quantity):
    validate_quantity(quantity)
    code, product = product_for(products, code)
    if code not in cart:
        raise ValueError('This product is not in the cart.')
    if quantity > product['stock']:
        raise ValueError('Requested quantity exceeds available stock.')
    cart[code] = quantity


def remove_from_cart(cart, code):
    code = code.strip().upper()
    if code not in cart:
        raise ValueError('This product is not in the cart.')
    del cart[code]


def catalogue_text(products):
    lines = ['PRODUCT CATALOGUE', f'{"Code":<7}{"Product":<25}{"Price RM":>10}{"Stock":>8}', '-' * 50]
    for code, product in products.items():
        lines.append(f'{code:<7}{product["name"]:<25}{Decimal(product["price"]):>10.2f}{product["stock"]:>8}')
    return '\n'.join(lines)
