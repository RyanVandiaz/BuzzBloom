# app.py

import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI
import json
from io import BytesIO

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Media Intelligence Dashboard",
    page_icon="🟢",
    layout="wide",
)

# --- FUNGSI BANTUAN ---

# Fungsi untuk berkomunikasi dengan API AI (Gaya OpenRouter)
def get_ai_insights(prompt_text, api_key):
    """
    Mengirimkan prompt ke API AI dan mengembalikan responsnya.
    Menggunakan basis URL kustom untuk kompatibilitas gaya OpenRouter.
    """
    if not api_key:
        return "Kunci API OpenAI tidak diberikan. Masukkan kunci API di bilah sisi untuk mengaktifkan wawasan AI."
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        completion = client.chat.completions.create(
            extra_headers={
              "HTTP-Referer": "http://localhost:8501", # Opsional. URL Situs untuk peringkat di openrouter.ai.
              "X-Title": "Ryan Media Intelligence", # Opsional. Judul situs untuk peringkat di openrouter.ai.
            },
            model="deepseek/deepseek-r1-0528:free",
            messages=[
                {"role": "system", "content": "You are an expert media analyst. Provide three brief, actionable insights based on the data provided. Use bullet points."},
                {"role": "user", "content": prompt_text},
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Terjadi kesalahan saat menghubungi API AI: {e}"


# --- GAYA KUSTOM (CSS) ---
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# local_css("style.css") # Anda dapat membuat file style.css untuk gaya yang lebih kompleks jika diperlukan

# --- HEADER & UI UTAMA ---
st.markdown("""
    <div style="text-align: center;">
        <h1 style='color: #39FF14;'>Ryan Media Intelligence Agency</h1>
        <p>Dashboard Analisis Kinerja Konten Interaktif</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# --- BILAH SISI (SIDEBAR) ---
st.sidebar.header("Filter & Pengaturan")

# Input Kunci API AI
st.sidebar.subheader("Pengaturan AI")
openai_api_key = st.sidebar.text_input("Masukkan Kunci API OpenRouter/OpenAI Anda", type="password", help="Diperlukan untuk menghasilkan wawasan otomatis.")

# Fitur Unggah File
st.sidebar.subheader("Unggah Data Anda")
uploaded_file = st.sidebar.file_uploader("Pilih file CSV", type=["csv"])

# DataFrame Inisialisasi
df = None

if uploaded_file is not None:
    try:
        # Tampilkan status kepada pengguna
        with st.spinner('Memproses file... Membersihkan data...'):
            df = pd.read_csv(uploaded_file)
            
            # 1. Pembersihan Data Otomatis
            # Konversi kolom 'Date' ke datetime
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            
            # Isi nilai kosong pada 'Engagements' dengan 0
            if 'Engagements' in df.columns:
                df['Engagements'] = df['Engagements'].fillna(0).astype(int)

            # Hapus baris di mana tanggal tidak dapat di-parse
            df.dropna(subset=['Date'], inplace=True)
            
        st.sidebar.success(f"File '{uploaded_file.name}' berhasil diproses!")
        st.sidebar.info(f"Dataset berisi {df.shape[0]} baris dan {df.shape[1]} kolom.")
        
    except Exception as e:
        st.sidebar.error(f"Terjadi kesalahan saat memproses file: {e}")
        df = None # Pastikan df adalah None jika ada kesalahan
else:
    st.info("Silakan unggah file CSV melalui bilah sisi untuk memulai analisis.")

# --- Filter Interaktif (hanya ditampilkan jika df dimuat) ---
if df is not None:
    st.sidebar.markdown("---")
    st.sidebar.header("Filter Data")

    # Filter Rentang Tanggal
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    date_range = st.sidebar.date_input(
        "Pilih Rentang Tanggal",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])

    # Filter Multi-pilih
    selected_platforms = st.sidebar.multiselect("Platform", options=df['Platform'].unique(), default=df['Platform'].unique())
    selected_sentiments = st.sidebar.multiselect("Sentimen", options=df['Sentiment'].unique(), default=df['Sentiment'].unique())
    selected_media_types = st.sidebar.multiselect("Jenis Media", options=df['Media_Type'].unique(), default=df['Media_Type'].unique())
    
    # Terapkan filter ke DataFrame
    df_filtered = df[
        (df['Date'] >= start_date) & (df['Date'] <= end_date) &
        (df['Platform'].isin(selected_platforms)) &
        (df['Sentiment'].isin(selected_sentiments)) &
        (df['Media_Type'].isin(selected_media_types))
    ]

    # --- TAMPILAN DASHBOARD ---
    if not df_filtered.empty:
        # Metrik Utama
        total_engagement = df_filtered['Engagements'].sum()
        total_posts = len(df_filtered)
        avg_engagement_per_post = total_engagement / total_posts if total_posts > 0 else 0

        st.markdown("### Ringkasan Kinerja")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Keterlibatan", f"{total_engagement:,.0f}")
        col2.metric("Total Postingan", f"{total_posts:,.0f}")
        col3.metric("Keterlibatan Rata-rata/Postingan", f"{avg_engagement_per_post:,.2f}")

        st.markdown("<hr style='border:1px solid #39FF14'>", unsafe_allow_html=True)

        # --- VISUALISASI DAN WAWASAN AI ---
        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            # 1. Rincian Sentimen (Pie Chart)
            st.subheader("Distribusi Sentimen")
            sentiment_counts = df_filtered['Sentiment'].value_counts().reset_index()
            sentiment_counts.columns = ['Sentiment', 'Jumlah']
            fig_sentiment = px.pie(sentiment_counts, names='Sentiment', values='Jumlah',
                                   color='Sentiment',
                                   color_discrete_map={'Positive': '#39FF14', 'Neutral': 'grey', 'Negative': '#FF6347'},
                                   hole=.3)
            fig_sentiment.update_layout(template="plotly_dark", legend_title_text='Sentimen')
            st.plotly_chart(fig_sentiment, use_container_width=True)

            with st.expander("🤖 Wawasan AI tentang Sentimen"):
                prompt = f"""
                Analisis data distribusi sentimen berikut dan berikan tiga wawasan yang dapat ditindaklanjuti.
                Data: {sentiment_counts.to_json(orient='split')}
                Contoh: 'Sentimen Positif mendominasi, menunjukkan penerimaan audiens yang baik. Pertahankan strategi konten saat ini.'
                """
                if openai_api_key:
                    with st.spinner("Menganalisis sentimen..."):
                        st.write(get_ai_insights(prompt, openai_api_key))
                else:
                    st.warning("Masukkan kunci API untuk mendapatkan wawasan.")


        with col_chart2:
            # 2. Tren Keterlibatan dari Waktu ke Waktu (Line Chart)
            st.subheader("Tren Keterlibatan dari Waktu ke Waktu")
            engagement_trend = df_filtered.groupby(df_filtered['Date'].dt.to_period('D'))['Engagements'].sum().reset_index()
            engagement_trend['Date'] = engagement_trend['Date'].dt.to_timestamp()
            fig_trend = px.line(engagement_trend, x='Date', y='Engagements',
                                markers=True, labels={'Engagements': 'Total Keterlibatan'})
            fig_trend.update_traces(line=dict(color='#39FF14'))
            fig_trend.update_layout(template="plotly_dark", xaxis_title='Tanggal', yaxis_title='Total Keterlibatan')
            st.plotly_chart(fig_trend, use_container_width=True)

            with st.expander("🤖 Wawasan AI tentang Tren Keterlibatan"):
                prompt = f"""
                Analisis data tren keterlibatan dari waktu ke waktu berikut. Identifikasi puncak, penurunan, dan tren umum. Berikan tiga wawasan.
                Data: {engagement_trend.to_json(orient='split')}
                Contoh: 'Terlihat lonjakan keterlibatan yang signifikan pada tanggal X. Selidiki konten yang diposting pada hari itu untuk direplikasi.'
                """
                if openai_api_key:
                    with st.spinner("Menganalisis tren..."):
                        st.write(get_ai_insights(prompt, openai_api_key))
                else:
                    st.warning("Masukkan kunci API untuk mendapatkan wawasan.")
        
        st.markdown("<hr style='border:1px solid #39FF14'>", unsafe_allow_html=True)
        
        col_chart3, col_chart4, col_chart5 = st.columns(3)

        with col_chart3:
             # 3. Keterlibatan Platform (Bar Chart)
            st.subheader("Keterlibatan per Platform")
            platform_engagement = df_filtered.groupby('Platform')['Engagements'].sum().sort_values(ascending=False).reset_index()
            fig_platform = px.bar(platform_engagement, x='Platform', y='Engagements',
                                  color='Platform',
                                  color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_platform.update_layout(template="plotly_dark", showlegend=False)
            st.plotly_chart(fig_platform, use_container_width=True)

            with st.expander("🤖 Wawasan AI tentang Platform"):
                prompt = f"""
                Analisis data keterlibatan platform ini. Tunjukkan platform berkinerja terbaik dan terendah. Berikan tiga rekomendasi.
                Data: {platform_engagement.to_json(orient='split')}
                Contoh: 'Instagram adalah pendorong keterlibatan terbesar. Alokasikan lebih banyak sumber daya untuk konten Instagram.'
                """
                if openai_api_key:
                    with st.spinner("Menganalisis platform..."):
                        st.write(get_ai_insights(prompt, openai_api_key))
                else:
                    st.warning("Masukkan kunci API untuk mendapatkan wawasan.")

        with col_chart4:
            # 4. Perpaduan Jenis Media (Pie Chart)
            st.subheader("Distribusi Jenis Media")
            media_type_counts = df_filtered['Media_Type'].value_counts().reset_index()
            media_type_counts.columns = ['Media_Type', 'Jumlah']
            fig_media = px.pie(media_type_counts, names='Media_Type', values='Jumlah',
                               color_discrete_sequence=px.colors.sequential.Aggrnyl,
                               hole=.3)
            fig_media.update_layout(template="plotly_dark", legend_title_text='Jenis Media')
            st.plotly_chart(fig_media, use_container_width=True)

            with st.expander("🤖 Wawasan AI tentang Jenis Media"):
                prompt = f"""
                Analisis data distribusi jenis media ini. Jenis media mana yang paling sering digunakan? Kaitkan dengan keterlibatan jika memungkinkan. Berikan tiga wawasan.
                Data: {media_type_counts.to_json(orient='split')}
                """
                if openai_api_key:
                    with st.spinner("Menganalisis jenis media..."):
                        st.write(get_ai_insights(prompt, openai_api_key))
                else:
                    st.warning("Masukkan kunci API untuk mendapatkan wawasan.")

        with col_chart5:
            # 5. 5 Lokasi Teratas berdasarkan Keterlibatan (Bar Chart)
            st.subheader("5 Lokasi Teratas")
            top_locations = df_filtered.groupby('Location')['Engagements'].sum().nlargest(5).sort_values(ascending=True).reset_index()
            fig_location = px.bar(top_locations, y='Location', x='Engagements', orientation='h',
                                  color='Engagements', color_continuous_scale='Greens')
            fig_location.update_layout(template="plotly_dark", yaxis_title='Lokasi')
            st.plotly_chart(fig_location, use_container_width=True)

            with st.expander("🤖 Wawasan AI tentang Lokasi"):
                prompt = f"""
                Analisis data 5 lokasi teratas berdasarkan keterlibatan. Lokasi mana yang paling terlibat? Berikan tiga strategi penargetan geografis.
                Data: {top_locations.to_json(orient='split')}
                Contoh: 'Jakarta menunjukkan keterlibatan tertinggi. Pertimbangkan untuk menjalankan kampanye yang dilokalkan untuk audiens Jakarta.'
                """
                if openai_api_key:
                    with st.spinner("Menganalisis lokasi..."):
                        st.write(get_ai_insights(prompt, openai_api_key))
                else:
                    st.warning("Masukkan kunci API untuk mendapatkan wawasan.")

        st.markdown("<hr style='border:1px solid #39FF14'>", unsafe_allow_html=True)
        
        # --- FITUR LANJUTAN ---
        st.header("🧠 Analisis & Rekomendasi Lanjutan")
        
        if st.button("Hasilkan Ringkasan Strategi Kampanye", key="generate_summary"):
            if openai_api_key:
                with st.spinner("AI sedang menyusun ringkasan strategi... Ini mungkin memakan waktu sebentar."):
                    # Buat ringkasan data yang lebih kecil untuk dikirim sebagai prompt
                    summary_data = df_filtered.sample(min(100, len(df_filtered))).to_dict(orient='records')
                    
                    strategy_prompt = f"""
                    Anda adalah seorang ahli strategi media digital. Berdasarkan ringkasan data berikut dari kampanye media, buatlah ringkasan strategi yang komprehensif.
                    Fokus pada:
                    1.  **Ringkasan Kinerja Keseluruhan:** Apa sentimen dan tren keterlibatan umum?
                    2.  **Platform Unggulan:** Platform mana yang harus menjadi fokus utama dan mengapa?
                    3.  **Rekomendasi Konten:** Jenis media dan topik konten apa yang paling beresonansi dengan audiens?
                    4.  **Penargetan Audiens:** Lokasi mana yang harus diprioritaskan?
                    5.  **Peluang Peningkatan:** Area apa yang menunjukkan kinerja buruk dan bagaimana cara memperbaikinya?
                    
                    Data:
                    {json.dumps(summary_data, indent=2)}
                    
                    Berikan output dalam format markdown yang terstruktur dengan baik.
                    """
                    
                    strategy_summary = get_ai_insights(strategy_prompt, openai_api_key)
                    st.markdown(strategy_summary)
            else:
                st.error("Harap masukkan Kunci API OpenAI Anda di bilah sisi untuk menggunakan fitur ini.")

    else:
        st.warning("Tidak ada data yang tersedia untuk filter yang dipilih. Coba sesuaikan filter Anda.")
else:
    st.markdown("""
    ### Selamat Datang di Dashboard Intelijen Media Anda!
    
    Dashboard ini memungkinkan Anda untuk:
    - **Menganalisis** kinerja konten di berbagai platform.
    - **Memvisualisasikan** tren keterlibatan, distribusi sentimen, dan banyak lagi.
    - **Mendapatkan wawasan** yang dihasilkan AI untuk mendorong strategi Anda.
    
    **Untuk memulai:**
    1.  Gunakan bilah sisi di sebelah kiri untuk **mengunggah file CSV Anda**.
    2.  (Opsional) Masukkan **Kunci API OpenRouter/OpenAI** Anda untuk mengaktifkan fitur analisis AI.
    3.  Gunakan **filter interaktif** untuk menelusuri data Anda.
    """)
