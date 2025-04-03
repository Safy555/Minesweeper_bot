class Cell:
    
    
    def __init__(self, x, y, value):
        self.x = x
        self.y = y
        self.value =  value
    
    
    def __repr__(self):
        return f"Cell(x={self.x}, y={self.y}, value={self.value})"