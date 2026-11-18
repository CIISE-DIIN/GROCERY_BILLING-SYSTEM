"""Run with python3 -m unittest discover -s tests -v."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from billing import calculate_bill, checkout, parse_money
from inventory import add_to_cart, update_cart, remove_from_cart
from storage import load_state, new_state, save_state, StorageError

ROOT = Path(__file__).resolve().parents[1]


class GroceryTests(unittest.TestCase):
    def setUp(self):
        self.state = new_state()
        self.products = self.state['products']
        self.cart = {}

    def test_repeated_addition_and_code_normalization(self):
        add_to_cart(self.products, self.cart, ' p001 ', 1)
        add_to_cart(self.products, self.cart, 'P001', 2)
        self.assertEqual(self.cart, {'P001': 3})

    def test_unknown_product(self):
        with self.assertRaises(ValueError):
            add_to_cart(self.products, self.cart, 'BAD', 1)

    def test_invalid_quantities(self):
        for value in (0, -1, 1.5, True, 1000):
            with self.subTest(value=value), self.assertRaises(ValueError):
                add_to_cart(self.products, self.cart, 'P001', value)

    def test_stock_limit_includes_existing_cart(self):
        add_to_cart(self.products, self.cart, 'P001', 30)
        with self.assertRaises(ValueError):
            add_to_cart(self.products, self.cart, 'P001', 1)
        self.assertEqual(self.cart['P001'], 30)
        self.assertEqual(self.products['P001']['stock'], 30)

    def test_update_and_remove(self):
        add_to_cart(self.products, self.cart, 'P001', 2)
        update_cart(self.products, self.cart, 'p001', 3)
        self.assertEqual(self.cart['P001'], 3)
        remove_from_cart(self.cart, 'p001')
        self.assertFalse(self.cart)

    def test_update_and_remove_missing(self):
        with self.assertRaises(ValueError):
            update_cart(self.products, self.cart, 'P001', 1)
        with self.assertRaises(ValueError):
            remove_from_cart(self.cart, 'P001')

    def test_empty_cart(self):
        with self.assertRaises(ValueError):
            calculate_bill(self.products, self.cart)

    def test_ordinary_bill(self):
        bill = calculate_bill(self.products, {'P001': 2, 'P002': 1})
        self.assertEqual((bill['subtotal'], bill['discount'], bill['total']), ('64.20', '0.00', '64.20'))

    def test_discount_boundary(self):
        self.products['P001']['price'] = '99.99'
        self.assertEqual(calculate_bill(self.products, {'P001': 1})['discount'], '0.00')
        self.products['P001']['price'] = '100.00'
        bill = calculate_bill(self.products, {'P001': 1})
        self.assertEqual((bill['discount'], bill['total']), ('5.00', '95.00'))

    def test_discount_rounds_half_up(self):
        self.products['P001']['price'] = '100.10'
        self.assertEqual(calculate_bill(self.products, {'P001': 1})['discount'], '5.01')

    def test_bad_cash(self):
        for value in ('abc', '', '-1', 'NaN', 'Infinity', '1.001', '1000001'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_money(value)

    def test_insufficient_payment_does_not_mutate(self):
        with self.assertRaises(ValueError):
            checkout(self.state, {'P001': 1}, '1')
        self.assertEqual(self.products['P001']['stock'], 30)
        self.assertFalse(self.state['receipts'])

    def test_checkout_and_exact_change(self):
        state, receipt = checkout(self.state, {'P001': 4, 'P002': 2}, '150')
        self.assertEqual((receipt['subtotal'], receipt['discount'], receipt['total'], receipt['change']),
                         ('128.40', '6.42', '121.98', '28.02'))
        self.assertEqual(state['products']['P001']['stock'], 26)
        self.assertEqual(self.products['P001']['stock'], 30)
        self.assertEqual(state['next_receipt'], 2)

    def test_exact_payment(self):
        _, receipt = checkout(self.state, {'P003': 1}, '3.80')
        self.assertEqual(receipt['change'], '0.00')

    def test_stock_rechecked_at_checkout(self):
        self.products['P001']['stock'] = 0
        with self.assertRaises(ValueError):
            checkout(self.state, {'P001': 1}, '50')

    def test_save_reload_and_receipt_sequence(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'store.json'
            self.assertEqual(load_state(path)['next_receipt'], 1)
            state, _ = checkout(self.state, {'P003': 1}, '10')
            save_state(path, state)
            loaded = load_state(path)
            self.assertEqual(loaded, state)
            _, second = checkout(loaded, {'P003': 1}, '10')
            self.assertEqual(second['receipt_id'], 'GBS-00002')

    def test_corrupt_file_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'store.json'
            path.write_text('{bad json')
            with self.assertRaises(StorageError):
                load_state(path)
            self.assertEqual(path.read_text(), '{bad json')

    def test_invalid_saved_schema(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'store.json'
            for bad in ({}, dict(self.state, next_receipt=0), dict(self.state, products=[])):
                path.write_text(json.dumps(bad))
                with self.assertRaises(StorageError):
                    load_state(path)

    def test_failed_save_preserves_old_file(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'store.json'
            save_state(path, self.state)
            old = path.read_text()
            changed, _ = checkout(self.state, {'P003': 1}, '10')
            with patch('storage.os.replace', side_effect=OSError('simulated disk failure')):
                with self.assertRaises(StorageError):
                    save_state(path, changed)
            self.assertEqual(path.read_text(), old)
            self.assertEqual(len(list(Path(folder).iterdir())), 1)

    def test_cli_full_checkout_and_restart(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'store.json'
            command = [sys.executable, str(ROOT / 'main.py'), '--data-file', str(path)]
            result = subprocess.run(command, input='9\n2\nP001\n4\n2\nP002\n2\n6\n150\n0\n', text=True, capture_output=True)
            self.assertEqual(result.returncode, 0)
            self.assertIn('Invalid option', result.stdout)
            self.assertIn('Change:   RM 28.02', result.stdout)
            again = subprocess.run(command, input='7\nGBS-00001\n0\n', text=True, capture_output=True)
            self.assertIn('TOTAL:    RM 121.98', again.stdout)
            self.assertEqual(load_state(path)['products']['P001']['stock'], 26)

    def test_cli_cancel_and_invalid_quantity(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'store.json'
            result = subprocess.run([sys.executable, str(ROOT / 'main.py'), '--data-file', str(path)],
                                    input='2\nP001\nhello\n2\nP001\n1\n6\nC\n0\nY\n', text=True, capture_output=True)
            self.assertIn('Quantity must be a whole number.', result.stdout)
            self.assertIn('Checkout cancelled. Cart retained.', result.stdout)
            self.assertFalse(path.exists())


if __name__ == '__main__':
    unittest.main()
