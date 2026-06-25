import pandas as pd
from pathlib import Path


def main():
    project_root = Path(__file__).resolve().parents[1]

    input_file = project_root / "data" / "fed_experiment_logs.csv"
    high_acc_output = project_root / "data" / "high_accuracy_results.csv"
    best_method_output = project_root / "data" / "best_method_results.csv"

    df = pd.read_csv(input_file)

    print("===== Original Experiment Logs =====")
    print(df)

    print("\n===== First 5 Rows =====")
    print(df.head())

    high_acc_df = df[df["global_acc"] >= 88]

    print("\n===== Results with Accuracy >= 88 =====")
    print(high_acc_df)

    sorted_df = df.sort_values(by="global_acc", ascending=False)

    print("\n===== Sorted by Global Accuracy =====")
    print(sorted_df)

    best_by_method = (
        df.sort_values(by="global_acc", ascending=False)
        .groupby("method")
        .head(1)
        .reset_index(drop=True)
    )

    print("\n===== Best Result for Each Method =====")
    print(best_by_method)

    high_acc_df.to_csv(high_acc_output, index=False)
    best_by_method.to_csv(best_method_output, index=False)

    print("\nSaved high accuracy results to:")
    print(high_acc_output)

    print("\nSaved best method results to:")
    print(best_method_output)


if __name__ == "__main__":
    main()