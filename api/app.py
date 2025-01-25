from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import os
import base64
from pose_fall_detection import PoseFallDetector
import logging
from werkzeug.wrappers import Request, Response
from datetime import datetime, date

app = Flask(__name__)

# Configure logging to output to the console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s'
)


CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://fall-detection-system-eight.vercel.app",
            "https://fall-detection-system-production.up.railway.app",
            "http://localhost:3000"  # Add local development
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "max_age": 3600
    }
})


# Initialize detector with more lenient thresholds
pose_detector = PoseFallDetector(
    fall_threshold=0.2,  # More sensitive
    ground_threshold=0.7,
    detection_confidence=0.3,  # Lower threshold
    tracking_confidence=0.3
)
frame_count = 0

@app.route('/api/hello')
def hello():
    return jsonify(message="Hello from backend!")



@app.route('/api/toggle_pause', methods=['POST'])
def toggle_pause():
    pose_detector.toggle_pause()
    return jsonify({'paused': pose_detector.paused})

@app.route('/api/detect_fall', methods=['POST'])
def detect_fall():
    try:
        data = request.get_json()
        logging.info("Received detect_fall request")
        
        if not data:
            logging.error("No JSON data received")
            return jsonify({'error': 'No data received'}), 400
            
        frame_data = data.get('frame')
        if not frame_data:
            logging.error("No frame data in request")
            return jsonify({'error': 'No frame data'}), 400

        # Log frame data length
        logging.info(f"Frame data length: {len(frame_data)}")
        
        # Process frame
        img_bytes = base64.b64decode(frame_data.split(',')[1])
        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        if frame is None:
            logging.error("Failed to decode frame")
            return jsonify({'error': 'Invalid frame data'}), 400
            
        # Log frame shape
        logging.info(f"Frame shape: {frame.shape}")
        
        annotated_frame, fallen = pose_detector.process_frame(frame)
        
        if annotated_frame is not None:
            _, buffer = cv2.imencode('.jpg', annotated_frame)
            annotated_frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            return jsonify({
                'fall_detected': fallen,
                'annotated_frame': f'data:image/jpeg;base64,{annotated_frame_base64}',
                'paused': pose_detector.paused
            })
        
        logging.error("No annotated frame returned")
        return jsonify({'error': 'Processing failed'}), 500
        
    except Exception as e:
        logging.exception("Error in detect_fall")
        return jsonify({'error': str(e)}), 500


@app.route('/api/get_previous_frames', methods=['GET'])
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
@app.teardown_appcontext
def cleanup(exception=None):
    pass
    #if hasattr(app, 'pose_detector'):
        #app.pose_detector.pose.close()
    #logging.info("Cleaned up PoseFallDetector")

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )


