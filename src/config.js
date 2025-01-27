const API_URL = process.env.NODE_ENV === 'production' 
  ? 'https://fall-detection-system-production.up.railway.app/api'
  : 'http://localhost:5000/api';

export const endpoints = {
  detectFall: `${API_URL}/detect_fall`,
  togglePause: `${API_URL}/toggle_pause`,
  getPreviousFrames: `${API_URL}/get_previous_frames`
};

export { API_URL };