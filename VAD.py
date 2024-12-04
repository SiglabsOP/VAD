import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLabel, QLineEdit, QHBoxLayout, QScrollArea, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPalette, QIcon, QFont
import yfinance as yf
import pandas as pd
from plyer import notification
from PyQt5.QtWidgets import QDialog, QTextEdit
from PyQt5.QtWidgets import QSlider
 


def fetch_live_stock_data(ticker, period="1y"):
    try:
        # Fetch the data
        data = yf.download(ticker, period=period, group_by="Ticker")
        
        # Debugging: Print the columns and structure
        print(f"Columns for {ticker}: {data.columns}")
        print(data.head())
        
        if isinstance(data.columns, pd.MultiIndex):
            if (ticker, 'Volume') in data.columns and (ticker, 'Adj Close') in data.columns:
                # Extract relevant columns and flatten the MultiIndex
                data = data.loc[:, [(ticker, 'Adj Close'), (ticker, 'Volume')]]
                data.columns = ['Adj Close', 'Volume']  # Flatten column names
            else:
                print(f"Error: 'Adj Close' or 'Volume' column is missing for {ticker}")
                return None
        else:
            # Handle standard single-level columns
            if 'Volume' in data.columns and 'Adj Close' in data.columns:
                data = data[['Adj Close', 'Volume']]
            else:
                print(f"Error: 'Adj Close' or 'Volume' column is missing for {ticker}")
                return None
        
        return data
    except Exception as e:
        print(f"Error fetching live data for {ticker}: {e}")
        return None




def detect_volume_anomalies(data, ticker, threshold=2):
    if data is None or data.empty:
        print(f"No data available for {ticker}")
        return pd.DataFrame()

    if 'Volume' not in data.columns:
        print(f"Error: 'Volume' column is missing for {ticker}")
        return pd.DataFrame()

    # Calculate rolling average and detect anomalies
    data['RollingAvg'] = data['Volume'].rolling(window=20).mean()
    data.dropna(inplace=True)

    if data.empty:
        print(f"No data left after cleaning for {ticker}")
        return pd.DataFrame()

    data['VolumeAnomaly'] = data['Volume'] > (data['RollingAvg'] * threshold)
    anomalies = data[data['VolumeAnomaly']]
    print(f"Detected Anomalies for {ticker}:\n", anomalies)
    return anomalies

class VolumeAnomalyDetector(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Volume Anomaly Detector")
        self.setWindowIcon(QIcon("logo.png"))
        self.setGeometry(100, 100, 900, 700)
 
        self.set_theme()

        self.main_widget = QWidget(self)
        self.layout = QVBoxLayout(self.main_widget)

        self.create_menu()
        self.threshold = 2  # Set the default threshold value
        
        self.add_widgets()

        self.setCentralWidget(self.main_widget)

        # Initialize status label
        self.status_label = QLabel(self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: white; background-color: #1a1a1a; padding: 10px;")
        self.layout.addWidget(self.status_label)

        # Load the last ticker input
        self.load_last_ticker()

    def set_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(33, 37, 43))  # Dark gray background
        palette.setColor(QPalette.WindowText, QColor(255, 255, 255))  # White text
        self.setPalette(palette)
        
        
        
    def update_gui_with_anomalies(self, anomalies, ticker):
        if anomalies.empty:
            self.status_label.setText(f"No anomalies detected for {ticker}.")
            self.status_label.setStyleSheet("color: green; background-color: #1a1a1a; padding: 10px;")
            self.table.setRowCount(0)
            return
    
        self.table.setRowCount(len(anomalies))
        for row, (date, anomaly) in enumerate(anomalies.iterrows()):
            self.table.setItem(row, 0, QTableWidgetItem(str(date.date())))
            self.table.setItem(row, 1, QTableWidgetItem(f"{anomaly['Adj Close']:.2f}"))
            self.table.setItem(row, 2, QTableWidgetItem(f"{anomaly['Volume']:.0f}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{anomaly['RollingAvg']:.0f}"))
            self.table.setItem(row, 4, QTableWidgetItem("Yes" if anomaly['VolumeAnomaly'] else "No"))
    
        self.status_label.setText(f"Anomalies detected for {ticker}: {len(anomalies)}")
        self.status_label.setStyleSheet("color: red; background-color: #1a1a1a; padding: 10px;")
        

    def create_menu(self):
        menu_bar = self.menuBar()

        help_action = QPushButton("Help", self)
        help_action.clicked.connect(self.show_help_section)

        about_action = QPushButton("About", self)
        about_action.clicked.connect(self.show_about_section)

        menu_layout = QHBoxLayout()
        menu_layout.addWidget(help_action)
        menu_layout.addWidget(about_action)

        self.layout.addLayout(menu_layout)

    def show_help_section(self):
        self.clear_main_content()
        
        help_text = """
        <b>Volume Anomaly Detector</b><br><br>
        This application detects unusual volume patterns in stock data.<br><br>
        It fetches live stock data and highlights instances of anomalous trading volumes.<br><br>
        <b>Steps:</b><br>
        1. Enter a stock ticker (e.g., AAPL) in the input field.<br>
        2. Adjust the slider. The default and optimal value is 2. This is a good value for both low and high volume stocks.<br>
        3. Click the 'Analyze' button to check for volume anomalies.<br>
        
        4. If anomalies are detected, a notification and alert will be shown.<br><br>
        
        <b>How the Data is Read:</b><br>
        The application fetches live stock data from Yahoo Finance for the ticker you enter. It retrieves the following key data points:<br>
        - <b>Volume</b>: The number of shares traded during a given time period.<br>
        - <b>Adjusted Close</b>: The stock's closing price, adjusted for events like dividends and stock splits.<br><br>
    
        <b>How the Data is Analyzed:</b><br>
        The analysis is focused on identifying volume anomalies — instances when the trading volume is significantly higher than the typical trading volume.<br>
        1. A <b>20-day rolling average</b> of the volume is calculated to represent the typical daily trading volume.<br>
        2. The current day's volume is compared to this average, and if it is more than the specified threshold (default is 2), the day is flagged as having an anomaly.<br><br>
    
        <b>Why This is Helpful:</b><br>
        Volume anomalies are often indicative of significant market events, such as:<br>
        - Big news announcements or market shifts.<br>
        - Possible market manipulation or insider trading.<br>
        - Institutional buying or selling.<br><br>
    
        By analyzing volume patterns, traders can quickly spot unusual trading activity, allowing them to make more informed decisions.<br><br>
    
        <b>Steps to Use the Application:</b><br>
        1. Enter a stock ticker in the input field (e.g., AAPL for Apple).<br>
        2. Click the 'Analyze' button to check for volume anomalies.<br>
        3. Review the detected anomalies in the table.<br>
        4. Adjust the threshold if necessary for more sensitive or less sensitive detection.<br><br>
        
        <b>Interpreting the Results:</b><br>
        - <b>Date</b>: The date when the volume anomaly occurred.<br>
        - <b>Adjusted Close</b>: The stock's adjusted closing price on that day.<br>
        - <b>Volume</b>: The total number of shares traded on that day.<br>
        - <b>Rolling Average</b>: The average volume for the previous 20 days.<br>
        - <b>Volume Anomaly</b>: Indicates whether the volume on that day was significantly higher than the rolling average.<br><br>
        """
    
        self.display_section(help_text)
    
    def display_section(self, text):
        label = QLabel(text, self)
        label.setAlignment(Qt.AlignTop)
        label.setWordWrap(True)
        label.setFont(QFont("Arial", 12))
        label.setStyleSheet("color: white; background-color: #1a1a1a; border-radius: 5px; padding: 10px;")
        label.setFixedWidth(800)
    
        # Enable links to be clickable
        label.setOpenExternalLinks(True)
    
        # Create a scroll area to make the content scrollable
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(label)
    
        # Add the scroll area to the layout
        self.layout.addWidget(scroll_area)
    
        # Add a back button to return to the main window
        back_button = QPushButton("Back to Main", self)
        back_button.clicked.connect(self.return_to_main)
        self.layout.addWidget(back_button)

    def show_about_section(self):
        self.clear_main_content()
        about_text = """
        <b>Volume Anomaly Detector</b><br><br>
        (c) 2024 Peter De Ceuster, SIG Labs<br>
        All Rights Reserved.<br>
        Version: 11.107<br><br>
        This software is designed to detect volume anomalies in stock market data.<br>
        It helps traders monitor unusual trading activity based on volume data.<br><br>
        <a href="https://buymeacoffee.com/siglabo" style="color: #3498db;">Buy me a coffee</a><br><br>
        <a href="https://peterdeceuster.uk/doc/code-terms" style="color: #3498db;">Code License</a>
        """
        self.display_section(about_text)

    def display_section(self, text):
        label = QLabel(text, self)
        label.setAlignment(Qt.AlignTop)
        label.setWordWrap(True)
        label.setFont(QFont("Arial", 12))
        label.setStyleSheet("color: white; background-color: #1a1a1a; border-radius: 5px; padding: 10px;")
        label.setFixedWidth(800)

        # Enable links to be clickable
        label.setOpenExternalLinks(True)

        scroll_area = QScrollArea(self)
        scroll_area.setWidget(label)
        scroll_area.setWidgetResizable(True)
        self.layout.addWidget(scroll_area)

        # Add back button to return to main window
        back_button = QPushButton("Back to Main", self)
        back_button.clicked.connect(self.return_to_main)
        self.layout.addWidget(back_button)

    def return_to_main(self):
        # Clear the current content and restore main window content
        self.clear_main_content()
        self.add_widgets()

    def clear_main_content(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget() and item.widget() != self.status_label:  # Don't delete status_label
                item.widget().deleteLater()
            elif item.layout():
                self.clearLayout(item.layout())
    
        self.create_menu()  # Re-add the menu
    
    def clearLayout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clearLayout(item.layout())

    def send_notification(self, title, anomalies):
        # Truncate or summarize the message if it's too long
        summary = f"{len(anomalies)} anomaly(s) detected."
        message = summary + "\n" + "See the app for details."
    
        notification.notify(
            title=title,
            message=message[:256],  # Ensure the message fits within the character limit
            timeout=10
        )

    def fetch_data_and_analyze(self, ticker):
        print(f"Fetching data for {ticker}...")
        data = fetch_live_stock_data(ticker)
        if data is None or data.empty:
            self.status_label.setText(f"Error: Unable to fetch data for {ticker}.")
            self.status_label.setStyleSheet("color: red; background-color: #1a1a1a; padding: 10px;")
            return
    
        # Pass the updated threshold value from the slider
        anomalies = detect_volume_anomalies(data, ticker, threshold=self.threshold)
    
        self.update_gui_with_anomalies(anomalies, ticker)
    
        if not anomalies.empty:
            anomaly_message = f"Volume anomalies detected for {ticker}:\n{anomalies.to_string()}"
            self.send_notification(f"Volume Anomaly Alert - {ticker}", anomaly_message)
            self.show_anomaly_dialog(anomalies)


 
    
 
    
    def show_anomaly_dialog(self, anomalies):
        # Create a custom dialog to display the anomalies
        dialog = QDialog(self)
        dialog.setWindowTitle("Volume Anomaly Detected")
        dialog.setWindowIcon(QIcon("logo.png"))
        
        # Maximize the dialog window when opened
        dialog.setWindowState(Qt.WindowMaximized)
        
        # Create a scrollable area for the text
        scroll_area = QScrollArea(dialog)
        scroll_area.setWidgetResizable(True)
        
        # Create a QTextEdit to display the anomaly details (with scroll)
        text_edit = QTextEdit(dialog)
        text_edit.setReadOnly(True)  # Make it read-only
        text_edit.setText(anomalies[['Adj Close', 'Volume', 'RollingAvg']].to_string())  # Set anomaly details
        text_edit.setAlignment(Qt.AlignLeft)  # Align text to the left
        scroll_area.setWidget(text_edit)
        
        # Create a layout and add the scroll area
        layout = QVBoxLayout(dialog)
        layout.addWidget(scroll_area)
        
        # Add a button to close the dialog
        close_button = QPushButton("Close", dialog)
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)
        
        # Set the layout for the dialog
        dialog.setLayout(layout)
        
        # Show the dialog
        dialog.exec_()
        
        
    def update_threshold(self):
        self.threshold = self.anomaly_threshold_slider.value()
        print(f"Updated threshold: {self.threshold}")  # Debug print statement
        self.threshold_label.setText(f"Threshold: {self.threshold}")
        
        
    def add_widgets(self):
        title = QLabel("Volume Anomaly Detector", self)
        title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title)
        
    # Add the slider to adjust the threshold
        self.anomaly_threshold_slider = QSlider(Qt.Horizontal, self)
        self.anomaly_threshold_slider.setMinimum(1)
        self.anomaly_threshold_slider.setMaximum(10)
        self.anomaly_threshold_slider.setValue(self.threshold)  # Default to 2
        self.anomaly_threshold_slider.valueChanged.connect(self.update_threshold)
        self.layout.addWidget(QLabel("Volume Anomaly Detection Threshold (x):"))
        self.layout.addWidget(self.anomaly_threshold_slider)
    
    # Label to display the current threshold value
        self.threshold_label = QLabel(f"Threshold: {self.threshold}", self)
        self.layout.addWidget(self.threshold_label)
        
        # Add ticker input field
        self.ticker_input = QLineEdit(self)
        self.ticker_input.setPlaceholderText("Enter stock ticker (e.g., AAPL)")
        self.layout.addWidget(self.ticker_input)
        
        # Add button to trigger analysis
        self.analyze_button = QPushButton("Analyze", self)
        self.analyze_button.clicked.connect(self.on_analyze_button_clicked)
        self.layout.addWidget(self.analyze_button)
        
        self.table = QTableWidget(self)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Date", "Adj Close", "Volume", "Rolling Avg", "Volume Anomaly"])
        self.layout.addWidget(self.table)
        
        # Re-add status_label if not already added
        if not hasattr(self, 'status_label') or self.status_label is None:
            self.status_label = QLabel(self)
            self.status_label.setAlignment(Qt.AlignCenter)
            self.status_label.setStyleSheet("color: white; background-color: #1a1a1a; padding: 10px;")
            self.layout.addWidget(self.status_label)
    
    def on_analyze_button_clicked(self):
            ticker = self.ticker_input.text().strip().upper()
            if ticker:
                self.save_last_ticker(ticker)
                self.fetch_data_and_analyze(ticker)
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("Please enter a valid stock ticker.")
                msg.setWindowTitle("Invalid Input")
                msg.exec_()

 

    def load_last_ticker(self):
        """Load the last ticker input when the app starts."""
        if os.path.exists("last_ticker.txt"):
            with open("last_ticker.txt", "r") as file:
                last_ticker = file.read().strip()
                self.ticker_input.setText(last_ticker)

    def save_last_ticker(self, ticker):
        """Save the last ticker to a text file."""
        with open("last_ticker.txt", "w") as file:
            file.write(ticker)

    def closeEvent(self, event):
        """Save the final ticker before the window is closed."""
        self.save_last_ticker(self.ticker_input.text().strip())
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VolumeAnomalyDetector()
    window.showMaximized()  # Start the window maximized
    sys.exit(app.exec_())    
 
  