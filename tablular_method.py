binarynumbers = {
   0:"00000",
   1:"00001",
   2:"00010",
   3:"00011",
   4:"00100",
   5:"00101",
   6:"00110",
   7:"00111",
   8:"01000",
   9:"01001",
   10:"01010",
   11:"01011",
   12:"01100",
   13:"01101",
   14:"01110",
   15:"01111",
   16:"10000",
   17:"10001",
   18:"10010",
   19:"10011",
   20:"10100",
   21:"10101",
   22:"10110",
   23:"10111",
   24:"11000",
   25:"11001",
   26:"11010",
   27:"11011",
   28:"11100",
   29:"11101",
   30:"11110",
   31:"11111"
}

group0 = {}
group1 = {}
group2 = {}
group3 = {}
group4 = {}
group5 = {}

print("Enter the index of the minterms, seperated by commas")
input_numbers = [int(v) for v in input().split(",")]
for x in range(len(input_numbers)):
   count = 0
   for y in range(0,5):
      if(binarynumbers[input_numbers[x]][y] == "1"):
            count +=1
      if(count == 0):
         change = {"m{}".format(input_numbers[x]) : binarynumbers[input_numbers[x]]}
         group0.update(change)
      elif(count == 1):
         change = {"m{}".format(input_numbers[x]) : binarynumbers[input_numbers[x]]}
         group1.update(change)
      elif(count == 2):
         change = {"m{}".format(input_numbers[x]) : binarynumbers[input_numbers[x]]}
         group2.update(change)
      elif(count == 3):
         change = {"m{}".format(input_numbers[x]) : binarynumbers[input_numbers[x]]}
         group3.update(change)
      elif(count == 4):
         change = {"m{}".format(input_numbers[x]) : binarynumbers[input_numbers[x]]}
         group4.update(change)
      else:
         change = {"m{}".format(input_numbers[x]) : binarynumbers[input_numbers[x]]}
         group5.update(change)

print("group0 =",group0)
print("group1 =",group1)
print("group2 =",group2)
print("group3 =",group3)
print("group4 =",group4)
print("group5 =",group5)







