import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


def main():
    project_root = Path(__file__).resolve().parents[1]

    input_file = project_root / "data" / "fed_experiment_logs.csv"
    figure_dir = project_root / "figures"
    figure_dir.mkdir(exist_ok=True)

    df = pd.read_csv(input_file)

    print("===== Original Experiment Logs =====")
    print(df.head())

    alpha03_df = df[df["alpha"] == 0.1]

    print("\n===== Alpha = 0.3 Experiment Logs =====")
    print(alpha03_df)

    pivot_df = alpha03_df.pivot(
        index="round",
        columns="method",
        values="global_acc"
    )

    print("\n===== Pivot Table for Plotting =====")
    print(pivot_df)

    curve_output = figure_dir / "accuracy_curve_alpha01.png"

    pivot_df.plot(marker="o")
    plt.title("Global Accuracy Curve under alpha=0.1")
    plt.xlabel("Communication Round")
    plt.ylabel("Global Accuracy")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(curve_output)
    plt.close()

    print("\nSaved accuracy curve to:")
    print(curve_output)

    best_by_method = (
        df.sort_values(by="global_acc", ascending=False)
        .groupby("method")
        .head(1)
        .reset_index(drop=True)
    )

    print("\n===== Best Result for Each Method =====")
    print(best_by_method)

    bar_output = figure_dir / "best_method_accuracy.png"

    best_by_method.plot(
        x="method",
        y="global_acc",
        kind="bar",
        legend=False
    )
    plt.title("Best Global Accuracy of Each Method")
    plt.xlabel("Method")
    plt.ylabel("Best Global Accuracy")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(bar_output)
    plt.close()

    print("\nSaved best method bar chart to:")
    print(bar_output)


if __name__ == "__main__":
    main()