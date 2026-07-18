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


def load_method_summary(input_file):
    """
    职责：读取 Day 9 生成的方法与 alpha 汇总表。

    输入：
        input_file：CSV 文件路径

    输出：
        summary_df：方法汇总 DataFrame
    """
    # TODO 1：
    # 使用 pandas 读取 input_file，并返回结果
    summary_df=pd.read_csv(input_file)
    return summary_df
    pass


def build_fedavg_baseline(summary_df):
    """
    职责：
        提取每个 alpha 下 FedAvg 的最高准确率，
        作为其他方法的对比基线。

    输入：
        summary_df：Day 9 汇总结果

    输出：
        baseline_df：FedAvg 基线表

    预期结构：
        alpha  fedavg_max_accuracy
        0.1    86.7
        0.3    89.2
    """
    # TODO 2：
    # 1. 筛选 method == "FedAvg"
    # 2. 只保留 alpha 和 max_accuracy 两列
    # 3. 把 max_accuracy 改名为 fedavg_max_accuracy
    # 4. 返回 baseline_df
    baseline_df=summary_df[
        summary_df["method"]=="FedAvg"
    ]
    baseline_df=baseline_df[
       [ "alpha","max_accuracy"]
    ]
    baseline_df = baseline_df.rename(
        columns={
            "max_accuracy": "fedavg_max_accuracy"
        }
    )
    baseline_df = baseline_df.reset_index(drop=True)
    return baseline_df
    pass


def compare_with_fedavg(summary_df, baseline_df):
    """
    职责：
        把所有方法的结果与 FedAvg 基线合并，
        计算准确率提升。

    输入：
        summary_df：所有方法的汇总表
        baseline_df：每个 alpha 对应的 FedAvg 基线

    输出：
        comparison_df：基线对比结果表
    """
    # TODO 3：
    # 1. 使用 alpha 作为公共列，把两个表合并
    # 2. 计算 gain_pp
    # 3. 计算 relative_gain_pct
    # 4. 保留两位小数
    # 5. 先按 alpha 升序，再按 gain_pp 降序
    # 6. 重置索引并返回
    comparison_df=summary_df.merge(
        baseline_df,
        on="alpha",
        how="left"
    )
    comparison_df["gain_pp"] = (
            comparison_df["max_accuracy"]
            - comparison_df["fedavg_max_accuracy"]
    )

    comparison_df["relative_gain_pct"] = (
            comparison_df["gain_pp"]
            / comparison_df["fedavg_max_accuracy"]
            * 100
    )
    comparison_df = comparison_df.sort_values(
        by=["alpha", "gain_pp"],
        ascending=[True, False]
    )
    comparison_df = comparison_df.round(2)
    comparison_df = comparison_df.reset_index(drop=True)
    return comparison_df
    pass


def save_comparison(comparison_df, output_file):
    """
    职责：保存基线对比结果。

    输入：
        comparison_df：对比结果表
        output_file：CSV 输出路径

    输出：
        无返回值
    """
    # TODO 4：
    # 保存 CSV，不保存行索引
    comparison_df.to_csv(
        output_file,
        index=False
    )
    pass


def main():
    """
    Day 10 主流程：

    1. 获取项目根目录
    2. 读取 Day 9 汇总表
    3. 提取 FedAvg 基线
    4. 计算其他方法相对 FedAvg 的提升
    5. 保存对比结果
    """
    project_root = get_project_root()

    input_file = (
        project_root
        / "data"
        / "day9_method_alpha_summary.csv"
    )

    output_file = (
        project_root
        / "data"
        / "day10_vs_fedavg_comparison.csv"
    )

    # 读取 Day 9 汇总表
    summary_df = load_method_summary(input_file)

    print("===== Day 9 方法汇总表 =====")
    print(summary_df)

    # 提取每个 alpha 下的 FedAvg 基线
    baseline_df = build_fedavg_baseline(summary_df)

    print("\n===== FedAvg 基线 =====")
    print(baseline_df)

    # 合并表格并计算相对 FedAvg 的提升
    comparison_df = compare_with_fedavg(
        summary_df=summary_df,
        baseline_df=baseline_df
    )

    print("\n===== 相对 FedAvg 的提升结果 =====")
    print(comparison_df)

    # 保存结果
    save_comparison(
        comparison_df=comparison_df,
        output_file=output_file
    )

    print("\nDay 10 对比结果已保存到：")
    print(output_file)


if __name__ == "__main__":
    main()