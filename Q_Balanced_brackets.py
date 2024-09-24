"""Q: a string containing only brackets '{[()]}' is given. We need to check if: the number of opening brackets is equal to closing brackets and the order of opening and closing brackets is correct. Return True if the string is valid, False otherwise."""


def check_balanced_brackets(s):
    stack = []
    opening_brackets = ['{', '[', '(']
    closing_brackets = ['}', ']', ')']
    result = True
    for i in s:
        if i in opening_brackets:
            stack.append(i)
        elif i in closing_brackets and len(stack) > 0:
            index_of_closing_bracket_found = closing_brackets.index(i)
            if stack.pop() == opening_brackets[index_of_closing_bracket_found]:
                continue
            else:
                result = False
                return result
    return result



s = '{[()]}'
print(check_balanced_brackets(s))