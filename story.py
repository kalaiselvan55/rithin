import random

print("✨ Welcome to the Funny Story Generator ✨")

# Word banks
names = ["Alex", "Taylor", "Jordan", "Sam", "Riley"]
places = ["school", "zoo", "park", "beach", "museum"]
animals = ["monkey", "penguin", "elephant", "dog", "cat"]
actions = ["danced with", "ran away from", "sang to", "played soccer with", "told jokes to"]

# Randomly pick words
name = random.choice(names)
place = random.choice(places)
animal = random.choice(animals)
action = random.choice(actions)

# Create the story
print(f"One day, {name} went to the {place}.")
print(f"There, {name} {action} a {animal}.")
print("It was the funniest day ever! 😂")
