# {Project Name} — Data Preprocessing Pipeline Spec

> Created: {date}
> Status: {Draft / Approved by user}
> Handoff target: Data pipeline agent or direct implementation

---

## Purpose

This document defines the exact sequence of transforms from raw data to training-ready dataset. It is intended to be implementable without ambiguity.

## Input

| Property | Value |
|----------|-------|
| Source(s) | {data source names and locations} |
| Format | {CSV, Parquet, etc.} |
| Approximate size | {rows/files/GB} |
| Schema | {key columns and types, or reference to schema doc} |

## Output

| Property | Value |
|----------|-------|
| Format | {format of training-ready data} |
| Location | {where outputs are written} |
| Structure | {e.g., train/val/test directories, single file with split column} |

---

## Preprocessing Pipeline

Transforms are applied in this exact order.

### Step 1: {Transform name — verb phrase}

| Property | Value |
|----------|-------|
| Input | {what this step receives} |
| Output | {what this step produces} |
| Purpose | {why this transform is needed} |
| Details | {specific logic — thresholds, rules, formulas} |
| Validation | {what to assert after this step} |

Example:
> | Property | Value |
> |----------|-------|
> | Input | Raw CSV with all columns |
> | Output | Filtered CSV (rows with valid timestamps only) |
> | Purpose | Remove records that predate the system migration |
> | Details | Drop rows where `timestamp` is null or before 2020-01-01 |
> | Validation | Assert no null timestamps remain; assert min date >= 2020-01-01 |

### Step 2: {Next transform}

{Same structure}

### Step N: {Final transform}

{Same structure}

---

## Data Split

### Strategy: {chosen strategy name}

| Property | Value |
|----------|-------|
| Method | {e.g., temporal split, stratified random, group-aware} |
| Rationale | {why this method was chosen} |
| Train | {proportion or date range, e.g., "before 2025-01-01" or "70%"} |
| Validation | {proportion or date range} |
| Test | {proportion or date range} |
| Stratification key | {column used for stratification, if applicable} |
| Group key | {column used for grouping, if applicable — ensures same entity stays in one split} |
| Random seed | {seed value for reproducibility} |

---

## Data Validation Checks

Run these checks after the full pipeline completes:

| Check | Assertion | Stage |
|-------|-----------|-------|
| {e.g., No target leakage} | {e.g., No feature contains future information relative to prediction time} | After all transforms |
| {e.g., Split distribution} | {e.g., Class ratio in each split within 5% of overall ratio} | After split |
| {e.g., No nulls in required fields} | {e.g., Columns X, Y, Z have zero null values} | After step N |
| {e.g., No duplicate IDs} | {e.g., Each entity_id appears in exactly one split} | After split |
| {e.g., Output size sanity} | {e.g., Total output rows = input rows minus expected drops} | After all transforms |

---

## Implementation Notes

- {Any dependencies or libraries needed}
- {Performance considerations for large datasets}
- {Idempotency: can this be re-run safely?}
- {Seed management for reproducibility}
