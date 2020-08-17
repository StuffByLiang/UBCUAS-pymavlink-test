from pymavlink import mavutil
import time
from src.telemetry import Telemetry

# connect to autopilot system
mavlink_connection = mavutil.mavlink_connection('tcp:164.3.0.3:5760', retries=10)
# mavlink_connection = mavutil.mavlink_connection('udp:127.0.0.1:14550', retries=10)

# wait for heartbeat from system
mavlink_connection.wait_heartbeat()
print("Heartbeat from system (system %u component %u)" % (mavlink_connection.target_system, mavlink_connection.target_component))

telemetry = Telemetry(mavlink_connection)

# debugging variables
last_recieved_time = time.time()
begin_time = time.time()
time_usec_begin = mavlink_connection.recv_match(type="GPS_RAW_INT", blocking=True).time_usec/1000000

"""
if you comment the following code out, you'll notice that from the main thread's
GPS_RAW_INT time_usec data does not reflect real time data

"""
telemetry.start_polling()

# MAIN THREAD LOOP (i want to print out stuff every 2 seconds)
while True:
    # try: 
    #     altitude=mavlink_connection.messages['GPS_RAW_INT'].alt  # Note, you can access message fields as attributes!
    #     timestamp=mavlink_connection.time_since('GPS_RAW_INT')
    #     print(altitude)
    #     print(timestamp)
    # except:
    #     print('No GPS_RAW_INT message received')
    
    try:
        # print(mavlink_connection.location()) # this helper function calls recv_match(type="GPS_RAW_INT")
        msg = mavlink_connection.recv_match(type="GPS_RAW_INT", blocking=True)
        print("\nMain thread msg recieved after " + str(time.time() - last_recieved_time) + " seconds")
        time_lag = (time.time() - begin_time) - (msg.time_usec/1000000 - time_usec_begin)
        print(msg) # trys to read GPS_RAW_INT and blocks
        print("this msg was sent: " + str(time_lag) + " seconds ago from the autopilot")
        last_recieved_time = time.time()
        
    except Exception as e:
        print(e)
        pass
    time.sleep(2) # runs every 2 seconds