import datetime

def get_journal_prompt(mood):
    """Generate a reflective journal prompt based on mood."""
    prompts = {
        "happy": "What made you smile today?",
        "sad": "What’s one small thing that made you feel a bit better?",
        "angry": "What triggered your anger today, and how did you handle it?",
        "neutral": "What’s one highlight of your day?"
    }
    return prompts.get(mood, "How was your day?")

def write_journal_entry(mood):
    """Writes a journal entry based on user's mood."""
    prompt = get_journal_prompt(mood)
    speak(prompt)
    journal_entry = listen()

    with open("journal.txt", "a") as file:
        file.write(f"{datetime.datetime.now()}\nMood: {mood}\n{journal_entry}\n\n")
    
    speak("Your journal entry has been saved.")
