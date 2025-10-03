# app/agent/parsers.py
from pydantic import BaseModel, Field
from typing import List, Optional

# These models are specifically for the LLM to use as a structured output format.
# They are simpler than the final schemas, focusing only on what needs to be parsed from the raw text.

class ParsedRevenue(BaseModel):
    value: float | None = Field(description="The numerical value of the revenue. Use null if NOT FOUND.")
    unit: str | None = Field(description="The currency and scale found in the document, e.g., 'USD Billion' or 'INR Crores'. Use null if NOT FOUND.")
    source_page: int | None = Field(description="The page number where the data was found. Use null if NOT FOUND.")
    status: str = Field(description="Either 'FOUND' or 'NOT FOUND' based on whether data was found.", default="FOUND")
    converted_value: float | None = Field(description="The converted value if currency conversion was performed. Use null if no conversion.", default=None)
    converted_unit: str | None = Field(description="The converted unit if currency conversion was performed. Use null if no conversion.", default=None)
    conversion_note: str | None = Field(description="Note about conversion performed, e.g., 'Converted from INR Crores using rate 0.012'. Use null if no conversion.", default=None)

class ParsedNetIncome(BaseModel):
    value: float = Field(description="The numerical value of the net income or profit after tax.")
    unit: str = Field(description="The currency and scale.")
    source_page: int = Field(description="The page number where the data was found.")

class ParsedEPS(BaseModel):
    value: float = Field(description="The numerical value of the Diluted EPS.")
    source_page: int = Field(description="The page number where the data was found.")

class ParsedSegment(BaseModel):
    segment_name: str = Field(description="The name of the business segment.")
    percentage_contribution: float = Field(description="The percentage of revenue from this segment.")

class ParsedSegmentContribution(BaseModel):
    top_segments: List[ParsedSegment] = Field(description="A list of the top 3 contributing business segments.")
    source_page: int = Field(description="The page number where the data was found.")

class ParsedUtilization(BaseModel):
    rate_percentage: float = Field(description="The numerical percentage of employee utilization.")
    source_page: int = Field(description="The page number where the data was found.")

class ParsedRisk(BaseModel):
    risk_summary: str = Field(description="A concise summary of a single key risk.")

class ParsedKeyRisks(BaseModel):
    key_risks: List[ParsedRisk] = Field(description="A list of the top 2-3 most critical risks.")
    source_page: int = Field(description="The page number where the data was found.")

# A mapping to easily select the right parser for each task
TASK_PARSER_MAP = {
    "Consolidated Revenue (USD Billion)": ParsedRevenue,
    "Consolidated Net Income (Profit After Tax)": ParsedNetIncome,
    "Diluted Earnings Per Share (EPS in INR)": ParsedEPS,
    "Percentage contribution of the top 3 operating segments (e.g., BFSI, Retail)": ParsedSegmentContribution,
    "Employee Utilization Rate (excluding trainees)": ParsedUtilization,
    "Top 2-3 most critical risks from the Management Discussion & Analysis": ParsedKeyRisks,
}
