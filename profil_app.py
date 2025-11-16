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
# TEKNİK ÇİZİM SEÇİMİ
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
# AĞIRLIK HESABI
# ---------------------------------------------------------
def agirlik_hesap(A_m2, L_m, rho_g_cm3):
    hacim_m3 = A_m2 * L_m
    return hacim_m3 * rho_g_cm3 * 1000.0


# ---------------------------------------------------------
# WX – WY Yaklaşık Hesaplama Fonksiyonları
# ---------------------------------------------------------
def wx_wy_boru(row):
    OD = row.get("OD"); t = row.get("t")
    if not OD or not t: return None, None

    OD_m = OD/1000.0; t_m = t/1000.0
    ID_m = OD_m - 2*t_m
    if ID_m <= 0: return None, None

    Ix_m4 = (math.pi/64.0) * (OD_m**4 - ID_m**4)
    Wx_m3 = Ix_m4 / (OD_m/2.0)
    Wx_mm3 = Wx_m3 * 1e9
    return Wx_mm3, Wx_mm3


def wx_wy_rhs(row):
    A = row.get("A"); B = row.get("B"); t = row.get("t")
    if not A or not B or not t: return None, None

    h = A/1000.0; b = B/1000.0; t_m = t/1000.0

    if h <= 2*t_m or b <= 2*t_m:
        return None, None

    Ix = (b*h**3 - (b-2*t_m)*(h-2*t_m)**3) / 12.0
    Iy = (h*b**3 - (h-2*t_m)*(b-2*t_m)**3) / 12.0

    Wx = Ix / (h/2.0)
    Wy = Iy / (b/2.0)

    return Wx*1e9, Wy*1e9


def wx_wy_rect(h_mm, b_mm):
    h = h_mm/1000.0; b = b_mm/1000.0
    Ix = b*h**3 / 12.0
    Iy = h*b**3 / 12.0
    Wx = Ix / (h/2.0)
    Wy = Iy / (b/2.0)
    return Wx*1e9, Wy*1e9


def wx_wy_ipe(row):
    return wx_wy_rect(row.get("h"), row.get("b"))


def wx_wy_hea(row):
    return wx_wy_rect(row.get("h"), row.get("b"))


def wx_wy_heb(row):
    return wx_wy_rect(row.get("h"), row.get("b"))


def wx_wy_upn(row):
    return wx_wy_rect(row.get("h"), row.get("b"))


def wx_wy_L(row):
    a = row.get("a"); b = row.get("b"); t = row.get("t")
    if not a or not b or not t: return None, None

    a_m = a/1000.0; b_m = b/1000.0; t_m = t/1000.0

    Ix = (b_m*a_m**3 - (b_m-t_m)*(a_m-t_m)**3) / 12.0
    Iy = (a_m*b_m**3 - (a_m-t_m)*(b_m-t_m)**3) / 12.0

    Wx = Ix / (a_m/2.0)
    Wy = Iy / (b_m/2.0)

    return Wx*1e9, Wy*1e9


def wx_wy_round(row):
    d = row.get("d")
    if not d: return None, None

    d_m = d/1000.0
    Ix = math.pi * d_m**4 / 64.0
    Wx = Ix / (d_m/2.0)
    return Wx*1e9, Wx*1e9


def wx_wy_square(row):
    a = row.get("a")
    if not a: return None, None

    a_m = a/1000.0
    Ix = a_m**4 / 12.0
    Wx = Ix / (a_m/2.0)
    return Wx*1e9, Wx*1e9


def wx_wy_bulb(row):
    return wx_wy_rect(row.get("t"), row.get("B"))


# ---------------------------------------------------------
# TÜM PROFİLLERİN WX – WY LİSTESİ
# ---------------------------------------------------------
def build_all_profiles_wx_wy():
    lst = []

    for r in BORU_TABLO:
        Wx, Wy = wx_wy_boru(r)
        if Wx: lst.append({"Profil": f"DN {r['DN']} SCH {r['SCH']}", "Tip": "Boru", "Wx_mm3": Wx, "Wy_mm3": Wy})

    for r in RHS_TABLO:
        Wx, Wy = wx_wy_rhs(r)
        if Wx: lst.append({"Profil": r["profil"], "Tip": "RHS/SHS", "Wx_mm3": Wx, "Wy_mm3": Wy})

    for r in L_EQUAL_TABLO:
        Wx, Wy = wx_wy_L(r)
        if Wx: lst.append({"Profil": r["profil"], "Tip": "L eşit", "Wx_mm3": Wx, "Wy_mm3": Wy})

    for r in L_UNEQUAL_TABLO:
        Wx, Wy = wx_wy_L(r)
        if Wx: lst.append({"Profil": r["profil"], "Tip": "L eşit olmayan", "Wx_mm3": Wx, "Wy_mm3": Wy})

    for r in IPE_TABLO:
        Wx, Wy = wx_wy_ipe(r)
        if Wx: lst.append({"Profil": r["profil"], "Tip": "IPE", "Wx_mm3": Wx, "Wy_mm3": Wy})

    for r in HEA_TABLO:
        Wx, Wy = wx_wy_hea(r)
        if Wx: lst.append({"Profil": r["profil"], "Tip": "HEA", "Wx_mm3": Wx, "Wy_mm3": Wy})

    for r in HEB_TABLO:
        Wx, Wy = wx_wy_heb(r)
        if Wx: lst.append({"Profil": r["profil"], "Tip": "HEB", "Wx_mm3": Wx, "Wy_mm3": Wy})

    for r in UPN_TABLO:
        Wx, Wy = wx_wy_upn(r)
        if Wx: lst.append({"Profil": r["profil"], "Tip": "UPN", "Wx_mm3": Wx, "Wy_mm3": Wy})

    for r in ROUND_TABLO:
        Wx, Wy = wx_wy_round(r)
        if Wx: lst.append({"Profil": r["profil"], "Tip": "Yuvarlak", "Wx_mm3": Wx, "Wy_mm3": Wy})

    for r in SQUARE_TABLO:
        Wx, Wy = wx_wy_square(r)
        if Wx: lst.append({"Profil": r["profil"], "Tip": "Kare", "Wx_mm3": Wx, "Wy_mm3": Wy})

    for r in BULBFLAT_TABLO:
        Wx, Wy = wx_wy_bulb(r)
        if Wx: lst.append({"Profil": r["profil"], "Tip": "Bulb Flat", "Wx_mm3": Wx, "Wy_mm3": Wy})

    return lst


# ---------------------------------------------------------
# %10 MUADİL PROFİL FİLTRESİ
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
# ARAYÜZ
# ---------------------------------------------------------
st.set_page_config(page_title="Profil Hesaplama", layout="wide")

st.title("🔧 Profil Hesaplama Sistemi — Muadil %10 Filtreli (PNG Görselli)")


# =========================================================
#   SAĞDA TEKNİK ÇİZİM — SOLDa PROGRAM
# =========================================================
col1, col2 = st.columns([3, 1])


# ---------------------------------------------------------
# SOL SÜTUN — HESAPLAMA ALANI
# ---------------------------------------------------------
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
        "Hollanda Profili (Bulb Flat)"
    ])

    malzeme = st.selectbox("Malzeme:", list(MALZEMELER.keys()))
    rho = MALZEMELER[malzeme]

    metraj_mm = st.number_input("Metraj (mm):", min_value=0.0, value=6000.0, step=500.0)
    L_m = metraj_mm / 1000.0

    st.markdown("---")

    Wx_sec = None
    Wy_sec = None

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
            OD = s["OD"]; t = s["t"]

            st.markdown(f"**Seçilen boru:** DN {dn} SCH {sch}")
            st.markdown(f"- OD: **{OD:.2f} mm**, t: **{t:.2f} mm**")

            if st.button("Hesapla"):
                OD_m = OD/1000.0; t_m = t/1000.0
                ID_m = OD_m - 2*t_m
                A = (math.pi/4.0) * (OD_m**2 - ID_m**2)

                w = agirlik_hesap(A, L_m, rho)

                st.markdown(f"Kesit alanı: **{A*1e6:.2f} mm²**")
                st.success(f"Toplam ağırlık: **{w:.2f} kg**")

                Wx_sec, Wy_sec = wx_wy_boru(s)


    # ----------------------
    # RHS / SHS
    # ----------------------
    elif profil_tipi == "Kutu Profil (RHS/SHS)":

        st.subheader("Kutu Profil (RHS / SHS)")

        isimler = [p["profil"] for p in RHS_TABLO]
        isim = st.selectbox("Profil:", isimler)
        g = next(p for p in RHS_TABLO if p["profil"] == isim)

        A_mm, B_mm, t_mm = g["A"], g["B"], g["t"]

        st.markdown(f"**Seçilen profil:** {isim}")
        st.markdown(f"- A: **{A_mm} mm**, B: **{B_mm} mm**, t: **{t_mm} mm**")

        A_m = A_mm/1000.0; B_m = B_mm/1000.0; t_m = t_mm/1000.0

        A_out = A_m * B_m
        A_in = (A_m - 2*t_m) * (B_m - 2*t_m)
        A_k = A_out - A_in

        if st.button("Hesapla"):
            w = agirlik_hesap(A_k, L_m, rho)
            st.markdown(f"Kesit alanı: **{A_k*1e6:.2f} mm²**")
            st.success(f"Toplam ağırlık: **{w:.2f} kg**")

            Wx_sec, Wy_sec = wx_wy_rhs(g)


    # ----------------------
    # L EŞİT
    # ----------------------
    elif profil_tipi == "Köşebent (L Eşit)":

        st.subheader("Köşebent (L Eşit)")

        isimler = [p["profil"] for p in L_EQUAL_TABLO]
        isim = st.selectbox("Profil:", isimler)
        g = next(p for p in L_EQUAL_TABLO if p["profil"] == isim)

        a_mm, b_mm, t_mm = g["a"], g["b"], g["t"]

        st.markdown(f"**Seçilen profil:** {isim}")
        st.markdown(f"- a: **{a_mm} mm**, b: **{b_mm} mm**, t: **{t_mm} mm**")

        a_m = a_mm/1000.0; b_m = b_mm/1000.0; t_m = t_mm/1000.0
        A_k = (a_m*t_m) + (b_m*t_m) - (t_m*t_m)

        if st.button("Hesapla"):
            w = agirlik_hesap(A_k, L_m, rho)
            st.markdown(f"Kesit alanı (yakl.): **{A_k*1e6:.2f} mm²**")
            st.success(f"Toplam ağırlık (yakl.): **{w:.2f} kg**")

            Wx_sec, Wy_sec = wx_wy_L(g)


    # ----------------------
    # L EŞİT OLMAYAN
    # ----------------------
    elif profil_tipi == "Köşebent (L Eşit Değil)":

        st.subheader("Köşebent (L Eşit Olmayan)")

        isimler = [p["profil"] for p in L_UNEQUAL_TABLO]
        isim = st.selectbox("Profil:", isimler)
        g = next(p for p in L_UNEQUAL_TABLO if p["profil"] == isim)

        a_mm, b_mm, t_mm = g["a"], g["b"], g["t"]

        st.markdown(f"**Seçilen profil:** {isim}")
        st.markdown(f"- a: **{a_mm} mm**, b: **{b_mm} mm**, t: **{t_mm} mm**")

        a_m = a_mm/1000.0; b_m = b_mm/1000.0; t_m = t_mm/1000.0
        A_k = (a_m*t_m) + (b_m*t_m) - (t_m*t_m)

        if st.button("Hesapla"):
            w = agirlik_hesap(A_k, L_m, rho)
            st.markdown(f"Kesit alanı (yakl.): **{A_k*1e6:.2f} mm²**")
            st.success(f"Toplam ağırlık (yakl.): **{w:.2f} kg**")

            Wx_sec, Wy_sec = wx_wy_L(g)


    # ----------------------
    # UPN
    # ----------------------
    elif profil_tipi == "U Profil (UPN)":

        st.subheader("U Profil (UPN)")

        isimler = [p["profil"] for p in UPN_TABLO]
        isim = st.selectbox("Profil:", isimler)
        g = next(p for p in UPN_TABLO if p["profil"] == isim)

        h_mm, b_mm, tw_mm, tf_mm = g["h"], g["b"], g["tw"], g["tf"]

        st.markdown(f"**Seçilen profil:** {isim}")
        st.markdown(f"- h: **{h_mm} mm**, b: **{b_mm} mm**, tw: **{tw_mm} mm**, tf: **{tf_mm} mm**")

        h = h_mm/1000.0; b = b_mm/1000.0; tw = tw_mm/1000.0; tf = tf_mm/1000.0

        A_fl = 2 * (b * tf)
        A_web = (h - 2*tf) * tw
        A_k = A_fl + A_web

        if st.button("Hesapla"):
            w = agirlik_hesap(A_k, L_m, rho)
            st.markdown(f"Kesit alanı (yakl.): **{A_k*1e6:.2f} mm²**")
            st.success(f"Toplam ağırlık (yakl.): **{w:.2f} kg**")

            Wx_sec, Wy_sec = wx_wy_upn(g)


    # ----------------------
    # IPE
    # ----------------------
    elif profil_tipi == "I Profil (IPE)":

        st.subheader("I Profil (IPE)")

        isimler = [p["profil"] for p in IPE_TABLO]
        isim = st.selectbox("Profil:", isimler)
        g = next(p for p in IPE_TABLO if p["profil"] == isim)

        h_mm, b_mm, tw_mm, tf_mm = g["h"], g["b"], g["tw"], g["tf"]

        st.markdown(f"**Seçilen profil:** {isim}")
        st.markdown(f"- h: **{h_mm} mm**, b: **{b_mm} mm**, tw: **{tw_mm} mm**, tf: **{tf_mm} mm**")

        h = h_mm/1000.0; b = b_mm/1000.0; tw = tw_mm/1000.0; tf = tf_mm/1000.0

        A_fl = 2 * (b * tf)
        A_web = (h - 2*tf) * tw
        A_k = A_fl + A_web

        if st.button("Hesapla"):
            w = agirlik_hesap(A_k, L_m, rho)
            st.markdown(f"Kesit alanı (yakl.): **{A_k*1e6:.2f} mm²**")
            st.success(f"Toplam ağırlık (yakl.): **{w:.2f} kg**")

            Wx_sec, Wy_sec = wx_wy_ipe(g)


    # ----------------------
    # HEA
    # ----------------------
    elif profil_tipi == "H Profil (HEA)":

        st.subheader("H Profil (HEA)")

        isimler = [p["profil"] for p in HEA_TABLO]
        isim = st.selectbox("Profil:", isimler)
        g = next(p for p in HEA_TABLO if p["profil"] == isim)

        h_mm, b_mm, tw_mm, tf_mm = g["h"], g["b"], g["tw"], g["tf"]

        st.markdown(f"**Seçilen profil:** {isim}")
        st.markdown(f"- h: **{h_mm} mm**, b: **{b_mm} mm**, tw: **{tw_mm} mm**, tf: **{tf_mm} mm**")

        h = h_mm/1000.0; b = b_mm/1000.0; tw = tw_mm/1000.0; tf = tf_mm/1000.0

        A_fl = 2 * (b * tf)
        A_web = (h - 2*tf) * tw
        A_k = A_fl + A_web

        if st.button("Hesapla"):
            w = agirlik_hesap(A_k, L_m, rho)
            st.markdown(f"Kesit alanı (yakl.): **{A_k*1e6:.2f} mm²**")
            st.success(f"Toplam ağırlık (yakl.): **{w:.2f} kg**")

            Wx_sec, Wy_sec = wx_wy_hea(g)


    # ----------------------
    # HEB
    # ----------------------
    elif profil_tipi == "H Profil (HEB)":

        st.subheader("H Profil (HEB)")

        isimler = [p["profil"] for p in HEB_TABLO]
        isim = st.selectbox("Profil:", isimler)
        g = next(p for p in HEB_TABLO if p["profil"] == isim)

        h_mm, b_mm, tw_mm, tf_mm = g["h"], g["b"], g["tw"], g["tf"]

        st.markdown(f"**Seçilen profil:** {isim}")
        st.markdown(f"- h: **{h_mm} mm**, b: **{b_mm} mm**, tw: **{tw_mm} mm**, tf: **{tf_mm} mm**")

        h = h_mm/1000.0; b = b_mm/1000.0; tw = tw_mm/1000.0; tf = tf_mm/1000.0

        A_fl = 2 * (b * tf)
        A_web = (h - 2*tf) * tw
        A_k = A_fl + A_web

        if st.button("Hesapla"):
            w = agirlik_hesap(A_k, L_m, rho)
            st.markdown(f"Kesit alanı (yakl.): **{A_k*1e6:.2f} mm²**")
            st.success(f"Toplam ağırlık (yakl.): **{w:.2f} kg**")

            Wx_sec, Wy_sec = wx_wy_heb(g)


    # ----------------------
    # YUVARLAK DOLU
    # ----------------------
    elif profil_tipi == "Yuvarlak Dolu":

        st.subheader("Yuvarlak Dolu")

        isimler = [p["profil"] for p in ROUND_TABLO]
        isim = st.selectbox("Çap:", isimler)
        g = next(p for p in ROUND_TABLO if p["profil"] == isim)

        d_mm = g["d"]
        st.markdown(f"**Seçilen profil:** {isim} (d = {d_mm} mm)")

        d_m = d_mm/1000.0
        A = math.pi * (d_m/2.0)**2

        if st.button("Hesapla"):
            w = agirlik_hesap(A, L_m, rho)
            st.markdown(f"Kesit alanı: **{A*1e6:.2f} mm²**")
            st.success(f"Toplam ağırlık: **{w:.2f} kg**")

            Wx_sec, Wy_sec = wx_wy_round(g)


    # ----------------------
    # KARE DOLU
    # ----------------------
    elif profil_tipi == "Kare Dolu":

        st.subheader("Kare Dolu")

        isimler = [p["profil"] for p in SQUARE_TABLO]
        isim = st.selectbox("Profil:", isimler)
        g = next(p for p in SQUARE_TABLO if p["profil"] == isim)

        a_mm = g["a"]
        st.markdown(f"**Seçilen profil:** {isim} (a = {a_mm} mm)")

        a_m = a_mm/1000.0
        A = a_m * a_m

        if st.button("Hesapla"):
            w = agirlik_hesap(A, L_m, rho)
            st.markdown(f"Kesit alanı: **{A*1e6:.2f} mm²**")
            st.success(f"Toplam ağırlık: **{w:.2f} kg**")

            Wx_sec, Wy_sec = wx_wy_square(g)


    # ----------------------
    # BULB FLAT
    # ----------------------
    elif profil_tipi == "Hollanda Profili (Bulb Flat)":

        st.subheader("Hollanda Profili (Bulb Flat)")

        isimler = [p["profil"] for p in BULBFLAT_TABLO]
        isim = st.selectbox("Profil:", isimler)
        g = next(p for p in BULBFLAT_TABLO if p["profil"] == isim)

        B_mm, t_mm = g["B"], g["t"]

        st.markdown(f"**Seçilen profil:** {isim}")
        st.markdown(f"- B: **{B_mm} mm**, t: **{t_mm} mm**")

        B_m = B_mm/1000.0; t_m = t_mm/1000.0
        A_k = B_m * t_m * 1.2

        if st.button("Hesapla"):
            w = agirlik_hesap(A_k, L_m, rho)
            st.markdown(f"Kesit alanı (yakl.): **{A_k*1e6:.2f} mm²**")
            st.success(f"Toplam ağırlık (yakl.): **{w:.2f} kg**")

            Wx_sec, Wy_sec = wx_wy_bulb(g)


    # -----------------------------------------------------
    # MUADİL PROFİLLER
    # -----------------------------------------------------
    if Wx_sec is not None and Wy_sec is not None:
        st.markdown("---")
        st.subheader("📊 %10 Toleranslı Muadil Profiller")

        st.markdown(
            f"Seçilen profil için kesit modülleri:<br>"
            f"- Wx ≈ <b>{Wx_sec:,.0f}</b> mm³<br>"
            f"- Wy ≈ <b>{Wy_sec:,.0f}</b> mm³",
            unsafe_allow_html=True
        )

        muadiller = muadil_liste_10yuzde(Wx_sec, Wy_sec)

        if muadiller:
            st.dataframe(muadiller, use_container_width=True)
        else:
            st.info("Bu değerler için %10 toleransta muadil profil bulunamadı.")


# ---------------------------------------------------------
# SAĞ SÜTUN — TEKNİK ÇİZİM GÖRSELİ
# ---------------------------------------------------------
with col2:
    img_path = get_image_for_type(profil_tipi)
    if img_path:
        st.image(img_path, caption="Teknik Çizim Seti", width=550)
        st.markdown(
            "<small>Seçtiğiniz profil için referans teknik ölçü seti.</small>",
            unsafe_allow_html=True
        )
