---
name: data-extraction-verification
description: ALWAYS USE THIS SKILL when extracting numerical values from Treasury Bulletin tables. Systematic verification protocol to prevent common extraction errors like reading wrong tables, wrong metrics (outstanding vs sales vs redemptions), wrong time periods, or misread digits. Use BEFORE finalizing any extracted value.
---

# Data Extraction Verification Protocol

## Purpose

Prevent extraction errors that cause incorrect answers despite correct calculations. Common failure modes:
- Reading "amount outstanding" when question asks for "sales" or "redemptions"
- Extracting from wrong time period column (preliminary vs revised vs final)
- Misreading digits (3↔8, 1↔7, 6↔0)
- Regional aggregates vs individual country values
- Order of magnitude errors (261 vs 67,000)

## Verification Checklist

Before reporting ANY extracted value, verify each item:

### 1. Table-Question Alignment
- State explicitly: "Reading from Table [X]: [table title]"
- Confirm table subject matches question subject
- If asked about "redemptions," verify you're NOT reading "amount outstanding"
- If asked about a specific country, verify you're NOT reading a regional aggregate

### 2. Metric Type Match
Parse question for EXACT metric requested:

| Question keyword | Verify NOT reading |
|-----------------|-------------------|
| "sales" | outstanding, redemptions |
| "redemptions" | outstanding, sales |
| "outstanding" | sales, redemptions |
| "issued" | outstanding, redeemed |
| "yield" | price, return, rate |
| "rate" | yield, price, level |

### 3. Time Period Verification
- State: "Reading column: [full header path]"
- For multi-level headers, trace full path (e.g., "1982 > Q3 > September > Interest-bearing")
- Watch for column markers: p = preliminary, r = revised
- Verify fiscal vs calendar year alignment

### 4. Coordinate Lock
State explicitly:
- Row header: "[exact row label]"
- Column header: "[exact column label]"
- Cell value: "[extracted value]"

### 5. Magnitude Sanity Check
Before finalizing, ask:
- Does this magnitude make sense for the context?
- If expecting ~hundreds and got ~tens of thousands, STOP and re-verify
- Compare against adjacent values for plausibility

### 6. Cross-Reference (when available)
- Check if extracted value + siblings = stated total
- Compare against adjacent time periods
- Flag anomalies before proceeding

## Failure Pattern Recognition

**258x error pattern (Failure 2 type):** Extracted 67,238 when answer was 261
- Root cause: Read "Amount Outstanding" instead of net change/sales/redemptions
- Prevention: Explicitly verify metric type matches question

**Digit misread pattern (Failure 1 type):** Extracted 103,235 when answer was 103,375
- Root cause: OCR artifact or adjacent column read
- Prevention: State exact row/column coordinates; verify against totals

**Wrong basis pattern (Failure 3 type):** Calculated 0.06 when answer was 0.24
- Root cause: Read wrong years, wrong bond type, or wrong yield metric
- Prevention: Verify all coordinates before calculating

## Quick Protocol

```
BEFORE extracting, state:
□ Table: [name/number] - matches question topic?
□ Metric: [type] - matches what question asks?
□ Row: [label]
□ Column: [label with full path]
□ Value: [number]
□ Magnitude plausible? [yes/investigate]
```

Only proceed with calculations after completing this checklist.
