# Hand Gesture Chess

A real-time chess game controlled by hand gestures using computer vision. Move chess pieces on a virtual board by pinching and dragging with your fingers, detected via webcam and MediaPipe.

## Features
- Play chess against the computer using hand gestures
- Drag and drop pieces with pinch gesture
- Visual feedback for selection and movement
- Real-time camera feed and board overlay

## Developer / Creator
- tubakhxn :)

## How to Fork
1. Click the "Fork" button on the GitHub repository page.
2. Clone your forked repository:
   ```
   git clone https://github.com/<your-username>/hand-gesture-chess.git
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the project:
   ```
   python main.py
   ```

## Project Structure
- `main.py` — Entry point for the application
- `chess_cv/` — Main chess logic and computer vision
  - `app.py` — Application logic
  - `chessboard.py` — Board rendering
  - `engine.py` — Chess engine
  - `gesture.py` — Gesture detection
  - `hand_tracker.py` — Hand tracking
  - `assets/` — Piece images and board assets
- `requirements.txt` — Python dependencies
- `hand_landmarker.task` — MediaPipe model file

## Requirements
- Python 3.7+
- OpenCV
- MediaPipe
- chess

## License
MIT License

---


