"""Small, dependency-light statistics helpers (numpy + scipy only)."""
import math
import numpy as np
from scipy import stats


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"), float("nan"))
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return p, max(0.0, centre - half), min(1.0, centre + half)


def auroc(scores, labels):
    """Mann-Whitney AUROC with tie handling. labels in {0,1}. nan if one class missing."""
    s = np.asarray(scores, float); y = np.asarray(labels, int)
    pos, neg = s[y == 1], s[y == 0]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    ranks = stats.rankdata(np.concatenate([pos, neg]))
    return (ranks[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))


def spearman(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    if len(x) < 3 or np.all(x == x[0]) or np.all(y == y[0]):
        return float("nan")
    return float(stats.spearmanr(x, y).statistic)


def partial_spearman(x, y, z):
    """Rank-based partial correlation of x and y controlling for z."""
    rx, ry, rz = (stats.rankdata(v) for v in (x, y, z))
    def resid(a, b):
        b1 = np.column_stack([b, np.ones_like(b)])
        coef, *_ = np.linalg.lstsq(b1, a, rcond=None)
        return a - b1 @ coef
    ex, ey = resid(rx, rz), resid(ry, rz)
    if np.std(ex) == 0 or np.std(ey) == 0:
        return float("nan")
    return float(np.corrcoef(ex, ey)[0, 1])


def permutation_p_spearman(x, y, reps=10000, seed=0):
    """One-sided (rho > 0) permutation p-value by shuffling y."""
    rng = np.random.default_rng(seed)
    obs = spearman(x, y)
    if math.isnan(obs):
        return float("nan")
    y = np.asarray(y, float)
    count = 0
    for _ in range(reps):
        r = spearman(x, rng.permutation(y))
        if not math.isnan(r) and r >= obs:
            count += 1
    return (count + 1) / (reps + 1)


def cluster_bootstrap(df, cluster_col, stat_fn, reps=2000, seed=0, strata_col=None):
    """Resample clusters (games) with replacement, within strata if given; return array of stat values."""
    rng = np.random.default_rng(seed)
    out = []
    if strata_col:
        groups = {k: g[cluster_col].unique() for k, g in df.groupby(strata_col)}
    else:
        groups = {None: df[cluster_col].unique()}
    by_cluster = {k: g for k, g in df.groupby(cluster_col)}
    for _ in range(reps):
        parts = []
        for _, clusters in groups.items():
            pick = rng.choice(clusters, size=len(clusters), replace=True)
            parts.extend(by_cluster[c] for c in pick)
        import pandas as pd
        boot = pd.concat(parts, ignore_index=True)
        v = stat_fn(boot)
        if v is not None and not (isinstance(v, float) and math.isnan(v)):
            out.append(v)
    return np.asarray(out, float)


def ci(arr, alpha=0.05):
    if len(arr) == 0:
        return (float("nan"), float("nan"))
    return (float(np.percentile(arr, 100 * alpha / 2)), float(np.percentile(arr, 100 * (1 - alpha / 2))))


def rank_normalise(values):
    """Map values to [0,1] by average rank (ties share rank)."""
    v = np.asarray(values, float)
    if len(v) <= 1:
        return np.zeros_like(v)
    r = stats.rankdata(v)
    return (r - 1) / (len(v) - 1)


def tpr_at_fpr(scores, labels, max_fpr=0.10):
    s = np.asarray(scores, float); y = np.asarray(labels, int)
    neg, pos = s[y == 0], s[y == 1]
    if len(neg) == 0 or len(pos) == 0:
        return float("nan")
    thr = np.quantile(neg, 1 - max_fpr)  # at most max_fpr of negatives strictly above
    return float(np.mean(pos > thr))
