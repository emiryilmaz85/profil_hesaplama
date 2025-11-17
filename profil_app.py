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

# %2 tolerans sabiti
TOLERANS_ORAN = 0.02
TOLERANS_YUZDE = int(TOLERANS_ORAN * 100)
TOLERANS_METIN = f"±{TOLERANS_YUZDE}%"

# ----------------------------
# Teknik Çizim Görseli
# ----------------------------
def get_image_for_type(profil_tipi):
    if profil_tipi in ["I Profil (IPE)", "H Profil (HEA)", "H Profil (HEB)", "U Profil (UPN)"]:
        fname = "profil_set2.png"
    else:
        fname = "profil_set1.png"
    path = os.path.join(IMG_DIR, fname)
    return path if os.path.exists(path) else None

# ----------------------------
# Ağırlık Hesabı
# ----------------------------
def agirlik_hesap(A_m2, L_m, rho_g_cm3):
    hacim_m3 = A_m2 * L_m
    return hacim_m3 * rho_g_cm3 * 1000.0

# ----------------------------
# WX – WY Fonksiyonları
# ----------------------------

def wx_wy_boru(r):
    try:
        D = r["D_mm"]
        t = r["t_mm"]
    except:
        return None, None
    if t <= 0: 
        return None, None

    D_o = D
    D_i = D - 2*t
    if D_i <= 0:
        return None, None

    I = (math.pi / 64.0) * (D_o**4 - D_i**4)
    Wx = Wy = I / (D_o / 2.0)
    return Wx, Wy

def wx_wy_rhs(r):
    b = r["b_mm"]
    h = r["h_mm"]
    t = r["t_mm"]
    if min(b, h, t) <= 0:
        return None, None

    I_x = (b * h**3 / 12.0) - ((b - 2*t) * (h - 2*t)**3 / 12.0)
    I_y = (h * b**3 / 12.0) - ((h - 2*t) * (b - 2*t)**3 / 12.0)
    Wx = I_x / (h/2.0)
    Wy = I_y / (b/2.0)
    return Wx, Wy

def wx_wy_bulb(r):
    try:
        Wx = r["Wx_mm3"]
        Wy = r["Wy_mm3"]
        return Wx, Wy
    except:
        return None, None

def wx_wy_ipe(r):
    try:
        return r["Wx_mm3"], r["Wy_mm3"]
    except:
        return None, None

def wx_wy_hea(r):
    try:
        return r["Wx_mm3"], r["Wy_mm3"]
    except:
        return None, None

def wx_wy_heb(r):
    try:
        return r["Wx_mm3"], r["Wy_mm3"]
    except:
        return None, None

def wx_wy_upn(r):
    try:
        return r["Wx_mm3"], r["Wy_mm3"]
    except:
        return None, None

def wx_wy_round(r):
    try:
        return r["Wx_mm3"], r["Wy_mm3"]
    except:
        return None, None

def wx_wy_square(r):
    try:
        return r["Wx_mm3"], r["Wy_mm3"]
    except:
        return None, None

def wx_wy_flatbar(t, h):
    if t <= 0 or h <= 0:
        return None, None
    I_x = t * h**3 / 12.0
    I_y = h * t**3 / 12.0
    Wx = I_x / (h/2.0)
    Wy = I_y / (t/2.0)
    return Wx, Wy

# ---------------------------------------------------------
# TÜM PROFİLLERDEN WX/WY LİSTESİ
# ---------------------------------------------------------
def build_all_profiles_wx_wy():
    lst = []

    for r in BORU_TABLO:
        Wx, Wy = wx_wy_boru(r)
        if Wx:
            lst.append({"Profil": r["profil"], "Tip": "Boru", "Wx_mm3": Wx, "Wy_mm3": Wy})

    for r in RHS_TABLO:
        Wx, Wy = wx_wy_rhs(r)
        if Wx:
            lst.append({"Profil": r["profil"], "Tip": "Kutu (RHS)", "Wx_mm3": Wx, "Wy_mm3": Wy})

    for r in L_EQUAL_TABLO:
        try:
            Wx = r["Wx_mm3"]
            Wy = r["Wy_mm3"]
            lst.append({"Profil": r["profil"], "Tip": "L Eşit", "Wx_mm3": Wx, "Wy_mm3": Wy})
        except:
            pass

    for r in L_UNEQUAL_TABLO:
        try:
            Wx = r["Wx_mm3"]
            Wy = r["Wy_mm3"]
            lst.append({"Profil": r["profil"], "Tip": "L Eşitsiz", "Wx_mm3": Wx, "Wy_mm3": Wy})
        except:
            pass

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
# %2 MUADİL PROFİL LİSTESİ (WX/WY)
# ---------------------------------------------------------
def muadil_liste_2yuzde(Wx_target, Wy_target):
    tum = build_all_profiles_wx_wy()
    if Wx_target is None or Wy_target is None:
        return []

    Wx_min = Wx_target * (1 - TOLERANS_ORAN)
    Wx_max = Wx_target * (1 + TOLERANS_ORAN)
    Wy_min = Wy_target * (1 - TOLERANS_ORAN)
    Wy_max = Wy_target * (1 + TOLERANS_ORAN)

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
# LAMA MUADİL HESABI
# ---------------------------------------------------------
def lama_muadil_wx_wy(Wx_target, Wy_target, h_mm):
    """
    Verilen Wx, Wy hedeflerine göre sabit h_mm yükseklikte
    %2 toleransla muadil olabilecek lamaları döndürür.
    """
    if Wx_target is None or Wy_target is None or h_mm is None:
        return []

    liste = []
    for t in range(2, 101):  # 2..100 mm
        Wx_l, Wy_l = wx_wy_flatbar(t, h_mm)
        if Wx_l is None or Wy_l is None:
            continue

        if Wx_target <= 0 or Wy_target <= 0:
            continue

        cond_wx = abs(Wx_l - Wx_target) <= TOLERANS_ORAN * Wx_target
        cond_wy = abs(Wy_l - Wy_target) <= TOLERANS_ORAN * Wy_target

        if cond_wx or cond_wy:
            dWx = abs(Wx_l - Wx_target)
            dWy = abs(Wy_l - Wy_target)
            skor = dWx + dWy

            liste.append({
                "Lama": f"{h_mm} x {t}",
                "h (mm)": h_mm,
                "t (mm)": t,
                "Wx_lama": Wx_l,
                "Wy_lama": Wy_l,
                "ΔWx": dWx,
                "ΔWy": dWy,
                "Toplam Skor": skor
            })

    liste.sort(key=lambda x: x["Toplam Skor"])
    return liste


# ---------------------------------------------------------
# T PROFİL MUADİL HESABI
# ---------------------------------------------------------
def t_profil_wx_wy(Wx_target, Wy_target, H_mm, t_min_mm, t_max_mm):
    """
    Verilen Wx/Wy hedefleri için H yüksekliğinde flanş + gövde kombinasyonu
    içeren T profilleri tarar (%2 tolerans).
    """
    if Wx_target is None or Wy_target is None or H_mm is None:
        return []
    if t_min_mm is None or t_max_mm is None or t_min_mm <= 0 or t_max_mm < t_min_mm:
        return []

    H = float(H_mm)
    if H <= 0:
        return []

    base_t_list = [4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 25, 30]
    t_list = [t for t in base_t_list if t_min_mm <= t <= t_max_mm]

    if not t_list:
        return []

    b_min = max(20.0, 0.5 * H)
    b_max = 2.0 * H
    b_start = int(round(b_min / 10.0) * 10)
    b_end = int(round(b_max / 10.0) * 10)

    sonuc = []

    for b_f in range(b_start, b_end + 1, 10):
        for t_f in t_list:
            for t_w in t_list:
                h_w = H - t_f
                if h_w <= 0:
                    continue

                A_f = b_f * t_f
                A_w = t_w * h_w
                A_total = A_f + A_w

                y_f = H - (t_f / 2.0)
                y_w = h_w / 2.0
                y_bar = (A_f * y_f + A_w * y_w) / A_total

                Ix_f = b_f * t_f**3 / 12.0
                Ix_w = t_w * h_w**3 / 12.0
                Ix = Ix_f + A_f*(y_f - y_bar)**2 + Ix_w + A_w*(y_w - y_bar)**2

                Iy_f = t_f * b_f**3 / 12.0
                Iy_w = h_w * t_w**3 / 12.0
                Iy = Iy_f + Iy_w

                c_top = H - y_bar
                c_bot = y_bar
                c_x = max(c_top, c_bot)
                c_y = b_f / 2.0

                Ix_m4 = Ix * 1e-12
                Iy_m4 = Iy * 1e-12

                Wx_mm3 = (Ix_m4 / (c_x / 1000.0)) * 1e9
                Wy_mm3 = (Iy_m4 / (c_y / 1000.0)) * 1e9

                cond_wx = abs(Wx_mm3 - Wx_target) <= TOLERANS_ORAN * Wx_target
                cond_wy = abs(Wy_mm3 - Wy_target) <= TOLERANS_ORAN * Wy_target

                if not (cond_wx or cond_wy):
                    continue

                dWx = abs(Wx_mm3 - Wx_target)
                dWy = abs(Wy_mm3 - Wy_target)
                skor = dWx + dWy

                sonuc.append({
                    "T Profil": f"T (flanş {b_f}x{t_f}, gövde {h_w}x{t_w})",
                    "H (mm)": H,
                    "b_f (mm)": b_f,
                    "t_f (mm)": t_f,
                    "h_w (mm)": h_w,
                    "t_w (mm)": t_w,
                    "Wx_T": Wx_mm3,
                    "Wy_T": Wy_mm3,
                    "ΔWx": dWx,
                    "ΔWy": dWy,
                    "Toplam Skor": skor
                })

    sonuc.sort(key=lambda x: x["Toplam Skor"])
    return sonuc

# ---------------------------------------------------------
# STREAMLIT ARAYÜZÜ
# ---------------------------------------------------------

st.set_page_config(page_title="Profil Hesaplama", layout="wide")

st.title("📐 Profil Hesaplama ve Muadil Kesit Analizi")
st.markdown(
    f"""
Bu araç ile:
- Verdiğin **lama (flat bar)** boyutlarından ağırlık hesaplanır
- Kesit modülleri (**Wx, Wy**) bulunur
- Kütüphanedeki tüm profiller içinden **{TOLERANS_METIN} toleranslı muadil profiller** listelenir
- Aynı yüksekliğe sahip **lama muadilleri** ve **T profil muadilleri** hesaplanır
"""
)

st.markdown("---")

col1, col2 = st.columns([2, 1])

# Başlangıç değerleri
Wx_sec = None
Wy_sec = None
lama_list = []
t_list = []

# ---------------------------------------------------------
# SOL SÜTUN — LAMA GİRDİLERİ VE HESAPLAR
# ---------------------------------------------------------
with col1:
    st.subheader("🟫 Referans Lama (Flat Bar) Tanımı")

    h_mm = st.number_input("Lama yüksekliği h (mm)", min_value=1, max_value=3000, value=80, step=1)
    t_mm = st.number_input("Lama kalınlığı t (mm)", min_value=1, max_value=300, value=7, step=1)
    L_m = st.number_input("Parça boyu L (m)", min_value=0.1, max_value=100.0, value=1.0, step=0.1)
    rho = st.number_input("Malzeme yoğunluğu ρ (g/cm³)", min_value=1.0, max_value=30.0, value=7.85, step=0.01)

    st.markdown(
        "<small>Not: Çelik için ρ ≈ 7.85 g/cm³ alınabilir.</small>",
        unsafe_allow_html=True
    )

    h = h_mm / 1000.0
    t_m = t_mm / 1000.0
    A_k = h * t_m  # m²

    if st.button("Hesapla"):
        # Ağırlık
        w = agirlik_hesap(A_k, L_m, rho)
        st.markdown("Kesit alanı: **{:.2f} mm²**".format(A_k * 1e6))
        st.success("Toplam ağırlık: **{:.2f} kg**".format(w))

        # Lama için Wx, Wy
        Wx_sec, Wy_sec = wx_wy_flatbar(t_mm, h_mm)
        H_max = h_mm

        # T profilde kalınlık aralığı: t .. 2t
        t_min = t_mm
        t_max = 2 * t_mm

        lama_list = lama_muadil_wx_wy(Wx_sec, Wy_sec, H_max)
        t_list = t_profil_wx_wy(Wx_sec, Wy_sec, H_max, t_min, t_max)

    # ----------------------
    # WX / WY TABANLI MUADİL PROFİLLER
    # ----------------------
    if Wx_sec is not None and Wy_sec is not None:
        st.markdown("---")
        st.subheader(f"📊 {TOLERANS_METIN} Toleranslı Muadil Kesit Modülü Profilleri")

        st.markdown(
            "Seçilen lama için yakl. kesit modülleri:<br>"
            "- Wx ≈ <b>{:,.0f}</b> mm³<br>"
            "- Wy ≈ <b>{:,.0f}</b> mm³".format(Wx_sec, Wy_sec),
            unsafe_allow_html=True
        )

        muadiller = muadil_liste_2yuzde(Wx_sec, Wy_sec)
        if muadiller:
            st.dataframe(muadiller, use_container_width=True)
        else:
            st.info(f"{TOLERANS_METIN} tolerans içinde muadil profil bulunamadı. "
                    "Profil tablolarına daha fazla kesit eklersen sonuçlar zenginleşir.")

    # ----------------------
    # LAMA MUADİL LİSTESİ
    # ----------------------
    if lama_list:
        st.markdown("---")
        st.subheader("🟫 Bu profile muadil Lama (Flat Bar) boyutları")
        st.dataframe(lama_list, use_container_width=True)

    # ----------------------
    # T PROFİL MUADİL LİSTESİ
    # ----------------------
    if t_list:
        st.markdown("---")
        st.subheader("🅸 Bu profile muadil T Profiller (flanş + gövde kombinasyonu)")
        st.dataframe(t_list, use_container_width=True)
    elif Wx_sec is not None and Wy_sec is not None:
        st.markdown("---")
        st.info(
            f"Bu profil için {TOLERANS_METIN} Wx/Wy toleransı içinde muadil T profil bulunamadı. "
            "Arama aralığını genişletmek için kalınlık limitlerini koddan büyütebilirsin."
        )

# ---------------------------------------------------------
# SAĞ SÜTUN — TEKNİK ÇİZİM GÖRSELİ
# ---------------------------------------------------------
with col2:
    # Burada profil tipini sadece görsel seçimi için kullanıyoruz
    profil_tipi = "Lama (Flat Bar)"
    img_path = get_image_for_type(profil_tipi)
    if img_path:
        st.image(img_path, caption="Teknik Çizim Seti", use_column_width=True)
        st.markdown(
            "<small>Genel profil şemaları rehber amaçlı gösterilmektedir.</small>",
            unsafe_allow_html=True
        )
    else:
        st.info("Görsel klasöründe teknik çizim bulunamadı. `img/` altına uygun görselleri ekleyebilirsin.")
