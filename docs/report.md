# Grocery Billing System Technical Report

BIT2083 BIT1054 BCS2013
Fundamental of Computational Thinking Python
Assignment 2 Pair Assignment
Faculty of Information Technology
City University Malaysia Cyberjaya Campus
Assessment weight 20 percent
Submission deadline 20 November 2026

Student 1 full name: ________________________________________
Student 1 ID: ______________________________________________
Student 2 full name: ________________________________________
Student 2 ID: ______________________________________________
Class code: ________________________________________________
Program: ___________________________________________________

The project is a menu-driven Python application that calculates grocery bills, validates purchases, records cash payments, and retains stock and receipts. This report explains its problem analysis, implementation, use of computational thinking, verification, and limitations. Source code and execution evidence accompany the report.

[[PAGE]]
# 1 Introduction

Computational thinking provides a structured way to turn an everyday problem into steps that a computer can execute. Grocery checkout involves repeated calculations, decisions about available stock, and clear communication of the amount payable. Manual calculations can produce incorrect totals, omitted items, and inconsistent stock records. A small program can apply the same rules to each purchase and make its calculations visible to the cashier.

This project applies decomposition, pattern recognition, abstraction, and algorithm design to grocery billing. The resulting application separates user interaction, inventory operations, billing calculations, and file storage. These boundaries make the program easier to understand and allow important rules to be tested independently of keyboard input.

# 2 Task Overview

The selected application is the Grocery Billing System. The coding task is to develop a Python menu that supports a complete purchase: browse products, add or change quantities, calculate a bill, receive cash, produce a receipt, and preserve the completed transaction. The main challenges are validating input, calculating money accurately, and keeping saved stock consistent with receipt history.

The program uses four Python source modules and Python's standard library. It includes more than three reusable functions, variables, strings, integers, dictionaries, lists, loops, conditional branches, input and output, comments, and exception handling. The catalogue contains eight packaged products with product codes, prices, and stock quantities. No graphical interface or external database is required by this solution.

# 3 Problem Analysis

The problem is to produce reliable grocery bills while preventing purchases beyond available stock. For a small shop, an incorrect total affects payment and customer confidence. A stock count that is changed before payment succeeds can also make later purchases incorrect. The program therefore validates the cart before checkout and changes permanent stock only when a sale has been saved.

Expected users are a cashier, a small-shop operator, and students demonstrating introductory Python. A cashier needs concise menu choices and understandable error messages. The shop operator needs receipts that remain available after the program closes. Students need readable functions that expose the logic rather than hiding it behind a framework.

The scope is a single local operator using cash and whole packaged units. Prices are in RM. An assignment promotion gives 5 percent off a subtotal of RM 100.00 or more. No tax is added. This promotion and the tax-free teaching example are design choices rather than statements of legal or statutory requirements.

[[PAGE]]
# 4 Python Implementation

## 4.1 Program flow

The application reads its data-file path, loads validated stock and receipts, and creates an empty cart. If there is no saved file, it uses the initial catalogue. A loop displays the menu and dispatches the selected operation. Invalid menu choices and invalid purchase values produce an explanation and return control to the menu.

At checkout, the program validates the current cart and calculates its subtotal and discount. The cashier can enter C to cancel while retaining the cart. Otherwise, the cash amount must cover the total. A successful calculation produces a proposed new state with reduced stock, a receipt, and the next receipt number. The storage module saves that state before the application replaces its current state or clears the cart. This order prevents a failed save from being reported as a completed sale.

FLOW: Start -> load state -> display menu -> read choice -> validate input -> perform operation -> display result -> repeat menu. Checkout adds: calculate bill -> validate cash -> build proposed sale -> save state -> display receipt -> clear cart. Exit ends the loop; an unpaid cart requires confirmation before it is discarded.

## 4.2 Major modules and functions

| Module | Main responsibilities | Example functions |
| --- | --- | --- |
| main.py | Menu, keyboard input, operation dispatch, save coordination | run, read_quantity, main |
| inventory.py | Catalogue, product lookup, quantity and stock validation | add_to_cart, update_cart, remove_from_cart |
| billing.py | Exact money, discount, cash validation, sale and receipt | calculate_bill, parse_money, checkout, receipt_text |
| storage.py | Initial state, saved-data validation, atomic JSON persistence | new_state, load_state, validate_state, save_state |

## 4.3 Data representation

The product catalogue is a dictionary keyed by product code. Each value contains a name, a decimal price represented as text, and integer stock. The cart is a dictionary from product code to quantity. This avoids storing the same product more than once; adding the same code increases its existing quantity. A receipt contains a list of item records and the totals, cash, change, identifier, and timestamp.

The saved state contains a schema version, products, receipt history, and next receipt number. Product names and prices are copied into each receipt so the historical sale is self-contained. The unpaid cart remains in memory and is not restored after exit. Data storage grows with completed sales because this introductory system retains all receipts in one JSON document.

[[PAGE]]
# 4 Python Implementation Continued

## 4.4 Input and output

Inputs are menu choices, product codes, positive integer quantities, cash, confirmation responses, and receipt IDs. Product codes are trimmed and converted to uppercase. Quantity parsing rejects words and fractions, while validation rejects zero, negative values, excessive quantities, and stock shortages. Cash must be finite, nonnegative, within the configured upper limit, and expressible in whole sen.

Outputs include the catalogue, cart lines, subtotal, discount, payable total, cash, change, stock information, saved receipts, and validation messages. Successful receipts receive sequential identifiers such as GBS-00001 and an automatically recorded local timestamp. The optional --data-file argument selects a separate practice store without changing the source code.

## 4.5 Calculation rules and worked example

For each cart item, line total equals unit price multiplied by quantity. Subtotal is the sum of line totals. If subtotal is at least RM 100.00, discount is 5 percent of subtotal, rounded to two decimal places using ROUND_HALF_UP. Otherwise the discount is zero. Total equals subtotal minus discount, and change equals cash minus total. The system rejects cash below the total.

| Item or calculation | Quantity | Amount RM |
| --- | --- | --- |
| Rice at RM 28.50 | 4 | 114.00 |
| Milk at RM 7.20 | 2 | 14.40 |
| Subtotal | | 128.40 |
| Discount at 5 percent | | 6.42 |
| Payable total | | 121.98 |
| Cash received | | 150.00 |
| Change returned | | 28.02 |

The successful sale reduces rice stock from 30 to 26 and milk stock from 40 to 38. A cash entry of RM 100.00 is rejected because it is below RM 121.98. The rejected payment leaves both stock and the cart unchanged.

## 4.6 Development decisions

Decimal is used instead of binary floating-point arithmetic because billing needs predictable decimal amounts. Prices are saved as strings to preserve this representation through JSON. A dictionary is used for fast product lookup and consolidated cart quantities. Standard-library modules keep the application easy to run on another laptop.

Stock and receipts are saved together in one JSON state. A temporary file is written and flushed before os.replace replaces the previous state. This reduces partial-file risk and avoids separately saving stock and receipts. It does not provide a database transaction across concurrent processes, so one running instance per data file is an operating limitation.

[[PAGE]]
# 5 Application of Computational Thinking

## 5.1 Decomposition

The overall purchase is divided into catalogue management, cart editing, billing, payment, receipt presentation, and persistence. Each part has a defined responsibility. For example, add_to_cart validates and updates quantities without asking for keyboard input, while main.py obtains that input. calculate_bill returns structured totals without writing files. This separation allows a calculation error to be investigated independently of the menu and storage logic.

## 5.2 Pattern Recognition

Every product has the same attributes: code, name, price, and stock. Every bill line follows the same multiplication rule. Recognising these repeated structures leads to dictionaries and a loop rather than a separate branch for rice, milk, bread, and every other product. Repeated invalid-input cases also follow a common pattern: raise a descriptive error, display it at the menu boundary, and let the user try again.

Adding the same product repeatedly is another pattern. The cart consolidates these additions under one product code, and the stock check compares the combined quantity with availability. This prevents a cashier from bypassing the stock limit through multiple small additions.

## 5.3 Abstraction

The cashier interacts with a short product code and quantity rather than the full internal product record. The bill calculation works with those quantities and catalogue prices; it does not need to know how input was typed or where the JSON file is stored. The receipt exposes relevant information about a completed purchase without showing internal temporary filenames or Python objects.

The implementation also deliberately omits supplier ordering, loyalty accounts, variable-weight produce, and multiple payment methods. Keeping these outside the scope focuses the model on the details needed for a correct introductory checkout system.

## 5.4 Algorithm Design

The checkout algorithm is deterministic and uses explicit validation before state change. It processes each cart item once, checks stock, calculates the line total, sums the subtotal, applies the threshold rule, validates payment, builds a proposed updated state, and saves it. Only after saving does the menu clear the cart and confirm the sale.

PSEUDOCODE
1. Reject checkout when the cart is empty.
2. For each cart item, validate product and quantity; reject insufficient stock.
3. Calculate line totals and sum the subtotal.
4. Apply and round the 5 percent discount if subtotal reaches RM 100.00.
5. Read cash; reject invalid values or cash below the total.
6. Copy state; reduce stock; append receipt; increment receipt number.
7. Save the proposed state; if saving fails, retain the current state and cart.
8. On successful saving, replace current state, clear cart, and print receipt.

For c distinct cart items, bill calculation visits c items and therefore takes O(c) time. Saving rewrites the catalogue and full receipt history, so persistence cost increases with the number of stored sales. That tradeoff is acceptable for a small teaching project but suggests a database for larger use.

[[PAGE]]
# 6 Challenges Encountered

## 6.1 Technical issues

Money rounding and input validation need explicit rules. For example, five percent of RM 100.10 is RM 5.005 before rounding. The chosen rule gives RM 5.01, and an automated test fixes that expectation. Special values such as NaN and Infinity must also be rejected even though Decimal can parse them. Validating only whether conversion succeeds would be insufficient.

A second challenge is preserving consistency when payment is rejected or a disk write fails. Checkout therefore returns a separate proposed state. The current state changes only after saving succeeds. Persisted JSON is validated at startup; unreadable or inconsistent saved data stops the program with an explanation rather than being silently replaced by new stock.

## 6.2 Debugging and verification approach

The tests isolate calculations, cart edits, and storage operations before exercising the full menu in a subprocess. Tests cover the discount threshold, half-up rounding, invalid cash, combined quantities, out-of-stock checkout, sequential receipts, and restart persistence. A simulated file-replacement failure verifies that the previous saved file survives and that a temporary file is cleaned up.

The tests establish specific behaviours. Large receipt histories and simultaneous cashiers remain outside the verified scope.

## 6.3 Team collaboration

A suitable pair workflow separates implementation from independent checking and then swaps roles. One student can trace the menu and cart operations while the other manually calculates the receipt and checks validation cases. Both students should be able to explain how a sale moves from unpaid cart to saved receipt.

Student 1 actual contribution: __________________________________
________________________________________________________________
Student 2 actual contribution: __________________________________
________________________________________________________________
Actual coordination method and experience: ______________________
________________________________________________________________

[[PAGE]]
# 7 Reflection

The project demonstrates that computational thinking is useful before writing syntax. Choosing the right data representation removes repeated special cases, while separating calculation from input makes debugging more focused. A small program can still require careful decisions about when information becomes permanent.

The implementation provides practice with functions, modules, loops, dictionaries, exception handling, Decimal, JSON, and automated testing. Boundary checks reveal behaviour that an ordinary successful example cannot show. Testing both RM 99.99 and RM 100.00, for example, verifies the exact point at which the promotion begins.

Potential improvements include an operator-controlled restocking menu, receipt searching, refunds, and a database with concurrency control. These should be introduced only with corresponding validation and tests. Each student's personal learning and actual teamwork experience should be recorded below after reviewing and running the project.

Personal learning and skill improvement: _________________________
________________________________________________________________
Teamwork lesson and next improvement: ___________________________
________________________________________________________________

[[PAGE]]
# 8 Verification Results

The recorded verification run completed 21 automated tests successfully. The suite includes unit tests and complete command-line sessions. It uses temporary files, so the submitted project does not contain completed customer sales or reduced production stock.

| Test group | Cases | Verified behaviour |
| --- | --- | --- |
| Cart operations | 6 | Repeated add, unknown code, invalid quantities, combined stock limit, update and remove, missing cart item |
| Bill calculation | 4 | Empty cart, ordinary total, discount threshold, half-up rounding |
| Cash and checkout | 5 | Invalid cash, insufficient cash, discounted sale and change, exact payment, stock recheck |
| Storage | 4 | Save and reload, corrupt JSON preservation, invalid schema, failed replacement preserves old file |
| Full application | 2 | Checkout and restart, invalid quantity and cancelled payment |

[[IMAGE:05_tests.png|Figure 1 Actual automated test summary]]

Manual verification of the sample bill independently reproduces RM 114.00 plus RM 14.40 equals RM 128.40. Five percent is RM 6.42, leaving RM 121.98. Subtracting that total from RM 150.00 gives RM 28.02. These expected values are asserted in the checkout test and appear in the recorded application session.

A second test puts a product price at RM 99.99 and then RM 100.00. The first receives no discount; the second receives RM 5.00. Another test uses RM 100.10 and checks a discount of RM 5.01, demonstrating the selected rounding rule rather than depending on an accidental floating-point result.

Reproduce the suite from the project folder using python3 -m unittest discover -s tests -v. The full recorded output is docs/test_results.txt. The complete menu demonstration, including entered values, is docs/demo_transcript.txt.

# 9 Conclusion

The Grocery Billing System fulfils the local Python application requirements through a modular menu, structured data, validation, reusable functions, and complete cash checkout. It calculates bills consistently, rejects invalid purchases, and preserves completed stock changes with their receipts. Computational thinking connects the original shop problem to a clear data model and a testable algorithm.

The source folder and report provide a basis for demonstration and explanation. The remaining submission activities are completing student details and personal reflections, reviewing and signing the AI declaration, and uploading the source to the students' own GitHub repository before adding its URL to the final report.

[[PAGE]]
# Appendix A User Guide and Menu Evidence

## A1 Starting the program

Install Python 3.10 or later. Open a terminal in the supplied folder and run python3 main.py. On Windows, py main.py can be used if python3 is not available. The application and its tests use the standard library and require no extra packages or network access.

[[IMAGE:01_menu.png|Figure 2 Main menu from the recorded application session]]

## A2 Preparing a purchase

Choose 1 to browse the catalogue. Choose 2, enter a product code such as P001, and enter a positive whole quantity. Repeat to add other products. Choose 3 to review the bill, 4 to replace a quantity, or 5 to remove a product. Choose 8 and confirm Y to empty the cart.

Choose 6 to pay. Enter sufficient cash in RM, or C to cancel payment. A successful sale displays its receipt and clears the cart. Choose 7 to list saved receipts, then enter an identifier such as GBS-00001 to read one again. Choose 0 to exit. If the cart is unpaid, confirm whether to discard it.

## A3 Safe demonstration and recovery

Use python3 main.py --data-file practice/store.json for a separate practice shop. Completed sales persist in that file; the unpaid cart does not. Keep one running instance per file. If saved data is damaged, preserve it for investigation and recover a backup or use a fresh data-file path. The application intentionally stops rather than resetting damaged data automatically.

[[PAGE]]
# Appendix B Execution Evidence

The figures below reproduce actual console output captured through a pseudoterminal. The images are rendered excerpts of that recorded session, with the complete transcript supplied alongside the source. They show the catalogue and the completed sample sale.

[[IMAGE:02_catalogue.png|Figure 3 Initial catalogue with prices and available stock]]

[[IMAGE:04_receipt.png|Figure 4 Saved sale with subtotal discount cash and change]]

[[PAGE]]
# Appendix C Validation and Requirement Mapping

The first attempted payment in the captured session was RM 100.00. The program rejected it because the payable total was RM 121.98. Retrying with RM 150.00 then completed the same cart, demonstrating that the failed attempt did not discard it.

[[IMAGE:03_validation.png|Figure 5 Insufficient cash is rejected with the amount due]]

| Assignment requirement | Evidence in the delivered project |
| --- | --- |
| Python programming | main.py, inventory.py, billing.py, storage.py |
| Variables and data types | String codes, integer quantities, Decimal money, dictionaries and lists |
| Input and output | Menu prompts, catalogue, bill, receipts, error messages |
| Decision making | Menu branches, stock checks, discount threshold, payment validation |
| Loops | Repeated menu, catalogue display, cart processing, receipt listing |
| At least three functions | run, add_to_cart, calculate_bill, checkout and others |
| At least two Python files | Four application modules plus automated tests |
| Lists or dictionaries | Product catalogue, cart, receipt records and receipt history |
| Basic error handling | Quantity, code, stock, payment and saved-file validation |
| Menu-driven interface | Nine numbered choices including exit |
| Meaningful comments | Module and function docstrings, rounding and save-order comments |
| Source on GitHub | To be uploaded by the students from their own laptop |
| Report and demonstration | This PDF, captured session, evidence images and README |

GitHub repository URL: __________________________________________
________________________________________________________________

Competition certificate: Not applicable to this grocery application task.
Source reference: Assignment 2 brief supplied for BIT2083 BIT1054 BCS2013 Fundamental of Computational Thinking Python, pages 2 to 4 and 7 to 11. It supplies the task, report sections, AI declaration, rubric, and submission requirements. No external research claims or fabricated references are used in this report.

[[PAGE]]
# Appendix D Student AI Declaration

## Material AI contribution

AI tool or platform: OpenAI ChatGPT Codex
Purpose: Assistance with problem decomposition, Python source generation, test generation and execution, report drafting, execution-evidence preparation, and document formatting.

Material contribution: AI substantially assisted with the implementation and report. Automated verification is included in the delivered folder. Each student remains responsible for running the application, understanding its functions, checking the calculations, evaluating the report, and accurately recording their own contribution and learning.

## Declaration to sign after personal review

I declare that I used OpenAI ChatGPT Codex in preparing this assessment for software development, testing support, and report drafting. I have reviewed and critically evaluated the output, verified relevant information, and modified the material as appropriate. I accept full responsibility for the accuracy, integrity, and final content of my submission.

| Student | Full name | Signature | Date |
| --- | --- | --- | --- |
| Student 1 | | | |
| Student 2 | | | |

## Review record

Application run and main functions explained: ____________________
Sample calculation checked independently: _______________________
Source changes and report revisions made by the students: _______
________________________________________________________________
________________________________________________________________
Personal reflection and actual pair contributions completed: ____
________________________________________________________________

The declaration is intentionally unsigned. Signing records the student's own review and acceptance of responsibility; the delivered automated test results do not replace that personal review.
