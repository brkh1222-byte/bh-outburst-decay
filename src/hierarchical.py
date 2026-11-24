"""Robustness check (viii) of results/analysis_plan_v1.md: per-outburst hierarchical model.

Instead of averaging each source's outbursts, keep every outburst:
    log tau_ij = A + B x_i + u_i + e_ij
    u_i  ~ N(0, sigma_src^2)            one offset per source (all its outbursts share it)
    e_ij ~ N(0, sigma_out^2 + s_ij^2)   outburst-to-outburst scatter + measurement error
Integrating out u_i, the outbursts of one source are jointly Gaussian with covariance
    C = diag(sigma_out^2 + s_ij^2) + sigma_src^2 * (matrix of ones).
This separates "systems differ" (sigma_src) from "outbursts of one system differ" (sigma_out),
and lets GX 339-4's ten outbursts count as ten measurements of ONE system, not ten systems.
"""
from __future__ import annotations

import emcee
import numpy as np

from src.tau_vs_porb import outburst_table


def loglike(p, groups):
    A, B, ls_src, ls_out = p
    s_src2, s_out2 = (10 ** ls_src) ** 2, (10 ** ls_out) ** 2
    ll = 0.0
    for x, y, s in groups:
        C = np.diag(s_out2 + s ** 2) + s_src2
        r = y - (A + B * x)
        sign, logdet = np.linalg.slogdet(C)
        ll += -0.5 * (r @ np.linalg.solve(C, r) + logdet + len(y) * np.log(2 * np.pi))
    return ll


def logpost(p, groups):
    A, B, ls_src, ls_out = p
    if not (-1 <= A <= 4 and -3 <= B <= 3 and -3 <= ls_src <= 0.5 and -3 <= ls_out <= 0.5):
        return -np.inf
    return loglike(p, groups)


def run(col="tau_decay_10_90", nstep=6000, seed=0):
    ob = outburst_table(col=col)
    groups = []
    for _, g in ob.groupby("source"):
        x = np.log10(g.porb_d.values)
        groups.append((x, g.logtau.values, g.sig.values))
    rng = np.random.default_rng(seed)
    np.random.seed(seed)  # emcee uses numpy's global RNG
    p0 = np.array([1.5, 0.2, -0.8, -0.8]) + 1e-3 * rng.standard_normal((32, 4))
    sampler = emcee.EnsembleSampler(32, 4, logpost, args=(groups,))
    sampler.run_mcmc(p0, nstep, progress=False)
    ch = sampler.get_chain(discard=nstep // 4, flat=True)
    q = np.percentile(ch, [2.5, 50, 97.5], axis=0)
    names = ["A", "B", "log10_sigma_src", "log10_sigma_out"]
    return {n: q[:, i].round(3).tolist() for i, n in enumerate(names)} | {"N_outbursts": len(ob), "N_sources": len(groups)}


if __name__ == "__main__":
    print("decay:", run())
    print("rise :", run("tau_rise_10_90"))
