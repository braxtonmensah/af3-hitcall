"""Design arithmetic for the virtual screen, so PREREG_VSCREEN's numbers are checkable.

Everything here is a property of the DESIGN, not of any data: it runs before the screen and does
not read a single Boltz-2 score. Three questions:

  1. How often does the old decision rule ("compounds that beat every decoy") fire when nothing
     binds? This is what decides whether that rule was a test or a formality.
  2. How large would the null have to be for any individual compound to survive multiplicity
     correction? This decides whether per-compound significance is reachable at all.
  3. How much power does the distributional alternative have at the sizes we can afford?

Usage:
    python screen_power.py                    # the table quoted in PREREG_VSCREEN.md
    python screen_power.py --json out.json
"""
import argparse
import json
import math
import random

TRIALS = 20000
ALPHA = 0.05
Q = 0.10


def _phi(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def false_hits(n_screen, n_decoy, trials=TRIALS, seed=0):
    """Expected count and P(at least one) for 'screen compound beats every decoy', under the null.

    The expectation is exact and needs no simulation: the null makes all n_decoy+1 scores in the
    comparison exchangeable, so a given screen compound is the largest with probability
    1/(n_decoy+1), and expectations add whether or not the events are independent. P(at least one)
    is simulated because those events are dependent through the shared decoy maximum: they all
    hinge on the same threshold, which makes the outcomes clump and puts P(>=1) well below what
    independence would give.
    """
    expected = n_screen / (n_decoy + 1.0)
    rng = random.Random(seed)
    hits = 0
    for _ in range(trials):
        m = max(rng.random() for _ in range(n_decoy))
        # P(no screen compound exceeds m) = m**n_screen, given m. Sample it directly instead of
        # drawing n_screen uniforms, which is the same distribution and far cheaper.
        if rng.random() > m ** n_screen:
            hits += 1
    return expected, hits / trials


def decoys_for_fdr(n_screen, q=Q):
    """Decoys needed before the top-ranked compound can reach BH q, given empirical p-values.

    The smallest p an empirical null can produce is 1/(n_decoy+1). Benjamini-Hochberg asks the
    top-ranked of n_screen tests for p <= q/n_screen. Setting them equal and solving gives the
    count below. Nothing about the data can rescue a null too small to express the p-value.
    """
    return math.ceil(n_screen / q) - 1


def power_mannwhitney(n1, n2, auc, alpha=ALPHA):
    """Normal-approximation power for Mann-Whitney at a given AUC (the probability that a random
    screen compound outscores a random null compound). sigma is the null SD of the AUC statistic."""
    sigma = math.sqrt((n1 + n2 + 1.0) / (12.0 * n1 * n2))
    z = (auc - 0.5) / sigma
    crit = 1.959963985 if alpha == 0.05 else -_qnorm(alpha / 2.0)
    return (1.0 - _phi(crit - z)) + _phi(-crit - z)


def _qnorm(p):
    # Beasley-Springer-Moro, adequate for the tail probabilities used here.
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00, 3.754408661907416e+00]
    pl, ph = 0.02425, 1 - 0.02425
    if p < pl:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > ph:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    q, r = p - 0.5, (p - 0.5) ** 2
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)


def main(as_json=None):
    out = {"trials": TRIALS, "false_hits": [], "fdr": [], "power": []}

    print("1. 'Compounds that beat every decoy', under a pure null where nothing binds.")
    print("   This is the rule vscreen.py --rank uses to decide whether to buy compounds.\n")
    print("   %-8s %-8s %14s %18s" % ("screen", "decoys", "expected hits", "P(>=1 false hit)"))
    for ns, nd in [(300, 50), (300, 300), (1000, 50), (1000, 1000), (2000, 2000), (3273, 3273)]:
        e, p = false_hits(ns, nd)
        out["false_hits"].append({"n_screen": ns, "n_decoy": nd, "expected": round(e, 3),
                                  "p_at_least_one": round(p, 4)})
        print("   %-8d %-8d %14.2f %18.3f" % (ns, nd, e, p))
    print("\n   At a 1:1 ratio the expectation is exactly 1.0 at every scale, which is the only")
    print("   reading under which the top of the list is interpretable without correction.")

    print("\n2. Decoys needed before the TOP-ranked compound can reach Benjamini-Hochberg q<%.2f." % Q)
    print("   The floor on an empirical p-value is 1/(decoys+1).\n")
    print("   %-8s %12s" % ("screen", "decoys needed"))
    for ns in (300, 1000, 2000, 3273):
        n = decoys_for_fdr(ns)
        out["fdr"].append({"n_screen": ns, "decoys_needed": n})
        print("   %-8d %12d" % (ns, n))
    print("\n   Roughly ten times the screen. Per-compound significance is not reachable here,")
    print("   which is why PREREG_VSCREEN makes the distributional test primary and labels the")
    print("   shortlist as hypotheses.")

    print("\n3. Power of Mann-Whitney (screen vs matched null), alpha=%.2f, equal arms.\n" % ALPHA)
    aucs = (0.55, 0.57, 0.60, 0.65)
    print("   %-10s %s" % ("n per arm", "  ".join("AUC %.2f" % a for a in aucs)))
    for n in (150, 300, 1000):
        ps = [power_mannwhitney(n, n, a) for a in aucs]
        out["power"].append({"n_per_arm": n, "auc": list(aucs), "power": [round(p, 3) for p in ps]})
        print("   %-10d %s" % (n, "  ".join("%8.2f" % p for p in ps)))

    if as_json:
        with open(as_json, "w") as f:
            json.dump(out, f, indent=1)
        print("\nwrote", as_json)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    main(ap.parse_args().json)
