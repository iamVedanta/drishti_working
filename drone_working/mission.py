from dronekit import connect, VehicleMode, Command
from mission_utils import create_mission, haversine
import time

# vehicle = connect('127.0.0.1:14550', wait_ready=True)
vehicle = connect('tcp:127.0.0.1:5760', wait_ready=True)

# Set home
home_location = vehicle.location.global_relative_frame
print(f"Home set at: {home_location.lat}, {home_location.lon}")

def execute_mission(target_lat, target_lon):
    dist = haversine(home_location.lat, home_location.lon, target_lat, target_lon)
    print(f"Target distance: {dist:.2f} meters")
    if dist > 15:
        print("🚫 Target too far! Max allowed: 15m")
        return

    print("✅ Valid target. Creating mission...")
    create_mission(vehicle, target_lat, target_lon)

    # Arm and start mission
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True
    while not vehicle.armed:
        print("Waiting for arming...")
        time.sleep(1)

    vehicle.mode = VehicleMode("AUTO")
    print("🚀 Mission started.")






# # Example: target 10 meters North of home (adjust for your case)
# target_lat = home_location.lat + 0.00009  # ~10m North
# target_lon = home_location.lon            # same longitude

# execute_mission(target_lat, target_lon)

# # Optional: wait and monitor
# while vehicle.mode.name == "AUTO":
#     print(f"📡 Current location: {vehicle.location.global_relative_frame}")
#     time.sleep(2)

# # Close connection
# vehicle.close()