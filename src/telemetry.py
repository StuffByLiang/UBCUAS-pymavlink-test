from observable import Observable
from pymavlink import mavutil
from threading import Thread
import time

class Telemetry():
  def __init__(self, mavlink_connection):
    """
    Initializes telemetry data streams, observers, and listens to every incoming
    message from the autopilot

    Args:
        mavlink_connection (mavlink_connection): established mavlink connections
    """
    self.mavlink_connection = mavlink_connection
    self.heartbeat_lastsent = time.monotonic()
    self.event = Observable()
    self.init_data_streams()
    self.init_observers()
    self.thread = Thread(target=self.poll_for_data, daemon=True)
    self.thread.start()

  def init_data_streams(self):
    """
    Initializes message requests at a specific frequency
    """
    self.mavlink_connection.mav.request_data_stream_send(self.mavlink_connection.target_system, self.mavlink_connection.target_component,
                                         mavutil.mavlink.MAV_DATA_STREAM_ALL, 0, 0)
    self.set_message_interval(24, 1) # gps
    self.set_message_interval(0,  1) # heartbeat
    self.set_message_interval(74, 1) # vfr_hud

  def init_observers(self):
    """
    Initializes observers. These functions are called when a message has been recieved.

    example:
    @self.event.on('GPS_RAW_INT')
    def listener(msg):
        print(msg)
    """
    @self.event.on('HEARTBEAT')
    def listener(msg):
        # ignore groundstations
        if msg.type == mavutil.mavlink.MAV_TYPE_GCS:
            return
        print(msg)

  # set a message interval for a specific mavlink message
  def set_message_interval(self, messageid, interval):
    """
    requests message from autopilot at a specific interval (in hz)

    Args:
        messageid (number): mavlink message id
        interval (number): frequency of message in hz
    """    
    milliseconds = 0
    if interval == -1:
        milliseconds = -1
    elif milliseconds > 0:
        millseconds = (1000000 / interval)

    self.mavlink_connection.mav.command_long_send(
        self.mavlink_connection.target_system,
        self.mavlink_connection.target_component,
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, 0,
        messageid, # message id
        milliseconds, # interval in us
        0,
        0,
        0,
        0,
        0
    )

  def poll_for_data(self):
    """
    polls for any data from the autopilot. when recieved, triggers an event that
    notifies all observers listening to that specific msg type

    Raises:
        Exception: various exceptions
    """      
    try:
        while True:
            # send heartbeat to autopilot
            if time.monotonic() - self.heartbeat_lastsent > 1:
                self.mavlink_connection.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_GCS,
                                                mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, 0)
                self.heartbeat_lastsent = time.monotonic()

            # Sleep
            self.mavlink_connection.select(0.05)

            while True:
                try:
                    # try to get message
                    msg = self.mavlink_connection.recv_msg()
                except socket.error as error:
                    # If connection reset (closed), stop polling.
                    if error.errno == ECONNABORTED:
                        raise Exception('Connection aborting during send')
                    raise
                except mavutil.mavlink.MAVError as e:
                    # Avoid
                    #   invalid MAVLink prefix '73'
                    #   invalid MAVLink prefix '13'
                    print('mav recv error: %s' % str(e))
                    msg = None
                except Exception as e:
                    # Log any other unexpected exception
                    print('Exception while receiving message: ')
                    print(e)
                    msg = None
                if not msg:
                    # no message, restart polling loop
                    break

                print(msg.get_type() + " recieved")
                self.event.trigger(msg.get_type(), msg)

    except Exception as e:
        print('Exception in MAVLink input loop')
        print(e)
        return