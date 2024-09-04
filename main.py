import base64
import random
import time
import threading
import httpx
import cv2
import numpy as np
import easyocr
import re
import json
import os

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics.texture import Texture

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'], gpu=False, model_storage_directory=os.path.join(os.getcwd(), "model"), download_enabled=True)

class CaptchaApp(BoxLayout):
    def __init__(self, **kwargs):
        super(CaptchaApp, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.accounts = {}
        self.background_images = []
        self.last_status_code = None
        self.last_response_text = None
        self.corrections = self.load_corrections()

        self.add_account_button = Button(text="Add Account", size_hint=(1, 0.1))
        self.add_account_button.bind(on_release=self.add_account)
        self.add_widget(self.add_account_button)

        self.upload_background_button = Button(text="Upload Backgrounds", size_hint=(1, 0.1))
        self.upload_background_button.bind(on_release=self.upload_backgrounds)
        self.add_widget(self.upload_background_button)

        self.account_layout = GridLayout(cols=1, size_hint_y=None)
        self.account_layout.bind(minimum_height=self.account_layout.setter('height'))

        self.scrollview = ScrollView(size_hint=(1, 1))
        self.scrollview.add_widget(self.account_layout)
        self.add_widget(self.scrollview)

    def upload_backgrounds(self, instance):
        """Upload background images for processing."""
        filechooser = FileChooserListView(path=os.getcwd(), filters=['*.jpg', '*.png', '*.jpeg'])
        popup = Popup(title='Select Background Images', content=filechooser, size_hint=(0.9, 0.9))
        filechooser.bind(on_submit=self.on_backgrounds_selected)
        popup.open()

    def on_backgrounds_selected(self, filechooser, selection, touch):
        """Handle background image selection."""
        self.background_images = [cv2.imread(path) for path in selection]
        popup = Popup(title='Success', content=Label(text=f"{len(self.background_images)} background images uploaded successfully!"), size_hint=(0.5, 0.5))
        popup.open()

    def add_account(self, instance):
        """Add a new account for captcha solving."""
        self.show_add_account_popup()

    def show_add_account_popup(self):
        """Show a popup to add account details."""
        content = BoxLayout(orientation='vertical')
        username_input = TextInput(hint_text='Enter Username', multiline=False)
        password_input = TextInput(hint_text='Enter Password', password=True, multiline=False)
        submit_button = Button(text='Submit', size_hint=(1, 0.2))

        content.add_widget(username_input)
        content.add_widget(password_input)
        content.add_widget(submit_button)

        popup = Popup(title='Add Account', content=content, size_hint=(0.8, 0.5))
        submit_button.bind(on_release=lambda x: self.handle_account_submission(username_input.text, password_input.text, popup))
        popup.open()

    def handle_account_submission(self, username, password, popup):
        """Handle the account submission and login."""
        if username and password:
            user_agent = self.generate_user_agent()
            session = self.create_session(user_agent)
            if self.login(username, password, session):
                self.accounts[username] = {
                    'password': password,
                    'user_agent': user_agent,
                    'session': session,
                    'captcha_id1': None,
                    'captcha_id2': None
                }
                self.create_account_ui(username)
                popup.dismiss()
            else:
                error_popup = Popup(title='Error', content=Label(text=f"Failed to login for user {username}"), size_hint=(0.5, 0.5))
                error_popup.open()
        else:
            error_popup = Popup(title='Error', content=Label(text="Username and password cannot be empty"), size_hint=(0.5, 0.5))
            error_popup.open()

    def create_account_ui(self, username):
        """Create the UI elements for a specific account."""
        account_box = BoxLayout(size_hint_y=None, height=50)
        account_label = Label(text=f"Account: {username}", size_hint_x=0.4)
        account_box.add_widget(account_label)

        captcha_id1_input = TextInput(hint_text='Captcha ID 1', multiline=False)
        account_box.add_widget(captcha_id1_input)
        
        captcha_id2_input = TextInput(hint_text='Captcha ID 2', multiline=False)
        account_box.add_widget(captcha_id2_input)

        cap1_button = Button(text="Cap 1", size_hint_x=0.2)
        cap1_button.bind(on_release=lambda x: threading.Thread(target=self.request_captcha, args=(username, captcha_id1_input.text)).start())
        account_box.add_widget(cap1_button)

        cap2_button = Button(text="Cap 2", size_hint_x=0.2)
        cap2_button.bind(on_release=lambda x: threading.Thread(target=self.request_captcha, args=(username, captcha_id2_input.text)).start())
        account_box.add_widget(cap2_button)

        request_all_button = Button(text="Request All", size_hint_x=0.2)
        request_all_button.bind(on_release=lambda x: threading.Thread(target=self.request_all_captchas, args=(username,)).start())
        account_box.add_widget(request_all_button)

        self.account_layout.add_widget(account_box)

    def request_all_captchas(self, username):
        """Request all captchas for the specified account."""
        self.request_captcha(username, self.accounts[username]['captcha_id1'])
        self.request_captcha(username, self.accounts[username]['captcha_id2'])

    @staticmethod
    def create_session(user_agent):
        """Create an HTTP session with custom headers."""
        return httpx.Client(headers=CaptchaApp.generate_headers(user_agent))

    def login(self, username, password, session, retry_count=3):
        """Attempt to log in to the account."""
        login_url = 'https://api.ecsc.gov.sy:8080/secure/auth/login'
        login_data = {'username': username, 'password': password}

        for attempt in range(retry_count):
            try:
                response = session.post(login_url, json=login_data)

                if response.status_code == 200:
                    return True
                elif response.status_code in {401, 402, 403}:
                    continue
                else:
                    return False
            except Exception as e:
                continue
            time.sleep(2)
        return False

    def request_captcha(self, username, captcha_id):
        """Request a captcha image for processing."""
        session = self.accounts[username].get('session')
        if not session:
            error_popup = Popup(title='Error', content=Label(text=f"No session found for user {username}"), size_hint=(0.5, 0.5))
            error_popup.open()
            return

        # Send OPTIONS request before the GET request
        try:
            options_url = f"https://api.ecsc.gov.sy:8080/rs/reserve?id={captcha_id}&captcha=0"
            session.options(options_url)
        except httpx.RequestError as e:
            error_popup = Popup(title='Error', content=Label(text=f"Failed to send OPTIONS request: {e}"), size_hint=(0.5, 0.5))
            error_popup.open()
            return

        # Send GET request to retrieve the captcha image
        captcha_data = self.get_captcha(session, captcha_id)
        if captcha_data:
            Clock.schedule_once(lambda dt: self.show_captcha(captcha_data, username, captcha_id))
        else:
            if self.last_status_code == 403:  # Session expired
                info_popup = Popup(title='Session expired', content=Label(text=f"Session expired for user {username}. Re-logging in..."), size_hint=(0.5, 0.5))
                info_popup.open()
                if self.login(username, self.accounts[username]['password'], session):
                    success_popup = Popup(title='Re-login successful', content=Label(text=f"Re-login successful for user {username}. Please request the captcha again."), size_hint=(0.5, 0.5))
                    success_popup.open()
                else:
                    error_popup = Popup(title='Re-login failed', content=Label(text=f"Re-login failed for user {username}. Please check credentials."), size_hint=(0.5, 0.5))
                    error_popup.open()
            else:
                error_popup = Popup(title='Error', content=Label(text=f"Failed to get captcha. Status code: {self.last_status_code}, Response: {self.last_response_text}"), size_hint=(0.5, 0.5))
                error_popup.open()

    def get_captcha(self, session, captcha_id):
        """Retrieve the captcha image data."""
        try:
            captcha_url = f"https://api.ecsc.gov.sy:8080/files/fs/captcha/{captcha_id}"
            response = session.get(captcha_url)

            self.last_status_code = response.status_code
            self.last_response_text = response.text

            if response.status_code == 200:
                response_data = response.json()
                return response_data.get('file')
        except Exception as e:
            error_popup = Popup(title='Error', content=Label(text=f"Failed to get captcha: {e}"), size_hint=(0.5, 0.5))
            error_popup.open()
        return None

    def show_captcha(self, captcha_data, username, captcha_id):
        """Display the captcha image for user input."""
        try:
            captcha_base64 = captcha_data.split(",")[1] if ',' in captcha_data else captcha_data
            captcha_image_data = base64.b64decode(captcha_base64)

            with open("captcha.jpg", "wb") as f:
                f.write(captcha_image_data)

            captcha_image = cv2.imread("captcha.jpg")
            processed_image = self.process_captcha(captcha_image)

            # Convert processed image to a format that Kivy can display
            buf1 = cv2.flip(processed_image, 0)
            buf = buf1.tostring()
            texture = Texture.create(size=(processed_image.shape[1], processed_image.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

            # Create a popup to show the captcha
            captcha_layout = BoxLayout(orientation='vertical')

            captcha_img = Image(texture=texture)
            captcha_layout.add_widget(captcha_img)

            captcha_input = TextInput(hint_text='Enter Captcha', multiline=False)
            captcha_layout.add_widget(captcha_input)

            submit_button = Button(text='Submit Captcha')
            submit_button.bind(on_release=lambda x: threading.Thread(target=self.submit_captcha, args=(username, captcha_id, captcha_input.text)).start())
            captcha_layout.add_widget(submit_button)

            popup = Popup(title='Captcha', content=captcha_layout, size_hint=(0.8, 0.8))
            popup.open()

            # Now perform OCR processing
            img_array = np.array(processed_image)
            
            # تحسين الأداء من خلال تحديد أقصى عدد للأحرف المراد التعرف عليها
            predictions = reader.readtext(img_array, detail=0, allowlist='0123456789+-*/')

            # Correct the OCR output with our custom function
            corrected_text, _ = self.correct_and_highlight(predictions, img_array)

            captcha_solution = self.solve_captcha(corrected_text)

            # Update the entry with OCR result
            captcha_input.text = str(captcha_solution)

        except Exception as e:
            error_popup = Popup(title='Error', content=Label(text=f"Failed to show captcha: {e}"), size_hint=(0.5, 0.5))
            error_popup.open()

    def process_captcha(self, captcha_image):
        """Apply advanced image processing to remove the background using added backgrounds while keeping original colors."""
        captcha_image = cv2.resize(captcha_image, (110, 60))

        if not self.background_images:
            return captcha_image

        best_background = None
        min_diff = float('inf')

        for background in self.background_images:
            background = cv2.resize(background, (110, 60))
            processed_image = self.remove_background_keep_original_colors(captcha_image, background)
            gray_diff = cv2.cvtColor(processed_image, cv2.COLOR_BGR2GRAY)
            score = np.sum(gray_diff)

            if score < min_diff:
                min_diff = score
                best_background = background

        if best_background is not None:
            cleaned_image = self.remove_background_keep_original_colors(captcha_image, best_background)
            return cleaned_image
        else:
            return captcha_image

    @staticmethod
    def remove_background_keep_original_colors(captcha_image, background_image):
        """Remove background from captcha image while keeping the original colors of elements."""
        if background_image.shape != captcha_image.shape:
            background_image = cv2.resize(background_image, (captcha_image.shape[1], captcha_image.shape[0]))

        diff = cv2.absdiff(captcha_image, background_image)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY)
        result = cv2.bitwise_and(captcha_image, captcha_image, mask=mask)

        return result

    def submit_captcha(self, username, captcha_id, captcha_solution):
        """Submit the captcha solution to the server."""
        session = self.accounts[username].get('session')
        if not session:
            error_popup = Popup(title='Error', content=Label(text=f"No session found for user {username}"), size_hint=(0.5, 0.5))
            error_popup.open()
            return

        try:
            options_url = f"https://api.ecsc.gov.sy:8080/rs/reserve?id={captcha_id}&captcha={captcha_solution}"
            session.options(options_url)
        except httpx.RequestError as e:
            error_popup = Popup(title='Error', content=Label(text=f"Failed to send OPTIONS request: {e}"), size_hint=(0.5, 0.5))
            error_popup.open()
            return

        try:
            get_url = f"https://api.ecsc.gov.sy:8080/rs/reserve?id={captcha_id}&captcha={captcha_solution}"
            response = session.get(get_url)

            if response.status_code == 200:
                response_data = response.json()
                if 'message' in response_data:
                    success_popup = Popup(title='Success', content=Label(text=response_data['message']), size_hint=(0.5, 0.5))
                    success_popup.open()
                else:
                    success_popup = Popup(title='Success', content=Label(text="Captcha submitted successfully!"), size_hint=(0.5, 0.5))
                    success_popup.open()
            else:
                error_popup = Popup(title='Error', content=Label(text=f"Failed to submit captcha. Status code: {response.status_code}, Response: {response.text}"), size_hint=(0.5, 0.5))
                error_popup.open()

        except Exception as e:
            error_popup = Popup(title='Error', content=Label(text=f"Failed to submit captcha: {e}"), size_hint=(0.5, 0.5))
            error_popup.open()

    @staticmethod
    def generate_headers(user_agent):
        """Generate HTTP headers for the session."""
        return {
            'User-Agent': user_agent,
            'Content-Type': 'application/json',
            'Source': 'WEB',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://ecsc.gov.sy/',
            'Origin': 'https://ecsc.gov.sy',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site'
        }

    @staticmethod
    def generate_user_agent():
        """Generate a random user agent string."""
        user_agent_list = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv=89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/13.1.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/56.0.2924.87 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/47.0.2526.106 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
        ]
        
        return random.choice(user_agent_list)

    def correct_and_highlight(self, predictions, image):
        """Correct OCR predictions and apply color highlights to numbers and operators."""
        corrections = {
            'O': '0', 'S': '5', 'I': '1', 'B': '8', 'G': '6',
            'Z': '2', 'T': '7', 'A': '4', 'X': '*', '×': '*', 'L': '1',
            'H': '8', '_': '-', '/': '7', '£': '8', '&': '8'
        }

        corrected_text = ""
        
        for text in predictions:
            text = text.strip().upper()
            for char in text:
                corrected_char = corrections.get(char, char)
                corrected_text += corrected_char

        return corrected_text, image

    def save_corrections(self):
        """Save corrections to a file."""
        file_path = os.path.join(os.getcwd(), "corrections.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.corrections, f, ensure_ascii=False, indent=4)

    def load_corrections(self):
        """Load corrections from a file."""
        file_path = os.path.join(os.getcwd(), "corrections.json")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    @staticmethod
    def solve_captcha(corrected_text):
        """Solve the captcha by extracting two numbers and one operator."""
        corrected_text = re.sub(r"[._/]", "", corrected_text)

        numbers = re.findall(r'\d+', corrected_text)
        operators = re.findall(r'[+*xX-]', corrected_text)

        if len(numbers) == 2 and len(operators) == 1:
            num1, num2 = map(int, numbers)
            operator = operators[0]

            if operator in ['*', '×', 'x']:
                return abs(num1 * num2)
            elif operator == '+':
                return abs(num1 + num2)
            elif operator == '-':
                return abs(num1 - num2)

        if len(corrected_text) == 3 and corrected_text[0] in {'+', '-', '*', 'x', '×'}:
            num1, operator, num2 = corrected_text[1], corrected_text[0], corrected_text[2]
            num1, num2 = int(num1), int(num2)

            if operator in ['*', '×', 'x']:
                return abs(num1 * num2)
            elif operator == '+':
                return abs(num1 + num2)
            elif operator == '-':
                return abs(num1 - num2)

        return None


class CaptchaAppLauncher(App):
    def build(self):
        return CaptchaApp()


if __name__ == "__main__":
    CaptchaAppLauncher().run()
