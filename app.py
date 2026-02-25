import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
import time

# 1. Koneksi ke Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate('kunci_firebase.json')
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://pengering-sepatu-iot-default-rtdb.firebaseio.com/'
    })

# --- SISTEM LOGIN ---
def login():
    st.title("🔐 Login Sistem Pengering Sepatu")
    user = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Masuk"):
        if user == "admin" and password == "12345":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Username atau Password salah!")

# --- DASHBOARD UTAMA ---
def dashboard():
    st.set_page_config(page_title="IoT Shoe Dryer", layout="wide")
    
    # --- SIDEBAR KONTROL PANEL ---
    st.sidebar.title("🎮 Kontrol Panel")
    st.sidebar.write("Gunakan tombol di bawah untuk mengontrol alat")
    
    # Inisialisasi Firebase Reference untuk Kontrol
    ref_control = db.reference('/control')
    
    # Tombol Power Fan
    fan_on = st.sidebar.toggle("Power Fan (Kipas)")
    if fan_on:
        ref_control.update({'fan': True})
        st.sidebar.success("Kondisi: Fan Menyala")
    else:
        ref_control.update({'fan': False})
        st.sidebar.error("Kondisi: Fan Mati")

    # Tombol Power Heater
    heater_on = st.sidebar.toggle("Power Heater (Pemanas)")
    if heater_on:
        ref_control.update({'heater': True})
        st.sidebar.success("Kondisi: Heater Menyala")
    else:
        ref_control.update({'heater': False})
        st.sidebar.error("Kondisi: Heater Mati")

    st.sidebar.divider()
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()

    # --- BAGIAN MONITORING DATA ---
    if 'temp_history' not in st.session_state:
        st.session_state.temp_history = []
    if 'hum_history' not in st.session_state:
        st.session_state.hum_history = []

    placeholder = st.empty()

    while True:
        with placeholder.container():
            ref_sensor = db.reference('/sensor')
            data = ref_sensor.get()

            if data:
                suhu = data.get('suhu', 0)
                kelembapan = data.get('kelembapan', 0)
                menit = data.get('waktu_menit', 0)

                # Logika Status Sepatu berdasarkan menit
                if menit <= 29: status_sepatu = "💧 Sepatu Basah"
                elif 30 <= menit <= 50: status_sepatu = "🌤️ Sepatu Setengah Kering"
                else: status_sepatu = "✅ Sepatu Kering"

                st.header("📊 Monitoring Real-Time")
                c1, c2, c3 = st.columns(3)
                c1.metric("Suhu (°C)", f"{suhu}")
                c2.metric("Kelembapan (%)", f"{kelembapan}%")
                c3.metric("Waktu Berjalan", f"{menit} Menit")
                
                st.info(f"**Status Saat Ini:** {status_sepatu}")

                # Update riwayat data untuk grafik
                st.session_state.temp_history.append(suhu)
                st.session_state.hum_history.append(kelembapan)
                if len(st.session_state.temp_history) > 20:
                    st.session_state.temp_history.pop(0)
                    st.session_state.hum_history.pop(0)

                # Tampilan Grafik
                col_grafik1, col_grafik2 = st.columns(2)
                with col_grafik1:
                    st.subheader("📈 Grafik Riwayat Suhu")
                    st.line_chart(pd.DataFrame(st.session_state.temp_history, columns=['Suhu']))
                with col_grafik2:
                    st.subheader("📈 Grafik Riwayat Kelembapan")
                    st.line_chart(pd.DataFrame(st.session_state.hum_history, columns=['Kelembapan']))
            else:
                st.warning("Mencari data di Firebase... Pastikan ESP32 sudah menyala.")
            
            time.sleep(3)

# Jalankan Aplikasi
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
else:
    dashboard()
