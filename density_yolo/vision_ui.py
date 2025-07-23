import cv2
import threading
from ultralytics import YOLO
from PIL import Image, ImageTk
import tkinter as tk
import math
import time

# Load YOLO model and force it to GPU if available
model = YOLO("yolov8n.pt")
model.to("cuda")  # Remove this line if no GPU

# List of camera sources (IP cam or laptop cam with 0)
streams = [
    ("Camera 1", "http://192.168.0.109:8080/video"),
    ("Camera 2", 0),
    # ("Camera 3", "http://192.168.0.110:8080/video"), # Add more if needed
]

# Dicts to manage each feed
video_caps = {}
frame_labels = {}
count_labels = {}
people_counts = {}

# Count people using YOLOv8 (on GPU)
def count_people(frame):
    results = model(frame, device="cuda", verbose=False)
    count = sum(1 for cls in results[0].boxes.cls if int(cls) == 0)
    return count, results[0].plot()

# Threaded function to update each stream
def update_stream(name, cap, frame_label, count_label):
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.resize(frame, (640, 360))  # Resize for performance
        count, annotated_frame = count_people(frame)
        people_counts[name] = count

        # Convert frame to ImageTk format
        annotated_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(annotated_frame)
        imgtk = ImageTk.PhotoImage(image=img)

        # Update UI
        frame_label.imgtk = imgtk
        frame_label.configure(image=imgtk)
        count_label.config(text=f"{name}: {count} person(s)")

        time.sleep(0.05)  # ~20 FPS throttle

# Create Tkinter window
root = tk.Tk()
root.title("Security Dashboard - People Detection")
root.configure(bg="#222222")

# === Title Section ===
title = tk.Label(root, text="Live CCTV Monitoring Dashboard", font=("Segoe UI", 18, "bold"),
                 fg="white", bg="#222222")
title.pack(pady=10)

# === Frame Grid Section ===
grid_frame = tk.Frame(root, bg="#222222")
grid_frame.pack()

# Auto layout: arrange cameras in a grid
cols = 2  # You can change this
rows = math.ceil(len(streams) / cols)

for idx, (name, source) in enumerate(streams):
    cap = cv2.VideoCapture(source)
    video_caps[name] = cap
    people_counts[name] = 0

    row = idx // cols
    col = idx % cols

    cam_frame = tk.Frame(grid_frame, bg="#333333", bd=2, relief=tk.RIDGE)
    cam_frame.grid(row=row, column=col, padx=10, pady=10)

    label = tk.Label(cam_frame)
    label.pack()

    count_label = tk.Label(cam_frame, text=f"{name}: Loading...",
                           font=("Arial", 12), bg="#333333", fg="white")
    count_label.pack(pady=5)

    frame_labels[name] = label
    count_labels[name] = count_label

    thread = threading.Thread(target=update_stream, args=(name, cap, label, count_label))
    thread.daemon = True
    thread.start()

# === Total People Count Section ===
def update_total_count():
    total = sum(people_counts.values())
    total_label.config(text=f"Total People Across All Cameras: {total}")
    root.after(1000, update_total_count)

total_label = tk.Label(root, text="Total People Across All Cameras: 0",
                       font=("Segoe UI", 16, "bold"), fg="cyan", bg="#222222")
total_label.pack(pady=10)

update_total_count()
root.mainloop()

# Cleanup on exit
for cap in video_caps.values():
    cap.release()
cv2.destroyAllWindows()
