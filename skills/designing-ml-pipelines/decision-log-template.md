# {Project Name} — Decision Log

> Companion to: `{short_name}_ml_design.md`

---

## How to Read This Log

Each entry records **what was decided**, **why**, and **what alternatives were considered**. Entries are timestamped and grouped by stage. If a decision was later revised (backtracking), the original entry stays with a `REVISED` note linking to the new decision.

---

## Stage 1: Business Problem & Goals

### {YYYY-MM-DD} — Problem scope defined

**Decision:** {what was decided}
**Rationale:** {why this and not something else}
**Alternatives considered:** {what was rejected and why}

---

## Stage 2: Data Sources & Analysis Plan

### {YYYY-MM-DD} — Data sources identified

**Decision:** {what was decided}
**Rationale:** {why}

### {YYYY-MM-DD} — Data analysis plan approved

**Decision:** {EDA plan approved by user}
**Key analyses:** {brief summary of what's in the plan}

---

## Stage 3: ML Task Formulation

### {YYYY-MM-DD} — Task formulation chosen

**Decision:** {chosen formulation}
**Rationale:** {why this over alternatives}
**Alternatives rejected:** {list with brief reason each}

---

## Stage 4: Model Family Selection

### {YYYY-MM-DD} — Model family chosen

**Decision:** {chosen family}
**Rationale:** {why}
**User concerns noted:** {any reservations}

---

## Stage 5: Baseline Architecture

### {YYYY-MM-DD} — Baseline architecture chosen

**Decision:** {chosen architecture}
**Rationale:** {why — should emphasize simplicity}

---

## Stage 6: Preprocessing & Split Strategy

### {YYYY-MM-DD} — Preprocessing pipeline defined

**Decision:** {summary of pipeline}
**Key choices:** {any non-obvious preprocessing decisions}

### {YYYY-MM-DD} — Split strategy chosen

**Decision:** {chosen strategy}
**Rationale:** {why this over alternatives}

---

## Stage 7: Training Observability

### {YYYY-MM-DD} — Observability plan defined

**Decision:** {summary of monitoring approach}
**Experiment tracking:** {chosen tool/convention}

---

## Backtracking Log

{Record any decisions that were revised after being made. Link to both the original and revised entries.}

### {YYYY-MM-DD} — REVISED: {original decision title}

**Original (Stage N, {date}):** {what was originally decided}
**Revised to:** {new decision}
**Reason for change:** {what new information or contradiction prompted the revision}
**Impact:** {what other stages or decisions are affected}
