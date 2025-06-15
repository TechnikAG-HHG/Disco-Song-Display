from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room
import time
import threading
import numpy as np
import sounddevice as sd
from scipy.fft import fft
import queue

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
socketio = SocketIO(app, cors_allowed_origins="*")  # Initialize SocketIO with CORS support

# Audio parameters
SAMPLE_RATE = 44100  # Audio sample rate
BLOCK_SIZE = 1024    # Number of audio samples per block
N_BARS = 16          # Number of frequency bars to display
BASE_HEIGHT = 100    # Base height for the bars
MIN_HEIGHT = 10      # Minimum height of bars

# Audio processing variables
audio_queue = queue.Queue()
fft_data = np.ones(N_BARS) * MIN_HEIGHT  # Initialize with minimum height

# Track moving averages and timing
bar_averages = np.ones(N_BARS) * BASE_HEIGHT  # Moving average per frequency band
SMOOTHING_FACTOR = 0.01 # How quickly averages adapt (lower = slower)
DEFAULT_MOVEMENT_AMPLITUDE = 5  # Amplitude of movement at default position

# Store active WebSocket connections
active_connections = {}
thread_lock = threading.Lock()
worker_thread = None
audio_thread = None
audio_stream = None  # Store the audio stream as a global variable

def audio_callback(indata, frames, time_info, status):
    """Callback function for audio stream"""
    if status:
        print(f"Audio status: {status}")
    try:
        # Put the audio data in the queue
        audio_queue.put(indata[:, 0])  # Use first channel if stereo
    except Exception as e:
        print(f"Error in audio callback: {e}")

def process_audio():
    """Process audio data and calculate bar heights"""
    global fft_data, bar_averages
    while True:
        try:
            # Get audio data from the queue
            data = audio_queue.get(timeout=1)
            
            # Compute FFT
            magnitude = np.abs(fft(data)[:BLOCK_SIZE // 2])
            
            # Convert to decibels and normalize
            magnitude = 20 * np.log10(magnitude + 1e-10)
            magnitude = (magnitude - np.min(magnitude)) / (np.max(magnitude) - np.min(magnitude) + 1e-10)
            
            # Map FFT bins to frequency bars (logarithmic mapping)
            current_values = np.zeros(N_BARS)
            for i in range(N_BARS):
                # Logarithmic scale for frequency bands - preserve order with low freq (bass) on left
                start = int(BLOCK_SIZE / 2 * (10 ** (i / N_BARS) - 1) / (10 - 1))
                end = int(BLOCK_SIZE / 2 * (10 ** ((i+1) / N_BARS) - 1) / (10 - 1))
                start = max(0, min(start, BLOCK_SIZE // 2 - 1))
                end = max(1, min(end, BLOCK_SIZE // 2))
                
                # Average the magnitudes in this frequency band
                if end > start:
                    current_values[i] = np.mean(magnitude[start:end])
            
            # Update the moving average for each bar
            bar_averages = bar_averages * (1 - SMOOTHING_FACTOR) + current_values * SMOOTHING_FACTOR
            
            # Calculate relative changes from each bar's own average
            relative_changes = current_values / (bar_averages + 1e-10)  # Avoid division by zero
            
            # Scale bars based on deviation from their average
            # When a bar has its typical volume, it will be at BASE_HEIGHT
            # Deviations are amplified to make booms and drops more dramatic
            fft_data = BASE_HEIGHT * np.power(relative_changes, 3)  # Cubic power for dramatic effect
            
            # Ensure bars don't go below minimum height
            fft_data = np.maximum(fft_data, MIN_HEIGHT)
            
        except queue.Empty:
            pass
        except Exception as e:
            print(f"Audio processing error: {e}")
            time.sleep(0.1)  # Prevent CPU spinning on repeated errors

def calculate_bar_height(bar_id):
    """Calculate the height for a given bar based on audio data"""
    if bar_id < len(fft_data):
        height = fft_data[bar_id]
        
        # Add a small movement when the bar is close to baseline
        # Check if the bar is within 20% of BASE_HEIGHT
        if abs(height - BASE_HEIGHT) < (0.2 * BASE_HEIGHT):
            # Add a subtle movement that's unique to each bar (based on bar_id)
            small_movement = DEFAULT_MOVEMENT_AMPLITUDE * np.sin(time.time() * (2 + bar_id * 0.2))
            height += small_movement
            
        return int(height)
    else:
        # Return minimum height for bars beyond FFT data
        return MIN_HEIGHT

def background_thread():
    """Background thread that sends data to clients"""
    while True:
        # Update all active connections
        for room_id, connected in list(active_connections.items()):
            if connected:
                bar_id = int(room_id.split('-')[1])
                height = calculate_bar_height(bar_id)
                socketio.emit('bar_update', {'height': height, 'bar_id': bar_id}, room=room_id)
        socketio.sleep(0.05)  # Send updates 20 times per second

@socketio.on('connect')
def handle_connect():
    """Handle new WebSocket connections"""
    print("Client connected to socket")

def setup_audio():
    """Set up audio input stream with proper error handling"""
    global audio_stream
    try:
        # Close existing stream if present
        if audio_stream is not None:
            if audio_stream.active:
                audio_stream.stop()
                audio_stream.close()
        
        # Create new stream for audio input
        audio_stream = sd.InputStream(
            callback=audio_callback, 
            channels=1, 
            samplerate=SAMPLE_RATE, 
            blocksize=BLOCK_SIZE,
            device=None  # Use default device
        )
        audio_stream.start()
        print("Started audio input stream")
        return True
    except Exception as e:
        print(f"Error setting up audio stream: {e}")
        return False

@socketio.on('register_bar')
def handle_register_bar(data):
    """Register a client for a specific bar"""
    global worker_thread, audio_thread, audio_stream
    bar_id = data['bar_id']
    room = f"bar-{bar_id}"
    join_room(room)
    
    print(f"Client registered for bar {bar_id}")
    
    with thread_lock:
        active_connections[room] = True
        if worker_thread is None:
            worker_thread = socketio.start_background_task(background_thread)
        if audio_thread is None:
            # Start audio processing thread
            audio_thread = socketio.start_background_task(process_audio)
            # Set up audio stream
            setup_audio()
    
    # Send initial height
    height = calculate_bar_height(bar_id)
    emit('bar_update', {'height': height, 'bar_id': bar_id})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnections"""
    print("Client disconnected")
    # Check if there are no more clients
    with thread_lock:
        if len(active_connections) == 0:
            # Stop audio stream if no more clients
            global audio_stream
            if audio_stream is not None and audio_stream.active:
                try:
                    audio_stream.stop()
                    print("Stopped audio stream due to all clients disconnected")
                except Exception as e:
                    print(f"Error stopping audio stream: {e}")

# Keep the REST endpoint for compatibility
@app.route('/api/bar/<int:bar_id>', methods=['GET'])
def get_bar_height(bar_id):
    height = calculate_bar_height(bar_id)
    return jsonify({
        'bar_id': bar_id,
        'height': height
    })

if __name__ == '__main__':
    print("Starting audio visualizer server on http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)