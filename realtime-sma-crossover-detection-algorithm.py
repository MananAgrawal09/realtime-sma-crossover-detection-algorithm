import yfinance as yf
import pandas as pd
from datetime import datetime, time
from colorama import Fore, Style, init
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.animation import FuncAnimation
from matplotlib.ticker import MaxNLocator, FuncFormatter
import platform
import os
import pytz
import numpy as np

init(autoreset=True)

symbol = input("Enter Stock Ticker(eg.RELIANCE.NS): ")
lower = int(input("Enter lower crossover average(eg.5): "))
upper = int(input("Enter upper crossover average(eg.20): "))
interval = input("Enter interval for averages(1m,5m,15m,1d,1mo): ")
IS_SLOW_INTERVAL = interval in {"1d", "1mo"}
IS_INTRADAY = interval in ("1m", "5m", "15m")

fig, ax = plt.subplots(figsize=(10, 5))
price_line, = ax.plot([], [], label="Price")
lower_line, = ax.plot([], [], label=f"{lower}-DMA", color="green")
upper_line, = ax.plot([], [], label=f"{upper}-DMA", color="red")
signal_bars = []

ax.xaxis_date()
ax.xaxis.set_major_locator(mdates.AutoDateLocator())


def set_date_formatter():
    if interval.endswith("m") or interval.endswith("h"):
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    elif interval == "1d":
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%b"))
    elif interval == "1mo":
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    else:
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%b"))
    fig.autofmt_xdate(rotation=30)


set_date_formatter()
ax.set_title(f"{symbol} Intraday Price with {lower}-DMA & {upper}-DMA")
ax.set_xlabel("Time")
ax.set_ylabel("Price")
ax.legend()
ax.grid(True, linestyle="--", alpha=0.6)


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

    period = "8d" if (interval.endswith("m") or interval.endswith("h")) else "4y"

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

    try:
        if data.index.tz is None:
            try:
                data.index = data.index.tz_localize("UTC").tz_convert("Asia/Kolkata")
            except Exception:
                data.index = data.index.tz_localize("Asia/Kolkata")
        else:
            data.index = data.index.tz_convert("Asia/Kolkata")
    except Exception:
        try:
            data.index = data.index.tz_localize("Asia/Kolkata")
        except Exception:
            pass

    try:
        data.index = data.index.tz_localize(None)
    except Exception:
        pass

    if interval.endswith("m") or interval.endswith("h"):
        data = data.between_time("09:15", "15:30")

    data["lowerDMA"] = data["Close"].rolling(lower).mean()
    data["higherDMA"] = data["Close"].rolling(upper).mean()

    if len(data) < 2:
        print(Fore.RED + f"\nError: Not enough data bars to check crossover.")
        print(f"Only {len(data)} bar(s) available. Need at least 2 bars.")
        print("This may happen because:")
        print("  - Insufficient historical data for the selected interval")
        print("  - The ticker has very limited trading history")
        print("Try a longer period or different interval.\n")
        return

    prev, last = data.iloc[-2], data.iloc[-1]
    is_intraday_minute = interval.endswith("m") and interval != "1mo"
    if is_intraday_minute:
        ist = pytz.timezone("Asia/Kolkata")
        now = datetime.now(ist)
        cutoff_time = time(15, 29)
        capped_time = now.replace(hour=15, minute=29, second=0, microsecond=0) if now.time() > cutoff_time else now
        timestamp = capped_time.strftime("%Y-%m-%d %H:%M")
    else:
        timestamp = last.name.strftime("%Y-%m-%d %H:%M")

    print("\n" + "=" * 60)
    print(Fore.CYAN + f" Checking crossover for {symbol} at {timestamp}")
    print("=" * 60)
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

    print("=" * 60 + "\n")

    def build_plot_slice():
        now_kolkata = pd.Timestamp.now(tz="Asia/Kolkata").tz_localize(None)
        if interval in ("5m", "15m"):
            start = now_kolkata.normalize()
            end = start + pd.Timedelta(days=1)
            mask = (data.index >= start) & (data.index < end)
            subset = data.loc[mask]
        elif interval == "1m":
            subset = data.tail(60)
        else:
            subset = data.tail(30)
        if subset.empty:
            subset = data.tail(min(60, len(data)))
        return subset

    data_today = build_plot_slice()

    if data_today.empty:
        print(Fore.RED + "\nError: No data available to plot for the selected time slice.")
        print("This may happen because:")
        print("  - The selected date range has no trading activity\n")
    else:
        n_bars = len(data_today)
        if IS_INTRADAY:
            x_vals = np.arange(n_bars)
            price_line.set_data(x_vals, data_today["Close"].to_numpy())
            lower_line.set_data(x_vals, data_today["lowerDMA"].to_numpy())
            upper_line.set_data(x_vals, data_today["higherDMA"].to_numpy())
        else:
            x_vals = mdates.date2num(data_today.index.to_pydatetime())
            price_line.set_data(x_vals, data_today["Close"].to_numpy())
            lower_line.set_data(x_vals, data_today["lowerDMA"].to_numpy())
            upper_line.set_data(x_vals, data_today["higherDMA"].to_numpy())

        for bar in signal_bars:
            bar.remove()
        signal_bars.clear()

        dma_diff = data_today["lowerDMA"] - data_today["higherDMA"]

        for i in range(1, len(data_today)):
            prev_val = dma_diff.iloc[i - 1]
            curr_val = dma_diff.iloc[i]
            if pd.isna(prev_val) or pd.isna(curr_val):
                continue
            denom = curr_val - prev_val
            frac = 0 if denom == 0 else -prev_val / denom
            frac = max(0, min(1, frac))
            if IS_INTRADAY:
                cross_x = (i - 1) + frac
            else:
                prev_ts = data_today.index[i - 1]
                curr_ts = data_today.index[i]
                prev_num = mdates.date2num(prev_ts)
                curr_num = mdates.date2num(curr_ts)
                cross_x = prev_num + frac * (curr_num - prev_num)
            if prev_val <= 0 and curr_val > 0:
                bar = ax.axvline(cross_x, color="green", alpha=0.35, linewidth=2)
                signal_bars.append(bar)
            elif prev_val >= 0 and curr_val < 0:
                bar = ax.axvline(cross_x, color="red", alpha=0.35, linewidth=2)
                signal_bars.append(bar)

        ax.relim()
        ax.autoscale_view()

        if IS_INTRADAY:
            ax.set_xlim(-0.5, n_bars - 0.5)
            ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=min(12, max(2, n_bars))))
            times = data_today.index
            time_fmt = "%d-%b %H:%M" if interval == "15m" else "%H:%M"
            ax.xaxis.set_major_formatter(FuncFormatter(
                lambda x, _: times[int(np.clip(round(x), 0, n_bars - 1))].strftime(time_fmt)
                if n_bars > 0 else ""
            ))
            fig.autofmt_xdate(rotation=30)
        else:
            set_date_formatter()
        fig.canvas.draw_idle()


def start_auto_updates(interval_ms=60_000):
    def _update(_):
        check_crossover()

    check_crossover()

    if IS_SLOW_INTERVAL:
        print("Single-run mode for daily/monthly interval. Close the chart window when done.")
        plt.show()
        return

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
