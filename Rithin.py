import random

print("🎮 Let's play Rock, Paper, Scissors!")
print("Type your choice: rock, paper, or scissors")

choices = ["rock", "paper", "scissors"]

# Player's choice
player_choice = input("Your choice → ").lower()

# Computer's choice
computer_choice = random.choice(choices)
print("Computer chose:", computer_choice)

# Decide the winner
if player_choice == computer_choice:
    print("🤝 It's a tie!")
elif (player_choice == "rock" and computer_choice == "scissors") \
     or (player_choice == "paper" and computer_choice == "rock") \
     or (player_choice == "scissors" and computer_choice == "paper"):
    print("🎉 You win!")
else:
    print("😅 You lose!")
