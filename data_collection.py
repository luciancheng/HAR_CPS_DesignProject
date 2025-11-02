import global_parameters
from sense_hat import SenseHat
import time, random
import numpy as np
import csv
from datetime import datetime
import os
import math

# intiailize sensehat
sense = SenseHat()
sense.clear()

sample_rate = global_parameters.SAMPLE_RATE # Hz
window_size = global_parameters.WINDOW_SIZE # s

os.makedirs("raw_data", exist_ok=True)

filename = os.path.join("raw_data", f"log_{datetime.now().strftime('%H%M%S')}.csv")

# colours

green = global_parameters.GREEN

sleep_time = 1 / sample_rate # time between samples, in seconds

# flag for starting proper data collection of a task, will be active for a time of window_size, then will deactivate
# during this window, all the data will be computed into a vector
is_active = False
start_time = 0

data = []
	

try:
	with open(filename, 'w', newline='') as f:
		writer = csv.writer(f)
		writer.writerow(["time", "Ax", "Ay", "Az", "A_mag"])
        
		while True:
			a = sense.get_accelerometer_raw()
			ax, ay, az = a['x'], a['y'], a['z']
				
			# start window data collection processing
			if not is_active:
				for e in sense.stick.get_events():
					if e.direction == "middle" and e.action == "pressed":
						is_active = True
						sense.clear(green)
						start_time = time.time()
						data = []
				
			# window time ended
			if is_active:
				data.append([ax, ay, az])
				cur_time = time.time()
				
				# stop colleting data and compute the results feature vector over the window
				if cur_time - start_time >= window_size:
					is_active = False
					sense.clear()
					data_np = np.array(data)
					data_mean = data_np.mean(axis=0)
					print(data_mean, data_np.shape)
					ax_mean, ay_mean, az_mean = data_mean[0], data_mean[1], data_mean[2]
					a_mag_mean = math.sqrt(ax_mean**2 + ay_mean**2 + az_mean**2)

					writer.writerow([
						datetime.now().isoformat(),
						ax_mean,
						ay_mean,
						az_mean,
						a_mag_mean,
					])
			
			# sleep time
			time.sleep(sleep_time)
			
except KeyboardInterrupt:
    print("Logging stopped")
    sense.clear()
