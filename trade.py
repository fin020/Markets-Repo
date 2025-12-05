import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

trade = pd.read_excel("Trade_Policy_Uncertainty.xlsx", header=0, sheet_name="TPU_QUARTERLY")

trade['DATEQ'] = pd.to_datetime(trade['DATEQ'])
print(trade.head())

fig, ax = plt.subplots(figsize=(10, 6), dpi=150)

ax.plot(trade['DATEQ'],trade['TPUQ'], label="TPU", linewidth=2.5,
        color='#7F1718', marker='o', markersize=4, alpha=0.9)

# Styling
ax.set_title('Trade Policy Uncertainty Index', 
             fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Year', fontsize=12, fontweight='semibold')
ax.set_ylabel('TPU', fontsize=12, fontweight='semibold')

ax.xaxis.set_major_locator(mpl.dates.YearLocator())
ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%Y'))

# Grid styling
ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)
ax.set_axisbelow(True)

# Rotate x-axis labels for better readability
plt.xticks(rotation=45, ha='right')

# Add subtle background
ax.set_facecolor('#f8f9fa')
fig.patch.set_facecolor('white')

# Adjust spines
for spine in ax.spines.values():
    spine.set_edgecolor('#cccccc')
    spine.set_linewidth(1)

# Tight layout
plt.tight_layout()

# Save as high-resolution image for PowerPoint
plt.savefig('Trade Policy Uncertainity.png', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')

plt.show()



