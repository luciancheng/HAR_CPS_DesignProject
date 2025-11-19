import global_parameters
from sense_hat import SenseHat
import time
import numpy as np
import pickle
from sklearn.preprocessing import StandardScaler
import pandas as pd

# Initialize SenseHat
sense = SenseHat()
sense.clear()

scaler = StandardScaler()

# load model
with open("svm_model.pkl", "rb") as f:
    svm_classifier_loaded = pickle.load(f)

# load train data then transform for scaling
X_train = pd.read_csv("X_train.csv")
scaler.fit_transform(X_train)

class_to_colour = global_parameters.CLASS_TO_COLOUR
sample_rate = global_parameters.SAMPLE_RATE   # e.g., 25 Hz
window_size = global_parameters.WINDOW_SIZE   # e.g., 2 seconds
samples_per_window = int(sample_rate * window_size)  # expected = 50

sleep_time = 1 / sample_rate
raw_values = []

try:
    window_start = time.perf_counter()
    while True:
        """
        No window overlap necessary since each motion is static and very distinct
        """
        now = time.perf_counter()

        # Read sensors
        acc = sense.get_accelerometer_raw()
        gyro = sense.get_gyroscope_raw()
        ax, ay, az = acc['x'], acc['y'], acc['z']
        gx, gy, gz = gyro['x'], gyro['y'], gyro['z']
        raw_values.append([ax, ay, az, gx, gy, gz])

        # completed a round of window data collection
        if now >= window_start + window_size:
            # collect mean data of window and get prediction
            inference_data = np.array(raw_values).mean(axis=0)
            inference_data_scaled = scaler.transform(inference_data.reshape(1, -1))
            predicted_label = svm_classifier_loaded.predict([inference_data])[0]


            # display predicted label to sense hat colour
            sense.clear(class_to_colour[predicted_label])

            # reset info for next window
            raw_values = []     
            window_start = time.perf_counter() # start new window here

        # sleep until next sample
        time.sleep(sleep_time)

except KeyboardInterrupt:
    print("Inference stopped.")
    sense.clear()
