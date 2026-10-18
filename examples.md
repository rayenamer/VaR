# Examples, with the maths done

[← Back to VaR](README.md)

All dollar amounts use a $10,000 portfolio.

## Parametric

Using the worked example (mean 1%, standard deviation 1%, 1 year) and the formula `VaR = mean − z × standard deviation`:

```
95%:  1% − 1.65 × 1% = −0.65%
99%:  1% − 2.33 × 1% = −1.33%
```

On $10,000, that's a potential loss of **$65** at 95% and **$133** at 99% over the year.

## Historical

![100 daily returns sorted worst to best, 5th worst highlighted](images/historical_var.svg)

*(The returns in this chart are made up for illustration.)*

These are the five worst of the 100 days in the chart, sorted:

| Rank | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| Daily return | −2.78% | −2.67% | −2.63% | −2.32% | **−2.23%** |

- **95% VaR:** 5% of 100 days = 5 days, so you take the 5th-worst day. That's **−2.23%**.
- **99% VaR:** 1% of 100 days = 1 day, so you take the worst day. That's **−2.78%**.

On $10,000, that's a one-day potential loss of **$223** at 95% and **$278** at 99%.

## Monte Carlo

This uses the same assumptions as the worked example (mean 1%, standard deviation 1%, normal), with 1,000 simulated years:

- **95% VaR:** 5% of 1,000 = 50, so you take the 50th-worst simulated return. That's **−0.68%**.
- **99% VaR:** 1% of 1,000 = 10, so you take the 10th-worst. That's **−1.34%**.

These land very close to the formula's −0.65% and −1.33%. They're not exactly the same because the simulation is random, and 1,000 runs isn't that many. More runs get you closer.

On $10,000, that's **$68** at 95% and **$134** at 99%.

*(Simulated in Python with `random.seed(42)` and `random.gauss(1, 1)`, so you'll get the same numbers if you rerun it.)*
