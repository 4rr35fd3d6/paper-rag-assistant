import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


# 使用的中文 Embedding 模型
MODEL_NAME = "BAAI/bge-small-zh-v1.5"

# BGE 官方建议：短查询检索长文段时，
# 给查询添加检索指令，文档不需要添加
QUERY_INSTRUCTION = (
    "为这个句子生成表示以用于检索相关文章："
)


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

    if not chunks:
        raise ValueError("文本块文件中没有数据")

    return chunks


def load_embedding_model(model_name):
    """
    职责：加载 Sentence Transformer 模型。

    输入：
        model_name：Hugging Face 模型名称

    输出：
        model：Embedding 模型
    """
    print(f"正在加载 Embedding 模型：{model_name}")
#读取模型名称
# → 从 Hugging Face 下载配置
# → 下载模型权重
# → 下载 tokenizer分词器
# → 加载到内存
    model = SentenceTransformer(model_name)

    return model


def build_embedding_index(
    chunks,
    model,
    embeddings_file
):
    """
    职责：
        将所有文本块转换成 Embedding，
        并把向量保存为 NumPy 文件。

    输入：
        chunks：文本块列表
        model：Embedding 模型
        embeddings_file：向量保存路径

    输出：
        chunk_embeddings：文本块向量矩阵
    """
    corpus = []

    for chunk in chunks:
        corpus.append(chunk["content"])

    chunk_embeddings = model.encode(
        corpus,
        batch_size=32,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True#把每个向量的长度变为 方便后续余弦求相似度，省的后面再调用cosine_similarity()
    )

    embeddings_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    np.save(
        embeddings_file,
        chunk_embeddings
    )

    return chunk_embeddings


def retrieve_top_chunks(
    query,
    chunks,
    model,
    chunk_embeddings,
    top_k=3,
    min_similarity = 0.30
):
    """
    职责：
        将查询转换成 Embedding，
        计算查询与所有文本块的相似度，
        返回前 top_k 个结果。

    输入：
        query：用户问题
        chunks：原始文本块
        model：Embedding 模型
        chunk_embeddings：文本块向量矩阵
        top_k：最多返回几条结果

    输出：
        results：排序后的检索结果
    """
    if top_k <= 0:
        raise ValueError("top_k 必须大于 0")

    cleaned_query = query.strip()

    if not cleaned_query:
        return []

    # 只给查询添加检索指令
    instructed_query = (
        QUERY_INSTRUCTION
        + cleaned_query
    )

    # 将查询转换成向量
    query_embedding = model.encode(
        [instructed_query],
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    # 查询向量：(1, embedding_dimension)
    # 文本矩阵：(chunk_count, embedding_dimension)
    #
    # 两边都已归一化，因此矩阵乘法结果
    # 等价于余弦相似度
    similarities = (
        query_embedding
        @ chunk_embeddings.T#@ 表示矩阵乘法
    ).flatten()#降二维转一维

    # 按相似度从大到小取得索引
    ranked_indices = (
        similarities
        .argsort()[::-1]
    )

    # top_k 不能超过文本块总数
    actual_top_k = min(
        top_k,
        len(chunks)
    )

    results = []

    for chunk_index in ranked_indices[
        :actual_top_k
    ]:
        index = int(chunk_index)
        similarity = float(
            similarities[index]
        )

        # ranked_indices 已按分数从高到低排序。
        # 当前分数低于阈值，后面的分数只会更低，
        # 因此可以直接结束循环。
        if similarity < min_similarity:
            break

        result = chunks[index].copy()

        result["similarity"] = round(
            float(similarities[index]),
            4
        )

        results.append(result)
        if len(results) >= top_k:
         break
    return results


def display_results(query, results):
    """
    职责：显示语义检索结果。
    """
    print(f"\n查询内容：{query}")

    if not results:
        print("没有检索结果。")
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
            f"语义相似度："
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
    model_name,
    embedding_dimension,
    output_file
):
    """
    职责：保存语义检索结果。
    """
    result_data = {
        "retrieval_method": "dense embedding",
        "model_name": model_name,
        "embedding_dimension": (
            embedding_dimension
        ),
        "query_instruction": (
            QUERY_INSTRUCTION
        ),
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
    Day 15 主流程：

    离线索引阶段：
        1. 加载文本块
        2. 加载 Embedding 模型
        3. 生成文本块向量
        4. 保存向量文件

    在线检索阶段：
        5. 接收用户问题
        6. 生成查询向量
        7. 计算语义相似度
        8. 返回 Top K
        9. 显示并保存结果
    """
    project_root = get_project_root()

    input_file = (
        project_root
        / "data"
        / "day12_chunks.json"
    )

    embeddings_file = (
        project_root
        / "data"
        / "day15_chunk_embeddings.npy"
    )

    results_file = (
        project_root
        / "data"
        / "day15_embedding_results.json"
    )

    # 加载原始文本块
    chunks = load_chunks(input_file)

    # 加载模型
    model = load_embedding_model(
        MODEL_NAME
    )

    # 建立稠密向量索引
    chunk_embeddings = (
        build_embedding_index(
            chunks=chunks,
            model=model,
            embeddings_file=embeddings_file
        )
    )

    embedding_dimension = (
        model.get_embedding_dimension()
    )

    print("\n===== Day 15 Embedding 语义检索 =====")
    print(f"模型名称：{MODEL_NAME}")
    print(f"运行设备：{model.device}")
    print(f"文本块数量：{len(chunks)}")
    print(
        f"Embedding 维度："
        f"{embedding_dimension}"
    )
    print(
        f"向量矩阵形状："
        f"{chunk_embeddings.shape}"
    )
    print("输入 q 退出程序。")

    while True:
        query = input(
            "\n请输入检索问题："
        ).strip()

        if query.lower() == "q":
            print("已退出 Embedding 检索系统。")
            break

        if not query:
            print("查询不能为空。")
            continue

        results = retrieve_top_chunks(
            query=query,
            chunks=chunks,
            model=model,
            chunk_embeddings=chunk_embeddings,
            top_k=3,
            min_similarity=0.30
        )

        display_results(
            query=query,
            results=results
        )

        save_results(
            query=query,
            results=results,
            model_name=MODEL_NAME,
            embedding_dimension=(
                embedding_dimension
            ),
            output_file=results_file
        )

        print("\n检索结果已保存到：")
        print(results_file)


if __name__ == "__main__":
    main()