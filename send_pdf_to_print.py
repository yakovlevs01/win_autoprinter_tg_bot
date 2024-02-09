import subprocess

import win32api
import win32print


def send_any_doc_to_print(
    file_path: str,
    mode: str = "simplex",
    printer_name: str = win32print.GetDefaultPrinter(),  # Brother DCP-L2560DW series
):
    """Sends file to printer.

    Args:
        file_path: string-path to file to print

        mode: str - one of following values: "simplex", "duplexlong" or "duplexshort".
                simplex is single-sided printing (default)

                duplexlong is double-sided printing with flipping on long edge (booklet layout)

                duplexshort is double-sided printing with flipping on short edge (tablet layout)

        printer_name: string-name of desired printer. Defaults to OS default printer.

    """
    modes_windows = {"simplex": 1, "duplexlong": 2, "duplexshort": 3}

    print(f"Sending doc to {printer_name}")

    printdefaults = {"DesiredAccess": win32print.PRINTER_ALL_ACCESS}
    printer_handle = win32print.OpenPrinter(printer_name, printdefaults)
    printer_info = win32print.GetPrinter(printer_handle, 2)
    # режим печати: 1 - односторонняя, 2 двусторонняя по длинному краю, 3 - по короткому
    # https://learn.microsoft.com/ru-ru/windows/win32/api/wingdi/ns-wingdi-devmodea
    printer_info["pDevMode"].Duplex = modes_windows[mode]
    win32print.SetPrinter(printer_handle, 2, printer_info, 0)

    print(f"Режим печати: {printer_info['pDevMode'].Duplex}")

    win32api.ShellExecute(0, "print", file_path, None, ".", 0)

    win32print.ClosePrinter(printer_handle)


def send_pdf_to_print(pdf_file_path: str, mode: str = "simplex") -> None:
    """Sends pdf file to printer.

    Args:
        pdf_file_path: string-path to file to print

        mode: str - one of following values: simplex, duplexlong or duplexshort.
                simplex is single-sided printing (default)

                duplexlong is double-sided printing with flipping on long edge (booklet layout)

                duplexshort is double-sided printing with flipping on short edge (tablet layout)
    """
    assert mode in ("simplex", "duplex", "duplexshort", "duplexlong")
    print(f"Sending {pdf_file_path} with {mode} mode to default printer")
    sumatra = '"C:/Program Files/SumatraPDF/SumatraPDF.exe"'

    print(
        subprocess.run(
            f'{sumatra} -print-to-default -silent -print-settings "{mode},noscale" "{pdf_file_path}"',
            shell=True,
            text=True,
            capture_output=True,
            check=False,
        ).returncode
    )


if __name__ == "__main__":
    pdf_file_path = r".\test_files\test3.pdf"
    send_pdf_to_print(pdf_file_path=pdf_file_path, mode=2)
