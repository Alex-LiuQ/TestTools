import pymupdf

doc = pymupdf.open("input.pdf")

for page_num, page in enumerate(doc):
    print(f"处理第 {page_num + 1} 页...")

    page.clean_contents()
    xref = page.get_contents()[0]
    cont = bytearray(page.read_contents())

    deleted = 0
    while True:
        # 精确查找带 Watermark 的 Artifact
        i1 = cont.find(b"/Subtype/Watermark")
        if i1 < 0:
            break

        # 往前找最近的 /Artifact 或 BDC
        start = cont.rfind(b"/Artifact", 0, i1)
        if start < 0:
            start = cont.rfind(b"BDC", 0, i1)
        if start < 0:
            start = i1 - 50  # 兜底

        # 往后找对应的 EMC
        end = cont.find(b"EMC", i1)
        if end < 0:
            break

        # 再往前多包含一点（把前面的 q 也去掉更干净）
        start = max(0, start - 10)

        # 删除这一整段
        cont[start : end + 3] = b""
        deleted += 1

    if deleted:
        print(f"  已精确删除 {deleted} 处 Watermark")
        doc.update_stream(xref, bytes(cont))
    else:
        print("  未发现 Watermark")

doc.save("cleaned_v2.pdf", garbage=4, deflate=True)
doc.close()
print("\n处理完成，请打开 cleaned_v2.pdf 检查第3页表格是否恢复正常。")
