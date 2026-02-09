def slippage(price, volume, adv):
    return price * min(0.002, (volume/adv)*0.001)
