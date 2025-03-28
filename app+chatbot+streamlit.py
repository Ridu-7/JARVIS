import streamlit as st
import streamlit as st
import os
import base64
from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
import streamlit as st
import datetime
import webbrowser
import smtplib
import pywhatkit
import pyttsx3
import speech_recognition as sr
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
import threading

def speak(text):
    """Converts text to speech and speaks it in a separate thread."""
    def run_speech():
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.say(text)
# Initialize Text-to-Speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)

def listen():
    """Listens to the user's voice command and returns it as text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio).lower()
        st.write(f"User: {command}")
        return command
    except sr.UnknownValueError:
        st.write("Sorry, I couldn't understand.")
        return ""
    except sr.RequestError:
        st.write("Network issue.")
        return ""

def chat_with_groq(query):
    """Sends the user's query to Groq AI and returns the response."""
    try:
        empathetic_prompt = (
            "You are an empathetic AI chatbot who is a mental health companion and a general AI assistant. "
            "Make your responses supportive, compassionate, and concise. "
            "If the user expresses distress, respond in a comforting manner. "
            "Keep your responses brief but meaningful."
        )
        full_prompt = f"{empathetic_prompt}\nUser: {query}\nAI:"
        chat_model = ChatGroq(groq_api_key="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", model_name="llama3-8b-8192")
        response = chat_model.invoke([HumanMessage(content=full_prompt)])
        return response.content
    except Exception as e:
        return "Sorry, I couldn't connect to Groq. Error: " + str(e)

def take_command(command):
    """Processes voice commands and performs actions accordingly."""
    if "hello" in command or "hey" in command:
        speak("Hello, how can I assist you?")
    elif "open google" in command:
        webbrowser.open("https://google.com")
        speak("Opening Google")
    elif "open youtube" in command:
        webbrowser.open("https://youtube.com")
        speak("Opening YouTube")
    elif "search" in command:
        search_query = command.replace("search", "").strip()
        webbrowser.open(f"https://www.google.com/search?q={search_query}")
        speak(f"Searching Google for {search_query}")
    elif "time" in command:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The current time is {current_time}")
    elif "date" in command:
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        speak(f"Today's date is {current_date}")
    elif "play" in command:
        song = command.replace("play", "").strip()
        pywhatkit.playonyt(song)
        speak(f"Playing {song} on YouTube")
    elif "shutdown" in command:
        speak("Shutting down. Have a great day!")
        exit()
    else:
        response = chat_with_groq(command)
        speak(response)

def send_email(to, message):
    """Sends an email to the specified recipient."""
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login("your_email@gmail.com", "your_password")
        server.sendmail("your_email@gmail.com", to, message)
        server.close()
        speak("Email sent successfully.")
    except Exception as e:
        speak(f"Failed to send email. Error: {str(e)}")



def journaling_entry():
    st.header("Journaling Entry")
    st.text_area("Write your thoughts here:")
import base64

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def talk_with_ai():
    image_path = "giphy.gif"  # Make sure this file is in the same folder
    encoded_image = get_base64_image(image_path)
    
    st.markdown(
        f"""
        <style>
            .talk-ai {{
                background-image: url("data:image/gif;base64,{encoded_image}");
                background-size: cover;
                background-position: center;
                color: #00FFFF;
                padding: 20px;
                border-radius: 10px;
                height: 80vh;
                display: flex;
                align-items: center;
                justify-content: center;
                text-align: center;
            }}
            body {{
                background-color: black;
                color: #00FFFF;
            }}
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown('<div class="talk-ai"><h1>Talk with AI</h1><p>Welcome to the AI chat section. How can I assist you today?</p></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    if "is_listening" not in st.session_state:
        st.session_state.is_listening = False

    with col1:
        if st.button("Start Speaking with AI"):
            st.session_state.is_listening = True
    
    if st.session_state.is_listening:
        command = listen()
        if command:
            take_command(command)
            st.session_state.is_listening = False

    with col2:
        if st.button("Chat with AI"):
            st.session_state.show_chat = True
    if "show_chat" in st.session_state and st.session_state.show_chat:
        chat_interface()

def chat_interface():
    """
    Handles the AI chat interaction using the Groq API.
    """
    groq_api_key = "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"

    # Sidebar customization options
    st.sidebar.title("Customization")
    system_prompt = st.sidebar.text_input("System prompt:", value="You are a helpful AI assistant.if they express respond in comforting manner and keep responses brief.if needed ask more questions.if needed mention helpline number in crisis situation and inform nearby police loaction ")  
    model = st.sidebar.selectbox(
        "Choose a model",
        ["llama3-8b-8192", "mixtral-8x7b-32768", "gemma-7b-it"]
    )
    conversational_memory_length = st.sidebar.slider("Conversational memory length:", 1, 10, value=5)

    # Initialize memory for chat history
    memory = ConversationBufferWindowMemory(k=conversational_memory_length, memory_key="chat_history", return_messages=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Load previous chat history
    for message in st.session_state.chat_history:
        memory.save_context({"input": message["human"]}, {"output": message["AI"]})

    # Initialize Groq chat model
    groq_chat = ChatGroq(
        groq_api_key=groq_api_key,
        model_name=model
    )

    # User input field
    user_question = st.text_input("Ask a question:")

    if user_question:
        # Create a chat prompt template
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{human_input}")
        ])

        # Create conversation chain
        conversation = LLMChain(
            llm=groq_chat,
            prompt=prompt,
            verbose=True,
            memory=memory
        )

        # Generate AI response
        response = conversation.predict(human_input=user_question)

        # Save conversation history
        message = {"human": user_question, "AI": response}
        st.session_state.chat_history.append(message)

    # Display conversation history
    st.subheader("Conversation History")
    for chat in st.session_state.chat_history:
        st.write(f"**You:** {chat['human']}")
        st.write(f"**AI:** {chat['AI']}")


   
def cbt_suggestions():
    st.header("CBT Suggestions & Protocols")
    st.write("Here are some Cognitive Behavioral Therapy (CBT) techniques and suggestions.")

# Streamlit App Layout
st.set_page_config(page_title="Mental Wellness App", page_icon="🧘", layout="wide")

st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to:", ["Journaling Entry", "Talk with AI", "CBT Suggestions/Protocols"])

st.markdown(
    """
    <style>
        .stApp {
            background-color: black;
            color: #00FFFF;
        }
    </style>
    """,
    unsafe_allow_html=True
)

if selection == "Journaling Entry":
    journaling_entry()
elif selection == "Talk with AI":
    talk_with_ai()
elif selection == "CBT Suggestions/Protocols":
    cbt_suggestions()
