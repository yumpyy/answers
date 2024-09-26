"""
Questions:
1. An instance of the Rectangle class requires length:int and width:int to be initialized.
2. We can iterate over an instance of the Rectangle class 
3. When an instance of the Rectangle class is iterated over, we first get its length in the format: {'length': <VALUE_OF_LENGTH>} followed by the width {width: <VALUE_OF_WIDTH>}
"""

class Rectangle:
    def __init__(self, length: int, width: int):
        self.length = length
        self.width = width

    def __iter__(self): 
        """
        i used generators for creating an interator
        """
        yield {'length': self.length}
        yield {'width': self.width}

rect = Rectangle(1, 2)  # rect instance of Rectangle class initialized with the values 1, 2
for dimensions in rect:
    print(dimensions)
