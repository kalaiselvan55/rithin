import random

print("🎉 Welcome to the Number Guessing Game! 🎉")
print("I'm thinking of a number between 1 and 20.")

# Computer picks a random number
secret_number = random.randint(1, 20)

# Ask the player to guess up to 5 times
for attempt in range(1, 6):
    guess = int(input(f"Attempt {attempt}: Enter your guess → "))

    if guess < secret_number:
        print("Too low! Try again.")
    elif guess > secret_number:
        print("Too high! Try again.")
    else:
        print(f"🎉 Great job! You guessed it in {attempt} tries!")
        break
else:
    print(f"😅 Sorry! The number was {secret_number}. Better luck next time!")
