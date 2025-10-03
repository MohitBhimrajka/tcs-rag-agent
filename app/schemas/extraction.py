# app/schemas/extraction.py
from pydantic import BaseModel, Field
from typing import List, Optional

class BaseMetric(BaseModel):
    """Base model for a financial metric, including source and reasoning."""
    source_page: Optional[int] = Field(
        None,
        description="The page number in the report where this information was found."
    )
    reasoning: Optional[str] = Field(
        None,
        description="A brief explanation of how the value was extracted or why it's considered correct."
    )

class ConsolidatedRevenue(BaseMetric):
    """Schema for the consolidated revenue of the company."""
    value: Optional[float] = Field(
        None,
        description="The final reported consolidated revenue figure."
    )
    unit: Optional[str] = Field(
        None,
        description="The currency and scale, e.g., 'USD Billion' or 'INR Crores'."
    )

class ConsolidatedNetIncome(BaseMetric):
    """Schema for the consolidated net income (Profit After Tax)."""
    value: Optional[float] = Field(
        None,
        description="The final Profit After Tax (PAT) or Net Income figure for the group."
    )
    unit: Optional[str] = Field(
        None,
        description="The currency and scale, e.g., 'USD Billion' or 'INR Crores'."
    )

class DilutedEPS(BaseMetric):
    """Schema for the Diluted Earnings Per Share."""
    value: Optional[float] = Field(
        None,
        description="The specific Diluted EPS figure."
    )
    unit: Optional[str] = Field(
        "INR",
        description="The currency of the EPS value, which is typically INR."
    )

class SegmentContribution(BaseModel):
    """Schema for the revenue contribution of a single business segment."""
    segment_name: str = Field(
        description="The name of the operating segment (e.g., BFSI, Retail)."
    )
    percentage_contribution: float = Field(
        description="The revenue contribution of this segment as a percentage."
    )

class EmployeeUtilization(BaseMetric):
    """Schema for the employee utilization rate."""
    rate_percentage: Optional[float] = Field(
        None,
        description="The reported employee utilization percentage, excluding trainees."
    )

class KeyManagementRisk(BaseModel):
    """Schema for a single identified key management risk."""
    risk_summary: str = Field(
        description="A concise summary of a critical risk cited in the Management Discussion & Analysis."
    )

class FinancialReportData(BaseModel):
    """Top-level model that aggregates all extracted financial data points."""
    consolidated_revenue: Optional[ConsolidatedRevenue] = None
    consolidated_net_income: Optional[ConsolidatedNetIncome] = None
    diluted_eps: Optional[DilutedEPS] = None
    top_3_segment_contributions: List[SegmentContribution] = Field(default_factory=list)
    employee_utilization: Optional[EmployeeUtilization] = None
    key_management_risks: List[KeyManagementRisk] = Field(default_factory=list)
