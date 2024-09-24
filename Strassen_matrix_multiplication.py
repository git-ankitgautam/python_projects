"""
def mm():
    return 0




n = input()
"""

n = int(input("Enter the size of the matrix: "))
matrix = []

# Taking input for the matrix in a single line
print("Enter the matrix elements (separated by space):")
for _ in range(n):
    row = list(map(int, input().split()))
    matrix.append(row)
    matrix.append(column)

# Printing the matrix
print("Matrix:")
for row in matrix:
    print(row)