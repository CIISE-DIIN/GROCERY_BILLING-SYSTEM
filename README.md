# Grocery Billing System

Python coursework project for BIT2083 / BIT1054 / BCS2013 Assignment 2.
This folder contains a menu-driven application, automated tests, execution evidence,
and the PDF technical report. It is a plain folder, without Git configuration.

## Run

Install Python 3.10 or later, then open a terminal in this folder:

```sh
python3 main.py
```

On Windows, use `py main.py` if `python3` is unavailable.
No external packages, database server, account, or internet connection are needed
for the application or its tests.

## Menu

1. View the eight-product catalogue, prices, and stock.
2. Add products using codes P001 to P008 and positive whole quantities.
3. Display the cart, subtotal, discount, and total.
4. Replace the quantity of an existing cart product.
5. Remove a product from the cart.
6. Accept cash and save a completed sale.
7. List saved receipts and reopen a receipt by ID.
8. Clear the unpaid cart after confirmation.
0. Exit; confirm if an unpaid cart remains.

At payment, enter `C` to cancel checkout and retain the cart.
Prices use Malaysian ringgit (RM). A teaching promotion gives 5% off when the
subtotal reaches RM 100.00, rounded half up to the nearest sen. No tax is added.
These are explicitly chosen assignment rules, not claims about Malaysian tax law.
Quantities are whole packaged units, including the packaged fruit product.

## Example sale

Add P001, quantity 4, then P002, quantity 2. Choose checkout and enter 150.
Subtotal = RM 128.40; discount = RM 6.42; total = RM 121.98;
change = RM 28.02. Rice stock falls from 30 to 26, and milk stock from 40 to 38.

## Saved data

A successful checkout creates `data/store.json` next to the source files. It
stores stock, receipt history, and the next receipt number together. The unpaid
cart exists only during the running session. Stock changes only on completed,
saved sales. No data file is created by simply browsing or cancelling checkout.

For an isolated practice session:

```sh
python3 main.py --data-file practice/store.json
```

Use a fresh path to start a separate sample shop. Keep a backup of any data you
want to retain. If the saved file is corrupted, the application stops and preserves
it; recover from a known good backup or start with a different data-file path.
Run only one instance against a particular data file. The project has no
multi-user locking, login system, stock replenishment, refunds, or barcode reader.

## Verify

```sh
python3 -m unittest discover -s tests -v
```

The supplied evidence records 21 passing tests. Test runs use temporary data,
leaving the real store untouched. See `docs/test_results.txt` and
`docs/demo_transcript.txt` for captured execution output.

## Files

- `main.py`: menu, input handling, and save-before-confirm workflow.
- `inventory.py`: catalogue and cart validation.
- `billing.py`: Decimal calculations, payment, checkout, and receipt formatting.
- `storage.py`: JSON validation and atomic file replacement.
- `tests/test_system.py`: unit and end-to-end tests.
- `output/pdf/Grocery_Billing_System_Report.pdf`: assignment report.
- `docs/report.md`: editable report text.
- `docs/screenshots/`: images of captured application output.
- `tools/`: optional scripts used to create evidence and the PDF report.

## Before submission

Fill the empty student details, add the pair's actual collaboration and personal
reflection, and review the code and report. Both students should complete and sign
the AI declaration after their own review. The PDF includes a blank GitHub URL
field. On the recipient's own laptop, create a GitHub repository, upload this
folder, and add that repository URL to the report as required by the brief.
No Git repository has been initialized and nothing has been uploaded from here.

The final submission requires the PDF report and the source repository through
Moodle. The brief gives 20 November 2026 as the submission deadline.

## Optional report regeneration

The application itself is dependency-free. Only PDF/evidence generation needs
`reportlab` and `Pillow`. With those installed:

```sh
python3 tools/capture_demo.py
python3 tools/build_report.py
```

The PDF report is provided ready to open; regeneration is optional. Editable
report prose is in `docs/report.md`.
