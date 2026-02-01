---
name: data-extraction-verification
description: Rigorous protocol for extracting numerical data from Treasury Bulletin tables. ALWAYS use this skill when extracting ANY value from treasury_bulletins_parsed tables. Prevents common extraction errors including adjacent cell misreads, wrong metric selection, and incorrect time granularity. Required by brainstorming skill for all data lookups.
---

# Data Extraction Verification Protocol

Mandatory verification steps before, during, and after reading values from Treasury Bulletin tables.

## Pre-Extraction: Metric Identification

Before extracting ANY value, explicitly document:

1. **Table identification**: Exact table name/title (e.g., "Table SB-2: Sales and Redemptions by Periods")
2. **Column header**: Exact text as it appears in the table
3. **Row label**: Exact text as it appears in the table
4. **Metric match check**: Verify the column measures EXACTLY what the question asks
   - "Amount outstanding" ≠ "Sales and redemptions"
   - "Calendar year average" ≠ "Specific month value"
   - "Regional aggregate" ≠ "Individual country"

## Extraction: Cell Verification

When reading the value:

1. **Record cell position**: "Row: '[exact label]', Column: '[exact header]'"
2. **Read value with units**: Note millions, billions, percent, etc.
3. **Read adjacent context**: Values one row above AND one row below
4. **Triple check**:
   - Is this the correct row?
   - Is this the correct column?
   - Are the units correct?

## Post-Extraction: Cross-Verification

After extraction:

1. **Compare against totals**: Does value fit within any table subtotals/totals?
2. **Check progression**: For time series, does value follow expected pattern?
3. **Re-extract**: Read the table again independently to confirm the value
4. **Alternative source**: If available, verify against a different table

## Verification Output Format

```
## Data Extraction Verification
Table: [exact table name]
Target Metric: [what question asks for]
Column Selected: [exact column header]
Row Selected: [exact row label]
Extracted Value: [value with units]
Adjacent Context:
  - Row above: [value]
  - Row below: [value]
Metric Match Confirmed: [yes/no - does column measure what question asks?]
Cross-Verification: [how verified - totals, re-read, alternative source]
```

## Common Pitfalls

| Error Type | Example | Prevention |
|------------|---------|------------|
| Adjacent cell | UK: 103,235 vs 103,375 | Always record and verify adjacent rows |
| Wrong metric | "Amount outstanding" when asked for "Sales and redemptions" | Explicit metric match check |
| Wrong granularity | Calendar year average vs specific month | Verify time period matches question |
| Wrong aggregation | Regional total vs individual country | Confirm geographic scope |
