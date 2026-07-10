import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


def get_project_root():
    """
    获取项目根目录。

    当前文件位置大概是：
    project1_paper_rag_assistant/practice/day6_function_refactor_visualization.py

    parents[1] 表示从当前文件往上找两层，回到：
    project1_paper_rag_assistant
    """
    project_root = Path(__file__).resolve().parents[1]
    return project_root


def load_experiment_logs(input_file):
    """
    读取联邦学习实验日志 CSV 文件。

    参数：
        input_file：CSV 文件路径

    返回：
        df：读取后的 pandas DataFrame 表格
    """
    df = pd.read_csv(input_file)
    return df


def get_alpha_data(df, alpha_value):
    """
    筛选指定 alpha 值对应的实验数据。

    参数：
        df：原始实验结果表格
        alpha_value：要筛选的 alpha 值，比如 0.1 或 0.3

    返回：
        alpha_df：只包含指定 alpha 的新表格
    """
    alpha_df = df[df["alpha"] == alpha_value]
    return alpha_df


def create_accuracy_pivot(alpha_df):
    """
    把长表转换成适合画折线图的透视表。

    原始长表大概是这样：

        method   round   global_acc
        FedAvg   10      76.8
        FedAvg   20      84.6
        LEDC     10      80.2
        LEDC     20      89.5

    转换后的透视表大概是这样：

        method   FedAvg   LEDC
        round
        10       76.8     80.2
        20       84.6     89.5

    参数：
        alpha_df：某一个 alpha 下的实验数据

    返回：
        pivot_df：适合画准确率曲线的表格
    """
    pivot_df = alpha_df.pivot(
        index="round",          # 横轴：通信轮次
        columns="method",       # 不同方法作为不同曲线
        values="global_acc"     # 曲线上的数值：全局准确率
    )
    return pivot_df


def plot_accuracy_curve(pivot_df, alpha_value, output_file):
    """
    画不同方法在某个 alpha 下的全局准确率曲线图。

    参数：
        pivot_df：由 create_accuracy_pivot() 生成的透视表
        alpha_value：当前图对应的 alpha 值
        output_file：图片保存路径

    返回：
        不返回变量。
        这个函数的作用是把图片保存到本地。
    """
    # 每一列画成一条折线，marker="o" 表示每个点用圆圈标出来
    pivot_df.plot(marker="o")

    # 设置图片标题和坐标轴名称
    plt.title(f"Global Accuracy Curve under alpha={alpha_value}")
    plt.xlabel("Communication Round")
    plt.ylabel("Global Accuracy")

    # 显示网格线，让图更容易看
    plt.grid(True)

    # 自动调整布局，防止标题或坐标轴文字被挡住
    plt.tight_layout()

    # 保存图片
    plt.savefig(output_file)

    # 关闭当前图片，防止下一张图和这张图混在一起
    plt.close()


def get_best_result_by_method(df):
    """
    找出每个方法的最佳实验结果。

    逻辑：
        1. 先按照 global_acc 从高到低排序
        2. 再按照 method 分组
        3. 每个方法组里取第一行
        4. 得到每个方法的最高准确率结果

    参数：
        df：原始实验结果表格

    返回：
        best_df：每个方法的最佳结果表格
    """
    best_df = (
        df.sort_values(by="global_acc", ascending=False)
        .groupby("method")
        .head(1)
        .reset_index(drop=True)
    )
    return best_df


def plot_best_method_bar(best_df, output_file):
    """
    画每个方法最佳准确率的柱状图。

    参数：
        best_df：每个方法的最佳结果表格
        output_file：图片保存路径

    返回：
        不返回变量。
        这个函数的作用是把柱状图保存到本地。
    """
    best_df.plot(
        x="method",         # 横轴：方法名
        y="global_acc",     # 纵轴：最佳准确率
        kind="bar",         # 图类型：柱状图
        legend=False        # 不显示图例
    )

    plt.title("Best Global Accuracy of Each Method")
    plt.xlabel("Method")
    plt.ylabel("Best Global Accuracy")

    # 横轴文字不旋转，保持水平显示
    plt.xticks(rotation=0)

    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()


def main():
    """
    Day 6 主流程。

    main() 的作用是把上面的小函数串起来：
        1. 找项目根目录
        2. 读取实验日志
        3. 分别画 alpha=0.1 和 alpha=0.3 的准确率曲线
        4. 找每个方法的最佳结果
        5. 画最佳准确率柱状图
    """
    # 获取项目根目录
    project_root = get_project_root()

    # 设置输入文件路径
    input_file = project_root / "data" / "fed_experiment_logs.csv"

    # 设置图片保存文件夹
    figure_dir = project_root / "figures"

    # 如果 figures 文件夹不存在，就自动创建
    figure_dir.mkdir(exist_ok=True)

    # 第一步：读取实验日志
    df = load_experiment_logs(input_file)

    print("===== 原始实验日志前 5 行 =====")
    print(df.head())

    # 第二步：分别分析 alpha=0.1 和 alpha=0.3
    alpha_values = [0.1, 0.3]

    print("\n要分析的 alpha 值：", alpha_values)

    for alpha_value in alpha_values:
        print(f"\n===== 正在处理 alpha={alpha_value} =====")

        # 筛选当前 alpha 的数据
        alpha_df = get_alpha_data(df, alpha_value)

        print("\n当前 alpha 对应的数据：")
        print(alpha_df)

        # 把数据转换成适合画折线图的透视表
        pivot_df = create_accuracy_pivot(alpha_df)

        print("\n用于画图的透视表：")
        print(pivot_df)

        # 设置当前 alpha 曲线图的保存路径
        # 例如 alpha=0.1 会变成 day6_accuracy_curve_alpha01.png
        curve_output = figure_dir / f"day6_accuracy_curve_alpha{str(alpha_value).replace('.', '')}.png"

        # 画准确率曲线并保存
        plot_accuracy_curve(
            pivot_df=pivot_df,
            alpha_value=alpha_value,
            output_file=curve_output
        )

        print("\n准确率曲线已保存到：")
        print(curve_output)

    # 第三步：找每个方法的最佳实验结果
    best_df = get_best_result_by_method(df)

    print("\n===== 每个方法的最佳实验结果 =====")
    print(best_df)

    # 设置柱状图保存路径
    bar_output = figure_dir / "day6_best_method_accuracy.png"

    # 画柱状图并保存
    plot_best_method_bar(
        best_df=best_df,
        output_file=bar_output
    )

    print("\n最佳准确率柱状图已保存到：")
    print(bar_output)

    print("\nDay 6 函数重构完成。")


if __name__ == "__main__":
    main()