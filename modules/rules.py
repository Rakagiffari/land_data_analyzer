from itertools import combinations
import pandas as pd

from modules.preprocessing import nilai_normalisasi


KOLOM_DILARANG = ["NIB", "Baris Excel"]


def analisis_rules(df, kolom_analisis, maksimum_kombinasi=3):

    df = df.copy().reset_index(drop=True)

    # Pastikan NIB tidak masuk pencocokan
    kolom_analisis = [
        kolom for kolom in kolom_analisis
        if kolom not in KOLOM_DILARANG
        and kolom in df.columns
    ]

    ringkasan = []
    detail = []

    nomor_kelompok = 1

    # Kombinasi variabel 1 sampai batas maksimum
    for jumlah in range(
        1, min(maksimum_kombinasi, len(kolom_analisis)) + 1
    ):

        for kombinasi in combinations(kolom_analisis, jumlah):

            kolom_bantu = []

            # Normalisasi nilai untuk pencocokan
            for i, kolom in enumerate(kombinasi):
                nama_bantu = f"_match_{i}"

                df[nama_bantu] = nilai_normalisasi(
                    df[kolom], kolom
                )

                kolom_bantu.append(nama_bantu)

            # Baris dengan nilai kosong tidak ikut dicocokkan
            data_valid = df.dropna(subset=kolom_bantu)

            if data_valid.empty:
                continue

            # Kelompokkan data berdasarkan nilai yang sama
            for nilai, anggota in data_valid.groupby(
                kolom_bantu, sort=False, dropna=True
            ):

                if len(anggota) < 2:
                    continue

                if not isinstance(nilai, tuple):
                    nilai = (nilai,)

                id_kelompok = f"GRP-{nomor_kelompok:05d}"

                nilai_kesamaan = " | ".join(
                    f"{kolom}: {val}"
                    for kolom, val in zip(kombinasi, nilai)
                )

                baris = anggota["Baris Excel"].astype(str).tolist()

                nib = (
                    anggota["NIB"].fillna("-").astype(str).tolist()
                    if "NIB" in anggota.columns
                    else ["-"] * len(anggota)
                )

                ringkasan.append({
                    "ID Kelompok": id_kelompok,
                    "Jumlah Data": len(anggota),
                    "Variabel yang Sama": " + ".join(kombinasi),
                    "Nilai Kesamaan": nilai_kesamaan,
                    "Baris Excel": ", ".join(baris),
                    "NIB (Informasi)": ", ".join(nib)
                })

                for indeks in anggota.index:
                    data_detail = df.loc[indeks].drop(
                        labels=[c for c in df.columns if c.startswith("_match_")],
                        errors="ignore"
                    ).to_dict()

                    data_detail["ID Kelompok"] = id_kelompok
                    data_detail["Variabel yang Sama"] = " + ".join(kombinasi)
                    data_detail["Nilai Kesamaan"] = nilai_kesamaan

                    detail.append(data_detail)

                nomor_kelompok += 1

            # Hapus kolom bantu sebelum kombinasi berikutnya
            df.drop(columns=kolom_bantu, inplace=True)

    return pd.DataFrame(ringkasan), pd.DataFrame(detail)
