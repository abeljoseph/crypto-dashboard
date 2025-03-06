# 2e9f1771-7616-433e-a93d-7e548c9a62b7

import sys
import requests
import matplotlib.pyplot as plt
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QPalette
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file

# CoinMarketCap API Key (Replace with your actual key)
API_KEY = os.getenv("API_KEY")
URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"

# Lists to store price data for plotting
timestamps = []
prices = []

class CryptoPriceApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.get_xrp_price()  # Initial fetch
        self.start_timer()

    def initUI(self):
        """Initialize GUI layout"""
        self.setWindowTitle("Live XRP Price Tracker")
        self.setGeometry(100, 100, 600, 500)

        # Create layout
        layout = QVBoxLayout()

        # Price Label (Top, with white and grey formatting)
        self.price_label = QLabel("Fetching...", self)
        self.price_label.setFont(QFont("Arial", 24, weight=QFont.Weight.Bold))
        layout.addWidget(self.price_label)

        # Data Output Area (Formatted Strings)
        self.data_output = QLabel("", self)
        self.data_output.setFont(QFont("Arial", 12))
        layout.addWidget(self.data_output)

        # Create two subplots: one for price, one for supply
        self.figure, (self.ax_price, self.ax_supply) = plt.subplots(1, 2, figsize=(10, 3))

        # Create separate canvases for embedding both charts in PyQt
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

    def get_xrp_price(self):
        """Fetches XRP price from CoinMarketCap API (in CAD)"""
        try:
            response = requests.get(URL, headers={"X-CMC_PRO_API_KEY": API_KEY}, params={"symbol": "XRP", "convert": "CAD"})
            data = response.json()
            quote = data["data"]["XRP"]["quote"]["CAD"]

            # Extracting the required data
            name = data["data"]["XRP"]["name"]
            
            self.circulating_supply = data["data"]["XRP"]["circulating_supply"]
            self.total_supply = data["data"]["XRP"]["total_supply"]

            price = quote["price"]
            percent_change_1h = quote["percent_change_1h"]
            percent_change_24h = quote["percent_change_24h"]

            price_str = f"{price:.10f}"  # Convert price to string with full precision
            main_part, decimals = price_str.split(".")  # Split into whole and decimal parts
            first_two_decimals, remaining_decimals = decimals[:2], decimals[2:]  # First 2 decimals + rest

            self.price_label.setText(
                f'CAD <span style="color:white">{main_part}.{first_two_decimals}</span>'
                f'<span style="color:grey">{remaining_decimals}</span>'
            )

            # Format other data
            formatted_data = f"""
<b>Name:</b> {name} <br>
<b>Circulating Supply:</b> {self.circulating_supply:,.0f} <br>
<b>Total Supply:</b> {self.total_supply:,.0f} <br>
<b>Price:</b> {price:.5f} CAD <br>
<b>Change (1h):</b> {percent_change_1h:+.2f}% <br>
<b>Change (24h):</b> {percent_change_24h:+.2f}% <br>
"""
            self.data_output.setText(formatted_data)

            # Store data for plotting
            timestamp = datetime.now().strftime("%H:%M:%S")  # Store time in HH:MM:SS format
            timestamps.append(timestamp)
            prices.append(price)

            # Update the chart
            self.update_chart()

        except Exception as e:
            self.price_label.setText("Error fetching price")

    def update_chart(self):
        """Updates both the price chart and the supply chart in the GUI"""
        if len(prices) > 1:
            # Update the price chart
            self.ax_price.clear()
            self.ax_price.plot(timestamps, prices, marker='o', linestyle='-', color='blue', label="XRP Price (CAD)")
            self.ax_price.set_xlabel("Time")
            self.ax_price.set_ylabel("Price (CAD)")
            self.ax_price.set_title("XRP Price Over Time")
            self.ax_price.legend()
            self.ax_price.tick_params(axis='x', rotation=45)

            # Update the supply chart
            self.ax_supply.clear()
            self.ax_supply.bar(["Circulating", "Total"], [self.circulating_supply, self.total_supply], color=['green', 'orange'])
            self.ax_supply.set_ylabel("Supply")
            self.ax_supply.set_title("Circulating vs Total Supply")

            # Refresh the canvas
            self.canvas.draw()


    def start_timer(self):
        """Refreshes price every 60 seconds"""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.get_xrp_price)
        self.timer.start(60000)  # Update every 60,000 ms (60 seconds)

# Run the application
app = QApplication(sys.argv)

# Set dark mode (Optional)
palette = QPalette()
palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
app.setPalette(palette)

window = CryptoPriceApp()
window.show()
sys.exit(app.exec())
