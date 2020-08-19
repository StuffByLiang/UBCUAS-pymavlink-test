# UBCUAS-pymavlink-test

Just testing to see if pymavlink (a low-level mavlink message processing library) can communicate with the autopilot of an unmanned aircraft for UBC UAS realtime

## The stupid problem I'm trying to fix
Basically, we request data stream from the drone in  `src/telemetry.py` in the `init_data_streams` method.

As multiple messages arrive at the specified frequency, calling `mavlink_connection.recv_match()` only gets the OLDEST ONE. which is a problem.

comment out line 25 `telemetry.start_polling()` in `app.py` to see problem in consoles

Ways to fix

1. Have another thread that constantly reads the data (ie the `poll_for_data` method in `src/telemetry.py`)

2. Somehow flush all other messages

FIXED implemented in app.py as `empty_socket`. thank god. took a while to figure out

## Getting Started

### Prerequisites

Install Docker on your system

### Run

```
docker-compose up
```