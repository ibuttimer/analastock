"""
Main entry point for application
"""
from utils import get_input


loop: bool = True

print('Hello, world!')

while loop:
    data = get_input("Enter something")
    loop = data.lower() != 'quit'
    if loop:
        print("Entered: " + data)
