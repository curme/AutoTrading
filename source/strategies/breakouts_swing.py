"""
Momentum trading: Using pre-market trading and range breaks out

"""
"""
range break out

Assumption is the market moves in the same direction as pre-market trade when market
moves outside the prior day's range

Short stocks making lower daily lows
Long stocks making high daily highs


Enter signal:
Market open higher that previous day's high(H(1))
When P > H(1)*1.01
    Long P
Stop loss
    When P < P'*0.97
profit taking
    when P > P'*1.03

Market open lower than previous day's low(L(1))
When P < L(1)*1.01
    Short L
Stop Loss
    when P > P'*1.03
profit taking
    when P < P'*0.97
"""