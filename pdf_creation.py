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


def create_pdf_with_2pps(path_to_orgnl_pdf: str):
    """
    DEPRECATED

    Creates new pdf file with 2 pages per sheet in tablet (horizontal) layout.

    Saves it to the same folder but adds "2pps_" at the beggining of filename

    Args:

        `path_to_orgnl_pdf`: string-path to file used as source of new file

    """
    orgnl_pdf_doc = fitz.open(path_to_orgnl_pdf)

    result_file_path = add_prefix_to_filename("2pps_", path_to_orgnl_pdf)
    pdf_file_land_2pps = FPDF(orientation="L", unit="mm", format="A4")

    for i in range(0, len(orgnl_pdf_doc), 2):
        pdf_file_land_2pps.add_page()
        for j in range(2):
            page_idx = i + j
            if page_idx < len(orgnl_pdf_doc):
                img = pixmap_to_image(orgnl_pdf_doc.load_page(page_idx).get_pixmap())
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                buffer.seek(0)
                x_offset = j * HALF_A4_HEIGHT
                y_offset = 0
                pdf_file_land_2pps.image(
                    buffer, x=x_offset, y=y_offset, w=HALF_A4_HEIGHT, h=A4_WIDTH
                )
    pdf_file_land_2pps.output(result_file_path)


def create_pdf_with_4pps(path_to_orgnl_pdf: str):
    """
    DEPRECATED

    Creates new pdf file with 4 pages per sheet in booklet (vertical) layout.

    Saves it to the same folder but adds "4pps_" at the beggining of filename

    Args:

        `path_to_orgnl_pdf`: string-path to file used as source of new file

    """
    orgnl_pdf_doc = fitz.open(path_to_orgnl_pdf)

    result_file_path = add_prefix_to_filename("4pps_", path_to_orgnl_pdf)
    pdf_file_4pps = FPDF()

    for i in range(0, len(orgnl_pdf_doc), 4):
        pdf_file_4pps.add_page()
        for j in range(4):
            page_idx = i + j
            if page_idx < len(orgnl_pdf_doc):
                img = pixmap_to_image(orgnl_pdf_doc.load_page(page_idx).get_pixmap())
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                buffer.seek(0)
                x_offset = (j % 2) * HALF_A4_WIDTH
                y_offset = (j // 2) * HALF_A4_HEIGHT
                pdf_file_4pps.image(
                    buffer, x=x_offset, y=y_offset, w=HALF_A4_WIDTH, h=HALF_A4_HEIGHT
                )
    pdf_file_4pps.output(result_file_path)


def create_pdf(path_to_orgnl_pdf: str, pages_per_sheet: int):
    orgnl_pdf_doc = fitz.open(path_to_orgnl_pdf)

    result_file_path = add_prefix_to_filename(
        f"{pages_per_sheet}pps_", path_to_orgnl_pdf
    )

    if pages_per_sheet not in {2, 4}:
        raise ValueError("pages_per_sheet must be 2 or 4")

    nvertical = pages_per_sheet // 2
    nhorizontal = pages_per_sheet // nvertical

    if pages_per_sheet == 2:
        new_pdf = FPDF(orientation="L")
    else:
        new_pdf = FPDF()

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
