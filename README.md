# Interactive English Learning Quiz for Children

An interactive learning system that combines face recognition, gesture control, and TUIO markers to create an engaging English learning experience for children.

## 🌟 Features

- **Face Recognition Login**: Secure login system using facial recognition
- **Gender-Based Themes**: Dynamic GUI that changes colors (pink for girls, blue for boys)
- **Interactive Learning Mode**: Place TUIO markers (0-8) to learn words with images and sounds
- **Quiz Mode**: Test knowledge with gesture-based and laser pointer interactions
- **Circular Menu**: TUIO-controlled navigation menu
- **Progress Tracking**: Database system to track child progress and quiz results
- **Teacher Interface**: Dashboard for monitoring student performance

## 📋 Requirements

### Python Packages
Install required packages using:
```bash
pip install -r requirements.txt
```

### Key Dependencies
- `opencv-python` - Computer vision and camera access
- `face-recognition` - Face detection and recognition
- `mediapipe` - Hand gesture recognition
- `tkinter` - GUI framework (usually included with Python)
- `sqlite3` - Database (included with Python)

### System Requirements
- Python 3.8 or higher
- Webcam for face recognition
- Windows 10/11 (for C# TUIO application)
- reacTIVision for TUIO marker tracking (optional)

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Main GUI
```bash
python main_gui.py
```

Or use the batch file:
```bash
run_main_gui.bat
```

### 3. Using TUIO Markers

**Marker Functions:**
- **Marker 0-8**: Learning mode - Display images, play sounds, show words
- **Marker 9**: Face login
- **Marker 10**: Face signup/registration
- **Marker 11**: Start quiz mode
- **Marker 12**: Open circular menu
- **Marker 15**: Open main GUI
- **Marker 50**: Teacher marker (rotation control)

## 📁 Project Structure

```
Interactive learnig english quiz for children/
├── main_gui.py              # Main GUI application
├── face_auth.py             # Face recognition system
├── database.py              # Database management
├── control_database.py      # Database control tool
├── view_database.py         # Database viewer
├── quiz side/               # Quiz application
│   ├── quiz_app.py
│   ├── gesture_training_and_recognition.py
│   └── laser_detector.py
├── teacher_interface/       # Teacher dashboard
├── TUIO11_NET-master/       # C# TUIO application
└── reacTIVision-1.5.1-win64/ # TUIO marker tracking
```

## 🎮 Usage

### Login/Signup
1. Click "Face Login" or place **Marker 9** for login
2. Click "Sign Up" or place **Marker 10** for registration
3. System will recognize face and apply appropriate theme

### Learning Mode
1. Click "Start Learning Mode" or place **Marker 11**
2. Place markers 0-8 on the table
3. System displays images, plays sounds, and shows words

### Quiz Mode
1. Click "Start Quiz Mode" or place **Marker 11**
2. Use hand gestures (swipe left/right) for gesture questions
3. Use laser pointer for selection questions
4. Press 'q' to quit

### Database Management
- **View Database**: `python view_database.py` or `view_database.bat`
- **Control Database**: `python control_database.py` or `control_database.bat`

## 🎨 Theme System

The GUI automatically changes colors based on the logged-in child's gender:
- **Girls**: Pink theme (#ffe4e1 background, #ff69b4 header)
- **Boys**: Blue/Gray theme (#2c3e50 background, #34495e header)

## 📊 Database

The system uses SQLite database (`children.db`) to store:
- Child information (name, gender, registration date)
- Face encodings for recognition
- Quiz results and progress tracking

### Database Tools
- **Viewer**: Interactive tool to browse database
- **Controller**: Full CRUD operations (Create, Read, Update, Delete)

## 🔧 Configuration

### Camera Settings
Edit `face_auth.py` to change camera index:
```python
auth = FaceAuthManager(camera_index=0)  # Change 0 to 1, 2, etc.
```

### Socket Ports
- **C# Communication**: Port 8888
- **GUI Login Updates**: Port 8889
- **Teacher Interface**: Port 5000

## 📝 Development

### Adding New Features
1. Follow the existing code structure
2. Update database schema if needed
3. Test with both GUI and TUIO markers
4. Update documentation

### Database Schema
- `children` table: Child information
- `face_encodings` table: Face recognition data
- `quiz_results` table: Quiz attempt records

## 🐛 Troubleshooting

### Face Recognition Not Working
- Ensure camera is connected and accessible
- Install `dlib` properly (may need Visual C++ Build Tools on Windows)
- Check camera permissions

### TUIO Markers Not Detected
- Ensure reacTIVision is running
- Check camera calibration
- Verify marker IDs are correct

### Database Issues
- Use `view_database.py` to check database
- Use `control_database.py` to manage data
- Database file: `children.db`

## 📄 License

This project is for educational purposes.

## 👥 Contributors

- Salah El Dein

## 🔗 Repository

GitHub: https://github.com/29SalahMo/Interactive-learnig

## 📚 Documentation

- `DATABASE_GUIDE.md` - Complete database documentation
- `GITHUB_SETUP.md` - GitHub setup instructions
- `SOCKET_CODE_LOCATIONS.md` - Socket communication details

## 🎯 Future Enhancements

- [ ] Multi-language support
- [ ] Advanced analytics
- [ ] Cloud database integration
- [ ] Mobile app companion
- [ ] More interactive games

---

**Note**: This system requires proper camera setup and TUIO marker tracking for full functionality. Some features may require additional hardware setup.
