# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
from pose_fall_detection import PoseFallDetector

app = Flask(__name__)
CORS(app)

# Initialize detector
pose_detector = PoseFallDetector()
frame_count = 0

@app.route('/toggle_pause', methods=['POST'])
def toggle_pause():
    pose_detector.toggle_pause()
    return jsonify({'paused': pose_detector.paused})

@app.route('/detect_fall', methods=['POST'])
def detect_fall():
    try:
        data = request.get_json()
        frame_data = data.get('frame')
        
        # Decode base64 image
        img_bytes = base64.b64decode(frame_data.split(',')[1])
        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        # Process frame
        annotated_frame, fallen = pose_detector.process_frame(frame)
        
        if annotated_frame is not None:
            # Encode processed frame
            _, buffer = cv2.imencode('.jpg', annotated_frame)
            annotated_frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            return jsonify({
                'fall_detected': fallen,
                'annotated_frame': f'data:image/jpeg;base64,{annotated_frame_base64}',
                'paused': pose_detector.paused
            })
        
        return jsonify({'paused': pose_detector.paused})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/get_previous_frames', methods=['GET'])
def get_previous_frames():
    frames = []
    for frame, timestamp in pose_detector.frame_buffer:
        _, buffer = cv2.imencode('.jpg', frame)
        frame_base64 = base64.b64encode(buffer).decode('utf-8')
        frames.append({
            'frame': f'data:image/jpeg;base64,{frame_base64}',
            'timestamp': timestamp
        })
    return jsonify({'frames': frames})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
