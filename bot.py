
import os
import time
import glob
import random
import logging
import pickle
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired
from transformers import pipeline

# Configuration
USERNAME = os.getenv('INSTAGRAM_USERNAME')
PASSWORD = os.getenv('INSTAGRAM_PASSWORD')
WELCOME_MESSAGE = 
"༘˚⋆𐙚｡⋆𖦹.✧˚ heyyy I am noor.༘˚⋆𐙚｡⋆𖦹.✧˚ Welcome to S Î Ž Ĺ È Ř 🌷 Your INTRO ≽^• ˕ • ྀི≼ "
ABUSE_WARNING = "⚠️ Your message was removed for violating our community guidelines."
GREETING_RESPONSES = ["Hello pookie 🎀 (✿ᴗ͈ˬᴗ͈)⁾⁾ how r u??"]
ABUSIVE_WORDS = {"hate", "stupid", "idiot", "kill", "fuck", "shit", "asshole", "bitch", "retard"}
USER_STORAGE_FILE = "welcomed_users.pkl"
CHECK_INTERVAL = 60  # Seconds between checks

# Initialize AI model (free text generation)
ai_generator = pipeline('text-generation', model='gpt2')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InstagramBot:
    def __int__(self);
    self.download_artifacts()def init(self):
    self.download_artifacts()
    # ... rest of existing code

def download_artifacts(self):
    # Find latest artifact
    artifacts = glob.glob('user-data-*/welcomed_users.pkl')
    if artifacts:
        latest = max(artifacts, key=os.path.getctime)
        os.rename(latest, USER_STORAGE_FILE)
    def __init__(self):
        self.client = Client()
        self.welcomed_users = self.load_users()
        self.last_checked = time.time()

    def load_users(self):
        try:
            with open(USER_STORAGE_FILE, 'rb') as f:
                return pickle.load(f)
        except (FileNotFoundError, EOFError):
            return set()

    def save_users(self):
        with open(USER_STORAGE_FILE, 'wb') as f:
            pickle.dump(self.welcomed_users, f)

    def login(self):
        try:
            self.client.login(USERNAME, PASSWORD)
            logger.info("Logged in successfully!")
        except (LoginRequired, ChallengeRequired) as e:
            logger.error(f"Login failed: {e}")
            self.handle_challenge()

    def handle_challenge(self):
        # Implement challenge resolution logic here
        logger.error("Manual intervention required for challenge resolution")
        exit(1)

    def generate_ai_response(self, prompt):
        try:
            response = ai_generator(
                prompt,
                max_length=50,
                num_return_sequences=1,
                truncation=True
            )[0]['generated_text']
            return response.strip()
        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            return "I'm still learning. Could you rephrase that?"

    def moderate_content(self, text):
        text_lower = text.lower()
        return any(word in text_lower for word in ABUSIVE_WORDS)

    def handle_message(self, thread, message):
        user_id = message.user_id
        text = message.text or ""
        thread_id = thread.id

        # Skip own messages and system notifications
        if user_id == self.client.user_id or not text.strip():
            return

        # Content moderation
        if self.moderate_content(text):
            logger.info(f"Removing abusive content from user {user_id}")
            self.client.direct_send(ABUSE_WARNING, user_ids=[user_id])
            self.client.direct_thread_hide(thread_id)
            return

        # New user welcome
        if user_id not in self.welcomed_users:
            self.client.direct_send(WELCOME_MESSAGE, thread_ids=[thread_id])
            self.welcomed_users.add(user_id)
            self.save_users()
            logger.info(f"Welcomed {user_id} (✿ᴗ͈ˬᴗ͈)⁾⁾ I am noor⋆ 𐙚 ̊. apka intro cutie ⋆.˚🦋༘⋆ ")

        # Handle greetings
        elif text.lower() in {"hi", "hello", "hey", "hola"}:
            response = random.choice(GREETING_RESPONSES)
            self.client.direct_send(response, thread_ids=[thread_id])

        # AI-generated responses for other messages
        else:
            ai_response = self.generate_ai_response(text)
            self.client.direct_send(ai_response, thread_ids=[thread_id])

    def run(self):
        self.login()
        logger.info("Bot started. Monitoring messages...")
        
        while True:
            try:
                now = time.time()
                threads = self.client.direct_threads(20)
                
                for thread in threads:
                    messages = thread.messages
                    new_messages = [msg for msg in messages if msg.timestamp.timestamp() > self.last_checked]
                    
                    for message in new_messages:
                        self.handle_message(thread, message)
                
                self.last_checked = now
                time.sleep(CHECK_INTERVAL)
                
            except Exception as e:
                logger.error(f"Error: {e}")
                logger.info("Reconnecting in 60 seconds...")
                time.sleep(60)
                self.login()

if __name__ == "__main__":
    bot = InstagramBot()
    bot.run()
