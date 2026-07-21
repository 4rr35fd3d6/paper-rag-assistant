import json
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


def load_chunks(input_file):
    """
    职责：读取 Day 12 生成的文本块 JSON。

    输入：
        input_file：JSON 文件路径

    输出：
        chunks：文本块列表
    """
    # TODO 1：
    # 1. 使用 UTF-8 打开 JSON 文件
    # 2. 使用 json.load 读取数据
    # 3. 返回 chunks
    with input_file.open(
        "r",
        encoding="utf-8"
    )as file:
        chunks=json.load(file)
    return chunks
    pass


def parse_query(query):
    """
    职责：
        把用户输入拆分成多个关键词。

    输入：
        query：用户输入的查询字符串

    输出：
        keywords：关键词列表

    示例：
        输入："数据 异质性 联邦学习"
        输出：["数据", "异质性", "联邦学习"]
    """
    # TODO 2：
    # 1. 使用 split() 按空格拆分
    # 2. 删除每个关键词首尾空白
    # 3. 删除空字符串
    # 4. 返回 keywords
    raw_keywords=query.split()#默认按空格和换行进行划分
    keywords=[]
    for keyword in raw_keywords:
        cleaned_keyword=keyword.strip().lower()#转换为小写
        if cleaned_keyword:
            keywords.append(cleaned_keyword)
    return keywords


    pass


def calculate_chunk_score(chunk, keywords):
    """
    职责：
        计算一个文本块与查询关键词的匹配分数。

    输入：
        chunk：一个文本块字典
        keywords：关键词列表

    输出：
        score：总匹配次数
        matched_keywords：成功匹配的关键词列表
    """
    content = chunk["content"].lower()

    score = 0
    matched_keywords = []

    # TODO 3：
    # 遍历每个关键词：
    # 1. 统计关键词在 content 中出现的次数
    # 2. 如果出现次数大于 0，增加 score
    # 3. 把匹配成功的关键词加入 matched_keywords
    for keyword in keywords:
        match_count=content.count(keyword)
        if match_count>0:
            score+=match_count
            matched_keywords.append(keyword)

    return score, matched_keywords


def get_result_score(result):
    """
    职责：
        返回一个检索结果的分数。

    这个函数会提供给 sort() 使用。
    """
    return result["score"]


def retrieve_top_chunks(chunks, keywords, top_k=3):
    """
    职责：
        检索与关键词最相关的文本块。

    输入：
        chunks：全部文本块
        keywords：关键词列表
        top_k：最多返回多少个结果

    输出：
        top_results：分数最高的前 top_k 个结果
    """

    # TODO 4：
    # 1. 遍历每个 chunk
    # 2. 调用 calculate_chunk_score()
    # 3. 只保留 score 大于 0 的文本块
    # 4. 给结果增加 score 和 matched_keywords
    # 5. 按 score 从大到小排序
    # 6. 只返回前 top_k 个结果
    results=[]
    for chunk in chunks:
        score,matched_keywords=(
            calculate_chunk_score(
                chunk=chunk,
                keywords=keywords
            )
        )
        if score<=0:
            continue
        result=chunk.copy()
        result["score"] = score
        result["matched_keywords"] = (
            matched_keywords
        )
        results.append(result)
        results.sort(
            key=get_result_score,#按照分数排序
            reverse=True
        )
        top_results = results[:top_k]#取前三.0
        return top_results


def display_results(results):
    """
    职责：把检索结果打印到终端。

    输入：
        results：检索结果列表

    输出：
        无返回值
    """
    if not results:
        print("\n没有找到匹配的文本块。")
        return

    print(f"\n共找到 {len(results)} 个相关文本块：")

    for index, result in enumerate(
        results,
        start=1
    ):
        print("\n" + "=" * 60)

        print(
            f"结果 {index}："
            f"Chunk {result['chunk_id']}"
        )

        print(f"匹配分数：{result['score']}")

        print(
            "匹配关键词："
            + "、".join(result["matched_keywords"])
        )

        print(
            f"原文位置："
            f"{result['start']}～{result['end']}"
        )

        print("\n文本内容：")
        print(result["content"])


def save_results(results, query, output_file):
    """
    职责：保存本次搜索结果。

    输入：
        results：检索结果列表
        query：用户输入的查询
        output_file：JSON 输出路径

    输出：
        无返回值
    """
    # TODO 5：
    # 保存结构：
    # {
    #     "query": 查询内容,
    #     "result_count": 结果数量,
    #     "results": 搜索结果
    # }
    search_data = {
        "query": query,
        "result_count": len(results),
        "results": results
    }

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with output_file.open(
            "w",
            encoding="utf-8"
    ) as file:
        json.dump(
            search_data,
            file,
            ensure_ascii=False,
            indent=2
        )

    pass


def main():
    """
    Day 13 主流程：

    1. 获取项目根目录
    2. 读取 Day 12 文本块
    3. 循环接收用户查询
    4. 拆分关键词
    5. 检索最相关文本块
    6. 显示并保存结果
    """
    project_root = get_project_root()

    input_file = (
        project_root
        / "data"
        / "day12_chunks.json"
    )

    output_file = (
        project_root
        / "data"
        / "day13_search_results.json"
    )

    chunks = load_chunks(input_file)

    print("===== Day 13 关键词检索系统 =====")
    print(f"已加载文本块数量：{len(chunks)}")

    print("\n使用说明：")
    print("多个关键词之间使用空格分隔。")
    print("例如：数据 异质性")
    print("输入 q 可以退出程序。")

# 获取输入
# → 判断是否退出
# → 判断是否为空
# → 拆分关键词
# → 检索
# → 显示
# → 保存
# → 再次等待输入
    while True:#无限循环
        query = input(
            "\n请输入检索关键词："
        ).strip()

        # 输入 q 时退出程序
        if query.lower() == "q":
            print("已退出关键词检索系统。")
            break

        # 输入为空时重新输入
        if not query:
            print("查询内容不能为空。")
            continue

        # 把查询拆成关键词列表
        keywords = parse_query(query)

        if not keywords:
            print("没有识别到有效关键词。")
            continue

        print(f"识别到的关键词：{keywords}")

        # 检索前 3 个相关文本块
        results = retrieve_top_chunks(
            chunks=chunks,
            keywords=keywords,
            top_k=3
        )

        # 显示结果
        display_results(results)

        # 保存本次结果
        save_results(
            results=results,
            query=query,
            output_file=output_file
        )

        print("\n本次搜索结果已保存到：")
        print(output_file)


if __name__ == "__main__":
    main()