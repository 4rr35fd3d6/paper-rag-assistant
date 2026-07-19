import pandas as pd
import matplotlib.pyplot as plt
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


def load_comparison_data(input_file):
    """
    职责：读取 Day 10 生成的基线对比数据。

    输入：
        input_file：Day 10 CSV 文件路径

    输出：
        comparison_df：基线对比 DataFrame
    """
    # TODO 1：
    # 使用 pandas 读取 CSV
    # 返回 comparison_df
    comparison_df=pd.read_csv(input_file)
    return comparison_df
    pass


def filter_non_baseline_methods(comparison_df):
    """
    职责：
        去掉基线方法 FedAvg，
        只保留真正需要与基线比较的方法。

    输入：
        comparison_df：Day 10 对比结果

    输出：
        non_baseline_df：不包含 FedAvg 的数据
    """
    # TODO 2：
    # 筛选 method 不等于 FedAvg 的记录
    # 使用 copy() 创建独立副本
    # 重置索引
    # 返回结果
    non_baseline_df = comparison_df[
        comparison_df["method"] != "FedAvg"
        ].copy()
    non_baseline_df = non_baseline_df.reset_index(drop=True)
    return non_baseline_df

    pass


def find_best_gain_by_alpha(non_baseline_df):
    """
    职责：
        找出每个 alpha 下 gain_pp 最大的方法。

    输入：
        non_baseline_df：不包含 FedAvg 的方法结果

    输出：
        best_gain_df：每个 alpha 下提升最大的方法

    最终只保留：
        alpha
        method
        gain_pp
        relative_gain_pct
    """
    # TODO 3：
    # 1. 按 alpha 分组
    # 2. 找到每组 gain_pp 最大值所在的行索引
    # 3. 使用 loc 取出这些完整记录
    # 4. 只保留指定的四列
    # 5. 按 alpha 升序排序
    # 6. 重置索引并返回
    non_baseline_df.groupby("alpha")
    best_index = (
        non_baseline_df
        .groupby("alpha")["gain_pp"]
        .idxmax()
    )
    best_gain_df = non_baseline_df.loc[best_index]
    best_gain_df = best_gain_df[
        [
            "alpha",
            "method",
            "gain_pp",
            "relative_gain_pct"
        ]
    ]
    best_gain_df = best_gain_df.sort_values(
        by="alpha",
        ascending=True
    )

    best_gain_df = best_gain_df.reset_index(
        drop=True
    )
    return best_gain_df
    pass


def plot_gain_comparison(non_baseline_df, output_file):
    """
    职责：
        绘制不同 alpha 下，各方法相对 FedAvg 的提升柱状图。

    输入：
        non_baseline_df：不包含 FedAvg 的结果
        output_file：图片保存路径

    输出：
        无返回值，生成 PNG 图片
    """
    # TODO 4：
    # 1. 使用 pivot 创建绘图数据
    # 2. 绘制柱状图
    # 3. 添加柱状图数值标签
    # 4. 设置标题、坐标轴名称
    # 5. 保存图片
    plot_df = non_baseline_df.pivot(
        index="alpha",
        columns="method",
        values="gain_pp"
    )
    ax = plot_df.plot(
        kind="bar",
        figsize=(9, 6)
    )
    for container in ax.containers:
        ax.bar_label(
            container,
            fmt="%.2f"
        )
    ax.set_title(
            "Accuracy Gain Compared with FedAvg"
        )
    ax.set_xlabel("Alpha")
    ax.set_ylabel("Accuracy Gain (percentage points)")
    plt.xticks(rotation=0)
    output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )
    plt.tight_layout()

    plt.savefig(
            output_file,
            dpi=300,
            bbox_inches="tight"
        )

    plt.close()
    pass



def save_best_gain(best_gain_df, output_file):
    """
    职责：保存每个 alpha 下的最佳提升方法。

    输入：
        best_gain_df：最佳方法结果表
        output_file：CSV 输出路径

    输出：
        无返回值
    """
    best_gain_df.to_csv(
        output_file,
        index=False
    )


def main():
    """
    Day 11 主流程：

    1. 获取项目根目录
    2. 读取 Day 10 对比结果
    3. 去掉 FedAvg 基线
    4. 找出每个 alpha 下提升最大的方法
    5. 保存最佳方法结果
    6. 绘制提升对比柱状图
    """
    project_root = get_project_root()

    input_file = (
        project_root
        / "data"
        / "day10_vs_fedavg_comparison.csv"
    )

    best_gain_output = (
        project_root
        / "data"
        / "day11_best_gain_by_alpha.csv"
    )

    figure_output = (
        project_root
        / "figures"
        / "day11_gain_comparison.png"
    )

    # 读取 Day 10 对比数据
    comparison_df = load_comparison_data(input_file)

    print("===== Day 10 基线对比数据 =====")
    print(comparison_df)

    # 去掉基线方法 FedAvg
    non_baseline_df = filter_non_baseline_methods(
        comparison_df
    )

    print("\n===== 去掉 FedAvg 后的数据 =====")
    print(non_baseline_df)

    # 找出每个 alpha 下提升最大的方法
    best_gain_df = find_best_gain_by_alpha(
        non_baseline_df
    )

    print("\n===== 每个 Alpha 下提升最大的方法 =====")
    print(best_gain_df)

    # 保存最佳提升结果
    save_best_gain(
        best_gain_df=best_gain_df,
        output_file=best_gain_output
    )

    # 绘制柱状图
    plot_gain_comparison(
        non_baseline_df=non_baseline_df,
        output_file=figure_output
    )

    print("\n最佳提升结果已保存到：")
    print(best_gain_output)

    print("\n提升对比图已保存到：")
    print(figure_output)


if __name__ == "__main__":
    main()