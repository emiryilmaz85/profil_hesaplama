
# -*- coding: utf-8 -*-
import streamlit as st
import math
import os

from tables.boru import BORU_TABLO
from tables.rhs import RHS_TABLO
from tables.l_equal import L_EQUAL_TABLO
from tables.l_unequal import L_UNEQUAL_TABLO
from tables.ipe import IPE_TABLO
from tables.hea import HEA_TABLO
from tables.heb import HEB_TABLO
from tables.upn import UPN_TABLO
from tables.bulbflat import BULBFLAT_TABLO
from tables.round import ROUND_TABLO
from tables.square import SQUARE_TABLO

BASE_DIR = os.path.dirname(__file__)
IMG_DIR = os.path.join(BASE_DIR, "img")


# ---------------------------------------------------------
# TEKNIK CIZIM SECIMI
# ---------------------------------------------------------
def get_image_for_type(profil_tipi):
    if profil_tipi in ["I Profil (IPE)", "H Profil (HEA)", "H Profil (HEB)", "U Profil (UPN)"]:
        fname = "profil_set2.png"
    else:
        fname = "profil_set1.png"
    path = os.path.join(IMG_DIR, fname)
    if os.path.exists(path):
        return path
    return None


# ---------------------------------------------------------
# AGIRLIK HESABI
# ---------------------------------------------------------
def agirlik_hesap(A_m2, L_m, rho_g_cm3):
    hacim_m3 = A_m2 * L_m
    return hacim_m3 * rho_g_cm3 * 1000.0


# ---------------------------------------------------------
# WX – WY HESAPLARI
# ---------------------------------------------------------
def wx_wy_boru(row):
    OD = row.get("OD")
    t = row.get("t")
    if not OD or not t:
        return None, None
    OD_m = OD / 1000.0
    t_m = t / 1000.0
    ID_m = OD_m - 2 * t_m
    if ID_m <= 0:
        return None, None
    Ix_m4 = (math.pi / 64.0) * (OD_m ** 4 - ID_m ** 4)
    Wx_m3 = Ix_m4 / (OD_m / 2.0)
    Wx_mm3 = Wx_m3 * 1e9
    return Wx_mm3, Wx_mm3


def wx_wy_rhs(row):
    A = row.get("A")
    B = row.get("B")
    t = row.get("t")
    if not A or not B or not t:
        return None, None
    h = A / 1000.0
    b = B / 1000.0
    t_m = t / 1000.0
    if h <= 2 * t_m or b <= 2 * t_m:
        return None, None
    Ix = (b * h ** 3 - (b - 2 * t_m) * (h - 2 * t_m) ** 3) / 12.0
    Iy = (h * b ** 3 - (h - 2 * t_m) * (b - 2 * t_m) ** 3) / 12.0
    Wx = Ix / (h / 2.0)
    Wy = Iy / (b / 2.0)
    return Wx * 1e9, Wy * 1e9


def wx_wy_rect(h_mm, b_mm):
    if h_mm is None or b_mm is None:
        return None, None
    h = h_mm / 1000.0
    b = b_mm / 1000.0
    Ix = b * h ** 3 / 12.0
    Iy = h * b ** 3 / 12.0
    Wx = Ix / (h / 2.0)
    Wy = Iy / (b / 2.0)
    return Wx * 1e9, Wy * 1e9


def wx_wy_ipe(row):
    return wx_wy_rect(row.get("h"), row.get("b"))


def wx_wy_hea(row):
    return wx_wy_rect(row.get("h"), row.get("b"))


def wx_wy_heb(row):
    return wx_wy_rect(row.get("h"), row.get("b"))


def wx_wy_upn(row):
    return wx_wy_rect(row.get("h"), row.get("b"))


def wx_wy_L(row):
    a = row.get("a")
    b = row.get("b")
    t = row.get("t")
    if not a or not b or not t:
        return None, None
    a_m = a / 1000.0
    b_m = b / 1000.0
    t_m = t / 1000.0
    Ix = (b_m * a_m ** 3 - (b_m - t_m) * (a_m - t_m) ** 3) / 12.0
    Iy = (a_m * b_m ** 3 - (a_m - t_m) * (b_m - t_m) ** 3) / 12.0
    Wx = Ix / (a_m / 2.0)
    Wy = Iy / (b_m / 2.0)
    return Wx * 1e9, Wy * 1e9


def wx_wy_round(row):
    d = row.get("d")
    if not d:
        return None, None
    d_m = d / 1000.0
    Ix = math.pi * d_m ** 4 / 64.0
    Wx = Ix / (d_m / 2.0)
    Wx_mm3 = Wx * 1e9
    return Wx_mm3, Wx_mm3


def wx_wy_square(row):
    a = row.get("a")
    if not a:
        return None, None
    a_m = a / 1000.0
    Ix = a_m ** 4 / 12.0
    Wx = Ix / (a_m / 2.0)
    Wx_mm3 = Wx * 1e9
    return Wx_mm3, Wx_mm3


def wx_wy_bulb(row):
    B = row.get("B")
    t = row.get("t")
    if not B or not t:
        return None, None
    return wx_wy_rect(t, B)


def wx_wy_flatbar(b_mm, h_mm):
    b = b_mm / 1000.0
    h = h_mm / 1000.0
    Ix = b * h ** 3 / 12.0
    Iy = h * b ** 3 / 12.0
    Wx = Ix / (h / 2.0)
    Wy = Iy / (b / 2.0)
    return Wx * 1e9, Wy * 1e9


# ---------------------------------------------------------
# TUM PROFILLERIN WX – WY LISTESI
# ---------------------------------------------------------
def build_all_profiles_wx_wy():
    lst = []

    for r in BORU_TABLO:
        Wx, Wy = wx_wy_boru(r)
        if Wx:
            lst.append({"Profil": "DN {} SCH {}".format(r["DN"], r["SCH"]), "Tip": "Boru",
                        "Wx_mm3": Wx, "Wy_mm3": Wy})

    for r in RHS_TABLO:
        Wx, Wy = wx_wy_rhs(r)
        if Wx:
            lst.append({"Profil": r["profil"], "Tip": "RHS/SHS", "Wx_mm3": Wx, "Wy_mm3": Wy})

    for r in L_EQUAL_TABLO:
        Wx, Wy = wx_wy_L(r)
        if Wx:
            lst.append({"Profil": r["profil"], "Tip": "L eşit", "Wx_mm3": Wx, "Wy_mm3": Wy})

    for r in L_UNEQUAL_TABLO:
        Wx, Wy = wx_wy_L(r)
        if Wx:
            lst.append({"Profil": r["profil"], "Tip": "L eşit olmayan", "Wx_mm3": Wx, "Wy_mm3": Wy})

    for r in IPE_TABLO:
        Wx, Wy = wx_wy_ipe(r)
        if Wx:
            lst.append({"Profil": r["profil"], "Tip": "IPE", "Wx_mm3": Wx, "Wy_mm3": Wy})

    for r in HEA_TABLO:
        Wx, Wy = wx_wy_hea(r)
        if Wx:
            lst.append({"Profil": r["profil"], "Tip": "HEA", "Wx_mm3": Wx, "Wy_mm3": Wy})

    for r in HEB_TABLO:
        Wx, Wy = wx_wy_heb(r)
        if Wx:
            lst.append({"Profil": r["profil"], "Tip": "HEB", "Wx_mm3": Wx, "Wy_mm3": Wy})

    for r in UPN_TABLO:
        Wx, Wy = wx_wy_upn(r)
        if Wx:
            lst.append({"Profil": r["profil"], "Tip": "UPN", "Wx_mm3": Wx, "Wy_mm3": Wy})

    for r in ROUND_TABLO:
        Wx, Wy = wx_wy_round(r)
        if Wx:
            lst.append({"Profil": r["profil"], "Tip": "Yuvarlak", "Wx_mm3": Wx, "Wy_mm3": Wy})

    for r in SQUARE_TABLO:
        Wx, Wy = wx_wy_square(r)
        if Wx:
            lst.append({"Profil": r["profil"], "Tip": "Kare", "Wx_mm3": Wx, "Wy_mm3": Wy})

    for r in BULBFLAT_TABLO:
        Wx, Wy = wx_wy_bulb(r)
        if Wx:
            lst.append({"Profil": r["profil"], "Tip": "Bulb Flat", "Wx_mm3": Wx, "Wy_mm3": Wy})

    return lst


# ---------------------------------------------------------
# %10 MUADIL PROFIL LISTESI (WX/WY)
# ---------------------------------------------------------
def muadil_liste_10yuzde(Wx_target, Wy_target):
    tum = build_all_profiles_wx_wy()
    if Wx_target is None or Wy_target is None:
        return []

    Wx_min = Wx_target * 0.9
    Wx_max = Wx_target * 1.1
    Wy_min = Wy_target * 0.9
    Wy_max = Wy_target * 1.1

    sonuc = []
    for r in tum:
        Wx = r["Wx_mm3"]
        Wy = r["Wy_mm3"]
        if not ((Wx_min <= Wx <= Wx_max) or (Wy_min <= Wy <= Wy_max)):
            continue
        dWx = abs(Wx_target - Wx)
        dWy = abs(Wy_target - Wy)
        skor = dWx + dWy
        r2 = dict(r)
        r2["ΔWx"] = dWx
        r2["ΔWy"] = dWy
        r2["Toplam Skor"] = skor
        sonuc.append(r2)

    sonuc.sort(key=lambda x: x["Toplam Skor"])
    return sonuc


# ---------------------------------------------------------
# TUM PROFILLER ICIN MUADIL LAMA HESABI (A SECENEGI)
# ---------------------------------------------------------
def lama_muadil_hesap(high_mm, thick_mm):
    """Profilin karakteristik yüksekliği (high_mm) ve kalınlığı (thick_mm)
    icin %10 toleransla muadil lama (flat bar) kalinliklarini hesaplar."""
    if high_mm is None or thick_mm is None:
        return []

    t_min = thick_mm * 0.9
    t_max = thick_mm * 1.1

    standart_t = [3, 4, 5, 6, 7, 8, 10, 12, 15, 20, 25]

    liste = []
    for t in standart_t:
        if t_min <= t <= t_max:
            liste.append({
                "Profil": "{} x {}".format(high_mm, t),
                "h (mm)": high_mm,
                "t (mm)": t,
                "Tip": "Lama (Flat Bar)"
            })
    return liste


# ---------------------------------------------------------
# ARAYUZ
# ---------------------------------------------------------
st.set_page_config(page_title="Profil Hesaplama", layout="wide")

st.title("🔧 Profil Hesaplama Sistemi — Muadil %10 + Lama Muadil (Flat Bar)")


col1, col2 = st.columns([3, 1])

with col1:
    MALZEMELER = {"Çelik": 7.85, "Paslanmaz Çelik": 7.90, "Alüminyum": 2.70}

    profil_tipi = st.selectbox("Profil Tipi:", [
        "Boru",
        "Kutu Profil (RHS/SHS)",
        "Köşebent (L Eşit)",
        "Köşebent (L Eşit Değil)",
        "U Profil (UPN)",
        "I Profil (IPE)",
        "H Profil (HEA)",
        "H Profil (HEB)",
        "Yuvarlak Dolu",
        "Kare Dolu",
        "Hollanda Profili (Bulb Flat)",
        "Lama (Flat Bar)"
    ])

    malzeme = st.selectbox("Malzeme:", list(MALZEMELER.keys()))
    rho = MALZEMELER[malzeme]

    metraj_mm = st.number_input("Metraj (mm):", min_value=0.0, value=6000.0, step=500.0)
    L_m = metraj_mm / 1000.0

    st.markdown("---")

    Wx_sec = None
    Wy_sec = None
    lama_list = []

    # ----------------------
    # BORU
    # ----------------------
    if profil_tipi == "Boru":
        st.subheader("Boru (DN + SCH)")

        dn_list = sorted({r["DN"] for r in BORU_TABLO})
        dn = st.selectbox("DN:", dn_list)

        sch_list = sorted({r["SCH"] for r in BORU_TABLO if r["DN"] == dn})
        sch = st.selectbox("SCH:", sch_list)

        sec = [r for r in BORU_TABLO if r["DN"] == dn and r["SCH"] == sch]
        if sec:
            s = sec[0]
            OD = s["OD"]
            t = s["t"]

            st.markdown("**Seçilen boru:** DN {} SCH {}".format(dn, sch))
            st.markdown("- OD: **{:.2f} mm**, t: **{:.2f} mm**".format(OD, t))

            if st.button("Hesapla"):
                OD_m = OD / 1000.0
                t_m = t / 1000.0
                ID_m = OD_m - 2 * t_m
                A = (math.pi / 4.0) * (OD_m ** 2 - ID_m ** 2)

                w = agirlik_hesap(A, L_m, rho)

                st.markdown("Kesit alanı: **{:.2f} mm²**".format(A * 1e6))
                st.success("Toplam ağırlık: **{:.2f} kg**".format(w))

                Wx_sec, Wy_sec = wx_wy_boru(s)
                lama_list = lama_muadil_hesap(OD, t)

    # ----------------------
    # RHS / SHS
    # ----------------------
    elif profil_tipi == "Kutu Profil (RHS/SHS)":
        st.subheader("Kutu Profil (RHS / SHS)")

        isimler = [p["profil"] for p in RHS_TABLO]
        isim = st.selectbox("Profil:", isimler)
        g = next(p for p in RHS_TABLO if p["profil"] == isim)

        A_mm = g["A"]
        B_mm = g["B"]
        t_mm = g["t"]

        st.markdown("**Seçilen profil:** {}".format(isim))
        st.markdown("- A: **{} mm**, B: **{} mm**, t: **{} mm**".format(A_mm, B_mm, t_mm))

        A_m = A_mm / 1000.0
        B_m = B_mm / 1000.0
        t_m = t_mm / 1000.0

        A_out = A_m * B_m
        A_in = (A_m - 2 * t_m) * (B_m - 2 * t_m)
        A_k = A_out - A_in

        if st.button("Hesapla"):
            w = agirlik_hesap(A_k, L_m, rho)
            st.markdown("Kesit alanı: **{:.2f} mm²**".format(A_k * 1e6))
            st.success("Toplam ağırlık: **{:.2f} kg**".format(w))

            Wx_sec, Wy_sec = wx_wy_rhs(g)
            lama_list = lama_muadil_hesap(A_mm, t_mm)

    # ----------------------
    # L EŞIT
    # ----------------------
    elif profil_tipi == "Köşebent (L Eşit)":
        st.subheader("Köşebent (L Eşit)")

        isimler = [p["profil"] for p in L_EQUAL_TABLO]
        isim = st.selectbox("Profil:", isimler)
        g = next(p for p in L_EQUAL_TABLO if p["profil"] == isim)

        a_mm = g["a"]
        b_mm = g["b"]
        t_mm = g["t"]

        st.markdown("**Seçilen profil:** {}".format(isim))
        st.markdown("- a: **{} mm**, b: **{} mm**, t: **{} mm**".format(a_mm, b_mm, t_mm))

        a_m = a_mm / 1000.0
        b_m = b_mm / 1000.0
        t_m = t_mm / 1000.0
        A_k = (a_m * t_m) + (b_m * t_m) - (t_m * t_m)

        if st.button("Hesapla"):
            w = agirlik_hesap(A_k, L_m, rho)
            st.markdown("Kesit alanı (yakl.): **{:.2f} mm²**".format(A_k * 1e6))
            st.success("Toplam ağırlık (yakl.): **{:.2f} kg**".format(w))

            Wx_sec, Wy_sec = wx_wy_L(g)
            lama_list = lama_muadil_hesap(a_mm, t_mm)

    # ----------------------
    # L ESIT OLMAYAN
    # ----------------------
    elif profil_tipi == "Köşebent (L Eşit Değil)":
        st.subheader("Köşebent (L Eşit Olmayan)")

        isimler = [p["profil"] for p in L_UNEQUAL_TABLO]
        isim = st.selectbox("Profil:", isimler)
        g = next(p for p in L_UNEQUAL_TABLO if p["profil"] == isim)

        a_mm = g["a"]
        b_mm = g["b"]
        t_mm = g["t"]

        st.markdown("**Seçilen profil:** {}".format(isim))
        st.markdown("- a: **{} mm**, b: **{} mm**, t: **{} mm**".format(a_mm, b_mm, t_mm))

        a_m = a_mm / 1000.0
        b_m = b_mm / 1000.0
        t_m = t_mm / 1000.0
        A_k = (a_m * t_m) + (b_m * t_m) - (t_m * t_m)

        if st.button("Hesapla"):
            w = agirlik_hesap(A_k, L_m, rho)
            st.markdown("Kesit alanı (yakl.): **{:.2f} mm²**".format(A_k * 1e6))
            st.success("Toplam ağırlık (yakl.): **{:.2f} kg**".format(w))

            Wx_sec, Wy_sec = wx_wy_L(g)
            lama_list = lama_muadil_hesap(a_mm, t_mm)

    # ----------------------
    # UPN
    # ----------------------
    elif profil_tipi == "U Profil (UPN)":
        st.subheader("U Profil (UPN)")

        isimler = [p["profil"] for p in UPN_TABLO]
        isim = st.selectbox("Profil:", isimler)
        g = next(p for p in UPN_TABLO if p["profil"] == isim)

        h_mm = g["h"]
        b_mm = g["b"]
        tw_mm = g["tw"]
        tf_mm = g["tf"]

        st.markdown("**Seçilen profil:** {}".format(isim))
        st.markdown("- h: **{} mm**, b: **{} mm**, tw: **{} mm**, tf: **{} mm**".format(
            h_mm, b_mm, tw_mm, tf_mm))

        h = h_mm / 1000.0
        b = b_mm / 1000.0
        tw = tw_mm / 1000.0
        tf = tf_mm / 1000.0

        A_fl = 2 * (b * tf)
        A_web = (h - 2 * tf) * tw
        A_k = A_fl + A_web

        if st.button("Hesapla"):
            w = agirlik_hesap(A_k, L_m, rho)
            st.markdown("Kesit alanı (yakl.): **{:.2f} mm²**".format(A_k * 1e6))
            st.success("Toplam ağırlık (yakl.): **{:.2f} kg**".format(w))

            Wx_sec, Wy_sec = wx_wy_upn(g)
            lama_list = lama_muadil_hesap(h_mm, tw_mm)

    # ----------------------
    # IPE
    # ----------------------
    elif profil_tipi == "I Profil (IPE)":
        st.subheader("I Profil (IPE)")

        isimler = [p["profil"] for p in IPE_TABLO]
        isim = st.selectbox("Profil:", isimler)
        g = next(p for p in IPE_TABLO if p["profil"] == isim)

        h_mm = g["h"]
        b_mm = g["b"]
        tw_mm = g["tw"]
        tf_mm = g["tf"]

        st.markdown("**Seçilen profil:** {}".format(isim))
        st.markdown("- h: **{} mm**, b: **{} mm**, tw: **{} mm**, tf: **{} mm**".format(
            h_mm, b_mm, tw_mm, tf_mm))

        h = h_mm / 1000.0
        b = b_mm / 1000.0
        tw = tw_mm / 1000.0
        tf = tf_mm / 1000.0

        A_fl = 2 * (b * tf)
        A_web = (h - 2 * tf) * tw
        A_k = A_fl + A_web

        if st.button("Hesapla"):
            w = agirlik_hesap(A_k, L_m, rho)
            st.markdown("Kesit alanı (yakl.): **{:.2f} mm²**".format(A_k * 1e6))
            st.success("Toplam ağırlık (yakl.): **{:.2f} kg**".format(w))

            Wx_sec, Wy_sec = wx_wy_ipe(g)
            lama_list = lama_muadil_hesap(h_mm, tw_mm)

    # ----------------------
    # HEA
    # ----------------------
    elif profil_tipi == "H Profil (HEA)":
        st.subheader("H Profil (HEA)")

        isimler = [p["profil"] for p in HEA_TABLO]
        isim = st.selectbox("Profil:", isimler)
        g = next(p for p in HEA_TABLO if p["profil"] == isim)

        h_mm = g["h"]
        b_mm = g["b"]
        tw_mm = g["tw"]
        tf_mm = g["tf"]

        st.markdown("**Seçilen profil:** {}".format(isim))
        st.markdown("- h: **{} mm**, b: **{} mm**, tw: **{} mm**, tf: **{} mm**".format(
            h_mm, b_mm, tw_mm, tf_mm))

        h = h_mm / 1000.0
        b = b_mm / 1000.0
        tw = tw_mm / 1000.0
        tf = tf_mm / 1000.0

        A_fl = 2 * (b * tf)
        A_web = (h - 2 * tf) * tw
        A_k = A_fl + A_web

        if st.button("Hesapla"):
            w = agirlik_hesap(A_k, L_m, rho)
            st.markdown("Kesit alanı (yakl.): **{:.2f} mm²**".format(A_k * 1e6))
            st.success("Toplam ağırlık (yakl.): **{:.2f} kg**".format(w))

            Wx_sec, Wy_sec = wx_wy_hea(g)
            lama_list = lama_muadil_hesap(h_mm, tw_mm)

    # ----------------------
    # HEB
    # ----------------------
    elif profil_tipi == "H Profil (HEB)":
        st.subheader("H Profil (HEB)")

        isimler = [p["profil"] for p in HEB_TABLO]
        isim = st.selectbox("Profil:", isimler)
        g = next(p for p in HEB_TABLO if p["profil"] == isim)

        h_mm = g["h"]
        b_mm = g["b"]
        tw_mm = g["tw"]
        tf_mm = g["tf"]

        st.markdown("**Seçilen profil:** {}".format(isim))
        st.markdown("- h: **{} mm**, b: **{} mm**, tw: **{} mm**, tf: **{} mm**".format(
            h_mm, b_mm, tw_mm, tf_mm))

        h = h_mm / 1000.0
        b = b_mm / 1000.0
        tw = tw_mm / 1000.0
        tf = tf_mm / 1000.0

        A_fl = 2 * (b * tf)
        A_web = (h - 2 * tf) * tw
        A_k = A_fl + A_web

        if st.button("Hesapla"):
            w = agirlik_hesap(A_k, L_m, rho)
            st.markdown("Kesit alanı (yakl.): **{:.2f} mm²**".format(A_k * 1e6))
            st.success("Toplam ağırlık (yakl.): **{:.2f} kg**".format(w))

            Wx_sec, Wy_sec = wx_wy_heb(g)
            lama_list = lama_muadil_hesap(h_mm, tw_mm)

    # ----------------------
    # YUVARLAK DOLU
    # ----------------------
    elif profil_tipi == "Yuvarlak Dolu":
        st.subheader("Yuvarlak Dolu")

        isimler = [p["profil"] for p in ROUND_TABLO]
        isim = st.selectbox("Çap:", isimler)
        g = next(p for p in ROUND_TABLO if p["profil"] == isim)

        d_mm = g["d"]
        st.markdown("**Seçilen profil:** {} (d = {} mm)".format(isim, d_mm))

        d_m = d_mm / 1000.0
        A = math.pi * (d_m / 2.0) ** 2

        if st.button("Hesapla"):
            w = agirlik_hesap(A, L_m, rho)
            st.markdown("Kesit alanı: **{:.2f} mm²**".format(A * 1e6))
            st.success("Toplam ağırlık: **{:.2f} kg**".format(w))

            Wx_sec, Wy_sec = wx_wy_round(g)

            # Eşdeğer lama kalınlığı: A / h ~ A / d
            A_mm2 = A * 1e6
            t_eq = A_mm2 / d_mm
            lama_list = lama_muadil_hesap(d_mm, t_eq)

    # ----------------------
    # KARE DOLU
    # ----------------------
    elif profil_tipi == "Kare Dolu":
        st.subheader("Kare Dolu")

        isimler = [p["profil"] for p in SQUARE_TABLO]
        isim = st.selectbox("Profil:", isimler)
        g = next(p for p in SQUARE_TABLO if p["profil"] == isim)

        a_mm = g["a"]
        st.markdown("**Seçilen profil:** {} (a = {} mm)".format(isim, a_mm))

        a_m = a_mm / 1000.0
        A = a_m * a_m

        if st.button("Hesapla"):
            w = agirlik_hesap(A, L_m, rho)
            st.markdown("Kesit alanı: **{:.2f} mm²**".format(A * 1e6))
            st.success("Toplam ağırlık: **{:.2f} kg**".format(w))

            Wx_sec, Wy_sec = wx_wy_square(g)

            A_mm2 = A * 1e6
            t_eq = A_mm2 / a_mm
            lama_list = lama_muadil_hesap(a_mm, t_eq)

    # ----------------------
    # BULB FLAT
    # ----------------------
    elif profil_tipi == "Hollanda Profili (Bulb Flat)":
        st.subheader("Hollanda Profili (Bulb Flat)")

        isimler = [p["profil"] for p in BULBFLAT_TABLO]
        isim = st.selectbox("Profil:", isimler)
        g = next(p for p in BULBFLAT_TABLO if p["profil"] == isim)

        B_mm = g["B"]
        t_mm = g["t"]

        st.markdown("**Seçilen profil:** {}".format(isim))
        st.markdown("- B: **{} mm**, t: **{} mm**".format(B_mm, t_mm))

        B_m = B_mm / 1000.0
        t_m = t_mm / 1000.0
        A_k = B_m * t_m * 1.2  # yaklasik

        if st.button("Hesapla"):
            w = agirlik_hesap(A_k, L_m, rho)
            st.markdown("Kesit alanı (yakl.): **{:.2f} mm²**".format(A_k * 1e6))
            st.success("Toplam ağırlık (yakl.): **{:.2f} kg**".format(w))

            Wx_sec, Wy_sec = wx_wy_bulb(g)
            lama_list = lama_muadil_hesap(B_mm, t_mm)

    # ----------------------
    # LAMA (FLAT BAR) MANUEL
    # ----------------------
    elif profil_tipi == "Lama (Flat Bar)":
        st.subheader("Lama (Flat Bar)")

        h_mm = st.number_input("Lama yüksekliği (h, mm):", min_value=1.0, value=80.0)
        t_mm = st.number_input("Lama kalınlığı (t, mm):", min_value=1.0, value=7.0)

        h = h_mm / 1000.0
        t_m = t_mm / 1000.0
        A_k = h * t_m  # m^2

        if st.button("Hesapla"):
            w = agirlik_hesap(A_k, L_m, rho)
            st.markdown("Kesit alanı: **{:.2f} mm²**".format(A_k * 1e6))
            st.success("Toplam ağırlık: **{:.2f} kg**".format(w))

            Wx_sec, Wy_sec = wx_wy_flatbar(t_mm, h_mm)
            # Lama kendi muadili zaten lama oldugu icin ek muadil liste gerekmiyor


    # ----------------------
    # WX / WY TABANLI MUADIL PROFILLER
    # ----------------------
    if Wx_sec is not None and Wy_sec is not None:
        st.markdown("---")
        st.subheader("📊 %10 Toleranslı Muadil Kesit Modülü Profilleri")

        st.markdown(
            "Seçilen profil için yakl. kesit modülleri:<br>"
            "- Wx ≈ <b>{:,.0f}</b> mm³<br>"
            "- Wy ≈ <b>{:,.0f}</b> mm³".format(Wx_sec, Wy_sec),
            unsafe_allow_html=True
        )

        muadiller = muadil_liste_10yuzde(Wx_sec, Wy_sec)
        if muadiller:
            st.dataframe(muadiller, use_container_width=True)
        else:
            st.info("%10 tolerans içinde muadil profil bulunamadı. Tablolara daha fazla profil ekleyebilirsin.")

    # ----------------------
    # LAMA MUADIL LISTESI (TUM PROFILLER ICIN)
    # ----------------------
    if lama_list:
        st.markdown("---")
        st.subheader("🟫 Bu profile muadil Lama (Flat Bar) boyutları")
        st.dataframe(lama_list, use_container_width=True)


# ---------------------------------------------------------
# SAG SUTUN — TEKNIK CIZIM GORSELI
# ---------------------------------------------------------
with col2:
    img_path = None
    try:
        img_path = get_image_for_type(profil_tipi)
    except Exception:
        img_path = None

    if img_path:
        st.image(img_path, caption="Teknik Çizim Seti", use_column_width=True)
        st.markdown(
            "<small>Seçtiğiniz profil için referans teknik ölçü şemaları (genel set).</small>",
            unsafe_allow_html=True
        )
