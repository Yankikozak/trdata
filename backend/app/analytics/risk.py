from __future__ import annotations

import numpy as np


def historical_var(returns: list[float], confidence: float = 0.95) -> float:
    if not returns:
        return 0.0
    return float(-np.quantile(np.asarray(returns), 1 - confidence))


def parametric_var(returns: list[float], confidence: float = 0.95) -> float:
    if len(returns) < 2:
        return 0.0
    z_score = 1.645 if confidence == 0.95 else 2.326
    values = np.asarray(returns)
    return float(-(values.mean() - z_score * values.std(ddof=1)))


def max_drawdown(prices: list[float]) -> float:
    if not prices:
        return 0.0
    values = np.asarray(prices)
    drawdowns = values / np.maximum.accumulate(values) - 1
    return float(drawdowns.min())


def sharpe_ratio(returns: list[float], risk_free: float = 0.0) -> float:
    values = np.asarray(returns)
    if len(values) < 2 or values.std(ddof=1) == 0:
        return 0.0
    return float((values.mean() - risk_free) / values.std(ddof=1) * np.sqrt(252))
