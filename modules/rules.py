from itertools import combinations
import pandas as pd

from modules.preprocessing import nilai_normalisasi


KOLOM_DILARANG = ["NIB", "Baris Excel"]


def analisis_rules(df, kolom_analisis, maksimum_kombinasi=3):

    df = df.copy().reset_index(drop=True)

    kolom_analisis = [
        kolom for kolom in kolom_analisis
        if kolom not in KOLOM_DILARANG
        and kolom in df.columns
    ]

    if "Baris Excel" not in df.columns:
        df["Baris Excel"] = range(2, len(df) + 2)

    # Normalisasi hanya satu kali
    data_normal = pd.DataFrame(index=df.index)

    for kolom in kolom_analisis:
        data_normal[kolom] = nilai_normalisasi(
            df[kolom], kolom
        )

    semua_ringkasan = []
    semua_detail = []

    nomor_kelompok = 1

    batas = min(maksimum_kombinasi, len(kolom_analisis))

    for jumlah in range(1, batas + 1):

        for kombinasi in combinations(kolom_analisis, jumlah):

            # Abaikan baris yang memiliki nilai kosong
            valid = data_normal[list(kombinasi)].notna().all(axis=1)

            data_valid = data_normal.loc[valid, list(kombinasi)]

            if len(data_valid) < 2:
                continue

            # Groupby sekaligus
            grouped = data_valid.groupby(
                list(kombinasi),
                sort=False,
                dropna=True
            ).indices

            for nilai, posisi in grouped.items():

                if len(posisi) < 2:
                    continue

                indeks_asli = data_valid.index.take(posisi)

                anggota = df.loc[indeks_asli]

                id_kelompok = f"GRP-{nomor_kelompok:05d}"

                if not isinstance(nilai, tuple):
                    nilai = (nilai,)

                nilai_kesamaan = " | ".join(
                    f"{kolom}: {val}"
                    for kolom, val in zip(kombinasi, nilai)
                )

                semua_ringkasan.append({
                    "ID Kelompok": id_kelompok,
                    "Jumlah Data": len(anggota),
                    "Variabel yang Sama": " + ".join(kombinasi),
                    "Nilai Kesamaan": nilai_kesamaan,
                    "Baris Excel": ", ".join(
                        anggota["Baris Excel"].astype(str)
                    ),
                    "NIB (Informasi)": ", ".join(
                        anggota["NIB"].fillna("-").astype(str)
                    ) if "NIB" in anggota.columns else "-"
                })

                detail = anggota.copy()

                detail["ID Kelompok"] = id_kelompok
                detail["Variabel yang Sama"] = " + ".join(kombinasi)
                detail["Nilai Kesamaan"] = nilai_kesamaan

                semua_detail.append(detail)

                nomor_kelompok += 1

    ringkasan = pd.DataFrame(semua_ringkasan)

    detail = (
        pd.concat(semua_detail, ignore_index=True)
        if semua_detail
        else pd.DataFrame()
    )

    return ringkasan, detail
