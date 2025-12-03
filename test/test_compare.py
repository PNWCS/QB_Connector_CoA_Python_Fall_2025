from src.compare import compare_account_types
from src.models import Account


def test_qb_only_account() -> None:
    excel_terms: list[Account] = []
    qb_terms: list[Account] = [
        Account(
            id="5",
            number="30000",
            AccountType="LIABILITY",
            name="Loan",
            source="quickbooks",
        )
    ]
    result = compare_account_types(excel_terms, qb_terms)

    # QB-only accounts go into qb_only
    assert len(result.qb_only) == 1
    assert result.qb_only[0].id == "5"
    assert len(result.conflicts) == 1


def test_name_mismatch_conflict() -> None:
    excel_terms = [
        Account(
            id="1",
            number="10000",
            AccountType="EXPENSE",
            name="Expense",
            source="excel",
        )
    ]
    qb_terms = [
        Account(
            id="1",
            number="10000",
            AccountType="EXPENSE",
            name="Expenses",
            source="quickbooks",
        )
    ]
    result = compare_account_types(excel_terms, qb_terms)

    # Same ID, same number, same type, but different name → conflict
    assert len(result.conflicts) == 1
    conflict = result.conflicts[0]
    assert conflict.ConflictReason == "data_mismatch"
    assert conflict.excel_name == "Expense"
    assert conflict.qb_name == "Expenses"


def test_perfect_match() -> None:
    excel_terms = [
        Account(
            id="2", number="40000", AccountType="INCOME", name="Income", source="excel"
        )
    ]
    qb_terms = [
        Account(
            id="2",
            number="40000",
            AccountType="INCOME",
            name="Income",
            source="quickbooks",
        )
    ]
    result = compare_account_types(excel_terms, qb_terms)

    # Perfect match → no conflicts, no excel_only, no qb_only
    assert len(result.added_chart_of_accounts) == 0
    assert len(result.qb_only) == 0
    assert len(result.conflicts) == 0
