# {Project Name} — ML Pipeline Design

> Created: {date}
> Last updated: {date}
> Status: In Progress — Stage {N}/7

---

## Stage 1: Business Problem & Goals

### Problem Statement

{1-3 sentences. Clear enough for a new team member to understand what this pipeline solves.}

### Functional Goals

- {What the model should do, e.g., "predict customer churn 30 days ahead"}

### Non-Functional Goals

| Constraint | Requirement | Notes |
|-----------|-------------|-------|
| Latency | {e.g., <100ms inference} | {or TBD/N/A} |
| Throughput | {e.g., 10k predictions/hour} | |
| Compute budget | {e.g., 4x A100 for training} | |
| Training timeline | {e.g., must train in <24h} | |
| Interpretability | {e.g., feature importances required} | |
| Fairness | {e.g., equal performance across demographics} | |

### Non-Goals

- {What is explicitly out of scope, e.g., "real-time retraining is out of scope for v1"}

### Success Metrics

- {Measurable business metric, e.g., "reduce churn by 5%"}
- {ML metric tied to business goal, e.g., "precision >0.9 at recall >0.7"}

---

## Stage 2: Data Sources & Analysis Plan

### Data Sources

#### {Source Name 1}

| Property | Value |
|----------|-------|
| Format | {CSV, Parquet, database table, API, etc.} |
| Size | {approximate rows/size} |
| Freshness | {how often updated, last update date} |
| Access | {S3 path, database connection, API endpoint} |
| Contents | {brief description of what this data represents} |
| Quality issues | {known issues, or "none known"} |
| Relation to problem | {how this data connects to the ML task} |

#### {Source Name 2}

{Same structure as above}

### Missing / Desired Data

- {Data that would be valuable but isn't available, and why}
- {Or: "No critical data gaps identified"}

### Data Analysis Plan

Saved to: `docs/design/{short_name}_data_analysis.md`

User approved: {Yes/No — date}

---

## Stage 3: ML Task Formulation

### Model Inputs

{What data goes into the model, at what granularity. Be specific about features, modalities, context windows, etc.}

### Model Outputs

{What the model produces. Format, dimensionality, interpretation.}

### Training Example Structure

```
One training example:
- Input: {concrete example of one input}
- Output: {concrete example of corresponding output}
- Context: {any additional context provided}
```

### Alternative Formulations Considered

| Formulation | Pros | Cons |
|------------|------|------|
| {e.g., Binary classification} | {pros} | {cons} |
| {e.g., Survival analysis} | {pros} | {cons} |
| {e.g., Ranking} | {pros} | {cons} |

### Chosen Formulation

**{Formulation name}** — {rationale for this choice over alternatives}

---

## Stage 4: Model Family Selection

### Problem Type

{Generative / Discriminative} — {Specific approach: classification, regression, detection, generation, etc.}

### Model Family Options

| Model Family | Pros | Cons | Training Cost | Data Requirements |
|-------------|------|------|--------------|-------------------|
| {e.g., Gradient boosted trees} | {pros} | {cons} | {cost} | {data needs} |
| {e.g., Transformer encoder} | {pros} | {cons} | {cost} | {data needs} |
| {e.g., CNN + linear head} | {pros} | {cons} | {cost} | {data needs} |

### Chosen Model Family

**{Family name}** — {rationale}

### Metrics

| Metric | Type | Description |
|--------|------|-------------|
| {e.g., Binary cross-entropy} | Primary (training loss) | {what it optimizes} |
| {e.g., Per-class F1} | Auxiliary (eval) | {what it measures} |
| {e.g., Calibration error} | Auxiliary (eval) | {what it measures} |

---

## Stage 5: Baseline Model & Architecture

### Architecture Options

| Architecture | Parameters | GPU Requirement | Min Dataset Size | Notes |
|-------------|-----------|----------------|-----------------|-------|
| {e.g., XGBoost defaults} | {~1k trees} | {CPU only} | {~10k rows} | {notes} |
| {e.g., BERT-base fine-tune} | {110M} | {1x A100} | {~50k examples} | {notes} |
| {e.g., 2-layer MLP} | {~100k} | {CPU} | {~5k rows} | {notes} |

### Chosen Baseline

**{Architecture}** — {rationale, emphasizing simplicity and fast iteration}

### Hyperparameter Starting Points

| Parameter | Value / Range | Rationale |
|-----------|-------------|-----------|
| Learning rate | {e.g., 3e-5} | {why} |
| Batch size | {e.g., 32} | {why} |
| {other relevant params} | {value} | {why} |

---

## Stage 6: Data Preprocessing & Dataset Pipeline

### Preprocessing Pipeline

Detailed spec saved to: `docs/design/{short_name}_data_pipeline.md`

**Summary of transforms (in order):**

| Step | Transform | Input | Output | Purpose |
|------|----------|-------|--------|---------|
| 1 | {e.g., Remove nulls in timestamp} | {raw rows} | {filtered rows} | {why} |
| 2 | {e.g., Encode categorical features} | {filtered rows} | {encoded rows} | {why} |
| ... | ... | ... | ... | ... |

### Data Split Strategy

| Strategy | Pros | Cons |
|----------|------|------|
| {e.g., Temporal split} | {pros} | {cons} |
| {e.g., Stratified random} | {pros} | {cons} |
| {e.g., Group-aware split} | {pros} | {cons} |

**Chosen:** {strategy} — {rationale}

### Data Validation Checks

- {e.g., No target leakage: features must not contain future information}
- {e.g., Class distribution in train/val/test within 5% of overall}
- {e.g., No null values in required columns after preprocessing}

---

## Stage 7: Training Observability

### Training Curves

| Chart | Metrics | Logging Frequency |
|-------|---------|------------------|
| {e.g., Loss curve} | {train loss, val loss — same chart} | {every 100 steps} |
| {e.g., Primary metric} | {train/val accuracy} | {every epoch} |
| {e.g., Learning rate schedule} | {current LR} | {every 100 steps} |

### Sample Inspection Plan

- **Number of samples:** {e.g., 16 fixed samples from validation set}
- **Selection criteria:** {e.g., 4 easy positives, 4 hard positives, 4 easy negatives, 4 hard negatives}
- **Visualization:** {e.g., table showing input features, ground truth label, predicted probability, predicted label — updated every epoch}
- **Purpose:** {catch issues aggregate metrics miss: systematic bias on certain input patterns, overconfident wrong predictions, etc.}

### Experiment Tracking

- **Tool:** {e.g., Weights & Biases, MLflow, TensorBoard, spreadsheet}
- **What to log per run:** {hyperparameters, final metrics, training curves, sample predictions, git commit hash}
- **Naming convention:** {e.g., `{model}_{dataset}_{date}_{short_description}`}
