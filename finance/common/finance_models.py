from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BudgetActualRecord:
    period: str
    department: str
    account: str
    budget_amount: float
    actual_amount: float
    variance_amount: float
    variance_rate: float
    business_driver: str
    remark: str


@dataclass
class FinanceDataset:
    records: list[BudgetActualRecord]
    source_path: str | None = None

    def periods(self) -> list[str]:
        return sorted({record.period for record in self.records})

    def departments(self) -> list[str]:
        return sorted({record.department for record in self.records})

    def accounts(self) -> list[str]:
        return sorted({record.account for record in self.records})

    def total_budget(self) -> float:
        return sum(record.budget_amount for record in self.records)

    def total_actual(self) -> float:
        return sum(record.actual_amount for record in self.records)

    def total_variance(self) -> float:
        return sum(record.variance_amount for record in self.records)

    def material_variances(
        self,
        threshold_rate: float = 0.1,
        threshold_amount: float = 50000,
    ) -> list[BudgetActualRecord]:
        return [
            record
            for record in self.records
            if abs(record.variance_rate) >= threshold_rate
            or abs(record.variance_amount) >= threshold_amount
        ]
