
import math
import time
limit = int(input("enter the limit: "))
start = time.time()




"""prime_numbers = []
for i in range(2, limit):
    flag = 0
    for j in range(2, int(i/2)+1):
        if i % j == 0:
            flag = 1
            break
    if flag == 0:
        print(i)
"""


# sieve of eratosthenes
prime_numbers = [1] * (limit+1)
prime_numbers[0] = prime_numbers[1] = 0
for i in range(2, int(math.sqrt(limit))+1):
    if prime_numbers[i]:
        for j in range (i*i , limit+1, i):
            prime_numbers[j] = 0

for x in range(2, limit):
    if prime_numbers[x] == 1:
        print(x)




















































end = time.time()
print(end - start)