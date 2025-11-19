import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os
import global_parameters

# Paths to raw CSV files
DATA_DIR = "raw_data"
axis_files = {
    "ax": os.path.join(DATA_DIR, "acceleration_x.csv"),
    "ay": os.path.join(DATA_DIR, "acceleration_y.csv"),
    "az": os.path.join(DATA_DIR, "acceleration_z.csv"),
    "gx": os.path.join(DATA_DIR, "gyroscope_x.csv"),
    "gy": os.path.join(DATA_DIR, "gyroscope_y.csv"),
    "gz": os.path.join(DATA_DIR, "gyroscope_z.csv"),
    "labels": os.path.join(DATA_DIR, "labels.csv")
}

COLORS = {
    global_parameters.CLASS_A: "tab:red",
    global_parameters.CLASS_B: "tab:green",
    global_parameters.CLASS_C: "tab:blue",
    global_parameters.CLASS_D: "tab:yellow",
}

def load_and_compute_means():
    """
    Load each CSV (no headers), compute mean across each row (window)
    Returns:
        accel_means: DataFrame with columns ['Ax', 'Ay', 'Az']
        gyro_means: DataFrame with columns ['Gx', 'Gy', 'Gz']
        labels: Series of labels for each window
    """
    accel_means = pd.DataFrame()
    gyro_means = pd.DataFrame()

    # Load labels (assume only one column)
    labels_df = pd.read_csv(axis_files["labels"], header=None)
    labels = labels_df.iloc[:, 0]  # get first column

    # Load accelerometer data
    for axis, col_name in zip(["ax", "ay", "az"], ["Ax", "Ay", "Az"]):
        df = pd.read_csv(axis_files[axis], header=None)
        # Compute mean across samples (columns)
        accel_means[col_name] = df.mean(axis=1)

    # Load gyroscope data
    for axis, col_name in zip(["gx", "gy", "gz"], ["Gx", "Gy", "Gz"]):
        df = pd.read_csv(axis_files[axis], header=None)
        gyro_means[col_name] = df.mean(axis=1)

    return accel_means, gyro_means, labels

def plot_3d(means_df, labels, title):
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    sizes = 100  # constant point size

    for label, color in COLORS.items():
        class_data = means_df[labels == label]
        if len(class_data) == 0:
            continue
        ax.scatter(
            class_data.iloc[:, 0],  # X
            class_data.iloc[:, 1],  # Y
            class_data.iloc[:, 2],  # Z
            s=sizes,
            c=color,
            label=label,
            alpha=0.7,
            edgecolors='k'
        )

    ax.set_xlabel(means_df.columns[0])
    ax.set_ylabel(means_df.columns[1])
    ax.set_zlabel(means_df.columns[2])
    ax.set_title(title)
    ax.legend(title="Label")
    plt.tight_layout()
    plt.show()

def main():
    accel_means, gyro_means, labels = load_and_compute_means()

    # Plot accelerometer
    plot_3d(accel_means, labels, "Accelerometer Mean per Window")

    # Plot gyroscope
    plot_3d(gyro_means, labels, "Gyroscope Mean per Window")

if __name__ == "__main__":
    main()
