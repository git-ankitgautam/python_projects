import random
import os
import time


def display(current_state_of_word):
    os.system('cls')
    print("   ")
    for x in range(len(current_state_of_word)):
        print(f"{current_state_of_word[x]} ", end="")

    print("\n incorrect letters: ",end="")
    for x in range(len(incorrect_guesses_list)):
        print(f"{incorrect_guesses_list[x]}, ", end="")
    print("\n")
    guessed_letter = str(input("Please enter a letter:")).lower()
    result_of_guess = check_guess(selected_word, guessed_letter, current_state_of_word)
    print(result_of_guess)
    time.sleep(1)

def check_guess(selected_word, guessed_letter, current_state_of_word):
    if guessed_letter.isalpha() == False or len(guessed_letter) > 1:
        return "invalid input"
    
    elif guessed_letter not in selected_word:
        incorrect_guesses_list.append(guessed_letter)
        return "incorrect!"
    
    elif guessed_letter in correct_guesses_list or guessed_letter in incorrect_guesses_list:
        return "already guessed!"
    
    else:
        all_occurances_of_guessed_letter = [i for i, letter in enumerate(selected_word) if letter == guessed_letter]
        correct_guesses_list.append(guessed_letter)
        for x in all_occurances_of_guessed_letter:
            current_state_of_word[x] = selected_word[x]
        return "Correct!"


with open('hangman_wordlist.txt', 'r') as words_file:
    words = words_file.readlines()
    words = [word.strip("\n") for word in words]

words_file.close()

selected_word = list(random.choice(words).lower())
time.sleep(2)
incorrect_guesses_list = []
correct_guesses_list = []
current_state_of_word = ["_"] * len(selected_word)
incorrect_guesses_limit = len(selected_word)
while len(incorrect_guesses_list) <= incorrect_guesses_limit and current_state_of_word != selected_word:
    if len(incorrect_guesses_list) == incorrect_guesses_limit:
        print("Careful, this is your final chance!")
        time.sleep(2)
        display(current_state_of_word)
    else:
        display(current_state_of_word)

if selected_word == current_state_of_word:
    print("You Win!")

elif len(incorrect_guesses_list) == len(selected_word)+1:
    print("oof, ran out of guesses")