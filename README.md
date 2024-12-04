# Volume Anomaly Detector

 


Volume Anomaly Detector
 Version 11.107
Developed by Sig Labs - Peter De Ceuster

Volume Anomaly Detector is a Python-based desktop application built with PyQt5 that helps users detect unusual trading volume patterns in stock data. The tool fetches live stock data, analyzes it for abnormal trading volumes, and provides an interface for users to view and interpret these anomalies.

This can be especially helpful for traders who want to quickly identify unusual trading activity, such as market-moving news, institutional trades, or potential market manipulation.

Features
Fetches live stock data from Yahoo Finance.
Detects anomalies in trading volume by comparing it with a rolling average.
Allows customization of the volume anomaly detection threshold through the Threshold slider.
Displays detected anomalies in a user-friendly table.
Provides notifications when anomalies are detected.
 



How It Works
The application works by fetching stock data for a given ticker from Yahoo Finance. It then calculates a rolling average of the trading volume and compares the current day's volume against this average. If the current volume is significantly higher than the average (by a defined threshold), the day is marked as an anomaly.

Anomaly Detection
The volume anomaly detection works as follows:

Rolling Average: The application calculates a 20-day rolling average of the stock's volume.
Threshold: The current day's volume is compared with the rolling average. If it exceeds the rolling average by a set threshold (default: 2x), the day is flagged as an anomaly.
Notification: The user is notified when volume anomalies are detected.
Why Volume Anomalies Matter
Volume anomalies often indicate significant market events, such as:

News Announcements: Major company or market news can cause abnormal trading volumes.
Market Shifts: A sudden change in trading activity can signal a change in market sentiment or trends.
Potential Manipulation: Unusual volume spikes can sometimes indicate market manipulation, insider trading, or large institutional trades.

User Interface
Ticker Input: Enter the stock ticker (e.g., AAPL) for the stock you want to analyze.
Analyze Button: Click the "Analyze" button to check for volume anomalies.
Results Table: The results are displayed in a table showing the date, adjusted closing price, volume, rolling average, and whether the volume on that day was anomalous.
Help Section: A help section is available to guide users on how the tool works and how to interpret the results.

How to Use
Launch the application: Run the program with python main.py.
Enter a stock ticker: Type a stock ticker (e.g., AAPL) into the input field.
Click "Analyze": The application will fetch the data and check for volume anomalies.
View Results: Detected anomalies are displayed in a table.
Adjust Threshold: Modify the threshold for anomaly detection to increase or decrease sensitivity.
Adjust the slider. 2 is optimal in most situations.

Example
Ticker: AAPL (Apple Inc.)
Threshold: 2x (default)
Results: The tool will display dates when the volume of AAPL trading exceeded twice the 20-day rolling average, signaling a potential market-moving event.




If you enjoy this program, buy me a coffee https://buymeacoffee.com/siglabo
You can use it free of charge or build upon my code. 
 
(c) Peter De Ceuster 2024
Software Distribution Notice: https://peterdeceuster.uk/doc/code-terms 
This software is released under the FPA General Code License.
 
