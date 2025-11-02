import sys
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import global_parameters

COLORS = {
    global_parameters.CLASS_A: "tab:blue",
    global_parameters.CLASS_B: "tab:orange",
    global_parameters.CLASS_C: "tab:green",
    global_parameters.CLASS_D: "tab:red",
}

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 plot_data.py <labeled_csv>")
        sys.exit(1)

    input_csv = sys.argv[1]

    try:
        df = pd.read_csv(input_csv)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        sys.exit(1)

    if not {"Ax", "Ay", "Az", "A_mag", "label"}.issubset(df.columns):
        print("Error: CSV must contain columns: Ax, Ay, Az, A_mag, label")
        sys.exit(1)

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Normalize point size for visualization
    sizes = 100 * (df["A_mag"] / df["A_mag"].max())

    # Plot each class separately
    for label, color in COLORS.items():
        class_data = df[df["label"] == label]
        if len(class_data) == 0:
            continue
        ax.scatter(
            class_data["Ax"],
            class_data["Ay"],
            class_data["Az"],
            s=sizes[class_data.index],
            c=color,
            label=label,
            alpha=0.6,
            edgecolors='k'
        )

    ax.set_xlabel("Ax", fontsize=12)
    ax.set_ylabel("Ay", fontsize=12)
    ax.set_zlabel("Az", fontsize=12)
    ax.set_title("3D Accelerometer Data Visualization", fontsize=14)
    ax.legend(title="Label")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
