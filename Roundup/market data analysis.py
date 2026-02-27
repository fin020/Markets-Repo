"""
Market Data Analysis Script
Fetches recent data on equities, bonds, and credit markets and creates visualisations.

Required packages:
    pip install yfinance fredapi pandas matplotlib seaborn

FRED API Key:
    Get a free API key from https://fred.stlouisfed.org/docs/api/api_key.html
    Replace 'YOUR_FRED_API_KEY' below with your actual key.
"""

import yfinance as yf
import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from fredapi import Fred
from datetime import datetime, timedelta
import os

# ============================================================================
# CONFIGURATION
# ============================================================================

# FRED API Key - REPLACE WITH YOUR KEY
FRED_API_KEY = os.getenv("FRED_API_KEY")  # Get from https://fred.stlouisfed.org/

# Date range for analysis
END_DATE = datetime.now()
START_DATE = END_DATE - timedelta(days=90)  # Last 3 months


def filter_by_date(df, start, end):
    """Filter DataFrame to rows between start and end (inclusive)."""
    if df.empty:
        return df
    # Ensure index is DatetimeIndex
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    # Sort index just in case
    df = df.sort_index()
    return df.loc[start:end]

# ============================================================================
# DATA FETCHING FUNCTIONS
# ============================================================================

def fetch_equity_indices():
    """Fetch major equity index data"""
    print("Fetching equity indices...")
    
    indices = {
        'S&P 500': '^GSPC',
        'Nasdaq': '^IXIC',
        'Dow Jones': '^DJI',
        'Russell 2000': '^RUT',
        'FTSE 100': '^FTSE',
        'DAX': '^GDAXI',
        'Nikkei 225': '^N225'
    }
    
    data = pd.DataFrame()
    for name, ticker in indices.items():
        try:
            df = yf.download(ticker, start=START_DATE, end=END_DATE, progress=False)
            data[name] = df['Close']
        except Exception as e:
            print(f"Error fetching {name}: {e}")
    
    return data


def fetch_vix():
    """Fetch VIX volatility index"""
    print("Fetching VIX...")
    try:
        vix = yf.download('^VIX', start=START_DATE, end=END_DATE, progress=False)
        vix_data = vix['Close']
        return vix_data
    except Exception as e:
        print(f"Error fetching VIX: {e}")
        return None

def fetch_treasury_yields(fred_api:str):
    """Fetch US Treasury yields across different maturities"""
    print("Fetching US Treasury yields...")
    
    # Treasury yield series from FRED
    treasury_series = {
        '1 Month': 'DGS1MO',
        '3 Month': 'DGS3MO',
        '6 Month': 'DGS6MO',
        '1 Year': 'DGS1',
        '2 Year': 'DGS2',
        '3 Year': 'DGS3',
        '5 Year': 'DGS5',
        '7 Year': 'DGS7',
        '10 Year': 'DGS10',
        '20 Year': 'DGS20',
        '30 Year': 'DGS30'
    }
    
    yields_data = pd.DataFrame()
    for name, series_id in treasury_series.items():
        try:
            data = fred_api.get_series(series_id, start_date=START_DATE, end_date=END_DATE)
            yields_data[name] = data
        except Exception as e:
            print(f"Error fetching {name}: {e}")
    
    return pd.DataFrame(yields_data)


def fetch_yield_curve(fred_api):
    """Fetch current yield curve snapshot"""
    print("Fetching current yield curve...")
    
    # Get most recent yields for yield curve
    treasury_series = {
        1/12: 'DGS1MO',    # 1 month
        3/12: 'DGS3MO',    # 3 months
        6/12: 'DGS6MO',    # 6 months
        1: 'DGS1',         # 1 year
        2: 'DGS2',         # 2 years
        3: 'DGS3',         # 3 years
        5: 'DGS5',         # 5 years
        7: 'DGS7',         # 7 years
        10: 'DGS10',       # 10 years
        20: 'DGS20',       # 20 years
        30: 'DGS30'        # 30 years
    }
    
    curve_data = pd.Series(dtype=float)
    for maturity, series_id in treasury_series.items():
        try:
            data = fred_api.get_series(series_id, start_date=START_DATE)
            if not data.empty:
                curve_data[maturity] = data.iloc[-1]  # Most recent value
        except Exception as e:
            print(f"Error fetching maturity {maturity}: {e}")
    
    return curve_data.sort_index()


def fetch_credit_spreads(fred_api):
    """Fetch credit spreads (IG and HY)"""
    print("Fetching credit spreads...")
    
    credit_series = {
        'IG Corporate Spread': 'BAMLC0A4CBBB',  # BBB Corporate Option-Adjusted Spread
        'HY Corporate Spread': 'BAMLH0A0HYM2',  # High Yield Option-Adjusted Spread
        'IG AAA Spread': 'BAMLC0A1CAAA',        # AAA Corporate Option-Adjusted Spread
    }
    
    spreads_data = pd.DataFrame()
    for name, series_id in credit_series.items():
        try:
            data = fred_api.get_series(series_id, start_date=START_DATE, end_date=END_DATE)
            spreads_data[name] = data
        except Exception as e:
            print(f"Error fetching {name}: {e}")
    
    return spreads_data


def fetch_european_sovereign_yields(fred_api:str):
    """Fetch European sovereign bond yields"""
    print("Fetching European sovereign yields...")
    
    # 10-year government bond yields
    european_yields = {
        'Germany 10Y': 'IRLTLT01DEM156N',  # Germany
        'France 10Y': 'IRLTLT01FRM156N',   # France
        'Italy 10Y': 'IRLTLT01ITM156N',    # Italy
        'Spain 10Y': 'IRLTLT01ESM156N',    # Spain
        'UK 10Y': 'IRLTLT01GBM156N',       # UK
    }
    
    yields_data = pd.DataFrame()
    for name, series_id in european_yields.items():
        try:
            data = fred_api.get_series(series_id, start_date=START_DATE, end_date=END_DATE)
            yields_data[name] = data
        except Exception as e:
            print(f"Error fetching {name}: {e}")
    
    return pd.DataFrame(yields_data)

# ============================================================================
# VISUALIsATION FUNCTIONS
# ============================================================================

def plot_equity_performance(equity_data:DataFrame):
    """Plot equity index performance (normalised)"""
    print("Creating equity performance chart...")
    
    # Normalise to 100 at start date
    normalised = (equity_data / equity_data.iloc[0]) * 100
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Plot each index
    for column in normalised.columns:
        ax.plot(normalised.index, normalised[column], label=column, linewidth=2)
    
    ax.set_title('Major Equity Indices Performance (Normalised to 100)', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Index Value (Normalised)', fontsize=12)
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.axhline(y=100, color='black', linestyle='--', linewidth=1, alpha=0.5)
    
    # Format x-axis with proper locator
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))  # Every 2 months
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    return fig


def plot_vix(vix_data:DataFrame):
    """Plot VIX volatility index"""
    print("Creating VIX chart...")
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    ax.plot(vix_data.index, vix_data.values, color='red', linewidth=2, label='VIX')
    ax.fill_between(vix_data.index, vix_data.values.flatten(), alpha=0.3, color='red')
    
    # Add threshold lines
    ax.axhline(y=20, color='orange', linestyle='--', linewidth=1, 
               label='Moderate Volatility (20)', alpha=0.7)
    ax.axhline(y=30, color='darkred', linestyle='--', linewidth=1, 
               label='High Volatility (30)', alpha=0.7)
    
    ax.set_title('VIX Volatility Index', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('VIX Level', fontsize=12)
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # Format x-axis with proper locator
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))  # Every 2 months
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    return fig


def plot_treasury_yields(yields_data:DataFrame):
    """Plot US Treasury yields over time"""
    print("Creating Treasury yields chart...")
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Plot key maturities
    key_maturities = ['2 Year', '5 Year', '10 Year', '30 Year']
    colors = ['blue', 'green', 'red', 'purple']
    
    for maturity, color in zip(key_maturities, colors):
        if maturity in yields_data.columns:
            ax.plot(yields_data.index, yields_data[maturity], 
                   label=maturity, linewidth=2, color=color)
    
    ax.set_title('US Treasury Yields Over Time', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Yield (%)', fontsize=12)
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # Format x-axis with proper locator
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))  # Every 2 months
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    return fig


def plot_yield_curve(curve_data:DataFrame):
    """Plot current yield curve"""
    print("Creating yield curve chart...")
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    maturities = curve_data.index.values
    yields = curve_data.values
    
    ax.plot(maturities, yields, marker='o', linewidth=2, markersize=8, color='navy')
    ax.fill_between(maturities, yields, alpha=0.2, color='navy')
    
    ax.set_title('US Treasury Yield Curve (Current)', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Maturity (Years)', fontsize=12)
    ax.set_ylabel('Yield (%)', fontsize=12)
    ax.grid(True, alpha=0.3)
    
    # Mark key points
    for x, y in zip(maturities, yields):
        ax.annotate(f'{y:.2f}%', xy=(x, y), xytext=(0, 10), 
                   textcoords='offset points', ha='center', fontsize=9)
    
    plt.tight_layout()
    return fig


def plot_yield_curve_dynamics(yields_data:DataFrame):
    """Plot yield curve changes over time (2s10s spread)"""
    print("Creating yield curve dynamics chart...")
    
    if '2 Year' in yields_data.columns and '10 Year' in yields_data.columns:
        spread = yields_data['10 Year'] - yields_data['2 Year']
        
        fig, ax = plt.subplots(figsize=(14, 6))
        
        ax.plot(spread.index, spread.values, linewidth=2, color='darkgreen', label='2s10s Spread')
        ax.fill_between(spread.index, spread.values, alpha=0.3, color='green', 
                       where=(spread.values >= 0), label='Normal (Positive)')
        ax.fill_between(spread.index, spread.values, alpha=0.3, color='red', 
                       where=(spread.values < 0), label='Inverted (Negative)')
        
        ax.axhline(y=0, color='black', linestyle='-', linewidth=1)
        
        ax.set_title('US Treasury Curve Dynamics (2s10s Spread)', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Spread (basis points)', fontsize=12)
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # Format x-axis with proper locator
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))  # Every 2 months
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        return fig
    else:
        print("2s10s spread data not available")
        return None


def plot_credit_spreads(spreads_data:DataFrame):
    """Plot credit spreads over time"""
    print("Creating credit spreads chart...")
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    colors = {'IG Corporate Spread': 'blue', 'HY Corporate Spread': 'red', 
              'IG AAA Spread': 'green'}
    
    for column in spreads_data.columns:
        color = colors.get(column, 'gray')
        ax.plot(spreads_data.index, spreads_data[column], 
               label=column, linewidth=2, color=color)
    
    ax.set_title('Credit Spreads (Option-Adjusted Spread)', 
                fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Spread (basis points)', fontsize=12)
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # Format x-axis with proper locator
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))  # Every 2 months
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    return fig


def plot_ig_hy_comparison(spreads_data:DataFrame):
    """Plot IG vs HY spread comparison"""
    print("Creating IG vs HY comparison chart...")
    
    if 'IG Corporate Spread' in spreads_data.columns and 'HY Corporate Spread' in spreads_data.columns:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        # Plot 1: Both spreads
        ax1.plot(spreads_data.index, spreads_data['IG Corporate Spread'], 
                label='Investment Grade', linewidth=2, color='blue')
        ax1.plot(spreads_data.index, spreads_data['HY Corporate Spread'], 
                label='High Yield', linewidth=2, color='red')
        ax1.set_title('Investment Grade vs High Yield Spreads', 
                     fontsize=14, fontweight='bold')
        ax1.set_ylabel('Spread (bps)', fontsize=11)
        ax1.legend(loc='best', fontsize=10)
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: HY-IG differential
        differential = spreads_data['HY Corporate Spread'] - spreads_data['IG Corporate Spread']
        ax2.plot(differential.index, differential.values, 
                linewidth=2, color='purple', label='HY-IG Differential')
        ax2.fill_between(differential.index, differential.values, alpha=0.3, color='purple')
        ax2.set_title('High Yield Premium over Investment Grade', 
                     fontsize=14, fontweight='bold')
        ax2.set_xlabel('Date', fontsize=11)
        ax2.set_ylabel('Differential (bps)', fontsize=11)
        ax2.legend(loc='best', fontsize=10)
        ax2.grid(True, alpha=0.3)
        
        # Format x-axis with proper locator
        for ax in [ax1, ax2]:
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))  # Every 2 months
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        return fig
    else:
        print("IG/HY comparison data not available")
        return None


def plot_european_yields(yields_data:DataFrame):
    """Plot European sovereign yields"""
    print("Creating European yields chart...")
    
    fig, ax = plt.subplots(figsize=(14, 8))
    dates = yields_data.index.strftime('%b %d').tolist()
    countries = yields_data.columns
    
    # Set bar width and positions
    bar_width = 0.35
    x = range(len(countries))  # positions for the country groups
    
    # Plot bars for each date
    bars1 = ax.bar([p - bar_width/2 for p in x], yields_data.iloc[0], 
                    width=bar_width, label=dates[0], alpha=0.8)
    bars2 = ax.bar([p + bar_width/2 for p in x], yields_data.iloc[1], 
                    width=bar_width, label=dates[1], alpha=0.8)
    
    # Add value labels on top of bars (optional)
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.2f}%',
                        xy=(bar.get_x() + bar.get_width()/2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=8)
    
        # Configure axes
        ax.set_title('European Sovereign Bond Yields (10-Year) – Two‑Date Comparison', 
                     fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Country', fontsize=12)
        ax.set_ylabel('Yield (%)', fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(countries, rotation=45, ha='right')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3, axis='y')  # grid only on y-axis
        
        plt.tight_layout()
        return fig


def create_summary_dashboard(equity_data:DataFrame, vix_data:DataFrame, yields_data:DataFrame, spreads_data:DataFrame):
    """Create a comprehensive summary dashboard"""
    print("Creating summary dashboard...")
    
    fig = plt.figure(figsize=(20, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # 1. Equity Performance (top left, spanning 2 columns)
    ax1 = fig.add_subplot(gs[0, :2])
    normalised = (equity_data / equity_data.iloc[0].fillna(0)) * 100
    for column in normalised.columns[:4]:  # Top 4 indices
        ax1.plot(normalised.index, normalised[column], label=column, linewidth=2)
    ax1.set_title('Equity Indices (Normalised)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Index Value (Normalised)', fontsize=10)
    ax1.legend(fontsize=8, loc='best')
    ax1.grid(True, alpha=0.3)
    ax1.axhline(y=100, color='black', linestyle='--', alpha=0.5)
    
    # 2. VIX (top right)
    ax2 = fig.add_subplot(gs[0, 2])
    ax2.plot(vix_data.index, vix_data.values, color='red', linewidth=2)
    ax2.fill_between(vix_data.index, vix_data.values.flatten(), alpha=0.3, color='red')
    ax2.axhline(y=20, color='orange', linestyle='--', alpha=0.7)
    ax2.set_title('VIX', fontsize=12, fontweight='bold')
    ax2.set_ylabel('VIX Level', fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.xaxis.set_major_locator(mdates.MonthLocator())  # Every 2 months
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    
    # 3. Treasury Yields (middle left)
    ax3 = fig.add_subplot(gs[1, 0])
    key_maturities = ['2 Year', '10 Year', '30 Year']
    for maturity in key_maturities:
        if maturity in yields_data.columns:
            ax3.plot(yields_data.index, yields_data[maturity], label=maturity, linewidth=2)
    ax3.set_title('Treasury Yields', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Yield (%)', fontsize=10)
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3)
    
    # 4. Credit Spreads (middle center)
    ax4 = fig.add_subplot(gs[1, 1])
    if 'IG Corporate Spread' in spreads_data.columns:
        ax4.plot(spreads_data.index, spreads_data['IG Corporate Spread'], 
                label='IG', linewidth=2, color='blue')
    if 'HY Corporate Spread' in spreads_data.columns:
        ax4.plot(spreads_data.index, spreads_data['HY Corporate Spread'], 
                label='HY', linewidth=2, color='red')
    ax4.set_title('Credit Spreads', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Spread (bps)', fontsize=10)
    ax4.legend(fontsize=8)
    ax4.grid(True, alpha=0.3)
    
    # 5. 2s10s Spread (middle right)
    ax5 = fig.add_subplot(gs[1, 2])
    if '2 Year' in yields_data.columns and '10 Year' in yields_data.columns:
        spread = yields_data['10 Year'] - yields_data['2 Year']
        ax5.plot(spread.index, spread.values, linewidth=2, color='darkgreen')
        ax5.fill_between(spread.index, spread.values, alpha=0.3, color='green')
        ax5.axhline(y=0, color='black', linestyle='-', linewidth=1)
    ax5.set_title('2s10s Spread', fontsize=12, fontweight='bold')
    ax5.set_ylabel("Spread (bps)", fontsize=10)
    ax5.grid(True, alpha=0.3)
    
    # 6. Performance Table (bottom, spanning all columns)
    ax6 = fig.add_subplot(gs[2, :])
    ax6.axis('off')
    
    # Calculate recent performance metrics
    metrics = []
    
    # Equity changes (last value vs first value)
    for column in equity_data.columns[:5]:
        pct_change = ((equity_data[column].iloc[-1] / equity_data[column].iloc[0]) - 1) * 100
        metrics.append([column, f'{pct_change:+.2f}%', 'Equity'])
    
    # VIX current level
    if vix_data is not None and len(vix_data) > 0:
        last_vix = vix_data.iloc[-1]
        if isinstance(last_vix, pd.Series):
            last_vix = last_vix.iloc[0]
        metrics.append(['VIX', f'{last_vix:.2f}', 'Volatility'])
    
    # Treasury yields current
    for maturity in ['2 Year', '10 Year', '30 Year']:
        if maturity in yields_data.columns:
            current = yields_data[maturity].iloc[-1]
            metrics.append([f'US {maturity}', f'{current:.2f}%', 'Treasury'])
    
    # Credit spreads current
    for spread_name in ['IG Corporate Spread', 'HY Corporate Spread']:
        if spread_name in spreads_data.columns:
            current = spreads_data[spread_name].iloc[-1]
            metrics.append([spread_name, f'{current:.0f} bps', 'Credit'])
    
    # Create table
    table_data = [[m[0], m[1], m[2]] for m in metrics]
    table = ax6.table(cellText=table_data, 
                     colLabels=['Instrument', 'Value/Change', 'Category'],
                     cellLoc='left', 
                     loc='center',
                     colWidths=[0.4, 0.3, 0.3])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)
    
    # Style table
    for i in range(len(table_data) + 1):
        for j in range(3):
            cell = table[(i, j)]
            if i == 0:
                cell.set_facecolor('#4472C4')
                cell.set_text_props(weight='bold', color='white')
            else:
                cell.set_facecolor('#E7E6E6' if i % 2 == 0 else 'white')
    
    fig.suptitle('Market Data Summary Dashboard', fontsize=18, fontweight='bold', y=0.995)
    
    return fig



# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    print("="*70)
    print("MARKET DATA ANALYSIS")
    print("="*70)
    print()
    
      # Check for FRED API key
    if FRED_API_KEY is None or FRED_API_KEY == "":
        print("ERROR: FRED API key not set. Please set the FRED_API_KEY environment variable.")
        return
    
    # Initialize FRED API
    fred = Fred(api_key=FRED_API_KEY)
    
    # Fetch all data
    print("\n" + "="*70)
    print("FETCHING DATA")
    print("="*70 + "\n")
    
    equity_data = fetch_equity_indices()
    equity_data = filter_by_date(equity_data, START_DATE, END_DATE)
    if not equity_data.empty:
        equity_data.to_csv("equity_indices.csv", index=True)
        print("✓ Saved: equity_indices.csv")
    
    vix_data = fetch_vix()
    vix_data = filter_by_date(vix_data, START_DATE, END_DATE)
    if vix_data is not None and not vix_data.empty:
        # Ensure vix_data is a Series for saving (if it's a single-column DataFrame, convert)
        if isinstance(vix_data, pd.DataFrame) and len(vix_data.columns) == 1:
            vix_data = vix_data.iloc[:, 0]
        vix_data.to_csv("vix.csv", index=True, header=True)
        print("✓ Saved: vix.csv")
    
    treasury_yields = fetch_treasury_yields(fred)
    treasury_yields = filter_by_date(treasury_yields, START_DATE, END_DATE)
    if not treasury_yields.empty:
        treasury_yields.to_csv("treasury_yields.csv", index=True)
        print("✓ Saved: treasury_yields.csv")
    
    yield_curve = fetch_yield_curve(fred)
    if not yield_curve.empty:
        # Series with maturity index
        yield_curve.to_csv("yield_curve.csv", index=True, header=["Yield"])
        print("✓ Saved: yield_curve.csv")
    
    credit_spreads = fetch_credit_spreads(fred)
    credit_spreads = filter_by_date(credit_spreads, START_DATE, END_DATE)
    if not credit_spreads.empty:
        credit_spreads.to_csv("credit_spreads.csv", index=True)
        print("✓ Saved: credit_spreads.csv")
    
    european_yields = fetch_european_sovereign_yields(fred)
    european_yields = filter_by_date(european_yields, START_DATE, END_DATE)
    if not european_yields.empty:
        european_yields.to_csv("european_yields.csv", index=True)
        print("✓ Saved: european_yields.csv")
    
    print("\n" + "="*70)
    print("CREATING VISUALISATIONS")
    print("="*70 + "\n")
    
    # Create visualisations
    figures = []
    
    # Equity charts
    if not equity_data.empty:
        figures.append(('equity_performance.png', plot_equity_performance(equity_data)))
    
    # VIX chart
    if vix_data is not None and len(vix_data) > 0:
        figures.append(('vix_volatility.png', plot_vix(vix_data)))
    
    # Treasury charts
    if not treasury_yields.empty:
        figures.append(('treasury_yields_time.png', plot_treasury_yields(treasury_yields)))
        figures.append(('yield_curve_dynamics.png', plot_yield_curve_dynamics(treasury_yields)))
    
    if not yield_curve.empty:
        figures.append(('yield_curve_current.png', plot_yield_curve(yield_curve)))
    
    # Credit spread charts
    if not credit_spreads.empty:
        figures.append(('credit_spreads.png', plot_credit_spreads(credit_spreads)))
        ig_hy_fig = plot_ig_hy_comparison(credit_spreads)
        if ig_hy_fig is not None:
            figures.append(('ig_hy_comparison.png', ig_hy_fig))
    
    # European yields
    if not european_yields.empty:
        figures.append(('european_sovereign_yields.png', plot_european_yields(european_yields)))
    
    # Summary dashboard
    if not equity_data.empty and vix_data is not None:
        figures.append(('summary_dashboard.png', 
                       create_summary_dashboard(equity_data, vix_data, 
                                               treasury_yields, credit_spreads)))
    
    # Save all figures
    print("\n" + "="*70)
    print("SAVING CHARTS")
    print("="*70 + "\n")
    
    for filename, fig in figures:
        if fig is not None:
            fig.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"[OK] Saved: {filename}")
            plt.close(fig)
    
    print("\n" + "="*70)
    print("COMPLETE!")
    print("="*70)
    print(f"\nGenerated {len(figures)} charts")
    print("Check the current directory for PNG files")


if __name__ == "__main__":
    main()