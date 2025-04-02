from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
import speech_recognition as sr
from threading import Thread
import pyttsx3

# Initialize TTS engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Speed—adjust if too fast/slow
engine.setProperty('volume', 1.0)  # Max volume

# Task dictionary with step-by-step guides
tasks = {
    "call": [
        "Open the Phone app. It’s usually a green icon with a phone.",
        "Tap the dial pad. It’s the numbers at the bottom.",
        "Enter the phone number. Use the keypad.",
        "Tap the green call button. It’s below the numbers."
    ],
    "text": [
        "Open the Messages app. Look for a speech bubble icon.",
        "Tap New Message or the plus sign. It’s usually at the bottom.",
        "Enter the phone number in the To field. Type it at the top.",
        "Tap the text box. It’s below the number.",
        "Type your message. Use the keyboard.",
        "Tap Send. It’s a button or arrow next to the text box."
    ],
    "email": [
        "Open the Gmail app. It’s a white envelope with a red M.",
        "Tap Compose. It’s a button, often at the bottom right.",
        "Enter the email address in the To field. Type it at the top.",
        "Tap the Subject line. It’s below the To field.",
        "Type your subject. Keep it short.",
        "Tap the body area. It’s below the subject.",
        "Type your email. Use the keyboard.",
        "Tap Send. It’s an arrow, usually top right."
    ],
    "web": [
        "Open Chrome. It’s a circle with red, green, and yellow.",
        "Tap the address bar. It’s at the top.",
        "Type the website address. Like google.com.",
        "Tap Go or the arrow on the keyboard. It’s at the bottom right."
    ],
    "app": [
        "Open the Play Store. It’s a white bag with a play arrow.",
        "Tap the search bar. It’s at the top.",
        "Type the app name. Like ‘Calculator’.",
        "Tap the app in the results. Pick the right one.",
        "Tap Install. It’s a green button.",
        "To delete, go to Settings. Tap Apps.",
        "Find the app in the list. Tap it.",
        "Tap Uninstall. Confirm if asked."
    ]
}

# Troubleshooting dictionary with fixes
fixes = {
    "wifi": "Go to Settings. Tap Wi-Fi. Turn the switch on.",
    "phone": "Turn your phone off. Wait 5 seconds. Turn it on.",
    "tv": "Check the cables. Turn the TV off and on.",
    "call": "Check your signal. Make sure the number is right.",
    "bluetooth": "Go to Settings. Tap Bluetooth. Turn it on.",
    "volume": "Press the side buttons up or down. Or go to Settings, then Sound.",
    "hotspot": "Go to Settings. Tap Network and internet. Tap Hotspot and tethering. Turn on Wi-Fi hotspot."
}

class HelperApp(App):
    def __init__(self):
        super().__init__()
        self.current_task = None
        self.step_index = 0
        self.mode = "task"  # Can be "task" or "fix"

    def build(self):
        layout = BoxLayout(orientation='vertical', padding=10)
        self.label = Label(text="How can I help you today?", font_size=30)
        layout.add_widget(self.label)
        speak_btn = Button(text="Speak", font_size=20, size_hint=(1, 0.2))
        speak_btn.bind(on_press=self.start_listening)
        layout.add_widget(speak_btn)
        next_btn = Button(text="Next", font_size=20, size_hint=(1, 0.2))
        next_btn.bind(on_press=self.next_step)
        layout.add_widget(next_btn)
        return layout
    
    def start_listening(self, instance):
        self.label.text = "Listening..."
        Thread(target=self.listen_and_process).start()

    def speak(self, text):
        engine.say(text)
        engine.runAndWait()

    def listen_and_process(self):
        recognizer = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                audio = recognizer.listen(source, timeout=5)
            self.label.text = "Processing..."
            question = recognizer.recognize_google(audio).lower()
            self.label.text = f"You said: {question}"
            self.speak(f"You said: {question}")
            
            # Handle quit command
            if "quit" in question:
                self.label.text = "Goodbye!"
                self.speak("Goodbye!")
                self.current_task = None
                self.mode = "task"
                return

            # Determine mode: task or fix
            if any(keyword in question for keyword in ["how to", "how do i", "help me"]):
                self.mode = "task"
                # Match task
                for task in tasks:
                    if task in question:
                        self.current_task = task
                        self.step_index = 0
                        self.label.text = tasks[task][0]  # First step
                        self.speak(tasks[task][0])
                        return
            elif any(keyword in question for keyword in ["fix", "trouble", "problem", "not working"]):
                self.mode = "fix"
                # Match fix
                for issue in fixes:
                    if issue in question:
                        self.current_task = issue
                        self.label.text = fixes[issue]
                        self.speak(fixes[issue])
                        return
                self.label.text = "I don’t know how to fix that yet. Try WiFi, phone, TV, call, Bluetooth, volume, or hotspot."
                self.speak("I don’t know how to fix that yet. Try WiFi, phone, TV, call, Bluetooth, volume, or hotspot.")
                return

            # If no match
            self.label.text = "I don’t understand. Try saying 'how to call' or 'fix WiFi'."
            self.speak("I don’t understand. Try saying 'how to call' or 'fix WiFi'.")
        except sr.WaitTimeoutError:
            self.label.text = "Timed out—say something faster!"
            self.speak("Timed out—say something faster!")
        except Exception as e:
            self.label.text = f"Error: {str(e)}"
            self.speak(f"Error: {str(e)}")

    def next_step(self, instance):
        if self.mode == "task" and self.current_task and self.step_index < len(tasks[self.current_task]) - 1:
            self.step_index += 1
            self.label.text = tasks[self.current_task][self.step_index]
            self.speak(tasks[self.current_task][self.step_index])
        elif self.mode == "task" and self.current_task:
            self.label.text = "All done! Anything else?"
            self.speak("All done! Anything else?")
            self.current_task = None
        elif self.mode == "fix" and self.current_task:
            self.label.text = "I’ve told you how to fix it. Anything else?"
            self.speak("I’ve told you how to fix it. Anything else?")
            self.current_task = None
        else:
            self.label.text = "Say something to start!"
            self.speak("Say something to start!")

if __name__ == "__main__":
    HelperApp().run()
