from io import BytesIO
import zipfile
import pandas as pd


def extract_data_file_from_zip(zip_bytes: bytes) -> tuple[str, bytes]:
    with zipfile.ZipFile(BytesIO(zip_bytes)) as zf:
        names = zf.namelist()

        # сначала ищем data.parquet / data.csv
        preferred_names = ["data.parquet", "data.csv"]

        for preferred in preferred_names:
            for name in names:
                if name.lower().endswith(preferred):
                    with zf.open(name) as f:
                        return name, f.read()

        # если именно data.* не нашли, ищем любой parquet/csv
        for name in names:
            lower = name.lower()
            if lower.endswith(".parquet") or lower.endswith(".csv"):
                with zf.open(name) as f:
                    return name, f.read()

    raise ValueError("В архиве не найден ни data.csv, ни data.parquet, ни другой csv/parquet файл")


def read_df_from_bytes(file_name: str, file_bytes: bytes) -> pd.DataFrame:
    lower = file_name.lower()

    if lower.endswith(".csv"):
        return pd.read_csv(BytesIO(file_bytes))

    if lower.endswith(".parquet"):
        return pd.read_parquet(BytesIO(file_bytes))

    raise ValueError("Поддерживаются только csv и parquet")


def df_to_xlsx_bytes(df: pd.DataFrame) -> BytesIO:
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    return buffer


def df_to_csv_bytes(df: pd.DataFrame) -> BytesIO:
    buffer = BytesIO()
    buffer.write(df.to_csv(index=False).encode("utf-8-sig"))
    buffer.seek(0)
    return buffer


def prepare_download_files(zip_bytes: bytes):
    inner_file_name, inner_file_bytes = extract_data_file_from_zip(zip_bytes)
    df = read_df_from_bytes(inner_file_name, inner_file_bytes)

    xlsx_buffer = df_to_xlsx_bytes(df)
    csv_buffer = df_to_csv_bytes(df)

    return df, xlsx_buffer, csv_buffer
