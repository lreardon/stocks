class TOHLCV:
    def __init__(self, timestamp, open_price, high_price, low_price, close_price, volume):
        self.timestamp = timestamp
        self.open_price = open_price
        self.high_price = high_price
        self.low_price = low_price
        self.close_price = close_price
        self.volume = volume

    def __str__(self):
        return f"Timestamp: {self.timestamp}, Open: {self.open_price}, " \
               f"High: {self.high_price}, Low: {self.low_price}, " \
               f"Close: {self.close_price}, Volume: {self.volume}"