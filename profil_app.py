 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/profil_app.py b/profil_app.py
index 282d77abcfaff8cfcfde2ee23d76eabe080ced81..b79a4a13cc2063867b05d0a41f8ffdfa7fcc5820 100644
--- a/profil_app.py
+++ b/profil_app.py
@@ -1,46 +1,50 @@
 
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
 
+# Tolerans oranı: ±%2 (Wx/Wy muadil aramalarında kullanılır)
+TOLERANS_ORAN = 0.02
+TOLERANS_YUZDE = int(TOLERANS_ORAN * 100)
+
 
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
@@ -208,132 +212,132 @@ def build_all_profiles_wx_wy():
 
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
-# %10 MUADIL PROFIL LISTESI (WX/WY)
+# %2 MUADIL PROFIL LISTESI (WX/WY)
 # ---------------------------------------------------------
-def muadil_liste_10yuzde(Wx_target, Wy_target):
+def muadil_liste_2yuzde(Wx_target, Wy_target):
     tum = build_all_profiles_wx_wy()
     if Wx_target is None or Wy_target is None:
         return []
 
-    Wx_min = Wx_target * 0.9
-    Wx_max = Wx_target * 1.1
-    Wy_min = Wy_target * 0.9
-    Wy_max = Wy_target * 1.1
+    Wx_min = Wx_target * (1 - TOLERANS_ORAN)
+    Wx_max = Wx_target * (1 + TOLERANS_ORAN)
+    Wy_min = Wy_target * (1 - TOLERANS_ORAN)
+    Wy_max = Wy_target * (1 + TOLERANS_ORAN)
 
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
 # LAMA MUADIL (WX/WY HEDEFINE GORE)
 # ---------------------------------------------------------
 def lama_muadil_wx_wy(Wx_target, Wy_target, h_mm):
-    """Verilen Wx, Wy hedeflerine göre sabit h_mm yükseklikte
-    hangi lama kalınlıkları (%10 toleransla) muadil olabilir?
-    Burada şart Wx veya Wy'den en az biri %10 bandında olsun (VEYA)."""
+    f"""Verilen Wx, Wy hedeflerine göre sabit h_mm yükseklikte
+    hangi lama kalınlıkları (%{TOLERANS_YUZDE} toleransla) muadil olabilir?
+    Burada şart Wx veya Wy'den en az biri %{TOLERANS_YUZDE} bandında olsun (VEYA)."""
     if Wx_target is None or Wy_target is None or h_mm is None:
         return []
 
     liste = []
     for t in range(2, 101):  # 2..100 mm kalınlık taraması
         Wx_l, Wy_l = wx_wy_flatbar(t, h_mm)
         if Wx_l is None or Wy_l is None:
             continue
 
         if Wx_target <= 0 or Wy_target <= 0:
             continue
 
-        cond_wx = abs(Wx_l - Wx_target) <= 0.10 * Wx_target
-        cond_wy = abs(Wy_l - Wy_target) <= 0.10 * Wy_target
+        cond_wx = abs(Wx_l - Wx_target) <= TOLERANS_ORAN * Wx_target
+        cond_wy = abs(Wy_l - Wy_target) <= TOLERANS_ORAN * Wy_target
 
         if cond_wx or cond_wy:
             dWx = abs(Wx_l - Wx_target)
             dWy = abs(Wy_l - Wy_target)
             skor = dWx + dWy
             liste.append({
                 "Lama": "{} x {}".format(h_mm, t),
                 "h (mm)": h_mm,
                 "t (mm)": t,
                 "Wx_lama (mm³)": Wx_l,
                 "Wy_lama (mm³)": Wy_l,
                 "ΔWx": dWx,
                 "ΔWy": dWy,
                 "Toplam Skor": skor
             })
 
     liste.sort(key=lambda x: x["Toplam Skor"])
     return liste
 
 
 # ---------------------------------------------------------
 # T PROFIL MUADIL (WX/WY HEDEFINE GORE)
 # ---------------------------------------------------------
 def t_profil_wx_wy(Wx_target, Wy_target, H_mm, t_min_mm, t_max_mm):
-    """
+    f"""
     H_mm toplam yüksekliğe sahip T profil için
     flanş + gövde kombinasyonlarını tarar.
     Flanş: b_f x t_f
     Gövde: h_w x t_w  (H = t_f + h_w)
-    Wx/Wy hedefe %10 içinde olanları listeler.
+    Wx/Wy hedefe %{TOLERANS_YUZDE} içinde olanları listeler.
     t_min_mm ve t_max_mm: flanş ve gövde kalınlığı için min/max (mm)
     """
     if Wx_target is None or Wy_target is None or H_mm is None:
         return []
     if t_min_mm is None or t_max_mm is None or t_min_mm <= 0 or t_max_mm < t_min_mm:
         return []
 
     H = float(H_mm)
     if H <= 0:
         return []
 
     # Kalınlık adayları (tipik sac/lamalar) – 4-30 mm
     base_t_candidates = [4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 25, 30]
     t_list = [t for t in base_t_candidates if t_min_mm <= t <= t_max_mm]
     if not t_list:
         return []
 
     # Flanş genişliği: H'nin yaklaşık 0.5x ile 2x arası, 10 mm adım
     b_min = max(20.0, 0.5 * H)
     b_max = 2.0 * H
     b_start = int(round(b_min / 10.0) * 10)
     b_end = int(round(b_max / 10.0) * 10)
 
     sonuc = []
 
@@ -365,53 +369,53 @@ def t_profil_wx_wy(Wx_target, Wy_target, H_mm, t_min_mm, t_max_mm):
                 Ix_f = b_f * t_f ** 3 / 12.0
                 Ix_w = t_w * h_w ** 3 / 12.0
                 Ix = Ix_f + A_f * (y_f - y_bar) ** 2 + Ix_w + A_w * (y_w - y_bar) ** 2
 
                 # Iy: y eksenine göre
                 Iy_f = t_f * b_f ** 3 / 12.0
                 Iy_w = h_w * t_w ** 3 / 12.0
                 Iy = Iy_f + Iy_w
 
                 # Ekstrem fiber mesafeleri
                 c_top = H - y_bar
                 c_bot = y_bar
                 c_x = max(c_top, c_bot)  # Wx için
                 c_y = b_f / 2.0          # Wy için
 
                 # Birimler: mm^4 -> m^4, sonra Wx,Wy -> mm^3
                 Ix_m4 = Ix * 1e-12
                 Iy_m4 = Iy * 1e-12
 
                 Wx_m3 = Ix_m4 / (c_x / 1000.0)
                 Wy_m3 = Iy_m4 / (c_y / 1000.0)
 
                 Wx_mm3 = Wx_m3 * 1e9
                 Wy_mm3 = Wy_m3 * 1e9
 
-                # %10 tolerans (VEYA)
-                cond_wx = abs(Wx_mm3 - Wx_t) <= 0.10 * Wx_t if Wx_t > 0 else False
-                cond_wy = abs(Wy_mm3 - Wy_t) <= 0.10 * Wy_t if Wy_t > 0 else False
+                # %2 tolerans (VEYA)
+                cond_wx = abs(Wx_mm3 - Wx_t) <= TOLERANS_ORAN * Wx_t if Wx_t > 0 else False
+                cond_wy = abs(Wy_mm3 - Wy_t) <= TOLERANS_ORAN * Wy_t if Wy_t > 0 else False
 
                 if not (cond_wx or cond_wy):
                     continue
 
                 dWx = abs(Wx_mm3 - Wx_t)
                 dWy = abs(Wy_mm3 - Wy_t)
                 skor = dWx + dWy
 
                 sonuc.append({
                     "T Profil": "T (flanş {}x{}, gövde {}x{})".format(b_f, t_f, h_w, t_w),
                     "H (mm)": H,
                     "b_f (mm)": b_f,
                     "t_f (mm)": t_f,
                     "h_w (mm)": h_w,
                     "t_w (mm)": t_w,
                     "Wx_T (mm³)": Wx_mm3,
                     "Wy_T (mm³)": Wy_mm3,
                     "ΔWx": dWx,
                     "ΔWy": dWy,
                     "Toplam Skor": skor
                 })
 
     sonuc.sort(key=lambda x: x["Toplam Skor"])
     return sonuc
 
@@ -893,72 +897,72 @@ with col1:
         h = h_mm / 1000.0
         t_m = t_mm / 1000.0
         A_k = h * t_m  # m^2
 
         if st.button("Hesapla"):
             w = agirlik_hesap(A_k, L_m, rho)
             st.markdown("Kesit alanı: **{:.2f} mm²**".format(A_k * 1e6))
             st.success("Toplam ağırlık: **{:.2f} kg**".format(w))
 
             Wx_sec, Wy_sec = wx_wy_flatbar(t_mm, h_mm)
             H_max = h_mm
 
             # Kalınlık aralığı: t .. 2t
             t_min = t_mm
             t_max = 2 * t_mm
 
             lama_list = lama_muadil_wx_wy(Wx_sec, Wy_sec, H_max)
             t_list = t_profil_wx_wy(Wx_sec, Wy_sec, H_max, t_min, t_max)
 
 
     # ----------------------
     # WX / WY TABANLI MUADIL PROFILLER
     # ----------------------
     if Wx_sec is not None and Wy_sec is not None:
         st.markdown("---")
-        st.subheader("📊 %10 Toleranslı Muadil Kesit Modülü Profilleri")
+        st.subheader(f"📊 %{TOLERANS_YUZDE} Toleranslı Muadil Kesit Modülü Profilleri")
 
         st.markdown(
             "Seçilen profil için yakl. kesit modülleri:<br>"
             "- Wx ≈ <b>{:,.0f}</b> mm³<br>"
             "- Wy ≈ <b>{:,.0f}</b> mm³".format(Wx_sec, Wy_sec),
             unsafe_allow_html=True
         )
 
-        muadiller = muadil_liste_10yuzde(Wx_sec, Wy_sec)
+        muadiller = muadil_liste_2yuzde(Wx_sec, Wy_sec)
         if muadiller:
             st.dataframe(muadiller, use_container_width=True)
         else:
-            st.info("%10 tolerans içinde muadil profil bulunamadı. Tablolara daha fazla profil ekleyebilirsin.")
+            st.info(f"%{TOLERANS_YUZDE} tolerans içinde muadil profil bulunamadı. Tablolara daha fazla profil ekleyebilirsin.")
 
     # ----------------------
     # LAMA MUADIL LISTESI
     # ----------------------
     if lama_list:
         st.markdown("---")
         st.subheader("🟫 Bu profile muadil Lama (Flat Bar) boyutları")
         st.dataframe(lama_list, use_container_width=True)
 
     # ----------------------
     # T PROFIL MUADIL LISTESI
     # ----------------------
     if t_list:
         st.markdown("---")
         st.subheader("🅸 Bu profile muadil T Profiller (flanş + gövde kombinasyonu)")
         st.dataframe(t_list, use_container_width=True)
     elif Wx_sec is not None and Wy_sec is not None:
         st.markdown("---")
-        st.info("Bu profil için %10 Wx/Wy toleransı içinde muadil T profil bulunamadı. "
+        st.info(f"Bu profil için %{TOLERANS_YUZDE} Wx/Wy toleransı içinde muadil T profil bulunamadı. "
                 "Arama aralığını genişletmek için kalınlık aralıklarının mantığını koddan güncelleyebilirsin.")
 
 
 # ---------------------------------------------------------
 # SAG SUTUN — TEKNIK CIZIM GORSELI
 # ---------------------------------------------------------
 with col2:
     img_path = get_image_for_type(profil_tipi)
     if img_path:
         st.image(img_path, caption="Teknik Çizim Seti", use_column_width=True)
         st.markdown(
             "<small>Seçtiğiniz profil için referans teknik ölçü şemaları (genel set).</small>",
             unsafe_allow_html=True
         )
 
EOF
)
