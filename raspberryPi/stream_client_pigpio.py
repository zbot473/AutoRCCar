import io
import socket
import struct
import time
import picamera
import pigpio

pi = pigpio.pi()
pi.set_mode(13, pigpio.OUTPUT)
pi.set_mode(19, pigpio.OUTPUT)
pi.set_mode(26, pigpio.OUTPUT)
pi.set_mode(21, pigpio.OUTPUT)
pi.set_mode(20, pigpio.OUTPUT)
pi.set_mode(16, pigpio.OUTPUT)
pi.write(13, 1)
pi.write(21, 1)


# create socket and bind host
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Enter your IP Address \/ here
client_socket.connect(('192.168.1.142', 8000))
connection = client_socket.makefile('wb')

try:
    with picamera.PiCamera() as camera:
        camera.resolution = (320, 240)      # pi camera resolution
        camera.framerate = 15               # 15 frames/sec
        # give 2 secs for camera to initilize
        time.sleep(2)
        start = time.time()
        stream = io.BytesIO()

        # send jpeg format video stream
        for i in camera.capture_continuous(stream, 'jpeg', use_video_port=True):
            client_socket.setblocking(True)
            connection.write(struct.pack('<L', stream.tell()))
            connection.flush()
            stream.seek(0)
            connection.write(stream.read())
            if time.time() - start > 600:
                break
            client_socket.setblocking(False)
            try:
                data = client_socket.recv(256)
                print(data)
                if data == b"\x01":    # up
                     pi.write(19, 0)
                     pi.write(26, 1)
                     pi.write(16, 0)
                     pi.write(20, 0)
                elif data == b"\x02":  # down
                     pi.write(19, 1)
                     pi.write(26, 0)
                     pi.write(16, 0)
                     pi.write(20, 0)
                elif data == b"\x03":  # right
                     pi.write(16, 0)
                     pi.write(20, 1)
                elif data == b"\x04":  # left
                     pi.write(16, 1)
                     pi.write(20, 0)
                elif data == b"\x06":  # up and right
                     pi.write(19, 0)
                     pi.write(26, 1)
                     pi.write(16, 0)
                     pi.write(20, 1)
                elif data == b"\x07":  # up and left
                     pi.write(19, 0)
                     pi.write(26, 1)
                     pi.write(16, 1)
                     pi.write(20, 0)
                elif data == b"\x08":  # down and right
                     pi.write(19, 1)
                     pi.write(26, 0)
                     pi.write(16, 0)
                     pi.write(20, 1)
                elif data == b"\x09": # down and left
                    pi.write(19, 1)
                    pi.write(26, 0)
                    pi.write(16, 1)
                    pi.write(20, 0)

            except BlockingIOError:
                pi.write(16, 0)
                pi.write(20, 0)
                pi.write(19, 0)
                pi.write(26, 0)
            stream.seek(0)
            stream.truncate()
    connection.write(struct.pack('<L', 0))
finally:
    connection.close()
    client_socket.close()