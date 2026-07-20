import json
import re
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


def load_text(input_file):
    """
    职责：读取文本文件。

    输入：
        input_file：文本文件路径

    输出：
        text：读取到的完整字符串
    """
    # TODO 1：
    # 使用 UTF-8 编码读取 input_file
    # 返回 text
    text=input_file.read_text(
        encoding="utf-8"
    )
    return text
    pass


def clean_text(text):
    """
    职责：清洗原始文本。

    输入：
        text：原始文本字符串

    输出：
        cleaned_text：清洗后的字符串

    清洗规则：
        1. 统一换行符
        2. 连续空格压缩成一个空格
        3. 三个及以上连续换行压缩成两个换行
        4. 删除文本首尾空白
    """
    # TODO 2：
    # 按照上面的规则清洗文本
    # 返回 cleaned_text
    # 把不同系统的换行服都统一成\n
    clean_text=text.replace(
        "\r\n","\n"
    ).replace(
        "\r","\n"
    )
    # 把连续的空格或者制表符都压缩成一个空格
    clean_text=re.sub(
        r"[\t]+",
        "",
        clean_text
    )
    # 把三个以上的换行压缩成两个换行+
    clean_text=re.sub(
        r"\n{3,}",
        "\n\n",
        clean_text
    )
    # 删除整个文本开头和结尾的空白
    clean_text=clean_text.strip()
    return clean_text
    pass


def split_text(text, chunk_size=200, overlap=40):
    """
    职责：按照字符数量切分文本。

    输入：
        text：清洗后的文本
        chunk_size：每个文本块的最大字符数量
        overlap：相邻文本块重复的字符数量

    输出：
        chunks：文本块列表

    每个文本块的格式：
        {
            "chunk_id": 1,
            "start": 0,
            "end": 200,
            "content": "文本内容"
        }
    """
    # 参数检查
    if chunk_size <= 0:
        raise ValueError("chunk_size 必须大于 0")

    if overlap < 0:
        raise ValueError("overlap 不能小于 0")

    if overlap >= chunk_size:
        raise ValueError("overlap 必须小于 chunk_size")

    # TODO 3：
    # 使用 while 循环切分文本
    # 返回 chunks
    chunks=[]
    start=0
    chunk_id=1
    while start<len(text):
        end=min(
            start+chunk_size,
            len(text)
        )
        content=text[start:end].strip()
        if content:
            chunk={
                "chunk_id": chunk_id,
                "start": start,
                "end": end,
                "content": content
            }
            chunks.append(chunk)
            chunk_id += 1
        if end>=len(text):
            break
        start=end-overlap
    return  chunks




def save_chunks(chunks, output_file):
    """
    职责：把文本块保存成 JSON 文件。

    输入：
        chunks：文本块列表
        output_file：JSON 输出路径

    输出：
        无返回值
    """
    # TODO 4：
    # 1. 确保输出目录存在
    # 2. 使用 json.dump 保存 chunks
    # 3. 保留中文并设置缩进
    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )
    with output_file.open(
            "w",
            encoding="utf-8"
    ) as file:
        json.dump(
            chunks,
            file,
            ensure_ascii=False,
            indent=2
        )
    pass


def main():
    """
    Day 12 主流程：

    1. 获取项目根目录
    2. 读取测试文档
    3. 清洗文本
    4. 切分文本
    5. 保存 JSON
    6. 打印切块结果
    """
    project_root = get_project_root()

    input_file = (
        project_root
        / "data"
        / "sample_paper.txt"
    )

    output_file = (
        project_root
        / "data"
        / "day12_chunks.json"
    )

    # 读取原始文本
    raw_text = load_text(input_file)

    print("===== 原始文本信息 =====")
    print(f"原始文本字符数：{len(raw_text)}")

    # 清洗文本
    cleaned_text = clean_text(raw_text)

    print("\n===== 清洗后文本信息 =====")
    print(f"清洗后字符数：{len(cleaned_text)}")

    # 切分文本
    chunks = split_text(
        text=cleaned_text,
        chunk_size=200,
        overlap=40
    )

    print("\n===== 文本切块结果 =====")
    print(f"文本块数量：{len(chunks)}")

    # 显示每个文本块的基本信息
    for chunk in chunks:
        print(
            f"\nChunk {chunk['chunk_id']}："
            f"start={chunk['start']}，"
            f"end={chunk['end']}，"
            f"字符数={len(chunk['content'])}"
        )

        print(chunk["content"])

    # 保存文本块
    save_chunks(
        chunks=chunks,
        output_file=output_file
    )

    print("\n文本块已保存到：")
    print(output_file)


if __name__ == "__main__":
    main()