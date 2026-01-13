"""
Circular Menu System controlled by TUIO Markers
A radial menu interface that responds to marker placement for easy navigation
"""
import tkinter as tk
from tkinter import Canvas
import math
import threading
import socket
import struct
import time
from typing import Dict, List, Callable, Optional, Tuple


class CircularMenu:
    """
    Circular/Radial menu controlled by TUIO markers
    Displays menu items in a circle and detects marker selection
    """
    
    def __init__(self, root: tk.Tk, menu_items: List[Dict], tuio_port: int = 3333, enable_mouse: bool = False):
        """
        Initialize circular menu
        
        Args:
            root: Tkinter root window
            menu_items: List of menu items, each with:
                - 'label': Display text
                - 'action': Callback function to execute
                - 'icon': Optional icon/emoji
                - 'color': Optional color for the sector
            tuio_port: TUIO UDP port (default 3333)
            enable_mouse: Enable mouse click testing (default False)
        """
        self.root = root
        self.menu_items = menu_items
        self.tuio_port = tuio_port
        self.num_items = len(menu_items)
        self.enable_mouse = enable_mouse
        
        # Menu geometry
        self.center_x = 400
        self.center_y = 400
        self.radius = 300
        self.inner_radius = 100
        
        # Marker tracking
        self.active_markers: Dict[int, Dict] = {}  # session_id -> marker_data
        self.marker_12_angle = None  # Rotation angle of marker 12 (navigation)
        self.selected_sector = None
        self.selection_time = None
        self.selection_delay = 1.0  # Hold marker for 1 second to select (not used with marker 12 rotation)
        
        # Visual feedback
        self.hovered_sector = None
        self.animation_angle = 0
        
        # TUIO socket
        self.tuio_socket = None
        self.running = True
        
        # Setup UI
        self.setup_canvas()
        
        # Enable mouse testing if requested (after canvas is created)
        if enable_mouse:
            self.enable_mouse_control()
        
        # Start TUIO listener
        self.start_tuio_listener()
        
        # Start animation loop
        self.animate()
    
    def setup_canvas(self):
        """Setup the canvas for drawing the circular menu"""
        self.canvas = Canvas(
            self.root,
            width=800,
            height=800,
            bg='#1a1a2e',
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Draw initial menu
        self.draw_menu()
    
    def enable_mouse_control(self):
        """Enable mouse click control for testing"""
        def on_click(event):
            # Convert mouse coordinates to normalized (0-1)
            x = event.x / 800.0
            y = event.y / 800.0
            
            # Process as marker
            self.process_marker(999, x, y, 0.0)  # Use ID 999 for mouse
        
        def on_motion(event):
            # Convert mouse coordinates to normalized (0-1)
            x = event.x / 800.0
            y = event.y / 800.0
            
            # Check which sector
            sector = self.get_sector_from_position(x, y)
            if sector is not None:
                self.hovered_sector = sector
                self.draw_menu()
        
        self.canvas.bind("<Button-1>", on_click)
        self.canvas.bind("<Motion>", on_motion)
        
        # Add instruction text
        self.canvas.create_text(
            400, 50,
            text="Mouse Mode: Click on a sector to select",
            font=('Arial', 12),
            fill='#00d4ff',
            tags='instruction'
        )
    
    def draw_menu(self):
        """Draw the circular menu"""
        self.canvas.delete("all")
        
        # Draw center circle
        self.canvas.create_oval(
            self.center_x - self.inner_radius,
            self.center_y - self.inner_radius,
            self.center_x + self.inner_radius,
            self.center_y + self.inner_radius,
            fill='#16213e',
            outline='#0f3460',
            width=3
        )
        
        # Draw center text
        self.canvas.create_text(
            self.center_x,
            self.center_y,
            text="MENU",
            font=('Arial', 24, 'bold'),
            fill='white'
        )
        
        # Calculate angle per sector
        angle_step = 360 / self.num_items
        
        # Draw sectors
        for i, item in enumerate(self.menu_items):
            start_angle = i * angle_step - 90  # Start from top
            end_angle = (i + 1) * angle_step - 90
            
            # Convert to radians
            start_rad = math.radians(start_angle)
            end_rad = math.radians(end_angle)
            
            # Determine if this sector is hovered or selected
            is_hovered = self.hovered_sector == i
            is_selected = self.selected_sector == i
            
            # Color
            color = item.get('color', '#0f3460')
            if is_selected:
                color = '#e94560'  # Red for selected
            elif is_hovered:
                color = '#533483'  # Purple for hovered
            
            # Draw sector
            self.draw_sector(
                self.center_x,
                self.center_y,
                self.inner_radius,
                self.radius,
                start_rad,
                end_rad,
                fill=color,
                outline='#16213e',
                width=2
            )
            
            # Draw label
            mid_angle = math.radians((start_angle + end_angle) / 2)
            label_radius = (self.inner_radius + self.radius) / 2
            label_x = self.center_x + label_radius * math.cos(mid_angle)
            label_y = self.center_y + label_radius * math.sin(mid_angle)
            
            # Icon (if provided)
            icon = item.get('icon', '')
            label_text = f"{icon}\n{item['label']}" if icon else item['label']
            
            self.canvas.create_text(
                label_x,
                label_y,
                text=label_text,
                font=('Arial', 14, 'bold'),
                fill='white',
                justify=tk.CENTER
            )
        
        # Draw active markers
        for marker_id, marker_data in self.active_markers.items():
            x = marker_data['x'] * 800  # Scale to canvas width
            y = marker_data['y'] * 800  # Scale to canvas height
            
            # Draw marker indicator
            self.canvas.create_oval(
                x - 15,
                y - 15,
                x + 15,
                y + 15,
                fill='#00d4ff',
                outline='white',
                width=2
            )
            
            # Draw marker ID
            self.canvas.create_text(
                x,
                y,
                text=str(marker_data.get('id', marker_id)),
                font=('Arial', 10, 'bold'),
                fill='black'
            )
        
        # Draw selection indicator
        if self.selected_sector is not None:
            start_angle = self.selected_sector * (360 / self.num_items) - 90
            end_angle = (self.selected_sector + 1) * (360 / self.num_items) - 90
            
            # Draw pulsing effect
            pulse_radius = self.radius + 20 * math.sin(self.animation_angle * 2)
            self.draw_sector(
                self.center_x,
                self.center_y,
                self.inner_radius,
                pulse_radius,
                math.radians(start_angle),
                math.radians(end_angle),
                fill='',
                outline='#e94560',
                width=4
            )
            
            # Draw instruction text
            instruction = "Rotate Marker 12 to navigate | Place Marker 13 to CONFIRM"
            self.canvas.create_text(
                self.center_x,
                self.center_y + self.radius + 40,
                text=instruction,
                font=('Arial', 11, 'bold'),
                fill='#2ecc71',
                justify=tk.CENTER
            )
            
            # Show current rotation angle if marker 12 is active
            if self.marker_12_angle is not None:
                angle_degrees = math.degrees(self.marker_12_angle) % 360
                angle_text = f"Marker 12 Rotation: {angle_degrees:.1f}°"
                self.canvas.create_text(
                    self.center_x,
                    self.center_y + self.radius + 60,
                    text=angle_text,
                    font=('Arial', 10),
                    fill='#f39c12',
                    justify=tk.CENTER
                )
    
    def draw_sector(self, cx, cy, r1, r2, start_angle, end_angle, **kwargs):
        """Draw a sector (arc between two radii)"""
        # Create points for the sector
        points = []
        
        # Inner arc points
        num_points = 20
        for i in range(num_points + 1):
            angle = start_angle + (end_angle - start_angle) * (i / num_points)
            x = cx + r1 * math.cos(angle)
            y = cy + r1 * math.sin(angle)
            points.append((x, y))
        
        # Outer arc points (reverse order)
        for i in range(num_points + 1):
            angle = end_angle - (end_angle - start_angle) * (i / num_points)
            x = cx + r2 * math.cos(angle)
            y = cy + r2 * math.sin(angle)
            points.append((x, y))
        
        # Draw polygon
        if points:
            self.canvas.create_polygon(points, **kwargs)
    
    def get_sector_from_position(self, x: float, y: float) -> Optional[int]:
        """
        Determine which sector a position (x, y) is in
        x, y are normalized coordinates (0-1)
        """
        # Convert to canvas coordinates
        canvas_x = x * 800
        canvas_y = y * 800
        
        # Calculate distance from center
        dx = canvas_x - self.center_x
        dy = canvas_y - self.center_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Check if within menu bounds
        if distance < self.inner_radius or distance > self.radius:
            return None
        
        # Calculate angle
        angle = math.degrees(math.atan2(dy, dx)) + 90  # Adjust to start from top
        if angle < 0:
            angle += 360
        
        # Determine sector
        sector = int((angle / 360) * self.num_items)
        if sector >= self.num_items:
            sector = self.num_items - 1
        
        return sector
    
    def process_marker(self, marker_id: int, x: float, y: float, angle: float):
        """Process marker position and check for selection"""
        # Marker 13 is the CONFIRM/SELECT button - execute action for currently selected sector
        if marker_id == 13:
            if self.selected_sector is not None:
                print(f"Marker 13 (CONFIRM) detected! Executing action for sector {self.selected_sector}: {self.menu_items[self.selected_sector]['label']}")
                self.execute_action(self.selected_sector)
                # Don't store marker 13 as active marker, it's just a button
                return
            else:
                print("Marker 13 (CONFIRM) detected but no sector selected. Rotate marker 12 first.")
                return
        
        # Marker 12 is used for navigation via rotation
        if marker_id == 12:
            # Store marker 12's rotation angle for navigation
            self.marker_12_angle = angle
            # Calculate which sector based on rotation angle
            # TUIO angle is in radians, convert to degrees
            angle_degrees = math.degrees(angle) % 360
            # Map angle to sector (0-360 degrees to 0-num_items)
            sector = int((angle_degrees / 360.0) * self.num_items) % self.num_items
            self.selected_sector = sector
            self.hovered_sector = sector
            print(f"Marker 12 rotation: {angle_degrees:.1f}° → Sector {sector}: {self.menu_items[sector]['label']}. Place marker 13 to confirm.")
            # Don't store marker 12 position, we only care about its rotation
            self.draw_menu()
            return
        
        # For all other markers, store their data (for visualization)
        self.active_markers[marker_id] = {
            'x': x,
            'y': y,
            'angle': angle,
            'id': marker_id
        }
        
        # Only update selection based on marker 12 rotation, not position
        # So we ignore position-based selection for other markers
        self.draw_menu()
    
    def remove_marker(self, marker_id: int):
        """Remove a marker from tracking"""
        # Marker 13 doesn't need to be tracked (it's just a button)
        if marker_id == 13:
            return
        
        # Marker 12 controls selection via rotation, clear it when removed
        if marker_id == 12:
            self.marker_12_angle = None
            self.selected_sector = None
            self.hovered_sector = None
            self.draw_menu()
            return
        
        # Remove other markers from visualization
        if marker_id in self.active_markers:
            del self.active_markers[marker_id]
        
        self.draw_menu()
    
    def execute_action(self, sector: int):
        """Execute the action for the selected sector"""
        if 0 <= sector < len(self.menu_items):
            item = self.menu_items[sector]
            action = item.get('action')
            if action:
                try:
                    action()
                except Exception as e:
                    print(f"Error executing action for {item['label']}: {e}")
    
    def start_tuio_listener(self):
        """Start listening for TUIO messages"""
        def listen_thread():
            try:
                self.tuio_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.tuio_socket.bind(('127.0.0.1', self.tuio_port))
                self.tuio_socket.settimeout(1.0)
                
                print(f"TUIO listener started on port {self.tuio_port}")
                
                while self.running:
                    try:
                        data, addr = self.tuio_socket.recvfrom(4096)
                        self.parse_tuio_message(data)
                    except socket.timeout:
                        continue
                    except Exception as e:
                        if self.running:
                            print(f"TUIO error: {e}")
            except Exception as e:
                print(f"Failed to start TUIO listener: {e}")
        
        thread = threading.Thread(target=listen_thread, daemon=True)
        thread.start()
    
    def parse_tuio_message(self, data: bytes):
        """Parse TUIO OSC message (simplified OSC parser)"""
        try:
            # OSC message format: address_pattern + type_tag + arguments
            # TUIO format: /tuio/2Dobj set s_id f_id xpos ypos angle ...
            
            if len(data) < 8:
                return
            
            # Find address pattern (null-terminated string)
            addr_end = data.find(b'\x00')
            if addr_end == -1:
                return
            
            address = data[:addr_end].decode('utf-8', errors='ignore')
            
            # Skip padding (OSC uses 4-byte alignment)
            type_tag_start = ((addr_end + 4) // 4) * 4
            
            if type_tag_start >= len(data):
                return
            
            # Find type tag (starts with ',', null-terminated)
            if data[type_tag_start] != ord(','):
                return
            
            type_tag_end = data.find(b'\x00', type_tag_start)
            if type_tag_end == -1:
                return
            
            type_tag = data[type_tag_start + 1:type_tag_end].decode('utf-8', errors='ignore')
            
            # Skip type tag padding
            args_start = ((type_tag_end + 4) // 4) * 4
            
            if address == '/tuio/2Dobj' and 'set' in type_tag:
                # Parse arguments: s_id (i), f_id (i), xpos (f), ypos (f), angle (f), ...
                # Format: iifff...
                args = []
                pos = args_start
                
                # Parse s_id (int32)
                if pos + 4 <= len(data):
                    s_id = struct.unpack('>i', data[pos:pos+4])[0]
                    pos += 4
                    
                    # Parse f_id (int32)
                    if pos + 4 <= len(data):
                        f_id = struct.unpack('>i', data[pos:pos+4])[0]
                        pos += 4
                        
                        # Parse xpos (float32)
                        if pos + 4 <= len(data):
                            xpos = struct.unpack('>f', data[pos:pos+4])[0]
                            pos += 4
                            
                            # Parse ypos (float32)
                            if pos + 4 <= len(data):
                                ypos = struct.unpack('>f', data[pos:pos+4])[0]
                                pos += 4
                                
                                # Parse angle (float32)
                                if pos + 4 <= len(data):
                                    angle = struct.unpack('>f', data[pos:pos+4])[0]
                                    
                                    # Process marker in main thread
                                    self.root.after(0, lambda sid=s_id, x=xpos, y=ypos, a=angle: 
                                                   self.process_marker(sid, x, y, a))
            
            elif address == '/tuio/2Dobj' and 'alive' in type_tag:
                # Handle alive message - markers that are still active
                # This would require parsing the list of session IDs
                pass
            
            elif address == '/tuio/2Dobj' and 'fseq' in type_tag:
                # Frame sequence - refresh display
                pass
                
        except Exception as e:
            # Silently ignore parsing errors (TUIO messages can be complex)
            pass
    
    def animate(self):
        """Animation loop"""
        self.animation_angle += 0.1
        if self.animation_angle > 2 * math.pi:
            self.animation_angle = 0
        
        # Redraw if needed
        if self.selected_sector is not None:
            self.draw_menu()
        
        # Schedule next frame
        self.root.after(50, self.animate)
    
    def cleanup(self):
        """Cleanup resources"""
        self.running = False
        if self.tuio_socket:
            self.tuio_socket.close()


def create_main_menu(root: tk.Tk, callbacks: Dict[str, Callable]) -> CircularMenu:
    """
    Create a main menu with standard options
    
    Args:
        root: Tkinter root
        callbacks: Dictionary with callback functions:
            - 'login': Face login callback
            - 'signup': Face signup callback
            - 'learning': Learning mode callback
            - 'quiz': Quiz mode callback
            - 'logout': Logout callback
    """
    menu_items = [
        {
            'label': 'Login',
            'icon': '🔐',
            'color': '#3498db',
            'action': callbacks.get('login', lambda: print("Login"))
        },
        {
            'label': 'Sign Up',
            'icon': '➕',
            'color': '#2ecc71',
            'action': callbacks.get('signup', lambda: print("Sign Up"))
        },
        {
            'label': 'Learning',
            'icon': '📚',
            'color': '#9b59b6',
            'action': callbacks.get('learning', lambda: print("Learning"))
        },
        {
            'label': 'Quiz',
            'icon': '🎯',
            'color': '#e67e22',
            'action': callbacks.get('quiz', lambda: print("Quiz"))
        },
        {
            'label': 'Logout',
            'icon': '🚪',
            'color': '#e74c3c',
            'action': callbacks.get('logout', lambda: print("Logout"))
        },
    ]
    
    return CircularMenu(root, menu_items)


# Example usage
if __name__ == "__main__":
    import sys
    
    root = tk.Tk()
    root.title("Circular Menu - TUIO Controlled")
    root.geometry("800x800")
    
    # Check for mouse mode flag
    enable_mouse = '--mouse' in sys.argv or '-m' in sys.argv
    
    # Define callbacks
    def login_action():
        print("Login action triggered!")
        # Add your login logic here
    
    def signup_action():
        print("Sign Up action triggered!")
        # Add your signup logic here
    
    def learning_action():
        print("Learning mode triggered!")
        # Add your learning mode logic here
    
    def quiz_action():
        print("Quiz mode triggered!")
        # Add your quiz mode logic here
    
    def logout_action():
        print("Logout action triggered!")
        # Add your logout logic here
    
    callbacks = {
        'login': login_action,
        'signup': signup_action,
        'learning': learning_action,
        'quiz': quiz_action,
        'logout': logout_action
    }
    
    # Create menu (with mouse mode if requested)
    menu = create_main_menu(root, callbacks)
    if enable_mouse:
        menu.enable_mouse = True
        menu.enable_mouse_control()
        print("Mouse mode enabled - Click on sectors to test!")
    
    # Handle window close
    def on_closing():
        menu.cleanup()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

