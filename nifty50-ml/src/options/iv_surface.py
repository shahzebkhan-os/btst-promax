import numpy as np

# simple polynomial fit for IV surface

def fit_iv_surface(strikes, ivs, degree=2):
    coeffs = np.polyfit(strikes, ivs, degree)
    return np.poly1d(coeffs)


def greeks_black_scholes(S, K, T, r, sigma):
    from math import log, sqrt
    from scipy.stats import norm
    if T <= 0 or sigma <= 0:
        return {"delta": 0, "gamma": 0, "vega": 0}
    d1 = (log(S/K) + (r+0.5*sigma**2)*T)/(sigma*sqrt(T))
    d2 = d1 - sigma*sqrt(T)
    delta = norm.cdf(d1)
    gamma = norm.pdf(d1)/(S*sigma*sqrt(T))
    vega = S*norm.pdf(d1)*sqrt(T)/100
    return {"delta": delta, "gamma": gamma, "vega": vega}


def interpolate_iv(strikes, ivs, target_strikes):
    f = fit_iv_surface(strikes, ivs)
    return [float(f(k)) for k in target_strikes]
