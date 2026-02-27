import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

Trade = pd.read_csv(r"Markets-Repo\World Trade.csv", header=0, parse_dates=["date"])

txt = 'Source: UN Trade and Development'
fig, ax = plt.subplots(figsize=(12, 6))

# Plot series
ax.plot(Trade['date'], Trade["Global Factor"], color='#7F1718', 
        label="Global Financial Cycle", linewidth=2 )

ax.plot(Trade['date'], Trade['CPB_res_std'], 
        linewidth=2, label='World Trade')

# Formatting
ax.legend()
ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)
ax.set_xlabel("Date", fontweight='semibold', fontsize=12)
ax.set_ylabel("Index Value", fontweight='semibold', fontsize=12)
ax.set_title("Financialisation of Trade", fontsize=16, fontweight='bold', pad=20)
ax.set_axisbelow(True)
# Date axis formatting
ax.xaxis.set_major_locator(mdates.YearLocator(5))  
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
fig.autofmt_xdate()

# Add text inside the plot space
ax.text(0.01, 0.02, txt, transform=ax.transAxes, fontsize=10, alpha=0.8)
ax.set_facecolor('#f8f9fa')
fig.patch.set_facecolor('white')
plt.tight_layout()

plt.savefig("Financialisation_of_trade.png", dpi=300, bbox_inches='tight', 
            facecolor='white')
plt.show()
