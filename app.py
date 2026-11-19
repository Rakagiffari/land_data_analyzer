import streamlit as st
import pandas as pd

from modules.preprocessing import bersihkan_data
from modules.rules import analisis_rules
from modules.report import buat_laporan


st.set_page_config(
    page_title="Land Data Analyzer",
    page_icon="📊",
    layout="wide"
)

st.title("Land Data Analyzer")
st.write(
    "Tools untuk menganalisis kesamaan data pertanahan "
    "berdasarkan aturan pencocokan."
)

st.divider()

# Upload Excel
file = st.file_uploader(
    "Upload file Excel",
    type=["xlsx"]
)

if file:

    excel = pd.ExcelFile(file)

    sheet = st.selectbox(
        "Pilih Sheet",
        excel.sheet_names
    )

    df_asli = pd.read_excel(
        file,
        sheet_name=sheet
    )

    # Nomor baris Excel, dengan asumsi baris pertama adalah header
    df_asli.insert(
        0,
        "Baris Excel",
        range(2, len(df_asli) + 2)
    )

    st.subheader("Preview Data")
    st.dataframe(df_asli.head(10), use_container_width=True)

    # Bersihkan data
    df = bersihkan_data(df_asli)

    # Variabel yang bisa dianalisis
    kolom_analisis = [
        kolom for kolom in df.columns
        if kolom not in ["NIB", "Baris Excel"]
    ]

    st.divider()
    st.subheader("Pengaturan Analisis")

    pilihan_kolom = st.multiselect(
        "Pilih variabel pencocokan",
        options=kolom_analisis,
        default=kolom_analisis
    )

    maksimum = st.selectbox(
        "Maksimal kombinasi variabel",
        options=[1, 2, 3],
        index=1
    )

    st.caption(
        "NIB tidak digunakan sebagai variabel pencocokan. "
        "NIB hanya ditampilkan sebagai informasi pendukung."
    )

    if st.button(
        "Mulai Analisis",
        type="primary",
        use_container_width=True
    ):

        if not pilihan_kolom:
            st.warning("Pilih minimal satu variabel.")
            st.stop()

        with st.spinner("Sedang menganalisis data..."):

            ringkasan, detail = analisis_rules(
                df,
                pilihan_kolom,
                maksimum
            )

        st.success("Analisis selesai!")

        # Ringkasan hasil
        jumlah_kelompok = len(ringkasan)

        jumlah_data_terlibat = (
            detail["Baris Excel"].nunique()
            if not detail.empty
            else 0
        )

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Data", len(df))
        col2.metric("Total Kelompok", jumlah_kelompok)
        col3.metric("Data Terlibat", jumlah_data_terlibat)

        st.divider()

        st.subheader("Ringkasan Kelompok")

        if ringkasan.empty:
            st.info(
                "Tidak ditemukan kelompok dengan kesamaan "
                "berdasarkan aturan yang dipilih."
            )

        else:
            st.dataframe(
                ringkasan,
                use_container_width=True,
                hide_index=True
            )

            st.subheader("Detail Data dalam Kelompok")

            st.dataframe(
                detail,
                use_container_width=True,
                hide_index=True
            )

        # Download laporan
        laporan = buat_laporan(
            df_asli,
            ringkasan,
            detail
        )

        st.download_button(
            label="Download Laporan Excel",
            data=laporan,
            file_name="Laporan_Analisis_Pertanahan.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
