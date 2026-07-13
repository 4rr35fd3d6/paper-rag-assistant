import pandas as pd
from pathlib import Path

from pandas import DataFrame


def get_project_root():
    """
    职责：获取项目根目录。

    输入：
        无

    输出：
        project_root：项目根目录路径
    """
    project_root = Path(__file__).resolve().parents[1]
    return project_root


def load_experiment_logs(input_file):
    """
    职责：读取实验日志 CSV。

    输入：
        input_file：CSV 文件路径

    输出：
        df：实验日志 DataFrame
    """
    # TODO 1：使用 pandas 读取 input_file
    df=pd.read_csv(input_file)
    return df
    pass


def build_method_summary(df):
    """
    职责：按 method 分组，计算每种方法的汇总指标。

    输入：
        df：原始实验日志

    输出：
        summary_df：方法汇总表

    需要统计：
        experiment_count：每个方法有多少条实验记录
        mean_accuracy：平均 global_acc
        max_accuracy：最高 global_acc
        mean_loss：平均 loss
        min_loss：最低 loss
    """
    # TODO 2：完成分组统计、排序和小数处理
    summary_df = (
        df.groupby("method")
        .agg(
            experiment_count=("global_acc", "count"),
            mean_accuracy=("global_acc", "mean"),
            max_accuracy=("global_acc", "max"),
            mean_loss=("loss", "mean"),
            min_loss=("loss", "min")
        )
        .reset_index()
    )
    summary_df = summary_df.round(2)
    summary_df = summary_df.sort_values(
        by="max_accuracy",
        ascending=False
    )
    summary_df = summary_df.reset_index(drop=True)

    return summary_df


def save_summary(summary_df, output_file):
    """
    职责：把汇总表保存成 CSV。

    输入：
        summary_df：方法汇总表
        output_file：输出文件路径

    输出：
        无返回值，函数会生成 CSV 文件
    """
    # TODO 3：保存 CSV，不保存 DataFrame 行索引
    summary_df.to_csv(
        output_file,
        # 删除行号
        index=False)


def main():
    """
    Day 8 主流程：

    1. 获取项目根目录
    2. 设置输入、输出文件路径
    3. 读取实验日志
    4. 生成方法汇总表
    5. 保存汇总结果
    """
    # 获取项目根目录
    project_root = get_project_root()

    # 原始实验日志路径
    input_file = (
        project_root
        / "data"
        / "fed_experiment_logs.csv"
    )

    # 汇总结果输出路径
    output_file = (
        project_root
        / "data"
        / "day8_method_summary.csv"
    )

    # 调用读取函数，得到原始实验表
    df = load_experiment_logs(input_file)

    print("===== 原始实验日志前 5 行 =====")
    print(df.head())

    # 调用汇总函数，得到每个方法的统计结果
    summary_df = build_method_summary(df)

    print("\n===== 每个方法的汇总结果 =====")
    print(summary_df)

    # 调用保存函数，把汇总结果保存成 CSV
    save_summary(
        summary_df=summary_df,
        output_file=output_file
    )

    print("\n汇总结果已保存到：")
    print(output_file)


if __name__ == "__main__":
    main()