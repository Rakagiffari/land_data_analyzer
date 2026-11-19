import pandas as pd
from io import BytesIO


def buat_laporan(df_asli, ringkasan, detail):

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        df_asli.to_excel(
            writer,
            sheet_name="Data Asli",
            index=False
        )

        ringkasan.to_excel(
            writer,
            sheet_name="Ringkasan Kelompok",
            index=False
        )

        detail.to_excel(
            writer,
            sheet_name="Detail Kelompok",
            index=False
        )

    output.seek(0)

    return output
