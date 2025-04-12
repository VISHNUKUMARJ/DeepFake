from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
import requests
import tempfile
from werkzeug.utils import secure_filename
from utils.image_checker import check_fake_image
from utils.video_checker import check_fake_video
from utils.audio_checker import check_fake_audio
from utils.text_checker import check_fake_text

# Remove this line as it's causing the error and isn't used:
# from keras.layers import LocallyConnected2D

app = Flask(__name__)
CORS(app)  # Allows frontend JS to talk to backend

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {
    'image': {'png', 'jpg', 'jpeg', 'gif', 'webp'},
    'video': {'mp4', 'avi', 'mov', 'webm'},
    'audio': {'mp3', 'wav', 'm4a', 'ogg'},
    'text': {'txt', 'doc', 'docx', 'pdf'}
}
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max upload size

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Helper functions
def allowed_file(filename, file_type):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS[file_type]

def download_file_from_url(url, file_type):
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, dir=UPLOAD_FOLDER)
        for chunk in response.iter_content(chunk_size=8192):
            temp_file.write(chunk)
        temp_file.close()
        
        return temp_file.name
    except Exception as e:
        app.logger.error(f"Error downloading file from URL: {e}")
        return None

# Routes
@app.route('/check_image', methods=['POST'])
def check_image():
    try:
        if 'image' in request.files:
            file = request.files['image']
            if file.filename == '':
                return jsonify({"error": "No file selected"}), 400
                
            if not allowed_file(file.filename, 'image'):
                return jsonify({"error": f"File type not allowed. Supported formats: {', '.join(ALLOWED_EXTENSIONS['image'])}"}), 400
                
            filename = secure_filename(f"{uuid.uuid4().hex}_{file.filename}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
        elif request.is_json and 'url' in request.json:
            url = request.json['url']
            filepath = download_file_from_url(url, 'image')
            
            if not filepath:
                return jsonify({"error": "Failed to download image from URL"}), 400
                
        else:
            return jsonify({"error": "No image file or URL provided"}), 400
            
        # Process the image
        result = check_fake_image(filepath)
        
        # Optional: Remove the file after processing
        try:
            os.remove(filepath)
        except:
            pass
            
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Error processing image: {str(e)}")
        return jsonify({"error": f"Error processing image: {str(e)}"}), 500

@app.route('/check_video', methods=['POST'])
def check_video():
    try:
        if 'video' in request.files:
            file = request.files['video']
            if file.filename == '':
                return jsonify({"error": "No file selected"}), 400
                
            if not allowed_file(file.filename, 'video'):
                return jsonify({"error": f"File type not allowed. Supported formats: {', '.join(ALLOWED_EXTENSIONS['video'])}"}), 400
                
            filename = secure_filename(f"{uuid.uuid4().hex}_{file.filename}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
        elif request.is_json and 'url' in request.json:
            url = request.json['url']
            filepath = download_file_from_url(url, 'video')
            
            if not filepath:
                return jsonify({"error": "Failed to download video from URL"}), 400
                
        else:
            return jsonify({"error": "No video file or URL provided"}), 400
            
        # Process the video (this may take time for large videos)
        result = check_fake_video(filepath)
        
        # Optional: Remove the file after processing
        try:
            os.remove(filepath)
        except:
            pass
            
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Error processing video: {str(e)}")
        return jsonify({"error": f"Error processing video: {str(e)}"}), 500

@app.route('/check_audio', methods=['POST'])
def check_audio():
    try:
        if 'audio' in request.files:
            file = request.files['audio']
            if file.filename == '':
                return jsonify({"error": "No file selected"}), 400
                
            if not allowed_file(file.filename, 'audio'):
                return jsonify({"error": f"File type not allowed. Supported formats: {', '.join(ALLOWED_EXTENSIONS['audio'])}"}), 400
                
            filename = secure_filename(f"{uuid.uuid4().hex}_{file.filename}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
        elif request.is_json and 'url' in request.json:
            url = request.json['url']
            filepath = download_file_from_url(url, 'audio')
            
            if not filepath:
                return jsonify({"error": "Failed to download audio from URL"}), 400
                
        else:
            return jsonify({"error": "No audio file or URL provided"}), 400
            
        # Process the audio
        result = check_fake_audio(filepath)
        
        # Optional: Remove the file after processing
        try:
            os.remove(filepath)
        except:
            pass
            
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Error processing audio: {str(e)}")
        return jsonify({"error": f"Error processing audio: {str(e)}"}), 500

@app.route('/check_text', methods=['POST'])
def check_text():
    try:
        if not request.is_json:
            return jsonify({"error": "Invalid request format"}), 400
            
        data = request.get_json()
        text = data.get("text", "")
        
        if not text.strip():
            return jsonify({"error": "No text provided"}), 400
            
        # Process the text
        result = check_fake_text(text)
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Error processing text: {str(e)}")
        return jsonify({"error": f"Error processing text: {str(e)}"}), 500

@app.route('/check_text_file', methods=['POST'])
def check_text_file():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
            
        if not allowed_file(file.filename, 'text'):
            return jsonify({"error": f"File type not allowed. Supported formats: {', '.join(ALLOWED_EXTENSIONS['text'])}"}), 400
            
        # For simplicity, we'll just read text files directly
        # For other formats like PDF, DOCX, etc., you'd need additional libraries
        if file.filename.endswith('.txt'):
            text_content = file.read().decode('utf-8')
            
            # Process the text content
            result = check_fake_text(text_content)
            return jsonify(result)
        else:
            return jsonify({"error": "Non-TXT files are not supported in this demo"}), 400
            
    except Exception as e:
        app.logger.error(f"Error processing text file: {str(e)}")
        return jsonify({"error": f"Error processing text file: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

