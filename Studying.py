import random
import time
import sys
import os

# --- Cross-platform timed input ---
def timed_input(prompt: str, timeout: int):
    """
    Returns (user_text, timed_out: bool).
    On macOS/Linux: uses signal alarm.
    On Windows: uses a background thread (can't cancel the prompt; see note).
    """
    if os.name == "posix":
        # macOS/Linux
        import signal

        class Timeout(Exception):
            pass

        def handler(signum, frame):
            raise Timeout()

        old = signal.signal(signal.SIGALRM, handler)
        try:
            signal.alarm(timeout)
            try:
                s = input(prompt)
                signal.alarm(0)  # cancel alarm
                return s, False
            except Timeout:
                print("\n⏰ Time’s up!")
                return "", True
        finally:
            signal.signal(signal.SIGALRM, old)
    else:
        # Windows fallback: non-interruptible input in another thread.
        # If time runs out, we ignore whatever is typed later.
        import threading
        result = {"text": None}
        done = threading.Event()

        def reader():
            try:
                result["text"] = input(prompt)
            except EOFError:
                result["text"] = ""
            finally:
                done.set()

        t = threading.Thread(target=reader, daemon=True)
        t.start()
        finished = done.wait(timeout)
        if finished:
            return result["text"], False
        else:
            print("\n⏰ Time’s up! (If you see a stray prompt, press Enter to clear it.)")
            return "", True

# --- Quiz settings ---
NUM_QUESTIONS = 10
MIN_VAL, MAX_VAL = 1, 30
PER_QUESTION_LIMIT = 10  # seconds

def main():
    print("🧮 Multiplication Quiz (1–30) with Timers")
    print(f"You have {PER_QUESTION_LIMIT} seconds per question. There are {NUM_QUESTIONS} questions.\n")

    score = 0
    total_time = 0.0

    for i in range(1, NUM_QUESTIONS + 1):
        a = random.randint(MIN_VAL, MAX_VAL)
        b = random.randint(MIN_VAL, MAX_VAL)
        correct = a * b

        print(f"Q{i}: What is {a} × {b}?")
        start = time.perf_counter()
        text, timed_out = timed_input("Your answer → ", PER_QUESTION_LIMIT)
        end = time.perf_counter()

        # time taken for this question (cap at limit if timed out)
        elapsed = end - start
        if timed_out:
            elapsed = PER_QUESTION_LIMIT

        total_time += elapsed

        if timed_out:
            print(f"❌ Time up! Correct answer: {correct}  |  Time: {elapsed:.1f}s\n")
            continue

        # parse answer
        try:
            ans = int(text.strip())
        except ValueError:
            print(f"❌ Invalid input. Correct answer: {correct}  |  Time: {elapsed:.1f}s\n")
            continue

        if ans == correct:
            score += 1
            print(f"✅ Correct!  |  Time: {elapsed:.1f}s\n")
        else:
            print(f"❌ Wrong. Correct: {correct}  |  Time: {elapsed:.1f}s\n")

    avg_time = total_time / NUM_QUESTIONS
    print("🎉 Quiz Over!")
    print(f"Score: {score}/{NUM_QUESTIONS}")
    print(f"Total time: {total_time:.1f}s  |  Average per question: {avg_time:.1f}s")

if __name__ == "__main__":
    # Tip for macOS/Homebrew Python: prefer the python.org installer if Tk/signal issues arise.
    main()
