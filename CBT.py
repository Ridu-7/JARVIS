def mental_health_coaching(mood):
    """Provides CBT techniques based on mood."""
    cbt_techniques = {
        "sad": "Try writing down three things you're grateful for. It helps shift your focus.",
        "angry": "Take a few deep breaths. Inhale for 4 seconds, hold for 4, and exhale for 6.",
        "anxious": "Try the 5-4-3-2-1 technique: Name 5 things you see, 4 you feel, 3 you hear, 2 you smell, and 1 you taste.",
        "neutral": "How about some mindfulness? Try focusing on your breath for 1 minute."
    }
    speak(cbt_techniques.get(mood, "Let's do a quick mindfulness exercise together."))
