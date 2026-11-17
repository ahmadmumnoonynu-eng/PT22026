"""Mode 5, Model insights: what the risk engine is, how well it scores, where it fails.

Everything on this page is read from the files train/train.py wrote
(results/<tag>/results.csv, meta.json, baseline_scores.npz) or computed live
from the replay sample against the recorded outcomes -- nothing is typed by hand,
so the page cannot drift away from what the models actually do.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

import ui
from common import ROOT, get_engine, get_run

MODEL_LABELS = {
    "risk_engine": "Risk engine (the blend)",
    "logistic_regression": "Logistic regression",
    "xgboost": "XGBoost",
    "isolation_forest": "Isolation forest",
    "baseline_always_approve": "Baseline: approve everything",
    "baseline_rule_large_transfer": "Baseline: rule, large transfers",
    "baseline_rule_full_balance_drain": "Baseline: rule, full-balance drain",
}
MODEL_ROLES = {
    "logistic_regression": "Linear baseline; steady on the patterns it has seen",
    "xgboost": "Gradient-boosted trees; learns the non-linear fraud shapes",
    "isolation_forest": "Unsupervised, never saw a label; flags shapes nobody has named yet",
}
FEATURE_NOTES = {
    "amount": "size of the transfer",
    "oldbalanceDest": "receiver balance before",
    "is_transfer": "TRANSFER vs CASH_OUT",
    "hour_of_day": "hour of the transaction",
    "dest_balance_zero": "receiver account is empty",
}
DROPPED_NOTES = {
    "amount_to_balance": "built from post-transaction balances, so it encodes the answer",
    "oldbalanceOrg": "post-transaction snapshot of the sender's balance",
}
LIMITS = (
    ("Labels arrive late.", "In production the outcome of an alert is known days later; the drift "
     "monitor watches the score distribution in the meantime."),
    ("2.1% base rate.", "PR-AUC, not accuracy, is the honest metric here -- approving everything "
     "would still be 97.9% accurate."),
    ("PaySim is synthesised.", "Amounts and patterns differ from a real bank's traffic; treat the "
     "money numbers as ratios, not rupees."),
    ("The generated live feed is harder.", "Its honest users overlap the fraud band, so the review "
     "budget, not the score, decides what gets caught."),
    ("No network features.", "The engine scores one transaction at a time; rings and mules across "
     "accounts are out of scope for now."),
)
CURVE_POINTS = 160            # vertices drawn of the PR curve
REVIEW_COLOR, BLOCK_COLOR = "#fcd34d", "#fb7185"


@st.cache_data(show_spinner="Reading the training results...")
def _results(tag: str) -> pd.DataFrame:
    return pd.read_csv(ROOT / "results" / tag / "results.csv")


@st.cache_data(show_spinner="Scoring the replay sample...")
def _scored_replay(tag: str) -> tuple[np.ndarray, np.ndarray]:
    """Engine risk for every replay transaction, with the outcomes beside it."""
    engine = get_engine(tag)
    df = get_run(tag).replay
    return engine.score(df).risk, df["isFraud"].to_numpy()


def _pr_curve(risk: np.ndarray, labels: np.ndarray) -> list[tuple[float, float]]:
    """(recall, precision) at every rank, downsampled to a drawable number of points."""
    order = np.argsort(-risk, kind="stable")
    hits = labels[order]
    tp = np.cumsum(hits)
    fp = np.cumsum(1 - hits)
    precision = tp / np.maximum(tp + fp, 1)
    recall = tp / max(int(hits.sum()), 1)
    idx = np.unique(np.linspace(0, len(hits) - 1, CURVE_POINTS).astype(int))
    return [(float(recall[i]), float(precision[i])) for i in idx]


def _operating(risk: np.ndarray, labels: np.ndarray, threshold: float) -> tuple[float, float]:
    flag = risk >= threshold
    flagged = int(flag.sum())
    if flagged == 0:
        return 0.0, 1.0
    precision = float(((labels == 1) & flag).sum() / flagged)
    recall = float(((labels == 1) & flag).sum() / max(int((labels == 1).sum()), 1))
    return recall, precision


def _metric_columns() -> list[tuple[str, str, object]]:
    """(results.csv column, shown heading, formatter)."""
    return [
        ("pr_auc", "PR-AUC", lambda v: f"{v:.3f}"),
        ("roc_auc", "ROC-AUC", lambda v: f"{v:.3f}" if pd.notna(v) else "-"),
        ("recall_at_precision_90", "Recall @ 90% precision", lambda v: f"{v:.1%}" if pd.notna(v) else "-"),
        ("precision_at_k", "Precision @ k", lambda v: f"{v:.1%}"),
        ("recall_at_k", "Recall @ k", lambda v: f"{v:.1%}"),
    ]


def _metrics_table(results: pd.DataFrame) -> str:
    cols = _metric_columns()
    headers = ["Model"] + [h for _, h, _ in cols]
    rows, strong = [], ()
    for i, row in results.iterrows():
        values = [MODEL_LABELS.get(row["model"], row["model"])]
        values += [fmt(row[col]) for col, _, fmt in cols]
        rows.append(tuple(values))
        if row["model"] == "risk_engine":
            strong = (i,)
    return ui.fact_table_html(headers, rows, strong)


def render(header, tag: str, run) -> None:
    """Draw the model insights page. `run` supplies the training metadata."""
    meta = run.meta
    header.markdown(ui.header_html(
        "model", "How the engine is built, what it caught and what it cannot do", "Model insights"),
        unsafe_allow_html=True)

    results = _results(tag)

    # ---- the decision path, one strip, no prose ---------------------------- #
    st.markdown(ui.card("How a decision is made", ui.pipeline_html([
        ("Transaction", "amount, type, hour, balances"),
        ("5 features", "the leakage-audited inputs"),
        ("3 detectors", "trees + linear + isolation forest"),
        ("Blend", "learned weights to one raw score"),
        ("Percentile", "risk 0-100 vs reference traffic"),
        ("Policy", "block, review or approve"),
    ]), "pulse"), unsafe_allow_html=True)

    # ---- the parts, and the inputs they are allowed to see ----------------- #
    weights = meta.get("engine_weights", {})
    det_rows = [(MODEL_LABELS[name], f"{weights.get(name, 0):.2f}", MODEL_ROLES[name])
                for name in ("xgboost", "logistic_regression", "isolation_forest") if name in weights]
    det_rows.append(("Stacker", f"{meta.get('engine_intercept', 0):.2f} intercept",
                     "Blends the three scores into one raw risk"))
    detectors = ui.card("The three detectors", ui.fact_table_html(
        ["Detector", "Blend weight", "What it does"], det_rows), "pie")

    used = [(name, FEATURE_NOTES.get(name, ""))
            for name in meta.get("features", []) if name not in meta.get("dropped_features", [])]
    dropped = [(name, DROPPED_NOTES.get(name, "post-transaction value, it leaks the answer"))
               for name in meta.get("dropped_features", [])]
    features = ui.card("Features after the leakage audit",
                       ui.feature_chips_html(used, dropped), "list")
    st.markdown(ui.two_cards(detectors, features), unsafe_allow_html=True)

    # ---- the measured scores ----------------------------------------------- #
    st.markdown(ui.card("Measured on the test window", _metrics_table(results), "bars"),
                unsafe_allow_html=True)

    # ---- the curve, and the honest boundaries ------------------------------ #
    risk, labels = _scored_replay(tag)
    review = _operating(risk, labels, 90.0)
    block = _operating(risk, labels, 99.5)
    curve = ui.card("Precision vs recall", ui.pr_curve_html(
        _pr_curve(risk, labels), [(review[0], review[1], REVIEW_COLOR),
                                  (block[0], block[1], BLOCK_COLOR)], float(labels.mean()),
        y_label="How right we are", x_label="How much we catch")
        + '<div class="fa-crvnote">'
        f'<span><i style="background:#38bdf8"></i>the engine, from strictest to loosest</span>'
        f'<span><i style="background:{BLOCK_COLOR}"></i>auto-block line (risk 99.5)</span>'
        f'<span><i style="background:{REVIEW_COLOR}"></i>review line (risk 90)</span>'
        '<span><i class="dash"></i>no engine at all</span></div>'
        f'<div class="fa-note"><b>How to read it:</b> the higher the blue curve, the better &mdash; '
        'the engine keeps catching more fraud while staying right. Right is <b>precision</b>: '
        'of what we flag, how much is really fraud. Catch is <b>recall</b>: of all the fraud in the '
        f'file, how much we found. The red dot is where the app blocks automatically: '
        f'{block[1]:.0%} of what it blocks is really fraud, and it finds {block[0]:.0%} of all fraud. '
        f'The yellow dot is the review line: {review[1]:.0%} right, {review[0]:.0%} found. '
        'The dashed line is the floor &mdash; flagging nothing would still be '
        f'{float(labels.mean()):.1%} right by luck. Measured on the {len(risk):,} replay transactions, '
        'where the real answer is known for every one.</div>', "pulse")
    limits = ui.card("What it cannot do", ui.limits_html(LIMITS), "alert")
    st.markdown(ui.two_cards(curve, limits), unsafe_allow_html=True)
