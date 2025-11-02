import sys
import time
import pandas as pd
from sense_hat import SenseHat
import global_parameters

sense = SenseHat()

# Define mapping from joystick direction to label
LABELS = {
    "up": global_parameters.CLASS_A,
    "down": global_parameters.CLASS_B,
    "left": global_parameters.CLASS_C,
    "right": global_parameters.CLASS_D,
    "middle": "skip"
}

OUTPUT_FILE = "labelled_data.csv"

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 label_data.py <input_csv>")
        sys.exit(1)

    input_csv = sys.argv[1]

    try:
        df = pd.read_csv(input_csv)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        sys.exit(1)

    print(f"Loaded {len(df)} rows from {input_csv}")

    # If labeled_data.csv doesn?t exist, create it with headers
    try:
        existing = pd.read_csv(OUTPUT_FILE)
        print(f"Appending to existing file: {OUTPUT_FILE}")
    except FileNotFoundError:
        df_out = pd.DataFrame(columns=["time", "Ax", "Ay", "Az", "A_mag", "label"])
        df_out.to_csv(OUTPUT_FILE, index=False)
        print(f"Created new output file: {OUTPUT_FILE}")

    for i, row in df.iterrows():
        # Display on LED matrix
        sense.show_message(f"{i+1}/{len(df)}", scroll_speed=0.05, text_colour=[0, 255, 0])

        print(f"\nSample {i+1}/{len(df)}")
        print(f"Ax={row['Ax']:.3f}, Ay={row['Ay']:.3f}, Az={row['Az']:.3f}, A_mag={row['A_mag']:.3f}")
        print("Use joystick: up - Class A | down - Class B | left - Class C | right - Class D | press=skip")

        label = None
        while label is None:
            for event in sense.stick.get_events():
                if event.action == "pressed":
                    direction = event.direction
                    if direction in LABELS:
                        label = LABELS[direction]
                        print(f"Labeled as: {label}")
                        break
            time.sleep(0.05)

        if label != "skip":
            # Append to labeled_data.csv
            new_row = pd.DataFrame({
                "time": [row["time"]],
                "Ax": [row["Ax"]],
                "Ay": [row["Ay"]],
                "Az": [row["Az"]],
                "A_mag": [row["A_mag"]],
                "label": [label]
            })
            new_row.to_csv(OUTPUT_FILE, mode="a", header=False, index=False)

        else:
            print("Skipped this entry.")

    sense.show_message("DONE", text_colour=[255, 255, 0])
    print("All samples processed and labeled!")

if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print("Labelling stopped")
		sense.clear()
		
