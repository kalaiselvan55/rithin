import random
import time

# ---------------- Settings ----------------
NUM_WORDS = 30              # words in the prompt
COUNTDOWN_SEC = 3           # 3-2-1 countdown before timing
# ------------------------------------------

# A small common-words bank (feel free to add more!)
WORD_BANK = """
the of and to in is you that it he was for on are as with his they I at be this
have from or one had by word but not what all were we when your can said there
use an each which she do how their if will up other about out many then them
these so some her would make like him into time has look two more write go see
number no way could people my than first water been call who oil its now find
long down day did get come made may part keep small large next while great early
light sound above below quick brown fox jumps over lazy dog happy bright green
blue red yellow purple orange build learn code game school family friend
""".split()

def make_prompt(n=NUM_WORDS):
    return " ".join(random.choice(WORD_BANK) for _ in range(n))

def levenshtein(a: str, b: str) -> int:
    """Edit distance (insert/delete/substitute) between strings a and b."""
    m, n = len(a), len(b)
    if m < n:
        a, b, m, n = b, a, n, m
    # now m >= n
    prev = list(range(n + 1))
    for i in range(1, m + 1):
        cur = [i] + [0] * n
        ai = a[i - 1]
        for j in range(1, n + 1):
            cost = 0 if ai == b[j - 1] else 1
            cur[j] = min(prev[j] + 1,      # deletion
                         cur[j - 1] + 1,   # insertion
                         prev[j - 1] + cost)  # substitution
        prev = cur
    return prev[-1]

def first_mismatch(a: str, b: str):
    """Return index of first differing character, or None if identical prefix."""
    for i, (ca, cb) in enumerate(zip(a, b)):
        if ca != cb:
            return i
    return None if len(a) == len(b) else min(len(a), len(b))

def run_test():
    print("⌨️  Typing Test — type the text as fast and accurately as you can.")
    prompt = make_prompt()
    print("\n--- PROMPT ---")
    print(prompt)
    print("--------------")
    input("\nPress Enter to start the countdown...")

    # 3-2-1 countdown
    for t in range(COUNTDOWN_SEC, 0, -1):
        print(f"{t}...", end="", flush=True)
        time.sleep(1)
    print(" Go!\n")

    # Time the user's typing
    start = time.perf_counter()
    typed = input("> ")
    end = time.perf_counter()
    elapsed = max(0.000001, end - start)  # avoid division by zero

    # Metrics
    chars_typed = len(typed)
    minutes = elapsed / 60.0
    gross_wpm = (chars_typed / 5.0) / minutes

    # Errors via edit distance
    errors = levenshtein(typed, prompt)
    correct_chars = max(chars_typed - errors, 0)
    accuracy = (correct_chars / chars_typed * 100.0) if chars_typed > 0 else 0.0
    net_wpm = ((correct_chars / 5.0) / minutes) if minutes > 0 else 0.0

    # Report
    print("\n📊 Results")
    print(f"Time: {elapsed:.2f}s")
    print(f"Gross WPM: {gross_wpm:.2f}")
    print(f"Net WPM:   {net_wpm:.2f}")
    print(f"Accuracy:  {accuracy:.1f}%")
    print(f"Errors:    {errors} (edit distance)")
    mm = first_mismatch(typed, prompt)
    if mm is not None:
        # Show a quick pointer to the first difference (trim around it)
        start_idx = max(0, mm - 20)
        end_idx = min(len(prompt), mm + 20)
        seg = prompt[start_idx:end_idx]
        caret_pos = mm - start_idx
        print("\nFirst difference near here in the prompt:")
        print(seg)
        print(" " * caret_pos + "^")

if __name__ == "__main__":
    while True:
        run_test()
        again = input("\nRun again? (y/n): ").strip().lower()
        if again != "y":
            break

