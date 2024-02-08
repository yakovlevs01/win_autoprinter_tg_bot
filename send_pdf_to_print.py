import subprocess

import win32api
import win32print


def deprecated_send_to_print(
    pdf_file_path: str,
    mode: int = 1,
    printer_name: str = win32print.GetDefaultPrinter(),  # Brother DCP-L2560DW series
):
    """Sends pdf file to printer.

    Args:
        pdf_file_path: string-path to file to print

        mode: int - one of following values: 1, 2 or 3.
                1 is single-sided printing (default)

                2 is double-sided printing with flipping on long edge (booklet layout)

                3 is double-sided printing with flipping on short edge (tablet layout)

        printer_name: string-name of desired printer. Defaults to OS default printer.

    """
    print(f"Sending pdf to {printer_name}")
    printdefaults = {"DesiredAccess": win32print.PRINTER_ALL_ACCESS}
    printer_handle = win32print.OpenPrinter(printer_name, printdefaults)
    printer_info = win32print.GetPrinter(printer_handle, 2)
    # режим печати: 1 - односторонняя, 2 двусторонняя по длинному краю, 3 - по короткому
    # https://learn.microsoft.com/ru-ru/windows/win32/api/wingdi/ns-wingdi-devmodea
    printer_info["pDevMode"].Duplex = mode
    win32print.SetPrinter(printer_handle, 2, printer_info, 0)
    print(f"Режим печати: {printer_info['pDevMode'].Duplex}")

    win32api.ShellExecute(0, "print", pdf_file_path, None, ".", 0)

    win32print.ClosePrinter(printer_handle)


def send_to_print(pdf_file_path: str, mode: str = "simplex") -> None:
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
            f'{sumatra} -print-to-default -silent -print-settings "{mode}" "{pdf_file_path}"',
            shell=True,
            text=True,
            capture_output=True,
        )
    )
    # print(subprocess.call([sumatra, "-print-to-default", "-silent", f'-print-settings "{mode}"', pdf_file_path]))


if __name__ == "__main__":
    pdf_file_path = r".\test_files\test3.pdf"
    send_to_print(pdf_file_path=pdf_file_path, mode=2)
