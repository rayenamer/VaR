# z-score

[← Back to VaR](README.md)

A z-score tells you how many standard deviations a value is from the mean [[1]](#sources):

```
z = (value − mean) / standard deviation
```

So a z of 1.65 means "1.65 standard deviations below the average return."

z-scores come from the **standard normal distribution** ([what's that?](normal-distribution.md)).

For VaR, you need the z that leaves exactly 5% (or 1%) of outcomes in the left tail. A standard normal table gives [[2]](#sources):

| Confidence | z (table) | z (rounded, as in the video) |
|---|---|---|
| 95% | 1.645 | 1.65 |
| 99% | 2.326 | 2.33 |

## Sources

1. Wikipedia, *Standard score*: https://en.wikipedia.org/wiki/Standard_score
2. NIST/SEMATECH e-Handbook of Statistical Methods, critical values table: https://www.itl.nist.gov/div898/handbook/eda/section3/eda3672.htm
