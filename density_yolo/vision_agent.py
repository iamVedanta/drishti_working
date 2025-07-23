import cv2
from ultralytics import YOLO

model = YOLO("yolov8n.pt")

streams = [
    ("Camera 1", "http://192.168.0.109:8080/video"),
   
]

output_file = "people_count.txt"

def count_people(frame):
    results = model(frame)
    count = sum(1 for cls in results[0].boxes.cls if int(cls) == 0)
    return count, results[0].plot()

# Create a video reader for each camera
caps = [(name, cv2.VideoCapture(url)) for name, url in streams]

while True:
    all_counts = []
    for name, cap in caps:
        ret, frame = cap.read()
        if not ret:
            continue

        count, annotated_frame = count_people(frame)
        density = count / 5.0

        cv2.putText(annotated_frame, f"{name}: {count} people, {density:.2f}/m2",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        cv2.imshow(name, annotated_frame)
        all_counts.append(f"{name}:{count}")

    # Write to shared text file
    with open(output_file, "w") as f:
        f.write(",".join(all_counts))

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

for _, cap in caps:
    cap.release()

cv2.destroyAllWindows()
