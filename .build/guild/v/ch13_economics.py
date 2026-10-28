"""Learning the business: the unit economics of a small invoicing product, and three engineering
projects priced in the same currency, so they can be compared and argued about."""

CUSTOMERS, PRICE = 4_000, 49                 # paying teams, dollars a month each
INFRA = 38_000                               # cloud bill, dollars a month
SUPPORT = 22_000                             # support staff, dollars a month
REQUESTS = 900e6                             # API requests a month
CHURN = 0.025                                # share of customers who leave each month
TRIALS, CONVERSION = 2_000, 0.18             # trial sign-ups a month, and the share who pay
ENGINEER_WEEK = 4_000                        # loaded cost of one engineer for a week

revenue = CUSTOMERS * PRICE
margin = (revenue - INFRA - SUPPORT) / revenue
lifetime_value = PRICE * margin / CHURN      # what one customer is worth over their lifetime
print(f"revenue ${revenue:,.0f} a month; gross margin {margin:.0%}; "
      f"infrastructure ${INFRA / (REQUESTS / 1000):.3f} per thousand requests")
print(f"a customer stays {1 / CHURN:.0f} months on average and is worth ${lifetime_value:,.0f} in margin")
hourly = revenue / (30 * 24)
print(f"customers pay ${hourly:,.0f} for each hour of service, so a 4-hour outage refunded in full "
      f"costs ${4 * hourly:,.0f};\nif it also makes 1% of customers leave, it costs "
      f"${0.01 * CUSTOMERS * lifetime_value:,.0f} in lifetime margin")


def annual_value(name):
    if name == "faster checkout":            # trial conversion 18% -> 19%, from an A/B test
        return TRIALS * 0.01 * 12 * lifetime_value / 2    # half the value lands within the year
    if name == "cache invoice PDFs":         # PDFs are 30% of the cloud bill; caching cuts that by 80%
        return INFRA * 0.30 * 0.80 * 12
    if name == "fix bulk-invoice failures":  # exit surveys blame it for a tenth of churn
        kept = CUSTOMERS * CHURN * 0.10 * 12
        return kept * lifetime_value / 2


PROJECTS = {"faster checkout": 6, "cache invoice PDFs": 3,          # engineer-weeks of work
            "fix bulk-invoice failures": 8}
print(f"\n{'project':28}{'value a year':>14}{'cost':>10}{'payback':>12}{'value/week':>14}")
rows = []
for name, weeks in PROJECTS.items():
    value, cost = annual_value(name), weeks * ENGINEER_WEEK
    rows.append((value / weeks, name, value, cost))
for per_week, name, value, cost in sorted(rows, reverse=True):
    print(f"{name:28}{value:>14,.0f}{cost:>10,.0f}{cost / (value / 52):>9.1f} wk{per_week:>14,.0f}")
best = max(rows)[1]
print(f"\nDo {best!r} first: its value per week of effort is the highest, "
      "so every week it waits costs the most.")
print("Each figure rests on one assumption written beside it; "
      "change the assumption and the ranking can change.")
