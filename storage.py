"""Validate and atomically persist stock and receipt history in one JSON file."""
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from decimal import Decimal, InvalidOperation
from inventory import default_products


class StorageError(Exception):
    """An unreadable or unwritable state must never be silently overwritten."""


def new_state():
    return {'version': 1, 'products': default_products(), 'receipts': [], 'next_receipt': 1}


def validate_state(state):
    try:
        if not isinstance(state, dict) or state['version'] != 1:
            raise ValueError('Unsupported data version.')
        if type(state['next_receipt']) is not int or state['next_receipt'] < 1:
            raise ValueError('Invalid receipt sequence.')
        products, receipts = state['products'], state['receipts']
        if not isinstance(products, dict) or not products or not isinstance(receipts, list):
            raise ValueError('Invalid products or receipt history.')
        for code, product in products.items():
            if not isinstance(code, str) or not code or not isinstance(product['name'], str) or not product['name']:
                raise ValueError('Invalid product.')
            if type(product['stock']) is not int or product['stock'] < 0:
                raise ValueError('Invalid stock.')
            price = Decimal(product['price'])
            if not price.is_finite() or not 0 < price <= Decimal('1000000') or price != price.quantize(Decimal('0.01')):
                raise ValueError('Invalid price.')
        expected_ids = []
        for receipt in receipts:
            if not isinstance(receipt['timestamp'], str) or not isinstance(receipt['items'], list) or not receipt['items']:
                raise ValueError('Invalid receipt.')
            expected_ids.append(receipt['receipt_id'])
            line_sum = Decimal('0.00')
            for item in receipt['items']:
                if not isinstance(item['name'], str) or not isinstance(item['code'], str) or type(item['quantity']) is not int or item['quantity'] < 1:
                    raise ValueError('Invalid receipt item.')
                unit, line = Decimal(item['unit_price']), Decimal(item['line_total'])
                if not unit.is_finite() or unit <= 0 or line != unit * item['quantity']:
                    raise ValueError('Invalid receipt line total.')
                line_sum += line
            amounts = [Decimal(receipt[key]) for key in ('subtotal', 'discount', 'total', 'cash', 'change')]
            if any(not n.is_finite() or n < 0 or n != n.quantize(Decimal('0.01')) for n in amounts):
                raise ValueError('Invalid receipt amounts.')
            subtotal, discount, total, cash, change = amounts
            if subtotal != line_sum or discount > subtotal or total != subtotal - discount or cash - total != change:
                raise ValueError('Inconsistent receipt totals.')
        if expected_ids != [f'GBS-{n:05d}' for n in range(1, len(receipts) + 1)] or state['next_receipt'] != len(receipts) + 1:
            raise ValueError('Inconsistent receipt sequence.')
    except (KeyError, TypeError, InvalidOperation, ValueError, AttributeError) as exc:
        raise StorageError(f'Invalid saved data: {exc}') from exc


def load_state(path):
    path = Path(path)
    if not path.exists():
        return new_state()
    try:
        with path.open(encoding='utf-8') as stream:
            state = json.load(stream)
    except (OSError, ValueError) as exc:
        raise StorageError(f'Cannot read {path}: {exc}') from exc
    validate_state(state)
    return state


def save_state(path, state):
    """Replace the entire state only after a complete temporary file is flushed."""
    validate_state(state)
    path = Path(path)
    temporary = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile('w', encoding='utf-8', dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(state, stream, indent=2, ensure_ascii=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except OSError as exc:
        raise StorageError(f'Cannot save {path}: {exc}') from exc
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
