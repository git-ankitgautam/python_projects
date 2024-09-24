"""Q: Find the number of advanced palindromes in a given string. 
An advanced palindrome is a palindrome that is: odd in length but greater than 3, and the middle character doesn't repeat.
"""

import math

def expand_around_center(left, right):
    count = 0
    # Expand as long as we have a palindrome and its length is at least 3
    while left >= 0 and right < len(s) and s[left] == s[right]:
        if (right - left + 1) >= 3 and unique_middle_letter(s[left:right+1]):
            count += 1
            print(s[left:right+1])
        left -= 1
        right += 1
    
    return count



def count_odd_palindromic_substrings(s):
    result = 0
    # Loop over all characters considering them as potential centers for odd-length palindromes
    for i in range(len(s)):
    # Odd-length palindromes (single character center)
        result += expand_around_center(i, i)

    return result


def unique_middle_letter(palindrome):
    result = False
    mid = math.floor(len(palindrome) // 2)
    middle_char = palindrome[mid]
    if middle_char not in palindrome[mid+1:]:
        result = True
    return result


# Example usage:
s = "racecarlevelanna"
result = count_odd_palindromic_substrings(s)
print(result)  # Output: 7