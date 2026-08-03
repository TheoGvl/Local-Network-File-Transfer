import os
import tempfile
import threading
from flask import Flask, request

app = Flask(__name__)
ui_callback = None

@app.route('/', methods=['GET'])
def index():
    return """
    <!doctype html>
    <html lang="en">
    <head>
      <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0">
      <title>LocalDrop</title>
      <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        
        body { 
            font-family: 'Inter', sans-serif; 
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            color: #ffffff; 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            justify-content: center; 
            height: 100vh; 
            margin: 0; 
        }
        
        .glass-card { 
            background: rgba(255, 255, 255, 0.05); 
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            padding: 35px 30px; 
            border-radius: 24px; 
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            text-align: center; 
            width: 85%;
            max-width: 350px;
        }
        
        h2 { margin-top: 0; font-weight: 800; font-size: 26px; letter-spacing: -0.5px; }
        p { color: #b0bec5; font-size: 14px; margin-bottom: 25px; }
        
        .custom-file-upload {
            display: inline-block;
            padding: 14px 28px;
            cursor: pointer;
            border-radius: 12px;
            background: rgba(255,255,255,0.1);
            border: 2px dashed rgba(255,255,255,0.3);
            transition: all 0.3s ease;
            width: 100%;
            box-sizing: border-box;
            margin-bottom: 20px;
            font-size: 15px;
        }
        
        .custom-file-upload:hover {
            background: rgba(255,255,255,0.15);
            border-color: #00d2ff;
        }

        input[type="file"] { display: none; }
        
        .send-btn { 
            background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
            color: white; 
            border: none; 
            padding: 16px 24px; 
            font-size: 16px; 
            border-radius: 12px; 
            cursor: pointer; 
            font-weight: 600; 
            width: 100%; 
            box-shadow: 0 4px 15px rgba(0, 210, 255, 0.4);
            transition: transform 0.2s;
        }
        
        .send-btn:active { transform: scale(0.96); }
        
        .sys-info {
            display: flex;
            justify-content: space-between;
            margin-top: 25px;
            padding-top: 15px;
            border-top: 1px solid rgba(255,255,255,0.1);
            font-size: 12px;
            color: #78909c;
            font-weight: 600;
        }
      </style>
      
      <script>
        function updateFileName() {
            const input = document.getElementById('file-upload');
            const label = document.getElementById('file-label');
            const btn = document.getElementById('submit-btn');
            
            if (input.files.length > 1) {
                label.innerHTML = "📁 " + input.files.length + " files selected";
                btn.innerHTML = "Send " + input.files.length + " files";
            } else if (input.files.length === 1) {
                label.innerHTML = "📄 " + input.files[0].name;
                btn.innerHTML = "Send 1 file";
            }
        }
      </script>
    </head>
    <body>
      <div class="glass-card">
        <h2>LocalDrop</h2>
        <p>Dashboard Connection Active</p>
        <form action="/upload" method="post" enctype="multipart/form-data">
          
          <label for="file-upload" class="custom-file-upload" id="file-label">
              Tap to select files
          </label>
          <input id="file-upload" type="file" name="files" multiple required onchange="updateFileName()">
          
          <button type="submit" id="submit-btn" class="send-btn">Send to Dashboard</button>
        </form>
        
        <div class="sys-info">
            <span>🔒 Local Transfer</span>
            <span>⚡ Wi-Fi Direct</span>
        </div>
      </div>
    </body>
    </html>
    """

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files' not in request.files:
        return "No file part", 400
        
    uploaded_files = request.files.getlist('files')
    if not uploaded_files or uploaded_files[0].filename == '':
        return "No selected files", 400
        
    temp_dir = tempfile.gettempdir()
    file_data = []
    
    for file in uploaded_files:
        if file.filename:
            temp_path = os.path.join(temp_dir, file.filename)
            file.save(temp_path)
            file_data.append((temp_path, file.filename))
    
    if ui_callback and file_data:
        ui_callback(file_data)
        
    return """
    <body style="background: linear-gradient(135deg, #0f2027, #203a43, #2c5364); color:white; font-family:'Inter', sans-serif; text-align:center; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0;">
        <div style="background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); padding: 40px 30px; border-radius: 24px; border: 1px solid rgba(255, 255, 255, 0.1); width: 80%; max-width: 350px;">
            <h2 style="color: #00d2ff; font-size: 28px; margin-top:0;">Sent! 🚀</h2>
            <p style="color:#b0bec5; margin-bottom: 30px;">Files are being processed by your Dashboard.</p>
            <button onclick="window.location.href='/'" style="background: rgba(255,255,255,0.1); color: white; border: 1px solid rgba(255,255,255,0.2); padding: 14px 24px; font-size: 16px; border-radius: 12px; cursor: pointer; font-weight: 600; width: 100%;">Send More</button>
        </div>
    </body>
    """

def start_server(port, callback):
    global ui_callback
    ui_callback = callback
    threading.Thread(
        target=lambda: app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False), 
        daemon=True
    ).start()