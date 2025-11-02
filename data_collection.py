import global_parameters
from sense_hat import SenseHat
import time, random
import numpy as np

# intiailize sensehat
sense = SenseHat()
sense.clear()

sample_rate = global_parameters.SAMPLE_RATE # Hz
window_size = global_parameters.WINDOW_SIZE # s

# colours
green = global_parameters.GREEN

sleep_time = 1 / sample_rate # time between samples, in seconds

# flag for starting proper data collection of a task, will be active for a time of window_size, then will deactivate
# during this window, all the data will be computed into a vector
is_active = False
start_time = 0

data = np.empty((0, 3))

def handle_data_collection():
	"""
	Function to let user know when data is actively being collected and processed during the window size
	- User feedback with a green LED to indicate that data is currently being collected and any motion during this time will be 
	  incorporated into the feature vector that will be used for labelling later
	- allow user to choose when to actively start tracking data by pressing the button
	"""
	global is_active, start_time, data
	a = sense.get_accelerometer_raw()
	ax, ay, az = a['x'], a['y'], a['z']
		
	# start window data collection processing
	for e in sense.stick.get_events():
		if e.direction == "middle" and e.action == "pressed" and not is_active:
			is_active = True
			sense.clear(green)
			start_time = time.time()
			data = np.empty((0, 3))
		
	# window time ended
	if is_active:
		#print(f"{ax}, {ay}, {az} - active: {is_active}")
		data = np.vstack((data, [[ax, ay, az]]))
		cur_time = time.time()
		
		# stop colleting data and compute the results feature vector over the window
		if cur_time - start_time >= window_size:
			is_active = False
			sense.clear()
			print(data)
			print(data.mean(axis=0), data.shape)

try:
	while True:
		handle_data_collection()
		
		# sleep time
		time.sleep(sleep_time)
		
except KeyboardInterrupt:
    print("Logging stopped")
    sense.clear()
