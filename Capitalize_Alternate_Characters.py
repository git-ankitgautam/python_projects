def capitalize_alternate_characters(s):
  new_string = ""
  for i, char in enumerate(s):
    if i % 2 == 1:
      new_string += char.upper()
    else:
      new_string += char
  return new_string

# Example usage
string = str(input()).lower()
altered_string = capitalize_alternate_characters(string)
print(altered_string)  # Output: HeLlO WoRlD