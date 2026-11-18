"""Run with python3 main.py. No third-party packages or network are needed."""
import argparse
from pathlib import Path
from billing import bill_text, calculate_bill, checkout, receipt_text
from inventory import add_to_cart, update_cart, remove_from_cart, catalogue_text
from storage import StorageError, load_state, save_state

MENU = '''
============================================
       ISSE GROCERY BILLING SYSTEM
============================================
1. View product catalogue
2. Add product to cart
3. View cart and bill
4. Update quantity
5. Remove product
6. Checkout and pay
7. View saved receipts
8. Clear cart
0. Exit
'''


def read_quantity():
    try:
        return int(input('Quantity (whole units): ').strip())
    except ValueError:
        raise ValueError('Quantity must be a whole number.') from None


def run(data_file):
    try:
        state = load_state(data_file)
    except StorageError as exc:
        print(f'STORAGE ERROR: {exc}')
        print('Keep the data file for recovery. The program has stopped safely.')
        return 1
    cart = {}
    print('Prices in RM. Promotion: 5% off a subtotal of RM 100 or more.')
    print('No tax is added in this teaching application.')
    try:
        while True:
            print(MENU)
            choice = input('Choose an option: ').strip()
            try:
                if choice == '1':
                    print(catalogue_text(state['products']))
                elif choice == '2':
                    code = input('Product code: ')
                    add_to_cart(state['products'], cart, code, read_quantity())
                    print('Product added to cart.')
                elif choice == '3':
                    print(bill_text(calculate_bill(state['products'], cart)))
                elif choice == '4':
                    code = input('Product code: ')
                    update_cart(state['products'], cart, code, read_quantity())
                    print('Quantity updated.')
                elif choice == '5':
                    remove_from_cart(cart, input('Product code: '))
                    print('Product removed.')
                elif choice == '6':
                    print(bill_text(calculate_bill(state['products'], cart)))
                    paid = input('Cash received in RM (or C to cancel): ').strip()
                    if paid.upper() == 'C':
                        print('Checkout cancelled. Cart retained.')
                        continue
                    updated, receipt = checkout(state, cart, paid)
                    # Save first: a failed write leaves the in-memory sale and cart intact.
                    save_state(data_file, updated)
                    state = updated
                    cart.clear()
                    print(receipt_text(receipt))
                    print('Sale saved. Cart cleared.')
                elif choice == '7':
                    if not state['receipts']:
                        print('No saved receipts yet.')
                    else:
                        for receipt in state['receipts']:
                            print(f'{receipt["receipt_id"]} | {receipt["timestamp"]} | RM {receipt["total"]}')
                        code = input('Receipt ID to view (Enter to return): ').strip().upper()
                        if code:
                            match = next((r for r in state['receipts'] if r['receipt_id'] == code), None)
                            if match is None:
                                raise ValueError('Receipt not found.')
                            print(receipt_text(match))
                elif choice == '8':
                    if input('Clear the cart? (Y/N): ').strip().upper() == 'Y':
                        cart.clear()
                        print('Cart cleared.')
                    else:
                        print('Cart retained.')
                elif choice == '0':
                    if cart and input('Discard unpaid cart and exit? (Y/N): ').strip().upper() != 'Y':
                        continue
                    print('Goodbye.')
                    return 0
                else:
                    print('Invalid option. Choose a number shown in the menu.')
            except (ValueError, StorageError) as exc:
                print(f'ERROR: {exc}')
    except (EOFError, KeyboardInterrupt):
        print('\nSession ended. Unpaid cart discarded; completed sales remain saved.')
        return 0


def main():
    parser = argparse.ArgumentParser(description='Menu-driven grocery checkout')
    parser.add_argument('--data-file', type=Path,
                        default=Path(__file__).resolve().parent / 'data' / 'store.json',
                        help='Path for saved stock and receipts')
    args = parser.parse_args()
    return run(args.data_file)


if __name__ == '__main__':
    raise SystemExit(main())
