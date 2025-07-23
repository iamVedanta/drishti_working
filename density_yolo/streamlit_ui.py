import cv2
from ultralytics import YOLO

# Load YOLOv8 model
model = YOLO("yolov8n.pt")  # Make sure this file exists in your directory

# IP Webcam stream from phone (use .mjpg and FFMPEG)
streams = [
    ("Camera 1", "http://192.168.0.109:8080/video.mjpg")  # Adjust IP if needed
]

output_file = "people_count.txt"

def count_people(frame):
    # Run YOLO model on the frame
    results = model(frame)
    
    # Count the number of detections with class == 0 (person)
    count = sum(1 for cls in results[0].boxes.cls if int(cls) == 0)
    
    # Return count and annotated frame
    return count, results[0].plot()

# Open video capture for each stream using FFMPEG backend
caps = [(name, cv2.VideoCapture(url, cv2.CAP_FFMPEG)) for name, url in streams]

# Check if all cameras opened successfully
for name, cap in caps:
    if not cap.isOpened():
        print(f"Failed to open stream for {name}")
        exit()

while True:
    all_counts = []

    for name, cap in caps:
        ret, frame = cap.read()
        if not ret:
            print(f"Failed to grab frame from {name}")
            continue

        count, annotated_frame = count_people(frame)
        density = count / 5.0  # Example density calculation

        # Display person count and density
        cv2.putText(annotated_frame, f"{name}: {count} people, {density:.2f}/m2",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        # Show video
        cv2.imshow(name, annotated_frame)

        # Save count
        all_counts.append(f"{name}:{count}")

    # Write counts to text file
    with open(output_file, "w") as f:
        f.write(",".join(all_counts))

    # Quit with 'q'
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

# Release resources
for _, cap in caps:
    cap.release()

cv2.destroyAllWindows()
