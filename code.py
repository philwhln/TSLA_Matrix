# Run on Metro M4 Airlift w RGB Matrix shield and 64x32 matrix display
# show current value of TSLA stock in USD

import time

import adafruit_requests as requests
import board
import terminalio
from adafruit_matrixportal.matrixportal import MatrixPortal

TICKER_SYMBOL = "TSLA"
DATA_SOURCE = "https://query2.finance.yahoo.com/v7/finance/quote?symbols=" + TICKER_SYMBOL

# the current working directory (where this file is)
cwd = ("/" + __file__).rsplit("/", 1)[0]

matrixportal = MatrixPortal(
    url=DATA_SOURCE,  # redundant request to get MatrixPortal to setup network
    status_neopixel=board.NEOPIXEL,
    bit_depth=4,
    default_bg=cwd + "/tesla_background.bmp",
    debug=True,
)

TEXT_REGULAR_HOURS = 0
matrixportal.add_text(
    text_color=0x3d1f5c,
    text_font=terminalio.FONT,
    text_position=(1, 7),
    text_scale=2,
)

TEXT_PERCENT = 1
matrixportal.add_text(
    text_color=0x3d3d3d,
    text_font=terminalio.FONT,
    text_position=(1, 24),
    text_scale=1,
)

TEXT_OUT_OF_HOURS = 2
matrixportal.add_text(
    text_color=0x3d1f5c,
    text_font=terminalio.FONT,
    text_position=(40, 24),
    text_scale=1,
)

matrixportal.preload_font(b"$012345789")  # preload numbers
matrixportal.preload_font((0x00A3, 0x20AC))  # preload gbp/euro symbol

while True:
    try:
        print(f'Fetching {DATA_SOURCE}')
        result = requests.get(DATA_SOURCE).json()["quoteResponse"]["result"][0]
        print(f'Got response: {result}')

        # regular hours
        regular_hours_color = 0x00ff00 if result["regularMarketPrice"] > 0 else 0xff0000
        matrixportal.set_text("$%d" % result["regularMarketPrice"], TEXT_REGULAR_HOURS)

        percent_change = result["regularMarketChangePercent"]

        if result["marketState"] == "PRE":
            # before hours
            afterHoursColor = 0x00ff00 if result["preMarketChangePercent"] > 0 else 0xff0000
            matrixportal.set_text_color(afterHoursColor, TEXT_OUT_OF_HOURS)
            matrixportal.set_text("$%d" % result["preMarketPrice"], TEXT_OUT_OF_HOURS)
            percent_change = result["preMarketChangePercent"]
            regular_hours_color = 0x009900 if result["regularMarketPrice"] > 0 else 0x990000
        elif result["marketState"] == "POST" or result["marketState"] == "POSTPOST":
            # after hours
            afterHoursColor = 0x00ff00 if result["postMarketChangePercent"] > 0 else 0xff0000
            matrixportal.set_text_color(afterHoursColor, TEXT_OUT_OF_HOURS)
            matrixportal.set_text("$%d" % result["postMarketPrice"], TEXT_OUT_OF_HOURS)
            percent_change += result["postMarketChangePercent"]
            regular_hours_color = 0x009900 if result["regularMarketPrice"] > 0 else 0x990000
        else:
            regular_hours_color = 0x00cc00 if result["regularMarketPrice"] > 0 else 0xcc0000

        percent_change_color = 0x00ff00 if percent_change > 0 else 0xff0000
        matrixportal.set_text_color(percent_change_color, TEXT_PERCENT)
        matrixportal.set_text("%0.2f%%" % percent_change, TEXT_PERCENT)

        matrixportal.set_text_color(regular_hours_color, TEXT_REGULAR_HOURS)

        print("Response is", result)
    except (ValueError, RuntimeError) as e:
        print("Some error occured, retrying! -", e)

    print("sleeping...")
    time.sleep(60)  # wait 1 minute
