import fitz
from io import BytesIO
from PIL import Image

def convert_images_to_rgb(input_pdf_path, output_pdf_path):
    """
    将 PDF 中所有非 RGB/Gray 的图像转换为 RGB 并重新嵌入。
    即使原始图像为 CMYK、Indexed 等也能安全处理。
    """
    doc = fitz.open(input_pdf_path)

    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images(full=True)

        for img in image_list:
            xref = img[0]
            try:
                # 获取原始 pixmap
                orig_pix = fitz.Pixmap(doc, xref)

                # 检查颜色空间
                if not orig_pix.colorspace:
                    print(f"第 {page_num + 1} 页，xref={xref}: 未知颜色空间，跳过")
                    continue

                cs_name = orig_pix.colorspace.name

                if 'rgb' in cs_name.lower() or 'gray' in cs_name.lower(): continue

                print(f"正在转换第 {page_num + 1} 页的图像 (xref={xref})，原颜色空间: {cs_name} -> 转为 RGB")

                # ✅ 关键步骤：将非 RGB pixmap 转为 RGB 格式的 pixmap
                if orig_pix.colorspace.n == 4:  # CMYK
                    # 方法1：直接创建一个新的 RGB pixmap 并复制数据
                    rgb_pix = fitz.Pixmap(fitz.csRGB, orig_pix)
                elif orig_pix.colorspace.n == 1:  # Gray（理论上不会到这里）
                    rgb_pix = fitz.Pixmap(fitz.csRGB, orig_pix)
                else:
                    # 其他情况（如 Indexed），先转为普通 pixmap
                    rgb_pix = fitz.Pixmap(fitz.csRGB, orig_pix)

                # 现在 rgb_pix 是 RGB 格式，可以安全 tobytes
                img_data = rgb_pix.tobytes("ppm")  # ✅ 安全
                pil_image = Image.open(BytesIO(img_data))

                # 可选：进一步用 PIL 处理（如压缩、重采样）
                # 这里确保是 RGB 模式
                if pil_image.mode != "RGB":
                    pil_image = pil_image.convert("RGB")

                # 保存为 PNG 字节流
                img_bytes_io = BytesIO()
                pil_image.save(img_bytes_io, format="PNG", optimize=True)
                img_bytes = img_bytes_io.getvalue()

                # ✅ 替换原始图像流
                doc.update_stream(xref, img_bytes)

            except Exception as e:
                print(f"处理 xref={xref} 时出错: {e}")
                continue

    # 保存结果
    doc.save(output_pdf_path, garbage=4, deflate=True, clean=True)
    doc.close()
    print(f"✅ 已保存转换后的 PDF 到: {output_pdf_path}")


# === 使用示例 ===
input_path = r"C:\Users\Lenovo\Downloads\esunfhc_annual_2024.pdf"
# input_path = r'D:\AiAgent\SBG\common\file\document_covert\output_rgb_converted1.pdf'
output_path = "output_rgb_converted.pdf"

convert_images_to_rgb(input_path, output_path)