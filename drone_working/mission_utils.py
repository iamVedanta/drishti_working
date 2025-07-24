from dronekit import Command
from pymavlink import mavutil
from math import radians, cos, sin, asin, sqrt

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return R * c

def create_mission(vehicle, target_lat, target_lon):
    altitude = 2  # Target altitude (meters)

    cmds = vehicle.commands
    cmds.clear()
    cmds.download()
    cmds.wait_ready()

    home = vehicle.location.global_frame
    home_lat = home.lat
    home_lon = home.lon

    print(f"[?] Detected home location: Latitude = {home_lat}, Longitude = {home_lon}")
    confirm = input("Is this correct? (y/n): ").strip().lower()

    if confirm != 'y':
        print("✖ Mission creation aborted. Please set correct home location.")
        return

    # 1. TAKEOFF
    cmds.add(Command(
        0, 0, 0,
        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
        0, 1,
        altitude, 0, 0, 0,
        home_lat, home_lon, altitude
    ))

    # 2. LOITER_TIME (3 sec) at takeoff
    cmds.add(Command(
        0, 0, 0,
        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
        mavutil.mavlink.MAV_CMD_NAV_LOITER_TIME,
        0, 1,
        3, 0, 0, 0,
        home_lat, home_lon, altitude
    ))

    # 3. Fly to waypoint
    cmds.add(Command(
        0, 0, 0,
        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
        mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
        0, 1,
        0, 0, 0, 0,
        target_lat, target_lon, altitude
    ))

    # 4. LOITER_TIME at waypoint (3 sec)
    cmds.add(Command(
        0, 0, 0,
        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
        mavutil.mavlink.MAV_CMD_NAV_LOITER_TIME,
        0, 1,
        3, 0, 0, 0,
        target_lat, target_lon, altitude
    ))

    # 5. DO_SET_SERVO (channel 7, PWM 2000)
    cmds.add(Command(
        0, 0, 0,
        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
        mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
        0, 1,
        7, 2000, 0, 0,
        0, 0, 0
    ))

    # 6. LOITER_TIME after action
    cmds.add(Command(
        0, 0, 0,
        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
        mavutil.mavlink.MAV_CMD_NAV_LOITER_TIME,
        0, 1,
        3, 0, 0, 0,
        target_lat, target_lon, altitude
    ))

    # 7. RTL (return to launch)
    cmds.add(Command(
        0, 0, 0,
        mavutil.mavlink.MAV_FRAME_MISSION,
        mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH,
        0, 1,
        0, 0, 0, 0,
        0, 0, 0
    ))

    cmds.upload()
    print("[✓] Mission created and uploaded successfully.")
