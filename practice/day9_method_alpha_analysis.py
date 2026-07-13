import pandas as pd
from pathlib import Path


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
    # TODO 1：
    # 使用 pandas 读取 input_file，并返回 df
    df=pd.read_csv(input_file)
    return df
    pass





def build_method_alpha_summary(df):
    """
    职责：
        同时按 method 和 alpha 分组，
        计算每组的实验数量、准确率和 loss 指标。

    输入：
        df：原始实验日志

    输出：
        summary_df：method + alpha 汇总表

    需要生成的列：
        experiment_count
        mean_accuracy
        max_accuracy
        mean_loss
        min_loss
    """
    # TODO 2：
    # 1. 按 method 和 alpha 分组
    # 2. 使用 agg 同时计算多个统计指标
    # 3. reset_index()
    # 4. 保留两位小数
    # 5. 先按 alpha 升序，再按 max_accuracy 降序
    # 6. 重置索引并返回
    summary_df=(
    df.groupby(["method","alpha"])
    .agg(
        experiment_count=("global_acc", "count"),
        mean_accuracy=("global_acc", "mean"),
        max_accuracy=("global_acc", "max"),
        mean_loss=("loss", "mean"),
        min_loss=("loss", "min")
    )
       .reset_index()
)
    pass
    summary_df = summary_df.round(2)
    summary_df = summary_df.sort_values(
        by=["alpha", "max_accuracy"],
        ascending=[True, False]
    )
    summary_df = summary_df.reset_index(drop=True)

    return summary_df

def build_max_accuracy_pivot(summary_df):
    """
    职责：
        把汇总表转换成方便比较的透视表。

    输入：
        summary_df：method + alpha 汇总结果

    输出：
        pivot_df：不同 alpha 下各方法最高准确率对比表

    预期结构：

    method  FedAvg  FedProx  LEDC
    alpha
    0.1       86.7     88.9  91.8
    0.3       89.2     90.1  93.4
    """
    # TODO 3：
    # index 使用 alpha
    # columns 使用 method
    # values 使用 max_accuracy
    pivot_df = summary_df.pivot(
        index="alpha",
        columns="method",
        values="max_accuracy"
    )
    pivot_df = pivot_df.reset_index()
    return pivot_df
    pass


def save_dataframe(df, output_file):
    """
    职责：把 DataFrame 保存成 CSV。

    输入：
        df：需要保存的表格
        output_file：输出文件路径

    输出：
        无返回值
    """
    # TODO 4：
    # 保存 CSV，不保存行索引
    df.to_csv(
        output_file,
        index=False
    )
    pass


def main():
    """
    Day 9 主流程：

    1. 获取项目根目录
    2. 设置输入和输出路径
    3. 读取实验日志
    4. 按 method + alpha 汇总
    5. 创建最高准确率透视表
    6. 保存两个 CSV 文件
    """
    project_root = get_project_root()

    input_file = (
        project_root
        / "data"
        / "fed_experiment_logs.csv"
    )

    summary_output = (
        project_root
        / "data"
        / "day9_method_alpha_summary.csv"
    )

    pivot_output = (
        project_root
        / "data"
        / "day9_max_accuracy_pivot.csv"
    )

    # 调用读取函数，得到原始实验表
    df = load_experiment_logs(input_file)

    print("===== 原始实验日志前 5 行 =====")
    print(df.head())

    # 调用汇总函数，得到 method + alpha 汇总表
    summary_df = build_method_alpha_summary(df)

    print("\n===== Method + Alpha 汇总结果 =====")
    print(summary_df)

    # 调用透视表函数，得到最高准确率横向对比表
    pivot_df = build_max_accuracy_pivot(summary_df)

    print("\n===== 不同 Alpha 下的最高准确率对比 =====")
    print(pivot_df)

    # 保存汇总结果
    save_dataframe(
        df=summary_df,
        output_file=summary_output
    )

    # 保存透视表
    save_dataframe(
        df=pivot_df,
        output_file=pivot_output
    )

    print("\nMethod + Alpha 汇总结果已保存到：")
    print(summary_output)

    print("\n最高准确率透视表已保存到：")
    print(pivot_output)


if __name__ == "__main__":
    main()