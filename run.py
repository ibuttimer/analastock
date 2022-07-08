# Your code goes here.
# You can delete these comments, but do not change the name of this file
# Write your code to expect a terminal of 80 characters wide and 24 rows high

loop = True

print('Hello, world!')

while loop:
    data = input("Enter something: ")
    loop = data.lower() != 'quit'
    if loop:
        print("Entered: " + data)
