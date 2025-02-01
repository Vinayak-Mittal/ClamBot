import streamlit as st
import json
from datetime import datetime
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    st.error("Please set GOOGLE_API_KEY in .env file")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)

# Initialize the chat model
model = genai.GenerativeModel("gemini-pro")

# Page configuration with custom theme and background
st.set_page_config(
    page_title="Mindful Companion - Mental Health Chatbot",
    page_icon="🌸",
    layout="wide"
)

# Custom CSS for interactive background and styling
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(45deg, #ff9a9e 0%, #fad0c4 99%, #fad0c4 100%);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.9);
    }
    .css-1d391kg {
        background-color: rgba(255, 255, 255, 0.85);
        border-radius: 15px;
        padding: 20px;
        backdrop-filter: blur(5px);
    }
    </style>
    """, unsafe_allow_html=True)

class MentalHealthChatbot:
    def __init__(self):
        self.history_file = "chat_history.json"
        self.system_prompt = """You are a compassionate mental health support chatbot that communicates in Hinglish 
        (mix of Hindi and English). You should:
        1. Always use emojis appropriately to make responses more engaging
        2. Show deep empathy and understanding in responses
        3. Provide practical mental health tips and exercises when relevant
        4. Share motivational thoughts that blend Hindi and English naturally
        5. Suggest breathing exercises or meditation techniques when someone seems stressed
        6. Keep responses warm and personal while maintaining professionalism
        7. Use both Devanagari and Roman scripts in responses
        Remember to keep responses concise but meaningful."""
        self.load_history()

    def load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r', encoding='utf-8') as f:
                self.history = json.load(f)
        else:
            self.history = []

    def save_history(self):
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def get_response(self, user_input):
        try:
            # Send the system prompt first if it's a new conversation
            if not st.session_state.chat.history:
                st.session_state.chat.send_message(self.system_prompt)
            
            # Send user message and get response
            response = st.session_state.chat.send_message(user_input)
            bot_response = response.text
            
            # Save to history
            chat_entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "user": user_input,
                "bot": bot_response
            }
            
            self.history.append(chat_entry)
            self.save_history()
            
            return bot_response
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return "🙏 I'm sorry, main abhi response nahi de pa raha hun. Please thodi der baad try karein."

    def generate_wellness_exercise(self):
        try:
            response = model.generate_content(
                "Generate a short mental wellness exercise in Hinglish with emojis. Include steps and benefits."
            )
            return response.text
        except Exception as e:
            return "🧘‍♀️ Quick Relaxation Exercise:\n1. Deep breathing (5 baar)\n2. Shoulders ko rotate karein\n3. Peaceful thoughts pe focus karein"

    def generate_motivation(self):
        try:
            response = model.generate_content(
                "Generate an inspiring quote or thought in Hinglish with emojis. Make it personal and uplifting."
            )
            return response.text
        except Exception as e:
            return "✨ Yaad rakhein: Har mushkil waqt guzar jata hai. Aap stronger ho than you think! 💪"

def main():
    st.title("🌸 Mindful Companion - Your Mental Health Friend")
    st.markdown("### _Aapka apna mental health saathi_ 🤗")

    # Initialize session state for conversation history if it doesn't exist
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
        st.session_state.chat = model.start_chat(history=[])

    # Initialize chatbot
    chatbot = MentalHealthChatbot()

    # Create two columns for layout
    col1, col2 = st.columns([3, 1])

    with col1:
        # Display chat history
        for msg in st.session_state.conversation_history:
            with st.chat_message("user"):
                st.write(msg["user"])
            with st.chat_message("assistant", avatar="🌸"):
                st.write(msg["bot"])

        # Chat input
        user_input = st.chat_input("Apne dil ki baat share karein... 💭")
        
        if user_input:
            with st.chat_message("user"):
                st.write(user_input)

            with st.chat_message("assistant", avatar="🌸"):
                bot_response = chatbot.get_response(user_input)
                st.write(bot_response)

            st.session_state.conversation_history.append({
                "user": user_input,
                "bot": bot_response
            })

    with col2:
        st.markdown("### 🌟 Wellness Tools")
        
        if st.button("🧘‍♀️ Wellness Exercise"):
            exercise = chatbot.generate_wellness_exercise()
            st.success(exercise)
            
        if st.button("✨ Daily Motivation"):
            motivation = chatbot.generate_motivation()
            st.info(motivation)
            
        if st.button("🗑️ Clear Chat History"):
            st.session_state.conversation_history = []
            st.session_state.chat = model.start_chat(history=[])
            if os.path.exists(chatbot.history_file):
                os.remove(chatbot.history_file)
            st.rerun()

        # Add helpful resources
        st.markdown("### 📚 Helpful Resources")
        st.markdown("""
        - 🏥 Emergency Helpline: 1800-599-0019
        - 💝 Self-Care Tips
        - 📝 Mood Journal
        - 🧘‍♀️ Meditation Guide
        """)

if __name__ == "__main__":
    main()
