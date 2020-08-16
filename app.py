from pymavlink import mavutil
import time
from src.telemetry import Telemetry

# connect to autopilot system
mavlink_connection = mavutil.mavlink_connection('tcp:164.3.0.3:5760', retries=10)

# wait for heartbeat from system
mavlink_connection.wait_heartbeat()
print("Heartbeat from system (system %u component %u)" % (mavlink_connection.target_system, mavlink_connection.target_component))

telemetry = Telemetry(mavlink_connection)


# print recieved data
while True:
#     try:
#         print(mavlink_connection.recv_match().to_dict())
#     except:
#         pass
    time.sleep(1)