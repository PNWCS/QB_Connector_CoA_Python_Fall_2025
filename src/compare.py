"""Comparison helpers for account types."""

from __future__ import annotations

from typing import Dict, Iterable

from .models import ComparisonReport
from .models import Conflict
from .models import Account


def compare_account_types(
    excel_terms: Iterable[Account],
    qb_terms: Iterable[Account],
) -> ComparisonReport:
    """Compare Excel and QuickBooks accounts and identify discrepancies.

    This function reconciles accounts from two sources (Excel and QuickBooks)
    by comparing their ``id`` field. Students must implement
    the logic to detect three types of discrepancies:

    1. Accounts that exist only in Excel
    2. Accounts that exist only in QuickBooks
    3. Accounts with matching ``id`` but different ``name`` and/or ``number`` and/or ``AccountType`` values

    **Input Parameters:**

    :param excel_terms: An iterable of :class:`~src.models.Account`
        objects sourced from Excel. Each Account has:

        - ``AccountType`` (str): account type identifier
        - ``id`` (str): Unique identifier of the account
        - ``name`` (str): Display name of the account type
        - ``number`` (str): Account number
        - ``source`` (SourceLiteral): Will be "excel" for these terms

        Example: ``Account(AccountType="Other Expense", id="101" name="Expense", number="123", source="excel")``

    :param qb_accounts: An iterable of :class:`~src.models.Account`
        objects sourced from QuickBooks. Structure is identical to ``excel_accounts``
        but with ``source="quickbooks"``.

        Example: ``Account(AccountType="Other Expense", id="101" name="Expense", number="123", source="quickbooks")``

    **Return Value:**

    :return: A :class:`~src.models.ComparisonReport` object containing
        three lists that categorize all discrepancies found:

        - ``excel_only`` (list[PaymentTerm]): Types with ``account_type`` values that
          appear in ``excel_terms`` but NOT in ``qb_terms``. These represent account
          types that need to be added to QuickBooks.

        - ``qb_only`` (list[PaymentTerm]): Types with ``account_type`` values that
          appear in ``qb_terms`` but NOT in ``excel_terms``. These represent account
          types that may need to be removed from QuickBooks or added to Excel.

        - ``conflicts`` (list[Conflict]): Types where the same ``id`` exists
          in both sources but the ``name`` and/or ``number`` and/or ``AccountType``
          field differs. Each :class:`~src.models.Conflict` must have:

          - id: str Identifier of the account type with the conflict

          - excel_AccountType: str - The account type from Excel
          - qb_AccountType: str - The account type from QuickBooks

          - excel_name: str | None - The name from Excel
          - qb_name: str | None - The name from QuickBooks

          - excel_number: str | None - The number from Excel
          - qb_number: str | None - The number from QuickBooks

         reason: ConflictReason - Set to "data_mismatch" to indicate differing data

    **Implementation Requirements:**

    1. Compare types based on their ``id`` field (case-sensitive)
    2. Build dictionaries or sets for efficient lookup of account types
    3. Identify ids unique to each source (Excel-only and QB-only)
    4. For matching ``id`` values, compare the ``name``, ``number``, and ``AccountType`` fields
    5. If any fields differ, create a Conflict with reason ``"data_mismatch"``
    6. Return all findings in a ComparisonReport object

    **Example:**

    Given these inputs::

        excel_terms = [
            Account(AccountType="ASSET", id="1", name="Asset", number="1000", source="excel"),
            Account(AccountType="EXPENSE", id="2", name="Expense", number="2000", source="excel"),
            Account(AccountType="INCOME", id="3", name="Income", number="3000", source="excel"),
        ]

        qb_terms = [
            Account(AccountType="LIABILITY", id="4", name="Liability", number="4000", source="quickbooks"),
            Account(AccountType="EXPENSE", id="2", name="Expenses", number="2000", source="quickbooks"),
            Account(AccountType="INCOME", id="3", name="Income", number="3000", source="quickbooks"),
        ]

    Expected output::

        ComparisonReport(
            excel_only=[Account(AccountType="ASSET", id="1", name="Asset", number="1000", source="excel")],
            qb_only=[Account(AccountType="LIABILITY", id="4", name="Liability", number="4000", source="quickbooks")],
            conflicts=[AccountType="EXPENSE", id="2", excel_name="Expense", qb_name="Expenses", reason="data_mismatch"]
        )

    Note: INCOME appears in both sources with the same name, so it does not appear
    in any of the report's collections (no conflict, not Excel-only, not QB-only).
    """

    excel_dict: Dict[str, Account] = {term.id: term for term in excel_terms}
    qb_dict: Dict[str, Account] = {term.id: term for term in qb_terms}

    conflicts: list[Conflict] = []
    conflicted_ids: set[str] = set()
    conflicted_numbers: set[str] = set()
    conflicted_names: set[str] = set()

    # Case 1: IDs match
    for acc_id in set(excel_dict.keys()).intersection(qb_dict.keys()):
        excel_term = excel_dict[acc_id]
        qb_term = qb_dict[acc_id]

        if (
            excel_term.number == qb_term.number
            and excel_term.AccountType == qb_term.AccountType
            and excel_term.name == qb_term.name
        ):
            continue  # perfect match
        elif (
            excel_term.number == qb_term.number
            and excel_term.AccountType == qb_term.AccountType
            and excel_term.name != qb_term.name
        ):
            conflicts.append(
                Conflict(
                    AccountType=excel_term.AccountType,
                    excel_id=excel_term.id,
                    qb_id=qb_term.id,
                    excel_number=excel_term.number,
                    qb_number=qb_term.number,
                    excel_name=excel_term.name,
                    qb_name=qb_term.name,
                    ConflictReason="name_mismatch",
                )
            )
            conflicted_ids.add(acc_id)
        else:
            conflicts.append(
                Conflict(
                    AccountType=excel_term.AccountType,
                    excel_id=excel_term.id,
                    qb_id=qb_term.id,
                    excel_number=excel_term.number,
                    qb_number=qb_term.number,
                    excel_name=excel_term.name,
                    qb_name=qb_term.name,
                    ConflictReason="id_conflict",
                )
            )
            conflicted_ids.add(acc_id)

    # Case 2: Different IDs but same number
    excel_numbers: Dict[str, Account] = {term.number: term for term in excel_terms}
    qb_numbers: Dict[str, Account] = {term.number: term for term in qb_terms}
    for num in set(excel_numbers.keys()).intersection(qb_numbers.keys()):
        excel_term = excel_numbers[num]
        qb_term = qb_numbers[num]
        if excel_term.id != qb_term.id:
            conflicts.append(
                Conflict(
                    AccountType=excel_term.AccountType,
                    excel_id=excel_term.id,
                    qb_id=qb_term.id,
                    excel_number=excel_term.number,
                    qb_number=qb_term.number,
                    excel_name=excel_term.name,
                    qb_name=qb_term.name,
                    ConflictReason="number_conflict",
                )
            )
            conflicted_numbers.add(num)

    # Case 3: Different IDs but same name
    excel_names: Dict[str, Account] = {term.name: term for term in excel_terms}
    qb_names: Dict[str, Account] = {term.name: term for term in qb_terms}
    for nm in set(excel_names.keys()).intersection(qb_names.keys()):
        excel_term = excel_names[nm]
        qb_term = qb_names[nm]
        if excel_term.id != qb_term.id:
            conflicts.append(
                Conflict(
                    AccountType=excel_term.AccountType,
                    excel_id=excel_term.id,
                    qb_id=qb_term.id,
                    excel_number=excel_term.number,
                    qb_number=qb_term.number,
                    excel_name=excel_term.name,
                    qb_name=qb_term.name,
                    ConflictReason="name_conflict",
                )
            )
            conflicted_names.add(nm)

    # Case 4: If not in quickbooks, add to conflicts
    excel_accounts: Dict[str, Account] = {term.id: term for term in excel_terms}
    qb_accounts: Dict[str, Account] = {term.id: term for term in qb_terms}
    for acc_id, excel_term in excel_accounts.items():
        if acc_id not in qb_accounts:
            conflicts.append(
                Conflict(
                    AccountType=excel_term.AccountType,
                    excel_id=excel_term.id,
                    qb_id=None,
                    excel_number=excel_term.number,
                    qb_number=None,
                    excel_name=excel_term.name,
                    qb_name=None,
                    ConflictReason="only_in_excel",
                )
            )

    # Build excel_only and qb_only excluding conflicts
    added_chart_of_accounts = [
        term
        for acc_id, term in excel_dict.items()
        if acc_id not in qb_dict
        and acc_id not in conflicted_ids
        and term.number not in conflicted_numbers
        and term.name not in conflicted_names
    ]
    qb_only = [
        term
        for acc_id, term in qb_dict.items()
        if acc_id not in excel_dict
        and acc_id not in conflicted_ids
        and term.number not in conflicted_numbers
        and term.name not in conflicted_names
    ]

    return ComparisonReport(
        added_chart_of_accounts=added_chart_of_accounts,
        qb_only=qb_only,
        conflicts=conflicts,
    )


__all__ = ["compare_account_types"]


if __name__ == "__main__":
    from pathlib import Path
    from dataclasses import asdict
    from excel_reader import extract_account
    from qb_gateway import fetch_accounts, add_accounts_batch
    from reporting import write_report, iso_timestamp

    def count_matching_account_types(
        excel_accounts: Iterable[Account], qb_accounts: Iterable[Account]
    ) -> int:
        excel_ids = {acc.id for acc in excel_accounts}
        qb_ids = {acc.id for acc in qb_accounts}

        matches = 0
        for acc_id in excel_ids.intersection(qb_ids):
            excel_acc = next(acc for acc in excel_accounts if acc.id == acc_id)
            qb_acc = next(acc for acc in qb_accounts if acc.id == acc_id)
            if excel_acc.name == qb_acc.name and excel_acc.number == qb_acc.number:
                matches += 1

        return matches

    report_payload: Dict[str, object] = {
        "status": "success",
        "generated_at": iso_timestamp(),
        "added_chart_of_accounts": [],
        "conflicts": [],
        "same_account_of_account_types": count_matching_account_types(
            fetch_accounts(),
            extract_account(
                Path(
                    "C:/Users/KieblesD/Project/QB_Connector_CoA_Python_Fall_2025/company_data.xlsx"
                )
            ),
        ),
        "error": None,
    }

    try:
        # 1. Load Excel accounts
        excel_accounts = extract_account(
            Path(
                "C:/Users/KieblesD/Project/QB_Connector_CoA_Python_Fall_2025/company_data.xlsx"
            )
        )

        # 2. Load QuickBooks accounts
        qb_accounts = fetch_accounts()

        # 3. Compare accounts
        report = compare_account_types(excel_accounts, qb_accounts)
        report_payload["added_chart_of_accounts"] = [
            asdict(acc) for acc in report.added_chart_of_accounts
        ]
        report_payload["conflicts"] = [
            asdict(conflict) for conflict in report.conflicts
        ]

        # 4. Write JSON report
        output_path = Path("reports/comparison.json")
        write_report(report_payload, output_path)
        print(f"Report written to {output_path}")

        # 5. Add Excel-only accounts into QuickBooks
        if report.added_chart_of_accounts:
            print(
                f"Adding {len(report.added_chart_of_accounts)} Excel-only accounts into QuickBooks..."
            )
            added = add_accounts_batch(None, report.added_chart_of_accounts)
            for acc in added:
                print(f"Added: {acc}")

    except Exception:
        report_payload["status"] = "error"
        report_payload["error"] = str(exec)
