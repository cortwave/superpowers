# {Project Name} — Data Analysis Plan

> Created: {date}
> Status: {Draft / Approved by user}
> Handoff target: EDA agent or manual execution

---

## Purpose

This plan defines specific analyses to run on the raw data **before any modeling work begins**. Each analysis answers a concrete question about the data.

## Data Sources

| Source | Location | Format |
|--------|----------|--------|
| {source 1} | {path/URL} | {format} |

---

## Analysis Steps

### 1. {Analysis title — verb phrase}

**Question:** {What specific question does this answer?}
**Action:** {Exact analysis to perform}
**Expected output:** {What the result looks like — chart, table, number}
**Why it matters:** {How this informs modeling decisions}

Example:
> **Question:** Is the target variable balanced?
> **Action:** Plot distribution of `churn_label` column. Compute class ratio.
> **Expected output:** Histogram + printed ratio (e.g., "positive: 12%, negative: 88%")
> **Why it matters:** Severe imbalance requires oversampling, class weights, or metric choice adjustment.

### 2. {Next analysis}

**Question:** {question}
**Action:** {action}
**Expected output:** {output}
**Why it matters:** {why}

{Continue for all planned analyses...}

---

## Summary Checklist

After completing all analyses, summarize findings:

- [ ] Target variable distribution documented
- [ ] Feature completeness (missing values) assessed
- [ ] Key feature distributions examined
- [ ] Feature-target correlations computed
- [ ] Data quality issues catalogued
- [ ] Temporal patterns checked (if time-series data)
- [ ] Duplicate detection performed
- [ ] Cross-source join quality verified (if multiple sources)

## Notes for EDA Agent

- {Any access instructions, credentials references, environment setup}
- {Known gotchas with the data format}
- {Preferred visualization library or output format}
