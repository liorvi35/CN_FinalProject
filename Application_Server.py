
import socket
import dash
import os
import ffmpeg_streaming
from ffmpeg_streaming import Formats, Bitrate, Representation, Size

# Set up the MPEG-DASH parameters
dash_folder = './'
dash_filename = 'mainfest.mpd'
segment_duration = 2000  # milliseconds
video = ffmpeg_streaming.input('/home/yoad/Desktop/final_proj/video.mp4')

# Read the video file
with open('video.mp4', 'rb') as f:
    video_data = f.read()

'''
# Set up the MPEG-DASH representation
dash_representation = dash.MPD_REPRESENTATION()
dash_representation.add_segment_template('$RepresentationID$/$Number$.m4s')
dash_representation.add_base_url(dash.BaseURL(dash_folder + '/'))

# Create the MPEG-DASH manifest
dash_manifest = dash.MPD()
dash_manifest.add_representation(dash_representation)
dash_manifest.add_period(dash.MPD_PERIOD())
'''

dash = video.dash(Formats.h264())
dash.auto_generate_representations()
dash.output('/home/yoad/Desktop/final_proj/manifest.mpd')
dash_manifest = '/home/yoad/Desktop/final_proj/manifest.mpd'

with open(os.path.join(dash_folder, dash_filename), 'w') as f:
    f.write(str(dash_manifest))

# Segment the video data and write it to disk
os.makedirs(os.path.join(dash_folder, 'video'), exist_ok=True)
num_segments = len(video_data) // (segment_duration * 1000)
for i in range(num_segments):
    segment_data = video_data[i*segment_duration*1000:(i+1)*segment_duration*1000]
    for j in range(0 , 6):
        for k in range (1 , 5):
            segment_filename = os.path.join(dash_folder, 'video', f'manifest_chunk_{j}_0000{k}.m4s')
    with open(segment_filename, 'wb') as f:
        f.write(segment_data)

# Create a TCP socket and listen for incoming connections
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('127.0.0.1', 9000))
server_socket.listen(1)

print('Waiting for client connection...')

# Accept a connection from a client
client_socket, client_address = server_socket.accept()

print(f'Client connected: {client_address}')

# Send the MPEG-DASH manifest to the client
with open(os.path.join(dash_folder, dash_filename), 'rb') as f:
    manifest_data = f.read()
client_socket.sendall(manifest_data)

# Send the video data in small chunks over the socket to the client
chunk_size = 1024
for i in range(num_segments):
    for j in range(0, 6):
        for k in range(1, 5):
            segment_filename = os.path.join(dash_folder, 'video', f'manifest_chunk_{j}_0000{k}.m4s')
    with open(segment_filename, 'rb') as f:
        segment_data = f.read()
    for j in range(0, len(segment_data), chunk_size):
        chunk = segment_data[j:j+chunk_size]
        client_socket.sendall(chunk)

# Close the socket and the file
client_socket.close()
server_socket.close()
