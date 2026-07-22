import json
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def get_project_root():
    """
    职责：获取项目根目录。

    输出：
        Path 类型的项目根目录
    """
    return Path(__file__).resolve().parents[1]


def load_chunks(input_file):
    """
    职责：读取 Day 12 生成的文本块。

    输入：
        input_file：JSON 文件路径

    输出：
        chunks：文本块列表
    """
    if not input_file.exists():
        raise FileNotFoundError(
            f"没有找到文本块文件：{input_file}"
        )

    with input_file.open(
        "r",
        encoding="utf-8"
    ) as file:
        chunks = json.load(file)

    return chunks


def build_tfidf_index(chunks):
    """
    职责：
        根据全部文本块建立 TF-IDF 索引。

    输入：
        chunks：文本块列表

    输出：
        vectorizer：已经学习词表和 IDF 的向量化器
        chunk_matrix：全部文本块的 TF-IDF 矩阵
    """
    corpus = []#语料库

    for chunk in chunks:
        corpus.append(chunk["content"])
    # 学习文本特征
    # 计算TF - IDF权重
    # 将文本转换为向量
    vectorizer = TfidfVectorizer(
        analyzer="char",
        ngram_range=(2, 4),
        min_df=1,#文档频率
        sublinear_tf=True#词频越高越不重要
    )

    chunk_matrix = vectorizer.fit_transform(
        corpus
    )#把文本块变成稀疏矩阵 行为文本块数 列为全部特征数,对于一个文本块而言,未出现的特征,他的值为0

    return vectorizer, chunk_matrix#因为后续用户输入问题时也要转换为同一个特征空间所以还要返回vectorizer


def retrieve_top_chunks(
    query,
    chunks,
    vectorizer,
    chunk_matrix,
    top_k=3,
    min_similarity=0.05
):
    """
    职责：
        将查询转换为 TF-IDF 向量，
        计算查询和所有文本块的余弦相似度，
        返回相似度最高的前 top_k 个结果。

    输入：
        query：用户查询
        chunks：原始文本块
        vectorizer：训练完成的 TF-IDF 向量化器
        chunk_matrix：文本块 TF-IDF 矩阵
        top_k：返回结果数量

    输出：
        results：排序后的检索结果
    """
    if top_k <= 0:
        raise ValueError("top_k 必须大于 0")

    cleaned_query = query.strip()

    if not cleaned_query:
        return []

    # 只能使用 transform，不能重新 fit,因为重新 fit 会重建特征空间
    query_vector = vectorizer.transform(
        [cleaned_query]
    )#得加[],转换后为一行 总特征数列的矩阵

    # 计算查询与所有文本块的相似度
    # 接收两个向量或矩阵
    # → 计算余弦相似度得到一个一行文本块数列的矩阵
    similarities = cosine_similarity(
        query_vector,
        chunk_matrix
    ).flatten()#把二维压缩成一维后续更好索引访问

    # argsort() 默认从小到大
    # [::-1] 将顺序反转为从大到小
    ranked_indices = (
        similarities
        .argsort()[::-1]
    )

    results = []

    for chunk_index in ranked_indices:
        similarity = float(
            similarities[chunk_index]
        )

        # 完全没有相似特征时跳过
        if similarity <= min_similarity:
            continue

        result = chunks[int(chunk_index)].copy()

        result["similarity"] = round(
            similarity,
            4
        )

        results.append(result)

        # 已经获得足够数量后结束循环
        if len(results) >= top_k:
            break

    return results


def display_results(query, results):
    """
    职责：在终端显示检索结果。
    """
    print(f"\n查询内容：{query}")

    if not results:
        print("没有找到相关文本块。")
        return

    print(f"返回结果数量：{len(results)}")

    for rank, result in enumerate(
        results,
        start=1
    ):
        print("\n" + "=" * 60)

        print(
            f"排名 {rank}："
            f"Chunk {result['chunk_id']}"
        )

        print(
            f"余弦相似度："
            f"{result['similarity']:.4f}"
        )

        print(
            f"原文位置："
            f"{result['start']}～{result['end']}"
        )

        print("\n文本内容：")
        print(result["content"])


def save_results(
    query,
    results,
    output_file
):
    """
    职责：保存本次 TF-IDF 检索结果。
    """
    result_data = {
        "retrieval_method": "TF-IDF char n-gram",
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
            result_data,
            file,
            ensure_ascii=False,
            indent=2
        )


def main():
    """
    Day 14 主流程：

    1. 加载文本块
    2. 建立 TF-IDF 索引
    3. 接收用户查询
    4. 将查询转换为向量
    5. 计算余弦相似度
    6. 返回 Top K
    7. 显示并保存结果
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
        / "day14_tfidf_results.json"
    )

    chunks = load_chunks(input_file)

    vectorizer, chunk_matrix = (
        build_tfidf_index(chunks)
    )

    print("===== Day 14 TF-IDF 向量检索 =====")
    print(f"文本块数量：{len(chunks)}")
    print(
        f"TF-IDF 矩阵形状："
        f"{chunk_matrix.shape}"
    )
    print(
        f"特征数量："
        f"{len(vectorizer.vocabulary_)}"
    )

    print("\n输入 q 退出程序。")

    while True:
        query = input(
            "\n请输入检索问题："
        ).strip()

        if query.lower() == "q":
            print("已退出 TF-IDF 检索系统。")
            break

        if not query:
            print("查询不能为空。")
            continue

        results = retrieve_top_chunks(
            query=query,
            chunks=chunks,
            vectorizer=vectorizer,
            chunk_matrix=chunk_matrix,
            top_k=3
        )

        display_results(
            query=query,
            results=results
        )

        save_results(
            query=query,
            results=results,
            output_file=output_file
        )

        print("\n检索结果已保存到：")
        print(output_file)


if __name__ == "__main__":
    main()