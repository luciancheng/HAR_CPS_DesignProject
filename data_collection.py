import global_parameters
from sense_hat import SenseHat
import time
import numpy as np
import csv
from datetime import datetime
import os

# Initialize SenseHat
sense = SenseHat()
sense.clear()

sample_rate = global_parameters.SAMPLE_RATE   # e.g., 25 Hz
window_size = global_parameters.WINDOW_SIZE   # e.g., 2 seconds
samples_per_window = int(sample_rate * window_size)  # expected = 50

# Colors
green = global_parameters.GREEN
red = global_parameters.RED
blue = global_parameters.BLUE
yellow = global_parameters.YELLOW

os.makedirs("raw_data", exist_ok=True)

axis_files = {
    "ax": os.path.join("raw_data", "acceleration_x.csv"),
    "ay": os.path.join("raw_data", "acceleration_y.csv"),
    "az": os.path.join("raw_data", "acceleration_z.csv"),
    "gx": os.path.join("raw_data", "gyroscope_x.csv"),
    "gy": os.path.join("raw_data", "gyroscope_y.csv"),
    "gz": os.path.join("raw_data", "gyroscope_z.csv"),
    "labels": os.path.join("raw_data", "labels.csv")
}

LABELS = {
    "up": global_parameters.CLASS_A,
    "down": global_parameters.CLASS_B,
    "left": global_parameters.CLASS_C,
    "right": global_parameters.CLASS_D,
    "middle": "skip"
}

mappings = {
    "up": "standing",
    "down": "sitting",
    "left": "lying",
    "right": "Turn on spot (CW)"
}

colour_mappings = {
    "up": red,
    "down": green,
    "left": blue,
    "right": yellow
}

# Ensure files exist and have headers
for axis, path in axis_files.items():
    if not os.path.exists(path):
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            header = ["timestamp"]
            header += [f"{axis}_{i}" for i in range(samples_per_window)]
            writer.writerow(header)

# Interpolation helper
def interpolate_window(times, values, t_start, t_end, target_hz):
    n = int((t_end - t_start) * target_hz)
    target_times = t_start + np.arange(n) / target_hz

    if len(times) < 2:
        # If not enough data, repeat the only sample
        return np.tile(values[0], (n, 1)).T

    interp_values = []
    for axis in range(values.shape[1]):
        interp = np.interp(target_times, times, values[:, axis])
        interp_values.append(interp)

    return np.array(interp_values)  # shape: (6, n)

sleep_time = 1 / sample_rate

is_active = False
start_time = 0

raw_times = []
raw_values = []  # stores [ax, ay, az, gx, gy, gz]

print("Ready. Press middle joystick button to start a window.")

try:
    while True:
        now = time.perf_counter()

        # Read sensors
        acc = sense.get_accelerometer_raw()
        gyro = sense.get_gyroscope_raw()
        ax, ay, az = acc['x'], acc['y'], acc['z']
        gx, gy, gz = gyro['x'], gyro['y'], gyro['z']

        # Check for start trigger
        for e in sense.stick.get_events():
            if e.direction == "middle" and e.action == "pressed":
                is_active = True
                sense.clear(green)
                start_time = now
                raw_times = []
                raw_values = []

        # Collect raw samples
        if is_active:
            raw_times.append(now)
            raw_values.append([ax, ay, az, gx, gy, gz])

            if now - start_time >= window_size:
                # Window finished
                is_active = False
                sense.clear()

                raw_times_np = np.array(raw_times) - raw_times[0]  # normalize to 0
                raw_values_np = np.array(raw_values)  # shape: (N, 6)

                # Interpolate to fixed number of samples
                interp = interpolate_window(
                    raw_times_np,
                    raw_values_np,
                    t_start=0,
                    t_end=window_size,
                    target_hz=sample_rate
                )  # shape: (6, samples_per_window)

                # Write each axis to its file
                timestamp = datetime.now().isoformat()

                # Label the data
                print("Up - Standing, Down - Sitting, Left - Lying, Right - Turning on spot (CW)")

                label = None
                pending_label = None

                while label is None:
                    for event in sense.stick.get_events():

                        # Step 1: Pick direction (not middle)
                        if event.action == "pressed" and event.direction in LABELS and event.direction != "middle":
                            pending_label = LABELS[event.direction]
                            print(f"You selected: {event.direction} - {mappings[event.direction]} : {pending_label}")
                            sense.clear(colour_mappings[event.direction])
                            print("Press MIDDLE button to confirm.")

                        # Step 2: Confirm using middle button
                        if event.action == "pressed" and event.direction == "middle":
                            if pending_label is not None:
                                label = pending_label
                                print(f"Confirmed label: {label}")
                                break
                            else:
                                print("No selection to confirm. Choose a direction first.")

                # Save raw axis data
                print(interp.shape)

                for idx, axis in enumerate(["ax", "ay", "az", "gx", "gy", "gz"]):
                    path = axis_files[axis]
                    with open(path, "a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow([timestamp] + interp[idx].tolist())

                # Save label
                with open(axis_files["labels"], "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([timestamp, label])

                print("Saved window:", timestamp)
                sense.clear()

        time.sleep(sleep_time)

except KeyboardInterrupt:
    print("Logging stopped.")
    sense.clear()
