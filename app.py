import pyttsx3
import speech_recognition as sr
import webbrowser
import datetime
import pywhatkit
import cv2
from deepface import DeepFace
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 170)
engine.setProperty('volume', 1)

# Initialize Groq AI Chat Model
chat_model = ChatGroq(model_name="llama3-8b-8192",
                      groq_api_key="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")  # Replace with your actual API key

# Load face detection model
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def speak(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

def listen():
    """Listen to user's voice and recognize speech."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio).lower()
        print(f"User: {command}")
        return command
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand.")
        return ""
    except sr.RequestError:
        print("Network issue.")
        return ""

def detect_face_mood():
    """Detect mood using facial expressions and respond empathetically."""
    speak("Opening camera to analyze your mood...")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        speak("Error: Camera not found!")
        return "neutral"

    detected_mood = "neutral"
    detection_count = 0  # Count how many times mood is detected

    while detection_count < 3:  # Limit detections to 3 times
        ret, frame = cap.read()
        if not ret:
            speak("Error: Could not capture your face!")
            break

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            face_roi = frame[y:y + h, x:x + w]
            result = DeepFace.analyze(face_roi, actions=['emotion'], enforce_detection=False)

            if len(result) > 0:
                detected_mood = result[0]['dominant_emotion']
                detection_count += 1  # Increase count after detection
                print(f"Detected Mood: {detected_mood}")

            # Draw a rectangle around the face
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, detected_mood, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        cv2.imshow("Mood Detection", frame)

        # Exit loop early if mood detected once
        if detection_count >= 1:
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit manually
            break

    cap.release()
    cv2.destroyAllWindows()

    # Speak the empathetic response
    mood_response = get_empathetic_response(detected_mood)
    speak(mood_response)

    return detected_mood

def get_empathetic_response(mood):
    """Generate an empathetic response based on the detected mood."""
    responses = {
        "You are JARVIS, a compassionate AI mental health companion. "
        "Your goal is to provide warm, supportive, and personalized responses "
        "based on the user's emotional state, current situation, and needs. "
        "Your responses should be empathetic, encouraging, and helpful, while remaining concise.\n\n"

        f"The user is currently feeling {mood}. Adjust your response accordingly to provide comfort, reassurance, or motivation. "
        "If the user is distressed, acknowledge their emotions with kindness and suggest simple actions to help them feel better. "

        "Use a conversational and friendly tone, making the user feel understood and valued. "
        "If appropriate, offer self-care suggestions such as deep breathing, music recommendations, or a positive affirmation.\n\n"

        "Now, respond to the user's message below with care and empathy:\n"
        f"User: {query}\n"
        "JARVIS:"
        "happy": "I can see you're happy! That’s wonderful. Keep smiling and enjoy your day!",
        "sad": "I see you're feeling sad. I'm here for you. Do you want to talk about it, or maybe listen to some uplifting music?",
        "angry": "You seem to be a bit upset. Take a deep breath, and let’s do something relaxing together.",
        "surprise": "You look surprised! Did something unexpected happen? Tell me more!",
        "fear": "You seem scared. Don't worry, everything will be okay. Would you like some calming music?",
        "disgust": "You look uncomfortable. Maybe a change of scenery or a fun video can help.",
        "neutral": "You seem neutral. Just another normal day, huh? Let me know if I can make it better!"
        "Strictly you have to speak 3-4 lines"
    }
    return responses.get(mood, "I'm not sure how you're feeling, but I'm here for you!")

def chat_with_groq(query, mood):
    """Chat with Groq AI using an empathetic prompt."""
    try:
        empathetic_prompt = (
            "You are an empathetic AI chatbot and mental health companion. "
            "Your responses should be warm, caring, and supportive. "
            f"The user is feeling {mood}. Adjust your response accordingly."
        )
        full_prompt = f"{empathetic_prompt}\nUser: {query}\nAI:"
        response = chat_model.invoke([HumanMessage(content=full_prompt)])
        return response.content
    except Exception as e:
        return "Sorry, I couldn't connect to Groq. Error: " + str(e)

def take_command(command):
    """Process the user's command and respond accordingly."""
    if "hello" in command or "hey" in command:
        speak("Hello! How can I assist you today?")

    elif "detect my mood" in command:
        mood = detect_face_mood()

    elif "open google" in command:
        webbrowser.open("https://google.com")
        speak("Opening Google.")

    elif "search" in command:
        search_query = command.replace("search", "").strip()
        webbrowser.open(f"https://www.google.com/search?q={search_query}")
        speak(f"Searching Google for {search_query}")

    elif "time" in command:
        time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The current time is {time}")

    elif "date" in command:
        date = datetime.datetime.now().strftime("%B %d, %Y")
        speak(f"Today's date is {date}")

    elif "play a song" in command:
        speak("Playing a song that matches your mood.")
        pywhatkit.playonyt("happy mood songs playlist")

    elif "shutdown" in command:
        speak("Shutting down. Have a great day!")
        exit()

    else:
        mood = "neutral"  # Default mood if not detected
        response = chat_with_groq(command, mood)
        speak(response)

# Start JARVIS
speak("JARVIS Activated. How can I help you?")
while True:
    command = listen()
    if command:
        take_command(command)
