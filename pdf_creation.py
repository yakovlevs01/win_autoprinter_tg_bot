import fitz
from fpdf import FPDF
from PIL import Image
from io import BytesIO


def pixmap_to_image(pixmap):
    img_data = pixmap.samples
    img = Image.frombytes("RGB", [pixmap.width, pixmap.height], img_data)
    return img


def get_folder_path(full_file_path: str) -> str:
    return full_file_path[: full_file_path.rfind("\\") + 1]


def get_filename(full_file_path: str) -> str:
    return full_file_path[full_file_path.rfind("\\") + 1 :]


def add_prefix_to_filename(prefix: str, str_to_mod: str) -> str:
    return get_folder_path(str_to_mod) + prefix + get_filename(str_to_mod)


A4_WIDTH = 210
A4_HEIGHT = 297
HALF_A4_WIDTH = 105
HALF_A4_HEIGHT = 148.5


def create_pdf(path_to_orgnl_pdf: str, pages_per_sheet: int):
    orgnl_pdf_doc = fitz.open(path_to_orgnl_pdf)

    result_file_path = add_prefix_to_filename(
        f"{pages_per_sheet}pps_", path_to_orgnl_pdf
    )

    if pages_per_sheet not in {2, 4}:
        raise ValueError("pages_per_sheet must be 2 or 4")

    nvertical = pages_per_sheet // 2
    nhorizontal = pages_per_sheet // nvertical

    new_pdf = FPDF(orientation="L") if pages_per_sheet == 2 else FPDF()

    for i in range(0, len(orgnl_pdf_doc), pages_per_sheet):
        new_pdf.add_page()
        for j in range(pages_per_sheet):
            page_idx = i + j
            if page_idx < len(orgnl_pdf_doc):
                img = pixmap_to_image(orgnl_pdf_doc.load_page(page_idx).get_pixmap())
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                buffer.seek(0)
                if pages_per_sheet == 2:  # new_pdf.cur_orientation == "L":
                    x_offset = j * A4_HEIGHT / nhorizontal
                    y_offset = 0
                    new_pdf.image(
                        buffer,
                        x=x_offset,
                        y=y_offset,
                        w=A4_HEIGHT / nhorizontal,
                        h=A4_WIDTH / nvertical,
                    )
                elif pages_per_sheet == 4:  # new_pdf.cur_orientation == "P":
                    x_offset = (j % nhorizontal) * A4_WIDTH / nhorizontal
                    y_offset = (j // nhorizontal) * A4_HEIGHT / nvertical
                    new_pdf.image(
                        buffer,
                        x=x_offset,
                        y=y_offset,
                        w=A4_WIDTH / nhorizontal,
                        h=A4_HEIGHT / nvertical,
                    )

    new_pdf.output(result_file_path)
    return result_file_path


if __name__ == "__main__":
    create_pdf(r".\test_files\1.pdf", 2)
