import cv2
import mediapipe as mp
import numpy as np
from collections import deque
import logging

class PoseFallDetector:
    def __init__(self, fall_threshold=0.3, ground_threshold=0.8, detection_confidence=0.5, tracking_confidence=0.5):
        """
        Initializes the PoseFallDetector with configurable thresholds and confidence levels.

        Args:
            fall_threshold (float): Threshold for vertical displacement to consider a fall.
            ground_threshold (float): Threshold to determine proximity to the ground.
            detection_confidence (float): Minimum confidence for pose detection.
            tracking_confidence (float): Minimum confidence for pose tracking.
        """
        # Configure logging
        logging.basicConfig(
            filename='pose_fall_detector.log',
            level=logging.INFO,
            format='%(asctime)s:%(levelname)s:%(message)s'
        )
        self.logger = logging.getLogger(__name__)

        # Initialize Mediapipe Pose
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )

        # Initialize frame buffer
        self.frame_buffer = deque(maxlen=150)  # 5 seconds at 30 fps
        self.fps = 30
        self.paused = False
        self.frame_count = 0

        # Thresholds for fall detection
        self.fall_threshold = fall_threshold
        self.ground_threshold = ground_threshold

    def process_frame(self, frame):
        """
        Processes a single video frame for fall detection.

        Args:
            frame (numpy.ndarray): The video frame to process.

        Returns:
            tuple: Annotated frame and a boolean indicating if a fall was detected.
        """
        try:
            if frame is None:
                self.logger.error("Received None frame")
                return None, False
            max_dimension = 640
            height, width = frame.shape[:2]
            if height > max_dimension or width > max_dimension:
                scale = max_dimension / max(height, width)
                frame = cv2.resize(frame, None, fx=scale, fy=scale)
            if not self.paused:
                self.frame_count += 1
                current_time = self.frame_count / self.fps

                # Convert the BGR frame to RGB for Mediapipe
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.pose.process(rgb_frame)
                annotated_frame = frame.copy()
                fallen = False

                if results.pose_landmarks:
                    landmarks = results.pose_landmarks.landmark

                    # Draw pose landmarks on the frame
                    self.mp_drawing.draw_landmarks(
                        annotated_frame,
                        results.pose_landmarks,
                        self.mp_pose.POSE_CONNECTIONS,
                        self.mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                        self.mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
                    )

                    # Validate presence of required landmarks
                    required_landmarks = [
                        self.mp_pose.PoseLandmark.NOSE.value,
                        self.mp_pose.PoseLandmark.LEFT_HIP.value,
                        self.mp_pose.PoseLandmark.RIGHT_HIP.value,
                        self.mp_pose.PoseLandmark.LEFT_SHOULDER.value,
                        self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value
                    ]

                    if all(landmarks[landmark].visibility > 0.5 for landmark in required_landmarks):
                        # Extract Y-coordinates of relevant landmarks
                        nose_y = landmarks[self.mp_pose.PoseLandmark.NOSE.value].y
                        left_hip_y = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y
                        right_hip_y = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y
                        left_shoulder_y = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y
                        right_shoulder_y = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y

                        # Calculate average Y-coordinates for hips and shoulders
                        avg_hip_y = (left_hip_y + right_hip_y) / 2
                        avg_shoulder_y = (left_shoulder_y + right_shoulder_y) / 2

                        # Method 1: Vertical displacement
                        vertical_displacement = avg_hip_y - avg_shoulder_y

                        # Method 2: Nose position relative to hips
                        nose_above_hips = nose_y > left_hip_y and nose_y > right_hip_y

                        # Method 3: Body angle
                        spine_vector = np.array([
                            landmarks[self.mp_pose.PoseLandmark.NOSE.value].y - landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y,
                            landmarks[self.mp_pose.PoseLandmark.NOSE.value].x - landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x
                        ])
                        angle = abs(np.degrees(np.arctan2(spine_vector[1], spine_vector[0])))

                        # Combine multiple detection methods
                        fallen = (
                            (vertical_displacement > self.fall_threshold and avg_hip_y > self.ground_threshold) or
                            nose_above_hips or
                            (angle > 60)  # Consider fallen if body is tilted more than 60 degrees
                        )

                        if fallen:
                            cv2.putText(
                                annotated_frame,
                                "FALL DETECTED!",
                                (10, 60),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1,
                                (0, 0, 255),
                                2
                            )
                            self.logger.info(f"Fall detected at {current_time:.2f} seconds.")

                # Add timer text to the frame
                self.logger.info(f"Processing frame: shape={frame.shape}")
                minutes = int(current_time // 60)
                seconds = int(current_time % 60)
                milliseconds = int((current_time % 1) * 100)
                timer_text = f'{minutes:02d}:{seconds:02d}.{milliseconds:02d}'
                cv2.putText(
                    annotated_frame,
                    timer_text,
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2
                )

                # Append the annotated frame and timestamp to the buffer
                self.frame_buffer.append((annotated_frame, current_time))
                return annotated_frame, fallen

            return None, False

        except Exception as e:
            self.logger.error(f"Error processing frame: {e}")
            return None, False

    def toggle_pause(self):
        """
        Toggles the paused state of the fall detector.
        """
        self.paused = not self.paused
        self.logger.info(f"Detection {'paused' if self.paused else 'resumed'}.")
        if self.paused:
            self.show_previous_5_seconds()

    def show_previous_5_seconds(self):
        """
        Displays the previous 5 seconds of video frames.
        """
        if not self.frame_buffer:
            self.logger.warning("Frame buffer is empty. No frames to display.")
            return

        try:
            for frame, timestamp in list(self.frame_buffer):
                cv2.imshow('Previous 5 Seconds', frame)
                if cv2.waitKey(int(1000 / self.fps)) & 0xFF == ord('q'):
                    self.logger.info("Playback interrupted by user.")
                    break
            cv2.destroyWindow('Previous 5 Seconds')
            self.logger.info("Finished displaying previous 5 seconds of footage.")
        except Exception as e:
            self.logger.error(f"Error displaying previous frames: {e}")

    def get_previous_frames(self):
        """
        Retrieves the list of previous frames.

        Returns:
            list: A list of tuples containing annotated frames and their timestamps.
        """
        return list(self.frame_buffer)

    def __del__(self):
        """
        Ensures that the Mediapipe Pose object is properly closed upon deletion.
        """
        if hasattr(self, 'pose'):
            self.pose.close()
            self.logger.info("Mediapipe Pose closed successfully.")