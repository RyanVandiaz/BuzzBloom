# app.py

import streamlit as st
import pandas as pd
import plotly.express as px
# import google.generativeai as genai  <- Tidak lagi dibutuhkan untuk simulasi
import json
import time

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Media Intelligence Dashboard",
    page_icon="🧠",
    layout="wide",
)

# --- FUNGSI BANTUAN (VERSI SIMULASI) ---

def get_simulated_insights(chart_type):
    """
    Mensimulasikan panggilan API dengan mengembalikan contoh wawasan yang telah ditulis sebelumnya.
    """
    time.sleep(1.5) # Mensimulasikan waktu pemrosesan AI
    insights = {
        "sentiment": """
        * **Sentimen Positif Mendominasi:** Ini menandakan penerimaan audiens yang kuat terhadap konten. Pertahankan strategi yang ada.
        * **Identifikasi Pemicu Negatif:** Meskipun kecil, selidiki konten dengan sentimen negatif untuk menghindari kesalahan serupa di masa depan.
        * **Manfaatkan Konten Positif:** Bagikan ulang atau promosikan konten dengan sentimen paling positif untuk memaksimalkan jangkauan.
        """,
        "trend": """
        * **Identifikasi Puncak Keterlibatan:** Ada lonjakan signifikan pada pertengahan periode. Analisis konten yang diposting saat itu untuk direplikasi.
        * **Waspadai Penurunan:** Terjadi penurunan keterlibatan menjelang akhir periode. Pertimbangkan untuk meluncurkan kampanye baru untuk meningkatkan kembali minat.
        * **Pola Konsisten:** Keterlibatan cenderung lebih tinggi pada akhir pekan. Jadwalkan postingan paling penting Anda pada hari Sabtu atau Minggu.
        """,
        "platform": """
        * **Instagram adalah Bintangnya:** Alokasikan sebagian besar sumber daya ke Instagram karena menghasilkan keterlibatan tertinggi.
        * **Peluang di YouTube:** Meskipun keterlibatannya lebih rendah, format video di YouTube bisa dieksplorasi lebih lanjut untuk menjangkau audiens baru.
        * **Evaluasi Ulang Twitter:** Keterlibatan di Twitter paling rendah. Pertimbangkan apakah platform ini masih relevan untuk audiens target Anda.
        """,
        "media": """
        * **Video Mendorong Keterlibatan:** Konten video, meskipun jumlahnya lebih sedikit, tampaknya paling efektif. Prioritaskan produksi video.
        * **Gambar Tetap Penting:** Gambar adalah format yang paling umum dan stabil. Pastikan kualitas visual tetap tinggi.
        * **Teks Kurang Efektif:** Konten berbasis teks murni menunjukkan kinerja terendah. Kombinasikan teks dengan elemen visual untuk meningkatkan daya tarik.
        """,
        "location": """
        * **Jakarta sebagai Pusat Audiens:** Jakarta menunjukkan keterlibatan tertinggi. Pertimbangkan kampanye yang ditargetkan secara geografis untuk wilayah ini.
        * **Potensi di Surabaya & Bandung:** Dua kota ini menunjukkan potensi pertumbuhan. Buat konten yang relevan secara lokal untuk meningkatkan penetrasi.
        * **Jangkau di Luar Jawa:** Medan dan Makassar menunjukkan minat awal. Eksplorasi kemitraan dengan influencer lokal di sana.
        """,
        "influencer": """
        * **Andalkan Performa Terbaik:** Influencer A dan Brand B adalah pendorong keterlibatan utama. Perkuat kemitraan dengan mereka.
        * **Evaluasi Kinerja Influencer C:** Kinerjanya jauh di bawah yang lain. Tinjau kembali kesesuaian konten atau pertimbangkan untuk tidak melanjutkan kerja sama.
        * **Cari Bintang Baru:** Ada potensi pada Influencer D yang mulai menunjukkan pertumbuhan keterlibatan.
        """,
        "strategy": """
        ### Ringkasan Strategi Kampanye (Contoh)

        **1. Ringkasan Kinerja Keseluruhan:**
        Secara umum, kampanye menunjukkan hasil yang positif dengan dominasi sentimen baik dan tren keterlibatan yang meningkat, meskipun ada sedikit perlambatan di akhir periode.

        **2. Fokus Platform:**
        * **Prioritas Utama (70%): Instagram.** Platform ini adalah pendorong keterlibatan terbesar. Fokus pada Reels dan Stories interaktif.
        * **Prioritas Kedua (20%): YouTube.** Gunakan untuk konten mendalam seperti tutorial atau di balik layar untuk membangun loyalitas.
        * **Pemeliharaan (10%): News Portal & Twitter.** Gunakan untuk pengumuman singkat dan distribusi siaran pers.

        **3. Rekomendasi Konten & Kreatif:**
        * **Prioritaskan Video:** Buat lebih banyak konten video pendek (di bawah 60 detik) untuk Instagram Reels dan YouTube Shorts.
        * **Konten Buatan Pengguna (UGC):** Adakan kontes atau kampanye yang mendorong audiens untuk membuat konten terkait brand Anda.
        * **Tema:** Fokus pada kisah sukses pelanggan dan konten edukasi yang relevan dengan produk.

        **4. Penargetan Audiens:**
        * **Utama:** Lanjutkan penargetan agresif di **Jakarta**.
        * **Sekunder:** Alokasikan sebagian anggaran untuk iklan bertarget di **Surabaya** dan **Bandung**.
        * **Influencer:** Perpanjang kontrak dengan **Influencer A** dan alokasikan dana untuk bereksperimen dengan 2-3 mikro-influencer baru.

        **5. Peluang Peningkatan:**
        * **Optimalkan Waktu Posting:** Jadwalkan postingan penting pada akhir pekan (Sabtu sore & Minggu pagi) untuk hasil maksimal.
        * **Tingkatkan Kualitas Visual:** Investasikan pada sesi foto/video profesional untuk meningkatkan daya saing visual konten gambar.
        """
    }
    return insights.get(chart_type, "Contoh wawasan tidak ditemukan untuk jenis grafik ini.")


# --- INISIALISASI SESSION STATE ---
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'analysis_triggered' not in st.session_state:
    st.session_state.analysis_triggered = False
if 'df' not in st.session_state:
    st.session_state.df = None

# --- HEADER & UI UTAMA ---
st.markdown("""
    <div style="text-align: center;">
        <h1 style='color: #39FF14;'>Ryan Media Intelligence Agency</h1>
        <p>Dashboard Analisis Kinerja Konten Interaktif</p>
    </div>
""", unsafe_allow_html=True)
st.markdown("---")

# --- BILAH SISI (SIDEBAR) ---
st.sidebar.header("Tentang Aplikasi")
st.sidebar.info(
    "Ini adalah dashboard interaktif untuk menganalisis data kinerja media. "
    "Wawasan AI yang ditampilkan adalah contoh yang telah diprogram sebelumnya untuk tujuan demonstrasi."
)


# --- KONTROL TAMPILAN UTAMA ---

# Langkah 1: Unggah Data (di menu utama)
st.subheader("Langkah 1: Unggah File Data Anda")
uploaded_file = st.file_uploader("Pilih file CSV", type=["csv"], label_visibility="collapsed")

if uploaded_file is not None:
    # Proses hanya jika file baru diunggah atau belum diproses
    if st.session_state.df is None or uploaded_file.name != st.session_state.get('file_name', ''):
        try:
            with st.spinner('Memproses file... Membersihkan data...'):
                df = pd.read_csv(uploaded_file)
                if 'Date' in df.columns:
                    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                if 'Engagements' in df.columns:
                    df['Engagements'] = df['Engagements'].fillna(0).astype(int)
                df.dropna(subset=['Date'], inplace=True)
                
                st.session_state.df = df
                st.session_state.data_loaded = True
                st.session_state.analysis_triggered = False # Reset analisis saat file baru diunggah
                st.session_state.file_name = uploaded_file.name
            st.success(f"File '{uploaded_file.name}' berhasil dimuat dan siap dianalisis.")
        except Exception as e:
            st.error(f"Gagal memproses file: {e}")
            st.session_state.data_loaded = False

# Tampilkan pesan sambutan jika belum ada data
if not st.session_state.data_loaded:
    st.info("Selamat Datang! Silakan mulai dengan mengunggah file CSV di atas.")
else:
    # Langkah 2: Tombol Analisis
    st.subheader("Langkah 2: Mulai Analisis")
    if st.button("🚀 Analyze Data", use_container_width=True, type="primary"):
        st.session_state.analysis_triggered = True

    # Jika analisis dipicu, tampilkan dashboard lengkap
    if st.session_state.analysis_triggered:
        df = st.session_state.df
        
        # Filter Interaktif (di menu utama dalam sebuah expander)
        with st.expander("⚙️ Tampilkan/Sembunyikan Filter", expanded=True):
            filter_col1, filter_col2, filter_col3 = st.columns([2, 1, 1])
            
            with filter_col1:
                min_date = df['Date'].min().date()
                max_date = df['Date'].max().date()
                date_range = st.date_input("Pilih Rentang Tanggal", value=(min_date, max_date), min_value=min_date, max_value=max_date)
                start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
            
            with filter_col2:
                selected_platforms = st.multiselect("Platform", options=df['Platform'].unique(), default=df['Platform'].unique())
                selected_sentiments = st.multiselect("Sentimen", options=df['Sentiment'].unique(), default=df['Sentiment'].unique())

            with filter_col3:
                selected_media_types = st.multiselect("Jenis Media", options=df['Media_Type'].unique(), default=df['Media_Type'].unique())
        
        # Terapkan filter ke DataFrame
        df_filtered = df[
            (df['Date'] >= start_date) & (df['Date'] <= end_date) &
            (df['Platform'].isin(selected_platforms)) &
            (df['Sentiment'].isin(selected_sentiments)) &
            (df['Media_Type'].isin(selected_media_types))
        ]

        st.markdown("---")

        if df_filtered.empty:
            st.warning("Tidak ada data yang cocok dengan filter yang Anda pilih. Coba perluas kriteria filter Anda.")
        else:
            # --- TAMPILAN DASHBOARD ---
            st.header("Hasil Analisis")
            total_engagement = df_filtered['Engagements'].sum()
            total_posts = len(df_filtered)
            avg_engagement_per_post = total_engagement / total_posts if total_posts > 0 else 0

            st.markdown("##### Ringkasan Kinerja")
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Keterlibatan", f"{total_engagement:,.0f}")
            c2.metric("Total Postingan", f"{total_posts:,.0f}")
            c3.metric("Keterlibatan Rata-rata/Postingan", f"{avg_engagement_per_post:,.2f}")
            st.markdown("<br>", unsafe_allow_html=True)

            # --- VISUALISASI DAN WAWASAN AI ---
            col_chart1, col_chart2 = st.columns(2)

            with col_chart1:
                st.subheader("Distribusi Sentimen")
                sentiment_counts = df_filtered['Sentiment'].value_counts().reset_index()
                fig_sentiment = px.pie(sentiment_counts, names='Sentiment', values='count', hole=.3,
                                       color='Sentiment', color_discrete_map={'Positive': '#39FF14', 'Neutral': 'grey', 'Negative': '#FF6347'})
                fig_sentiment.update_layout(template="plotly_dark", legend_title_text='Sentimen')
                st.plotly_chart(fig_sentiment, use_container_width=True)

                with st.expander("🤖 AI Insights (Demonstrasi)"):
                    with st.spinner("Menghasilkan wawasan..."):
                        st.markdown(get_simulated_insights("sentiment"))

            with col_chart2:
                st.subheader("Tren Keterlibatan dari Waktu ke Waktu")
                engagement_trend = df_filtered.groupby(df_filtered['Date'].dt.to_period('D'))['Engagements'].sum().reset_index()
                engagement_trend['Date'] = engagement_trend['Date'].dt.to_timestamp()
                fig_trend = px.line(engagement_trend, x='Date', y='Engagements', markers=True)
                fig_trend.update_traces(line=dict(color='#39FF14'))
                fig_trend.update_layout(template="plotly_dark", xaxis_title='Tanggal', yaxis_title='Total Keterlibatan')
                st.plotly_chart(fig_trend, use_container_width=True)

                with st.expander("🤖 AI Insights (Demonstrasi)"):
                     with st.spinner("Menghasilkan wawasan..."):
                        st.markdown(get_simulated_insights("trend"))
            
            st.markdown("<br>", unsafe_allow_html=True)
            col_chart3, col_chart4 = st.columns(2)

            with col_chart3:
                st.subheader("Keterlibatan per Platform")
                platform_engagement = df_filtered.groupby('Platform')['Engagements'].sum().sort_values(ascending=False).reset_index()
                fig_platform = px.bar(platform_engagement, x='Platform', y='Engagements', color='Platform', color_discrete_sequence=px.colors.qualitative.Pastel)
                fig_platform.update_layout(template="plotly_dark", showlegend=False)
                st.plotly_chart(fig_platform, use_container_width=True)

                with st.expander("🤖 AI Insights (Demonstrasi)"):
                    with st.spinner("Menghasilkan wawasan..."):
                        st.markdown(get_simulated_insights("platform"))

            with col_chart4:
                st.subheader("Distribusi Jenis Media")
                media_type_counts = df_filtered['Media_Type'].value_counts().reset_index()
                fig_media = px.pie(media_type_counts, names='Media_Type', values='count', hole=.3, color_discrete_sequence=px.colors.sequential.Aggrnyl)
                fig_media.update_layout(template="plotly_dark", legend_title_text='Jenis Media')
                st.plotly_chart(fig_media, use_container_width=True)

                with st.expander("🤖 AI Insights (Demonstrasi)"):
                    with st.spinner("Menghasilkan wawasan..."):
                        st.markdown(get_simulated_insights("media"))

            st.markdown("<br>", unsafe_allow_html=True)
            col_chart5, col_chart6 = st.columns(2)
            
            with col_chart5:
                st.subheader("5 Lokasi Teratas")
                top_locations = df_filtered.groupby('Location')['Engagements'].sum().nlargest(5).sort_values(ascending=True).reset_index()
                fig_location = px.bar(top_locations, y='Location', x='Engagements', orientation='h', color='Engagements', color_continuous_scale='Greens')
                fig_location.update_layout(template="plotly_dark", yaxis_title='Lokasi')
                st.plotly_chart(fig_location, use_container_width=True)

                with st.expander("🤖 AI Insights (Demonstrasi)"):
                    with st.spinner("Menghasilkan wawasan..."):
                        st.markdown(get_simulated_insights("location"))
            
            with col_chart6:
                st.subheader("5 Influencer/Brand Teratas")
                top_influencers = df_filtered.groupby('Influencer_Brand')['Engagements'].sum().nlargest(5).sort_values(ascending=True).reset_index()
                fig_influencer = px.bar(top_influencers, y='Influencer_Brand', x='Engagements', orientation='h', color='Engagements', color_continuous_scale='Purples')
                fig_influencer.update_layout(template="plotly_dark", yaxis_title='Influencer / Brand')
                st.plotly_chart(fig_influencer, use_container_width=True)

                with st.expander("🤖 AI Insights (Demonstrasi)"):
                    with st.spinner("Menghasilkan wawasan..."):
                        st.markdown(get_simulated_insights("influencer"))

            # --- FITUR STRATEGI LANJUTAN ---
            st.markdown("---")
            st.header("🧠 Analisis & Rekomendasi Strategi")
            if st.button("Hasilkan Ringkasan Strategi Kampanye", key="generate_summary"):
                with st.spinner("AI sedang menyusun ringkasan strategi..."):
                    st.markdown(get_simulated_insights("strategy"))
