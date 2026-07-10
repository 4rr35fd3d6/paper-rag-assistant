import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


def get_project_root():
    """
    获取项目根目录。

    当前代码文件位于 practice 文件夹中，
    parents[1] 可以返回项目根目录：
    project1_paper_rag_assistant
    """
    project_root = Path(__file__).resolve().parents[1]
    return project_root


def load_experiment_logs(input_file):
    """
    读取联邦学习实验日志，并检查数据格式。

    参数：
        input_file：实验日志 CSV 文件路径

    返回：
        df：读取后的 DataFrame

    可能抛出的异常：
        FileNotFoundError：输入文件不存在
        ValueError：CSV 缺少必要的列
    """
    # 先检查文件是否存在
    if not input_file.exists():
        raise FileNotFoundError(f"找不到实验日志文件：{input_file}")

    # 读取 CSV
    df = pd.read_csv(input_file)

    # 程序正常运行必须包含这些列
    required_columns = {
        "method",
        "alpha",
        "round",
        "global_acc",
        "loss"
    }

    # 找出缺失的列
    missing_columns = required_columns - set(df.columns)

    # 如果存在缺失列，主动抛出异常
    if missing_columns:
        raise ValueError(
            f"实验日志缺少必要的列：{sorted(missing_columns)}"
        )

    return df


def read_float(prompt_text):
    """
    从终端读取一个浮点数。

    参数：
        prompt_text：显示给用户的输入提示

    返回：
        value：用户输入并转换后的浮点数

    这个函数会持续询问，直到用户输入合法数字。
    """
    while True:
        user_input = input(prompt_text).strip()

        try:
            value = float(user_input)
            return value

        except ValueError:
            print("输入格式错误，请输入数字，例如 0.3 或 88。")


def filter_experiment_results(df, alpha_value, min_accuracy):
    """
    根据 alpha 和最低准确率筛选实验结果。

    筛选条件：
        1. alpha 等于 alpha_value
        2. global_acc 大于等于 min_accuracy

    参数：
        df：原始实验日志
        alpha_value：用户指定的 alpha
        min_accuracy：用户指定的最低准确率

    返回：
        filtered_df：筛选并按准确率降序排列后的结果
    """
    # alpha 条件
    # round(6) 可以减少浮点数比较可能产生的精度问题
    alpha_condition = (
        df["alpha"].round(6) == round(alpha_value, 6)
    )

    # 准确率条件
    accuracy_condition = (
        df["global_acc"] >= min_accuracy
    )

    # & 表示两个条件必须同时成立
    filtered_df = df[
        alpha_condition & accuracy_condition
    ]

    # 按照准确率从高到低排序
    filtered_df = filtered_df.sort_values(
        by="global_acc",
        ascending=False
    )

    # 重新生成从 0 开始的行索引
    filtered_df = filtered_df.reset_index(drop=True)

    return filtered_df


def format_number_for_filename(number):
    """
    把数字转换成适合放进文件名的文本。

    示例：
        0.3  -> 0p3
        88.0 -> 88
        88.5 -> 88p5

    参数：
        number：数字

    返回：
        filename_text：适合文件名使用的字符串
    """
    # 如果数字本质上是整数，就去掉末尾的 .0
    if float(number).is_integer():
        number_text = str(int(number))
    else:
        number_text = str(number)

    # 文件名中用 p 代替小数点
    filename_text = number_text.replace(".", "p")

    return filename_text


def save_filtered_results(filtered_df, output_file):
    """
    把筛选结果保存成 CSV。

    参数：
        filtered_df：筛选后的实验结果
        output_file：CSV 输出路径

    返回：
        无返回值，函数会在本地生成 CSV 文件。
    """
    filtered_df.to_csv(
        output_file,
        index=False
    )


def plot_filtered_results(
    filtered_df,
    alpha_value,
    min_accuracy,
    output_file
):
    """
    把筛选后的实验结果画成柱状图。

    横轴：
        方法名和训练轮次

    纵轴：
        global_acc

    参数：
        filtered_df：筛选后的结果
        alpha_value：当前分析的 alpha
        min_accuracy：最低准确率
        output_file：图片保存路径

    返回：
        无返回值，函数会保存 PNG 图片。
    """
    # copy() 创建副本，避免直接修改原始 filtered_df
    plot_df = filtered_df.copy()

    # 创建柱状图横轴标签
    # 例如：LEDC-r30、FedProx-r30
    plot_df["label"] = (
        plot_df["method"]
        + "-r"
        + plot_df["round"].astype(str)
    )

    # 绘制柱状图
    plot_df.plot(
        x="label",
        y="global_acc",
        kind="bar",
        legend=False
    )

    plt.title(
        f"Filtered Results: alpha={alpha_value}, "
        f"accuracy>={min_accuracy}"
    )
    plt.xlabel("Method and Round")
    plt.ylabel("Global Accuracy")

    # 让横轴文字保持水平
    plt.xticks(rotation=0)

    # 自动调整布局
    plt.tight_layout()

    # 保存图片
    plt.savefig(output_file)

    # 关闭当前图，防止影响下一次绘图
    plt.close()


def main():
    """
    Day 7 主流程。

    主要步骤：
        1. 获取项目路径
        2. 读取实验日志
        3. 显示可用的 alpha
        4. 接收用户输入
        5. 筛选实验结果
        6. 保存 CSV
        7. 保存柱状图
    """
    project_root = get_project_root()

    input_file = (
        project_root
        / "data"
        / "fed_experiment_logs.csv"
    )

    data_dir = project_root / "data"
    figure_dir = project_root / "figures"

    # 如果文件夹已经存在，不会报错
    data_dir.mkdir(exist_ok=True)
    figure_dir.mkdir(exist_ok=True)

    try:
        # 第一步：读取实验数据
        df = load_experiment_logs(input_file)

        print("===== 实验日志前 5 行 =====")
        print(df.head())

        # 找出日志中所有可用的 alpha
        # 把 NumPy 浮点数转换成普通 Python float，显示更简洁
        available_alphas = sorted(
            float(alpha) for alpha in df["alpha"].unique()
        )

        print("\n当前日志中可用的 alpha：")
        print(available_alphas)

        # 第二步：读取用户输入
        alpha_value = read_float(
            "\n请输入要分析的 alpha："
        )

        min_accuracy = read_float(
            "请输入最低准确率："
        )

        # 检查用户输入的 alpha 是否存在
        if alpha_value not in available_alphas:
            print(
                f"\n当前日志中不存在 alpha={alpha_value}。"
            )
            print(
                f"可用的 alpha 为：{available_alphas}"
            )
            return

        # 第三步：筛选数据
        filtered_df = filter_experiment_results(
            df=df,
            alpha_value=alpha_value,
            min_accuracy=min_accuracy
        )

        # 如果没有符合条件的结果，提前结束程序
        if filtered_df.empty:
            print("\n没有找到符合条件的实验结果。")
            return

        print("\n===== 筛选结果 =====")
        print(filtered_df)

        print(
            f"\n共筛选出 {len(filtered_df)} 条实验记录。"
        )

        # 把数字转换成适合文件名的文本
        alpha_text = format_number_for_filename(
            alpha_value
        )
        accuracy_text = format_number_for_filename(
            min_accuracy
        )

        # 动态生成输出文件名
        csv_output = (
            data_dir
            / (
                f"day7_filtered_alpha{alpha_text}"
                f"_acc{accuracy_text}.csv"
            )
        )

        figure_output = (
            figure_dir
            / (
                f"day7_filtered_alpha{alpha_text}"
                f"_acc{accuracy_text}.png"
            )
        )

        # 第四步：保存 CSV
        save_filtered_results(
            filtered_df=filtered_df,
            output_file=csv_output
        )

        # 第五步：保存图片
        plot_filtered_results(
            filtered_df=filtered_df,
            alpha_value=alpha_value,
            min_accuracy=min_accuracy,
            output_file=figure_output
        )

        print("\n筛选结果 CSV 已保存到：")
        print(csv_output)

        print("\n实验结果图片已保存到：")
        print(figure_output)

        print("\nDay 7 实验分析完成。")

    except FileNotFoundError as error:
        print("\n文件错误：")
        print(error)

    except ValueError as error:
        print("\n数据格式错误：")
        print(error)

    except Exception as error:
        print("\n程序出现未预料的错误：")
        print(error)


if __name__ == "__main__":
    main()