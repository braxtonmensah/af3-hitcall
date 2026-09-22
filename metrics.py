"""Tie-aware weighted AUROC / AUPRC and the node bootstrap used by every test.

A node bootstrap resamples proteins; pair (i, j) then carries weight c_i * c_j, where c is the
multiplicity of each protein in the resample. Scores never change between reps, so each score is
sorted once and every rep is a bincount over tie groups.
"""
import numpy as np
from scipy.stats import rankdata


class Ranked:
    """A score over a fixed pair list, pre-sorted into tie groups (ascending)."""

    def __init__(self, s):
        s = np.asarray(s, float)
        uniq, inv = np.unique(s, return_inverse=True)
        self.g = inv            # group id per pair, ascending by score
        self.ng = len(uniq)

    def _sums(self, wp, wn):
        P = np.bincount(self.g, wp, self.ng)
        N = np.bincount(self.g, wn, self.ng)
        return P, N

    def auroc(self, wp, wn):
        P, N = self._sums(wp, wn)
        below = np.cumsum(N) - N
        return float((P * (below + 0.5 * N)).sum() / (P.sum() * N.sum()))

    def auprc(self, wp, wn):
        P, N = self._sums(wp, wn)
        P, N = P[::-1], N[::-1]  # descending thresholds
        tp, al = np.cumsum(P), np.cumsum(P + N)
        prec = np.divide(tp, al, out=np.zeros_like(tp), where=al > 0)
        return float((P * prec).sum() / P.sum())


def node_weights(n, pi, pj, rng, reps):
    for _ in range(reps):
        c = np.bincount(rng.integers(0, n, n), minlength=n).astype(float)
        yield c[pi] * c[pj]


def ci(x, level):
    a = (1 - level) / 2
    return np.quantile(x, [a, 1 - a])


def per_bait(S, pos, eligible=None, k=5):
    """Macro-averaged per-bait recall@k, precision@k, reciprocal rank of best true partner.
    S, pos: full symmetric n x n (NaN diagonal). Ties use average ranks."""
    n = S.shape[0]
    out = []
    for i in range(n):
        if eligible is not None and not eligible[i]:
            continue
        m = np.arange(n) != i
        y = pos[i, m]
        if y.sum() == 0:
            continue
        r = rankdata(-S[i, m], method="average")
        top = r <= k
        out.append((i, (y & top).sum() / y.sum(), (y & top).sum() / k, 1.0 / r[y].min()))
    return np.array(out)
