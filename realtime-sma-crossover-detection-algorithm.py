import yfinance as yf
import pandas as pd
from datetime import datetime, time
from colorama import Fore, Style, init
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.animation import FuncAnimation
import platform
import os
import pytz

# Initialize colorama
init(autoreset=True)

symbol = input("Enter Stock Ticker(eg.RELIANCE.NS): ")
lower = int(input("Enter lower crossover average(eg.5): "))
upper = int(input("Enter upper crossover average(eg.20): "))
interval = input("Enter interval for averages(1m,5m,1d,1mo): ")
IS_SLOW_INTERVAL = interval in {"1d", "1mo"}


fig, ax = plt.subplots(figsize=(10,5))

price_line, = ax.plot([], [], label="Price")
lower_line, = ax.plot([], [], label=f"{lower}-DMA", color="green")
upper_line, = ax.plot([], [], label=f"{upper}-DMA", color="red")
signal_bars = []  # vertical bars marking buy/sell crossovers

ax.xaxis_date()  

ax.xaxis.set_major_locator(mdates.AutoDateLocator())

if interval.endswith("m") or interval.endswith("h"):
    # Intraday → show only time
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
elif interval == "1d":
    # Daily candles → show date
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%b"))
elif interval == "1mo":
    # Monthly candles → show Month + Year
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
else:
    # fallback
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%b"))

fig.autofmt_xdate(rotation=30)
# ---------------------------------------
fig.autofmt_xdate(rotation=30)  # rotate labels for readability

ax.set_title(f"{symbol} Intraday Price with {lower}-DMA & {upper}-DMA")
ax.set_xlabel("Time")
ax.set_ylabel("Price")
ax.legend()
ax.grid(True, linestyle="--", alpha=0.6)

#plt.show(block=False)
# ----------------------------------------------------------------------

def play_sound():
    if platform.system() == "Windows":
        import winsound
        winsound.Beep(1000, 500)
    elif platform.system() == "Darwin":
        os.system("afplay /System/Library/Sounds/Glass.aiff")
    else:
        os.system("beep -f 1000 -l 500")

def check_crossover():
    try:
        ticker = yf.Ticker(symbol)
    except Exception as e:
        print(Fore.RED + f"\nError: Failed to create ticker for '{symbol}'.")
        print("This may happen because:")
        print("  - Invalid ticker symbol format")
        print("  - Network connectivity issues")
        print("  - Yahoo Finance API is temporarily unavailable")
        print("  - Ticker symbol doesn't exist")
        print("  - Special characters or formatting errors in ticker name")
        print(f"Details: {str(e)}\n")
        return

    # --- choose a period that gives more intraday bars for short intervals ---
    if interval.endswith("m") or interval.endswith("h"):
        # '2d' often forces Yahoo to return the full intraday day bars
        period = "8d"
    else:
        period = "4y"

    try:
        data = ticker.history(period=period, interval=interval)
    except Exception as e:
        print(Fore.RED + f"\nError: Failed to fetch data for '{symbol}'.")
        print("This may happen because:")
        print("  - Invalid ticker symbol or symbol doesn't exist")
        print("  - Network connection issue or internet is down")
        print("  - Yahoo Finance API is temporarily unavailable")
        print(f"Details: {str(e)}\n")
        return

    if data.empty:
        print(Fore.RED + f"\nError: No data returned for '{symbol}' with interval '{interval}'.")
        print("This may happen because:")
        print("  - The ticker symbol is incorrect (e.g., use RELIANCE.NS for NSE stocks)")
        print("  - Insufficient historical data available")
        print("  - You are not connected to the internet")
        print("Try a different interval or ticker.\n")
        return

    # --- Robust timezone handling: convert index to Asia/Kolkata and then drop tzinfo for plotting
    try:
        # if index already tz-aware, tz will not be None
        if data.index.tz is None:
            # assume UTC if naive (yfinance sometimes returns tz-aware though)
            try:
                data.index = data.index.tz_localize("UTC").tz_convert("Asia/Kolkata")
            except Exception:
                # if localization fails, try to localize directly to Asia/Kolkata
                data.index = data.index.tz_localize("Asia/Kolkata")
        else:
            data.index = data.index.tz_convert("Asia/Kolkata")
    except Exception:
        # fallback: try naive localize
        try:
            data.index = data.index.tz_localize("Asia/Kolkata")
        except Exception:
            pass

    # drop tz info to make plotting / xlim comparisons simpler (naive datetimes)
    try:
        data.index = data.index.tz_localize(None)
    except Exception:
        # if already naive, this will raise — ignore
        pass

    # Filter intraday trading hours if minute/hour interval
    if interval.endswith("m") or interval.endswith("h"):
        data = data.between_time("09:15", "15:30")

    # compute DMAs
    data["lowerDMA"] = data["Close"].rolling(lower).mean()
    data["higherDMA"] = data["Close"].rolling(upper).mean()

    # ensure there are at least two rows before indexing [-2], [-1]
    if len(data) < 2:
        print(Fore.RED + f"\nError: Not enough data bars to check crossover.")
        print(f"Only {len(data)} bar(s) available. Need at least 2 bars.")
        print("This may happen because:")
        print("  - Insufficient historical data for the selected interval")
        print("  - The ticker has very limited trading history")
        print("Try a longer period or different interval.\n")
        return

    prev, last = data.iloc[-2], data.iloc[-1]
    if interval == "5m" :
        ist = pytz.timezone("Asia/Kolkata")
        now = datetime.now(ist)
        cutoff_time = time(15, 29)  # 3:29 PM

        if now.time() > cutoff_time:
            capped_time = now.replace(hour=15, minute=29, second=0, microsecond=0)
        else:
            capped_time = now
        timestamp = capped_time.strftime("%Y-%m-%d %H:%M")
    else:
        timestamp = last.name.strftime("%Y-%m-%d %H:%M")

    print("\n" + "="*60)
    print(Fore.CYAN + f" Checking crossover for {symbol} at {timestamp}")
    print("="*60)
    print(f" Price: {Fore.CYAN}{round(last['Close'], 2)}{Style.RESET_ALL}")
    print(f" {lower}DMA : {Fore.GREEN}{round(last['lowerDMA'], 2)}{Style.RESET_ALL}")
    print(f" {upper}DMA: {Fore.MAGENTA}{round(last['higherDMA'], 2)}{Style.RESET_ALL}")

    if prev["lowerDMA"] < prev["higherDMA"] and last["lowerDMA"] > last["higherDMA"]:
        print(Fore.GREEN + "\n Bullish Crossover → BUY signal\n")
        play_sound()
    elif prev["lowerDMA"] > prev["higherDMA"] and last["lowerDMA"] < last["higherDMA"]:
        print(Fore.RED + "\n Bearish Crossover → SELL signal\n")
        play_sound()
    else:
        print(Fore.YELLOW + "\n No crossover yet\n")

    print("="*60 + "\n")

    # slice data for plotting with timezone-safe masks
    def build_plot_slice():
        now_kolkata = pd.Timestamp.now(tz="Asia/Kolkata").tz_localize(None)

        if interval == "5m":
            start = now_kolkata.normalize()
            end = start + pd.Timedelta(days=1)
            mask = (data.index >= start) & (data.index < end)
            subset = data.loc[mask]
        elif interval == "1m":
            subset = data.tail(60)
        else:
            subset = data.tail(30)

        if subset.empty:
            # fallback so the plot never blanks out after-hours
            fallback_rows = min(60, len(data))
            subset = data.tail(fallback_rows)
        return subset

    data_today = build_plot_slice()

    # ---- LIVE PLOT UPDATE (REPLACES the old plt.figure()/plt.show() block) ----
    if data_today.empty:
        print(Fore.RED + "\nError: No data available to plot for the selected time slice.")
        print("This may happen because:")
        print("  - The selected date range has no trading activity\n")
    else:
        # convert index (datetime-like) to matplotlib date numbers
        x_nums = mdates.date2num(data_today.index.to_pydatetime())

        # set new data (x as date numbers, y as price/DMAs)
        price_line.set_data(x_nums, data_today["Close"].to_numpy())
        lower_line.set_data(x_nums, data_today["lowerDMA"].to_numpy())
        upper_line.set_data(x_nums, data_today["higherDMA"].to_numpy())

        # rebuild crossover bars
        for bar in signal_bars:
            bar.remove()
        signal_bars.clear()

        dma_diff = data_today["lowerDMA"] - data_today["higherDMA"]

        def interpolate_cross(prev_ts, curr_ts, prev_val, curr_val):
            prev_num = mdates.date2num(prev_ts)
            curr_num = mdates.date2num(curr_ts)
            denom = curr_val - prev_val
            if denom == 0:
                frac = 0
            else:
                frac = -prev_val / denom
            frac = max(0, min(1, frac))
            return prev_num + frac * (curr_num - prev_num)

        for i in range(1, len(data_today)):
            prev_val = dma_diff.iloc[i - 1]
            curr_val = dma_diff.iloc[i]
            if pd.isna(prev_val) or pd.isna(curr_val):
                continue

            prev_ts = data_today.index[i - 1]
            curr_ts = data_today.index[i]
            cross_num = interpolate_cross(prev_ts, curr_ts, prev_val, curr_val)

            if prev_val <= 0 and curr_val > 0:
                bar = ax.axvline(cross_num, color="green", alpha=0.35, linewidth=2)
                signal_bars.append(bar)
            elif prev_val >= 0 and curr_val < 0:
                bar = ax.axvline(cross_num, color="red", alpha=0.35, linewidth=2)
                signal_bars.append(bar)

        # rescale axes to new data
        ax.relim()
        ax.autoscale_view()

        # ensure x-axis treats numbers as dates and formats ticks
        # ---- DYNAMIC DATE/TIME FORMATTING ----
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        if interval.endswith("m") or interval.endswith("h"):
            # Intraday → show only time
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        elif interval == "1d":
            # Daily candles → show date
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%b"))
        elif interval == "1mo":
            # Monthly candles → show Month + Year
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        else:
            # fallback
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%b"))

        fig.autofmt_xdate(rotation=30)
# ---------------------------------------
        fig.canvas.draw_idle()   # efficient redraw
    # --------------------------------------------------------------------------------


def start_auto_updates(interval_ms=60_000):
    """Kick off an initial refresh and schedule minute-wise updates."""

    def _update(_):
        check_crossover()

    # run once immediately so users see data without waiting a minute
    check_crossover()

    if IS_SLOW_INTERVAL:
        print("Single-run mode for daily/monthly interval. Close the chart window when done.")
        plt.show()
        return

    # keep a reference on the figure object to avoid garbage collection
    # cache_frame_data=False prevents the unbounded cache warning
    fig.animation = FuncAnimation(fig, _update, interval=interval_ms, cache_frame_data=False)
    print(f"Live chart will refresh every {interval_ms // 1000} seconds. Close the window to stop.")
    plt.show()


if __name__ == "__main__":
    try:
        start_auto_updates()
    except KeyboardInterrupt:
        print("\n" + Fore.YELLOW + "Stopped by user")
    except Exception as e:
        print(Fore.RED + f"\nUnexpected error occurred: {str(e)}")
        print("This may happen because:")
        print("  - Invalid input values or format")
        print("  - Memory or system resource limitations")
        print("  - Library version compatibility issues")
        print("  - Corrupted data or file system errors")
        print("  - Unexpected API response format")
        print("Please check your inputs and try again.\n")