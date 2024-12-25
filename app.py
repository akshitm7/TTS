from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import google.generativeai as genai
from PIL import Image
import io
import requests  # For HTTP requests to ElevenLabs API

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

class EnhancedImageAnalyzer:
    def __init__(self):
        # Replace with your API key
        api_key = "AIzaSyDhY1MuHmLEVStBkgvHnuWINWydugH4SYM"
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        self.image_memory = {}

        # ElevenLabs TTS API Key (Replace with your own key)
        self.elevenlabs_api_key = "sk_2493130858923ce4d3f02e2bf8cd7556ba8813d1b3d8dff6"
        self.elevenlabs_url = "https://elevenlabs.io/app/speech-synthesis/text-to-speech"
    def _validate_image(self, image_data):
        try:
            with Image.open(io.BytesIO(image_data)) as img:
                img.verify()  # Validate the image integrity
                img_format = img.format.lower()
            if img_format not in ["jpeg", "jpg", "png", "bmp"]:
                raise ValueError(f"Unsupported image format: {img_format}")
            return True
        except Exception as e:
            raise ValueError(f"Image validation failed: {str(e)}")

    def analyze_image(self, image_data):
        try:
            self._validate_image(image_data)
            
            # Determine MIME type based on image format
            mime_type = "image/jpeg"  # Default MIME type
            with Image.open(io.BytesIO(image_data)) as img:
                if img.format.lower() == 'png':
                    mime_type = "image/png"
                elif img.format.lower() == 'bmp':
                    mime_type = "image/bmp"
            
            prompt = """
            Describe this image in detail and non-repetitive manner, including:
            - Main subjects and their characteristics
            - Setting and background
            - Colors and lighting
            - Notable actions or interactions
            - Overall mood or atmosphere
            """
            # Send the image data to the API
            response = self.model.generate_content([prompt, {"mime_type": mime_type, "data": image_data}])

            if not response.text:
                return "Error: No valid response from the image analysis API"
            
            unique_lines = list(dict.fromkeys(response.text.split("\n")))
            filtered_response = "\n".join(unique_lines)

            # Call the TTS engine to speak the description using ElevenLabs
            self.speak(filtered_response)

            return filtered_response

        except Exception as e:
            return f"Error analyzing image: {str(e)}"

    def speak(self, text):
        try:
        # Prepare the payload for ElevenLabs API
            payload = {
            "text": text,
            "voice": "en_us_male",  # Choose the voice; adjust as needed
            "output": "audio_url"   # The output can be an audio URL
            }

            headers = {
                "Authorization": f"Bearer {self.elevenlabs_api_key}",
                "Content-Type": "application/json"
            }

        # Send request to ElevenLabs API
            response = requests.post(self.elevenlabs_url, json=payload, headers=headers)

            if response.status_code == 200:
                audio_url = response.json().get("audio_url")
                print(f"Audio URL: {audio_url}")
                return audio_url  # Return the audio URL to play it in the frontend
            else:
                print(f"Error from ElevenLabs API: {response.text}")
                return "Error generating speech"
        except Exception as e:
            print(f"Error during TTS: {str(e)}")
            return "Error generating speech"
    def ask_question(self, image_data, question):
        try:
            description = self.image_memory.get("last_image_description")
            if not description:
                return "Error: Please analyze the image first."

            prompt = f"""
            Based on this image description:
            {description}

            Answer the following question: {question}
            """
            response = self.model.generate_content(prompt)

            # Call the TTS engine to speak the answer
            self.speak(response.text)

            return response.text

        except Exception as e:
            return f"Error processing question: {str(e)}"

analyzer = EnhancedImageAnalyzer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    try:
        # Read the image directly into memory without saving it to disk
        image_data = file.stream.read()
        result = analyzer.analyze_image(image_data)

        # Save the description to memory for question answering
        analyzer.image_memory["last_image_description"] = result
        
        return jsonify({'result': result})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ask', methods=['POST'])
def ask_question():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    question = request.form.get('question')
    
    if not question:
        return jsonify({'error': 'No question provided'}), 400

    try:
        # Read the image directly into memory without saving it to disk
        image_data = file.stream.read()
        
        # Analyze the image first before asking the question
        analyzer.analyze_image(image_data)

        # Now that the image is analyzed, answer the question
        result = analyzer.ask_question(image_data, question)
        return jsonify({'result': result})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
