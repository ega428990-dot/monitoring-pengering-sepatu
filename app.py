import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import time

# 1. Koneksi ke Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate('kunci_firebase.json')
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://pengering-sepatu-iot-default-rtdb.firebaseio.com/'
    })

# --- FUNGSI LOGIN SEDERHANA ---
def login():
    st.title("🔐 Login Sistem Pengering Sepatu")
    user = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Masuk"):
        if user == "admin" and password == "12345": # Silakan ganti user & pass sesuai keinginan
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Username atau Password salah!")

# --- DASHBOARD UTAMA ---
def dashboard():
    st.set_page_config(page_title="Dashboard Pengering Sepatu", layout="wide")
    
    st.title("🛡️ Monitoring Pengering Sepatu IoT")
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()

    placeholder = st.empty()

    while True:
        with placeholder.container():
            # Ambil data dari Firebase
            ref = db.reference('/sensor')
            data = ref.get()

            if data:
                # Ambil nilai dari Firebase (Pastikan ESP32 mengirim data ini)
                suhu = data.get('suhu', 0)
                waktu = data.get('waktu_menit', 0) # Waktu dalam menit
                status_val = data.get('kelembapan', 0) # Kita gunakan nilai kelembapan untuk menentukan status

                # Logika Penentuan Status Sepatu
                if status_val > 70:
                    status_teks = "💧 Basah"
                    warna = "inverse" # Merah/Gelap
                elif 30 <= status_val <= 70:
                    status_teks = "🌤️ Setengah Kering"
                    warna = "normal" # Oranye/Kuning
                else:
                    status_teks = "✅ Kering"
                    warna = "normal" # Hijau

                # Tampilan Kolom
                col1, col2, col3 = st.columns(3)
                col1.metric("Suhu (°C)", f"{suhu}")
                col2.metric("Lama Pengeringan", f"{waktu} Menit")
                col3.metric("Status Sepatu", status_teks)

                st.divider()
                st.info(f"Informasi: Saat ini sepatu terdeteksi dalam kondisi {status_teks}")
            else:
                st.warning("Menghubungkan ke alat... Pastikan ESP32 sudah mengirim data.")
            
            time.sleep(2)

# Jalankan Aplikasi
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
else:
    dashboard()