using System;
using System.Collections.Generic;
using System.Drawing;
using System.Media;
using System.Windows.Forms;
using TUIO;
using System.Net.Sockets;   // <-- added
using System.Text;          // <-- added
using System.Diagnostics;   // <-- for launching Python scripts
using System.IO;            // <-- for path handling

public class TuioSimple : Form, TuioListener
{
    private TuioClient client;
    private Dictionary<long, DisplayObject> objects = new Dictionary<long, DisplayObject>();

    private Dictionary<int, string> imageFiles = new Dictionary<int, string>()
    {
        // Fruits
        {0, "images/banana.jpg"},
        {1, "images/apple.jpg"},
        {2, "images/orange.jpeg"},
        // Animals
        {3, "images/elephant.jpg"},
        {4, "images/dog.jpg"},
        {5, "images/cat.jpg"},
        // Shapes
        {6, "images/circle.jpeg"},
        {7, "images/rectangle.jpeg"},
        {8, "images/triangle.jpeg"}
    };

    private Dictionary<int, string> soundFiles = new Dictionary<int, string>()
    {
        {0, "sounds/banana.wav"}, {1, "sounds/apple.wav"}, {2, "sounds/orange.wav"},
        {3, "sounds/elephant.wav"}, {4, "sounds/dog.wav"}, {5, "sounds/cat.wav"},
        {6, "sounds/circle.wav"}, {7, "sounds/rectangle.wav"}, {8, "sounds/triangle.wav"}
    };

    private Dictionary<int, string> wordFiles = new Dictionary<int, string>()
    {
        {0, "words/banana.txt"}, {1, "words/apple.txt"}, {2, "words/orange.txt"},
        {3, "words/elephant.txt"}, {4, "words/dog.txt"}, {5, "words/cat.txt"},
        {6, "words/circle.txt"}, {7, "words/rectangle.txt"}, {8, "words/triangle.txt"}
    };

    private Dictionary<int, Image> loadedImages = new Dictionary<int, Image>();
    private SoundPlayer player = new SoundPlayer();
    private bool firstMarkerAppeared = false;

    // ============================  
    //  Teacher Marker Integration
    // ============================
    private TcpClient teacherClient;
    private NetworkStream teacherStream;

    // Change this if you decide to use another fiducial ID as teacher marker
    private const int TEACHER_MARKER_ID = 50;

    private class DisplayObject
    {
        public Image Image;
        public string Word;
        public int X, Y, Width, Height;
    }

    public TuioSimple()
    {
        this.Text = "TUIO Teaching English";
        this.Size = new Size(1200, 600);

        // Load all images into memory
        foreach (var kv in imageFiles)
        {
            if (System.IO.File.Exists(kv.Value))
                loadedImages[kv.Key] = Image.FromFile(kv.Value);
            else
                MessageBox.Show("Image not found: " + kv.Value);
        }

        // Connect to TUIO
        client = new TuioClient(3333);
        client.addTuioListener(this);
        client.connect();

        // ============================
        // Connect to Python Teacher UI
        // ============================
        try
        {
            teacherClient = new TcpClient("localhost", 5000);
            teacherStream = teacherClient.GetStream();
            Console.WriteLine("Connected to Python Teacher Interface");
        }
        catch (Exception ex)
        {
            Console.WriteLine("Failed to connect to Python: " + ex.Message);
            teacherClient = null;
            teacherStream = null;
        }
    }

    public void addTuioObject(TuioObject obj)
    {
        int id = obj.SymbolID;

        // ============================
        // Teacher marker: only send angle, don't show image/sound
        // ============================
        if (id == TEACHER_MARKER_ID)
        {
            SendTeacherAngle(obj);
            // Do NOT create a DisplayObject for the teacher marker,
            // it is only used to control the teacher interface.
            return;
        }

        // ============================
        // Login / Sign-up / Quiz markers
        // ============================
        // Marker 9  -> Start face LOGIN (face_login.py)
        // Marker 10 -> Start face SIGN UP / registration (face_register.py)
        // Marker 11 -> Start QUIZ (start_quiz.py -> quiz side/quiz_app.py)
        // Marker 12 -> Open CIRCULAR MENU (open_circular_menu.py -> main_gui.py)
        // Marker 15 -> Open MAIN GUI (open_main_gui.py -> main_gui.py)
        if (id == 9)
        {
            Console.WriteLine("*** Marker 9 (LOGIN) detected! ***");
            LaunchPythonScript("face_login.py", "Login marker (9) detected");
            // Don't modify display - keep current content visible
            return;
        }
        else if (id == 10)
        {
            Console.WriteLine("*** Marker 10 (SIGNUP) detected! ***");
            LaunchPythonScript("face_register.py", "Sign-up marker (10) detected");
            // Don't modify display - keep current content visible
            return;
        }
        else if (id == 11)
        {
            Console.WriteLine("*** Marker 11 (QUIZ) detected! ***");
            LaunchPythonScript("start_quiz.py", "Quiz marker (11) detected");
            // Don't modify display - keep current content visible
            return;
        }
        else if (id == 12)
        {
            Console.WriteLine("*** Marker 12 (CIRCULAR MENU) detected! ***");
            LaunchPythonScript("open_circular_menu.py", "Circular menu marker (12) detected");
            // Don't modify display - keep current content visible
            return;
        }
        else if (id == 15)
        {
            Console.WriteLine("*** Marker 15 (MAIN GUI) detected! ***");
            LaunchPythonScript("open_main_gui.py", "Main GUI marker (15) detected");
            // Don't modify display - keep current content visible
            return;
        }

        // ============================
        // Normal learning markers (kids)
        // ============================
        if (!firstMarkerAppeared)
            firstMarkerAppeared = true;

        var dispObj = new DisplayObject();

        // Set image
        if (loadedImages.ContainsKey(id))
            dispObj.Image = loadedImages[id];

        // Set word
        if (wordFiles.ContainsKey(id))
        {
            string path = wordFiles[id];
            if (System.IO.File.Exists(path))
                dispObj.Word = System.IO.File.ReadAllText(path);
        }

        // Set fixed position
        dispObj.X = 100;
        dispObj.Y = 70;
        dispObj.Width = 450;
        dispObj.Height = 350;

        // Play sound
        if (soundFiles.ContainsKey(id))
        {
            string path = soundFiles[id];
            if (System.IO.File.Exists(path))
            {
                player.SoundLocation = path;
                player.Play();
            }
        }

        objects[obj.SessionID] = dispObj;
        Invalidate();
    }

    // Called when a TUIO object is updated (moved/rotated)
    public void updateTuioObject(TuioObject obj)
    {
        // Only care about rotation of the teacher marker
        if (obj.SymbolID == TEACHER_MARKER_ID)
        {
            SendTeacherAngle(obj);
        }
        // For markers 9/10/11/12/15 (login/signup/quiz/circular-menu/main-gui), do nothing - don't trigger display updates
        else if (obj.SymbolID == 9 || obj.SymbolID == 10 || obj.SymbolID == 11 || obj.SymbolID == 12 || obj.SymbolID == 15)
        {
            // Do nothing - these markers only launch scripts, don't affect display
            return;
        }
        // For student markers you currently ignore minor movement/rotation
        // which is fine for now.
    }

    public void removeTuioObject(TuioObject obj)
    {
        // Don't trigger display update for markers 9/10/11/12/15 (login/signup/quiz/circular-menu/main-gui) or teacher marker
        // These markers don't have DisplayObjects and shouldn't affect the screen
        if (obj.SymbolID == 9 || obj.SymbolID == 10 || obj.SymbolID == 11 || obj.SymbolID == 12 || obj.SymbolID == 15 || obj.SymbolID == TEACHER_MARKER_ID)
        {
            return;
        }

        if (objects.ContainsKey(obj.SessionID))
            objects.Remove(obj.SessionID);
        Invalidate();
    }

    public void addTuioCursor(TuioCursor c) { }
    public void updateTuioCursor(TuioCursor c) { }
    public void removeTuioCursor(TuioCursor c) { }
    public void addTuioBlob(TuioBlob b) { }
    public void updateTuioBlob(TuioBlob b) { }
    public void removeTuioBlob(TuioBlob b) { }
    public void refresh(TuioTime frameTime) { }

    // =========================================
    // Helper: launch Python face auth scripts
    // =========================================
    private void LaunchPythonScript(string scriptName, string logPrefix)
    {
        try
        {
            // Try to find the project root by looking for the Python script
            // Application.StartupPath = ...\TUIO11_NET-master\TUIO11_NET-master update\bin\Debug
            // Try 4 levels up first (most likely)
            string projectRoot = Path.GetFullPath(
                Path.Combine(Application.StartupPath, @"..\..\..\..")
            );
            string scriptPath = Path.Combine(projectRoot, scriptName);

            // If not found at 4 levels, try 3 levels (alternative structure)
            if (!File.Exists(scriptPath))
            {
                projectRoot = Path.GetFullPath(
                    Path.Combine(Application.StartupPath, @"..\..\..")
                );
                scriptPath = Path.Combine(projectRoot, scriptName);
            }

            // If still not found, try current directory
            if (!File.Exists(scriptPath))
            {
                projectRoot = Application.StartupPath;
                scriptPath = Path.Combine(projectRoot, scriptName);
            }

            // Debug: Show paths
            Console.WriteLine($"{logPrefix}: Looking for script at: {scriptPath}");
            Console.WriteLine($"{logPrefix}: Project root: {projectRoot}");
            Console.WriteLine($"{logPrefix}: Startup path: {Application.StartupPath}");

            if (!File.Exists(scriptPath))
            {
                string errorMsg = $"Script not found at:\n{scriptPath}\n\nProject root: {projectRoot}";
                Console.WriteLine($"{logPrefix}: {errorMsg}");
                MessageBox.Show(errorMsg, "Script Not Found", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }

            // Check if Python is available
            try
            {
                var pythonCheck = new ProcessStartInfo
                {
                    FileName = "python",
                    Arguments = "--version",
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    CreateNoWindow = true
                };
                var proc = Process.Start(pythonCheck);
                proc.WaitForExit(2000);
            }
            catch (Exception pyEx)
            {
                string errorMsg = $"Python is not available in PATH.\n\nError: {pyEx.Message}\n\nPlease ensure Python is installed and added to PATH.";
                Console.WriteLine($"{logPrefix}: {errorMsg}");
                MessageBox.Show(errorMsg, "Python Not Found", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }

            ProcessStartInfo psi = new ProcessStartInfo
            {
                FileName = "python",
                Arguments = $"\"{scriptPath}\"",
                WorkingDirectory = projectRoot,
                UseShellExecute = true,
                CreateNoWindow = false  // Show window so user can see the script running
            };

            Process.Start(psi);
            Console.WriteLine($"{logPrefix}: Successfully started {scriptName}");
            
            // Optional: Show brief confirmation
            // MessageBox.Show($"Launching {scriptName}...", "Marker Detected", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }
        catch (Exception ex)
        {
            string errorMsg = $"Error launching {scriptName}:\n{ex.Message}";
            Console.WriteLine($"{logPrefix}: {errorMsg}");
            MessageBox.Show(errorMsg, "Launch Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
    }

    // =========================================
    // Helper: send teacher marker angle to Python
    // =========================================
    private void SendTeacherAngle(TuioObject obj)
    {
        if (teacherStream == null)
            return;

        // TUIO gives angle in radians → convert to degrees
        double angleDeg = obj.Angle * (180.0 / Math.PI);
        string msg = angleDeg.ToString("F2");  // e.g. "123.45"

        byte[] data = Encoding.UTF8.GetBytes(msg);

        try
        {
            teacherStream.Write(data, 0, data.Length);
            Console.WriteLine("Sent angle to Python: " + msg);
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error sending angle to Python: " + ex.Message);
        }
    }

    protected override void OnPaint(PaintEventArgs e)
    {
        Graphics g = e.Graphics;
        g.Clear(Color.Black);

        if (objects.Count == 0)
        {
            // welcome message
            string msg = "Welcome to the Interactive Learning Program!\nPlace any marker to start.";
            using (Font f = new Font("Arial", 32, FontStyle.Bold))
            {
                SizeF textSize = g.MeasureString(msg, f);
                float x = (ClientSize.Width - textSize.Width) / 2;
                float y = (ClientSize.Height - textSize.Height) / 2;
                g.DrawString(msg, f, Brushes.White, x, y);
            }
        }
        else
        {
            foreach (var dispObj in objects.Values)
            {
                if (dispObj.Image != null)
                {
                    g.DrawImage(dispObj.Image, dispObj.X, dispObj.Y, dispObj.Width, dispObj.Height);
                }

                if (!string.IsNullOrEmpty(dispObj.Word))
                {
                    using (Font f = new Font("Arial", 32, FontStyle.Bold))
                    {
                        SizeF textSize = g.MeasureString(dispObj.Word, f);
                        float x = dispObj.X + (dispObj.Width - textSize.Width) / 2;
                        float y = dispObj.Y + dispObj.Height + 10;
                        g.DrawString(dispObj.Word, f, Brushes.Red, x, y);
                    }
                }
            }
        }
    }

    [STAThread]
    public static void Main()
    {
        Application.EnableVisualStyles();
        Application.Run(new TuioSimple());
    }
}
