import csv


def load_ip_list(csv_path):
    """
    Reads the first column (column A) from the CSV and returns a list of IP strings.
    Skips empty rows and header-like cells.
    """
    ips = []
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        rdr = csv.reader(f)
        for row in rdr:
            if not row:
                continue
            cell = (row[0] or "").strip()
            if not cell:
                continue
            # naive header skip
            if cell.lower() in {"ip", "ips", "address", "device_ip"}:
                continue
            ips.append(cell)
    return ips
