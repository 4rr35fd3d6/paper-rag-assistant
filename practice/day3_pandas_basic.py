import pandas as pd
from pathlib import Path


def main():
    project_root = Path(__file__).resolve().parents[1]

    input_file = project_root / "data" / "student_scores.csv"

    df = pd.read_csv(input_file)

    print("===== Original Data =====")
    print(df)

    print("\n===== First 3 Rows =====")
    print(df.head(3))

    print("\n===== Math Statistics =====")
    print("Mean:", df["math"].mean())
    print("Max :", df["math"].max())
    print("Min :", df["math"].min())

    summary = pd.DataFrame({
        "Metric": ["Mean", "Max", "Min"],
        "Math": [
            df["math"].mean(),
            df["math"].max(),
            df["math"].min()
        ]
    })

    output_file = project_root / "data" / "math_summary.csv"

    summary.to_csv(output_file, index=False)

    print("\nSummary saved to:")
    print(output_file)


if __name__ == "__main__":
    main()