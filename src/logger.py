class Logger:
    def __init__(self, name):
        # Pass in the class name from the initialization
        self.name = name

    def log(self, data):
        # Format and print data to console
        print(f"[{self.name}] {str(data).rstrip()}\n")
