## Fall Detection System

## Description
This repository contains a real-time Fall Detection System that leverages computer vision and pose estimation techniques. The frontend is built with React and deployed on Vercel, while the Flask-based backend is deployed on Railway. It continuously processes frames from a connected camera stream, detects falls, and provides visual alerts when a fall event is identified. I worked on this for straight 3 days due to deadlines.

## Table of Contents
- [Features](#features)  
- [Project Architecture](#project-architecture)  
- [Prerequisites](#prerequisites)  
- [Installation](#installation)  
- [Usage](#usage)  
- [Deployment](#deployment)  
- [Screenshots and Videos](#screenshots-and-videos)  
- [Contributing](#contributing)  
- [License](#license)

## Features
- Real-time camera stream capture and processing  
- Pose estimation and fall detection using OpenCV and MediaPipe  
- Visual overlays for detected falls  
- Pause/resume functionality to inspect historical frames  
- Fully responsive React frontend  

## Project Architecture
**Frontend (Vercel)**  
- Developed with React and Axios for communicating with the backend  
- Displays camera feed, overlays annotated frames, and provides controls for pausing/resuming detection  

**Backend (Railway)**  
- Flask application for handling frame data  
- Uses OpenCV and MediaPipe for pose estimation and fall detection  
- Exposes REST endpoints for real-time fall detection, pausing functionality, and retrieving previous frames  

## Prerequisites
- [Node.js](https://nodejs.org/) (for the frontend)  
- [Python 3.10](https://www.python.org/) (for the backend)  
- A camera-enabled device (for real-time detection)  

## Installation
1. **Clone this repository**  
   ```bash
   git clone https://github.com/<your-username>/fall-detection-system.git
   ```
2. **Frontend Setup**  
   ```bash
   cd client
   npm install
   ```
3. **Backend Setup**  
   ```bash
   cd ../api
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

## Usage
1. **Start the Backend**  
   ```bash
   cd api
   source venv/bin/activate
   python app.py
   ```
2. **Start the Frontend**  
   ```bash
   cd ../client
   npm start
   ```
3. **Open the Application**  
   - Navigate to `http://localhost:3000` in your web browser  
   - Allow camera access when prompted  
   - Observe real-time video feed and detection overlays  

## Deployment
- **Frontend on Vercel:**  
  1. Pushed my frontend code to a GitHub repository and deployed directly from VS Studio to vercel.

- **Backend on Railway:**  
  1. Pushed my backend code to a GitHub repository and deployed on Railway due to storage limitations at Vercel but for some reason it's not wokring as expected but it is still under developement.  


## Screenshots and Videos
> **Note:** 
>  
> ```
<img src="https://github.com/user-attachments/assets/48d464cd-d08e-405c-92fa-75284bad0cfc" width="400" height="300" alt="Fall Detection System Screenshot"> 
 
<img src="https://github.com/user-attachments/assets/3e153bb8-6991-4e37-9459-8a864f49be5e" width="400" height="300" alt="Fall Detection System Demo"> 



> ```

## Contributing
Contributions and suggestions are always welcome. Feel free to open issues or submit pull requests. Please follow these steps if you’d like to contribute:  
1. Fork this repository  
2. Create a new branch (`git checkout -b feature-name`)  
3. Make your changes and commit them  
4. Push to your fork and open a pull request  

## License
This project is licensed under the [MIT License](LICENSE). Feel free to use and modify the code in accordance with the license terms.
