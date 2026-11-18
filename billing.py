"""Exact bill calculations, payment validation, checkout, and text receipts."""
from copy import deepcopy
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from inventory import product_for, validate_quantity

CENT = Decimal('0.01')
DISCOUNT_THRESHOLD = Decimal('100.00')
DISCOUNT_RATE = Decimal('0.05')


def parse_money(text):
    """Accept finite, nonnegative cash values with no fraction of a sen."""
    try:
        amount = Decimal(str(text).strip())
    except (InvalidOperation, ValueError):
        raise ValueError('Enter a valid cash amount, for example 50.00.') from None
    if not amount.is_finite() or amount < 0 or amount > Decimal('1000000'):
        raise ValueError('Cash must be between RM 0.00 and RM 1000000.00.')
    if amount != amount.quantize(CENT):
        raise ValueError('Cash cannot contain fractions of a sen.')
    return amount.quantize(CENT)


def calculate_bill(products, cart):
    if not cart:
        raise ValueError('The cart is empty. Add products first.')
    items = []
    for code, quantity in cart.items():
        validate_quantity(quantity)
        code, product = product_for(products, code)
        if quantity > product['stock']:
            raise ValueError(f'Insufficient stock for {code}.')
        price = Decimal(product['price'])
        total = (price * quantity).quantize(CENT)
        items.append({'code': code, 'name': product['name'], 'quantity': quantity,
                      'unit_price': str(price), 'line_total': str(total)})
    subtotal = sum((Decimal(item['line_total']) for item in items), Decimal('0.00'))
    # This is an assignment store promotion, not a statutory tax policy.
    discount = (subtotal * DISCOUNT_RATE).quantize(CENT, rounding=ROUND_HALF_UP) if subtotal >= DISCOUNT_THRESHOLD else Decimal('0.00')
    return {'items': items, 'subtotal': str(subtotal), 'discount': str(discount),
            'total': str(subtotal - discount)}


def checkout(state, cart, payment, now=None):
    """Build a new state without mutating the original; caller must save it."""
    bill = calculate_bill(state['products'], cart)
    paid = parse_money(payment)
    total = Decimal(bill['total'])
    if paid < total:
        raise ValueError(f'Insufficient cash. Amount due is RM {total:.2f}.')
    result = deepcopy(state)
    receipt = dict(bill, receipt_id=f'GBS-{state["next_receipt"]:05d}',
                   timestamp=(now or datetime.now().astimezone()).isoformat(timespec='seconds'),
                   cash=str(paid), change=str(paid - total))
    for item in bill['items']:
        result['products'][item['code']]['stock'] -= item['quantity']
    result['receipts'].append(receipt)
    result['next_receipt'] += 1
    return result, receipt


def bill_text(bill):
    lines = [f'{"Item":<23}{"Qty":>4}{"RM each":>10}{"RM total":>11}', '-' * 48]
    for item in bill['items']:
        lines.append(f'{item["name"]:<23}{item["quantity"]:>4}{Decimal(item["unit_price"]):>10.2f}{Decimal(item["line_total"]):>11.2f}')
    lines += ['-' * 48, f'Subtotal: RM {bill["subtotal"]}',
              f'Discount: RM {bill["discount"]}', f'TOTAL:    RM {bill["total"]}']
    return '\n'.join(lines)


def receipt_text(receipt):
    return '\n'.join(['ISSE GROCERY BILLING SYSTEM', 'RECEIPT ' + receipt['receipt_id'],
                      receipt['timestamp'], bill_text(receipt),
                      f'Cash:     RM {receipt["cash"]}', f'Change:   RM {receipt["change"]}',
                      'Thank you for shopping with us.'])
