import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

# Load and prepare data
gdp = pd.read_csv("GDP_Per_Capita.csv", header=0)
gdp = gdp[['Reference area', 'TIME_PERIOD', 'OBS_VALUE']]
gdp = gdp.rename(columns={
    'Reference area': 'Country',
    'TIME_PERIOD': 'Time',
    'OBS_VALUE': 'Observation value'
})

# Filter major economies
Countries = ['United States', 'Germany', 'Japan', 'United Kingdom']
gdp = gdp[gdp['Country'].isin(Countries)]

# Convert time and set index
gdp['Time'] = pd.PeriodIndex(gdp['Time'], freq='Q').to_timestamp()
gdp = gdp.set_index('Time').sort_index()

# --------------------------
# 1) Annual GDP per capita (average if multiple periods)
# --------------------------
gdp_annual = gdp.groupby("Country").resample("YE").mean()

# --------------------------
# 2) Compute annual % change correctly PER COUNTRY
# --------------------------
gdp_annual['Change'] = gdp_annual.groupby('Country')['Observation value'].pct_change()
gdp_annual['Change'] = gdp_annual['Change'] * 100
# Reset index for plotting
gdp_annual = gdp_annual.reset_index()

# =======================
# 📈 Professional Plot
# =======================
txt = "Data Source: OECD GDP Per Capita Dataset"

fig, ax = plt.subplots(figsize=(12, 7), dpi=150)

colors = {
    'United States': '#7f1718',
    'Germany': '#6fa6ff',
    'Japan': '#003e8d',
    'United Kingdom': '#234a00',
}

for country, group in gdp_annual.groupby('Country'):
    ax.plot(group['Time'], group['Change'],
            label=country,
            color=colors.get(country, '#333333'),
            linewidth=2.5,
            marker='o',
            markersize=4,
            alpha=0.9)

# Styling
ax.set_title('Real GDP Per Capita Growth (%)', fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Year', fontsize=12, fontweight='semibold')
ax.set_ylabel('Annual % Change', fontsize=12, fontweight='semibold')

ax.xaxis.set_major_locator(mpl.dates.YearLocator())
ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%Y'))

ax.legend(title='Economy', title_fontsize=11, fontsize=10,
          loc='best', frameon=True, shadow=True, fancybox=True)

fig.text(0, 0.01, txt, ha='left', fontsize=9, color='#555555')

ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)
ax.set_axisbelow(True)
plt.xticks(rotation=45, ha='right')

ax.set_facecolor('#f8f9fa')
fig.patch.set_facecolor('white')

for spine in ax.spines.values():
    spine.set_edgecolor('#cccccc')
    spine.set_linewidth(1)

plt.tight_layout()
plt.savefig('gdp_outlook_professional.png', dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')

# ---- Global Average Line Across Countries ----
avg_growth = gdp_annual.groupby('Time')['Change'].mean()

ax.plot(avg_growth.index, avg_growth.values,
        label='Average (All Countries)',
        color='black',
        linestyle='--',
        linewidth=2.2,
        alpha=0.8)

plt.show()

print("Professional chart saved as 'gdp_outlook_professional.png'")


print(gdp_annual.tail())
