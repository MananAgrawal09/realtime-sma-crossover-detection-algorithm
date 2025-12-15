![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
# realtime-sma-crossover-detection-algorithm
I built a real-time stock analysis tool that streams live data, computes SMA indicators, detects bullish/bearish crossovers, and updates a live chart with visual and audio alerts. Features multi-interval analysis, timezone handling, and robust intraday data processing.


## Features:

1. Live data streaming using Yahoo Finance

2. Multi-timeframe support: 1m, 5m, 1d, 1mo

3. Dynamic moving averages: user-selectable (e.g., 5-DMA, 20-DMA)

4. Automatic crossover detection

5. Bullish crossover → Buy signal

6. Bearish crossover → Sell signal

7. Audio alerts when a crossover occurs

8. Live chart that updates every minute

9. Vertical markers showing crossover points

10. Timezone handling (Asia/Kolkata)

11. Intraday filtering for accurate 9:15–15:30 market hours

12. User friendly CLI output


## How It Works:

  1. Fetches the latest market data from Yahoo Finance

  2. Computes rolling moving averages in real time

  3. Compares previous vs. current SMA values to detect crossings

  4. Updates a live Matplotlib chart every 60 seconds

  5. Audio and Visual alert when a crossover occurs

  6. Refreshes the console display with the latest analysis

## USAGE

1. Create and activate a virtual environment.
   
2. Install dependencies: `pip install -r requirements.txt`
   
3. Run: `python realtime_sma_analyzer.py`

### Example Input

![Example Input](examples/inputexample.gif)

## Example Output
### Console (Real-Time Updates):
FOR 5 MIN:

<img width="940" height="465" alt="image" src="https://github.com/user-attachments/assets/6b8d8027-4ed2-457c-8b43-f9f194464bbe" />

<img width="943" height="470" alt="image" src="https://github.com/user-attachments/assets/2c5118af-2778-4cf7-b2c1-b7730eaa1150" />

FOR 1 MONTH:

<img width="694" height="240" alt="image" src="https://github.com/user-attachments/assets/5df496a7-ec0f-4359-9d5f-456404ec7ebe" />

### Live Chart Example

Price + 5-DMA + 20-DMA with crossover markers.

FOR 1 MIN INTERVAL:

<img width="959" height="503" alt="image" src="https://github.com/user-attachments/assets/c66acc13-6d58-4045-8c60-3c2b138851da" />

FOR 5 MIN INTERVAL:

<img width="959" height="502" alt="image" src="https://github.com/user-attachments/assets/d059ee98-9856-4afc-b0aa-c751a1161889" />

FOR 1 DAY INTERVAL:

<img width="959" height="502" alt="image" src="https://github.com/user-attachments/assets/b0536b14-30ae-473a-a79a-69db0f8c3882" />

FOR 1 MONTH INTERVAL:

<img width="959" height="502" alt="image" src="https://github.com/user-attachments/assets/6a4f9219-9065-450e-90f9-02e42ae6178b" />

## ALGORITHM:

<img width="361" height="402" alt="image" src="https://github.com/user-attachments/assets/b7ef97a3-01c5-473e-a28b-b5e199f7b24b" />

## LICENSE:

  This project is licensed under the MIT License.
