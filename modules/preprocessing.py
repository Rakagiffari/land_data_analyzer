import pandas as pd

KOLOM_ANGKA = ["Luas", "Luas Fisik", "Luas Peta"]


def bersihkan_data(df):
    df = df.copy()

    # Hilangkan spasi di nama kolom
    df.columns = df.columns.astype(str).str.strip()

    # Bersihkan kolom teks
    for kolom in df.columns:
        if kolom not in KOLOM_ANGKA:
            df[kolom] = df[kolom].apply(
                lambda x: x.strip().upper()
                if isinstance(x, str)
                else x
            )

    # Samakan format angka
    for kolom in KOLOM_ANGKA:
        if kolom in df.columns:
            df[kolom] = pd.to_numeric(
                df[kolom], errors="coerce"
            )

    return df


def nilai_normalisasi(series, kolom):
    if kolom in KOLOM_ANGKA:
        angka = pd.to_numeric(series, errors="coerce")
        return angka.map(
            lambda x: format(x, ".15g") if pd.notna(x) else pd.NA
        )

    hasil = series.astype("string").str.strip().str.upper()
    hasil = hasil.replace("", pd.NA)

    return hasil
