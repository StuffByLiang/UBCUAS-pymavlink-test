from pymavlink import mavutil
import time

# connect to autopilot system
mavlink_connection = mavutil.mavlink_connection('tcp:164.2.0.3:5760', retries=10)

# wait for heartbeat from system
mavlink_connection.wait_heartbeat()
print("Heartbeat from system (system %u component %u)" % (mavlink_connection.target_system, mavlink_connection.target_component))
print('test')
# set a message interval for a specific mavlink message
def set_message_interval(messageid, interval):
    mavlink_connection.mav.command_long_send(
        mavlink_connection.target_system,
        mavlink_connection.target_component,
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, 0,
        messageid, # message id
        1000000 / interval, # interval us
        0,
        0,
        0,
        0,
        0
    )

# request telemetry data streams
set_message_interval(24, 1) # gps
# set_message_interval(0, 1)  # heartbeat
set_message_interval(74, 1) # vfr_hud

# print recieved data
while True:
    try:
        print(mavlink_connection.recv_match().to_dict())
    except:
        pass
    time.sleep(0.1)