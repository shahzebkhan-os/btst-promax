def simulate_order(price, qty, slippage_bps=5, fee_bps=2):
    slip = price * slippage_bps / 10000
    fee = price * fee_bps / 10000
    fill = price + slip
    cost = fill * qty + fee * qty
    return {"fill": fill, "cost": cost}
