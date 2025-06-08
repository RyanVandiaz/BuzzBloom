import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai
import io
import requests # Diperlukan jika ada bagian lain kode yang menggunakan requests

# --- KONFIGURASI HALAMAN & GAYA ---
# Mengatur konfigurasi halaman. Ini harus menjadi perintah pertama Streamlit.
st.set_page_config(
    page_title="Media Intelligence Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- FUNGSI UTAMA & LOGIKA ---

def configure_gemini_api():
    """
    Mengkonfigurasi API Gemini menggunakan kunci API.
    Kunci API ini di-hardcode untuk tujuan demonstrasi.
    Dalam aplikasi produksi, sebaiknya gunakan st.secrets atau variabel lingkungan.
    """
    api_key = "AIzaSyC0VUu6xTFIwH3aP2R7tbhyu4O8m1ICxn4"

    if not api_key:
        st.warning("API Key Gemini tidak ditemukan. Beberapa fitur AI mungkin tidak berfungsi.")
        return False
    try:
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        st.error(f"Gagal mengkonfigurasi Gemini API: {e}. Pastikan API Key valid.")
        return False

def get_ai_insight(prompt):
    """
    Memanggil API Gemini untuk menghasilkan wawasan berdasarkan prompt yang diberikan.
    Menggunakan model 'gemini-2.0-flash'.
    """
    # Pastikan API sudah dikonfigurasi melalui configure_gemini_api()
    if not configure_gemini_api(): # Memanggil lagi untuk memastikan konfigurasi sebelum setiap request
        return "Gagal membuat wawasan: API tidak terkonfigurasi."

    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        # Mengembalikan teks dari respons. Memastikan respons memiliki struktur yang diharapkan.
        if response.candidates and response.candidates[0].content.parts:
            return response.candidates[0].content.parts[0].text
        else:
            st.error("Gemini API tidak menghasilkan teks yang valid. Respons tidak terduga.")
            return "Gagal membuat wawasan. Silakan coba lagi."
    except Exception as e:
        st.error(f"Error saat memanggil Gemini API: {e}. Pastikan API Key valid dan terhubung ke internet.")
        return "Gagal membuat wawasan: Terjadi masalah koneksi atau API."

def load_css():
    """Menyuntikkan CSS kustom untuk gaya visual tingkat lanjut."""
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400..900&display=swap');

            /* Pengaturan dasar */
            body {
                background-color: #0f172a !important;
            }
            .stApp {
                background-image: radial-gradient(at top left, #1e293b, #0f172a, black);
                color: #cbd5e1;
            }
            
            /* Header */
            .main-header {
                font-family: 'Orbitron', sans-serif;
                text-align: center;
                margin-bottom: 2rem;
            }
            .main-header h1 {
                background: -webkit-linear-gradient(45deg, #06B6D4, #6366F1);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-size: 2.75rem;
                font-weight: 900;
            }
            .main-header p {
                color: #94a3b8;
                font-size: 1.1rem;
            }

            /* Sidebar */
            [data-testid="stSidebar"] {
                background-color: rgba(15, 23, 42, 0.6);
                backdrop-filter: blur(10px);
                border-right: 1px solid #334155;
            }
            [data-testid="stSidebar"] h3 {
                color: #5eead4;
                font-weight: 600;
            }

            /* Container utama dan kartu */
            .stVerticalBlock > .stHorizontalBlock:nth-child(1) {
                border: 1px solid #475569;
                background-color: rgba(30, 41, 59, 0.6);
                backdrop-filter: blur(15px);
                border-radius: 1rem;
                padding: 1.5rem;
                box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
            }
            .chart-container, .insight-hub, .anomaly-card {
                border: 1px solid #475569;
                background-color: rgba(30, 41, 59, 0.6);
                backdrop-filter: blur(15px);
                border-radius: 1rem;
                padding: 1.5rem;
                box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
                margin-bottom: 2rem;
            }
             .anomaly-card {
                border: 2px solid #f59e0b;
                background-color: rgba(245, 158, 11, 0.1);
             }

            /* Kotak Wawasan AI */
            .insight-box {
                background-color: rgba(15, 23, 42, 0.7);
                border: 1px solid #334155;
                border-radius: 0.5rem;
                padding: 1rem;
                margin-top: 1rem;
                min-height: 150px;
                white-space: pre-wrap; /* Mempertahankan format teks dari AI */
                font-size: 0.9rem;
            }
            
            /* Judul Kartu */
            .chart-container h3, .insight-hub h3, .anomaly-card h3 {
                color: #5eead4;
                margin-bottom: 1rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
                font-weight: 600;
            }
            
            /* Tombol */
            .stButton>button {
                border-radius: 0.5rem;
                font-weight: bold;
                color: white;
                transition: all 0.2s ease-in-out;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
            }
            /* Tombol default/insight */
            .stButton>button:not(:hover) {
                background-image: linear-gradient(to right, #8b5cf6, #a855f7);
                border: 1px solid #a855f7;
            }
            .stButton>button:hover {
                transform: scale(1.05);
                box-shadow: 0 4px 20px rgba(168, 85, 247, 0.4);
            }
            
        </style>
    """, unsafe_allow_html=True)

@st.cache_data
def parse_csv(uploaded_file):
    """Membaca file CSV yang diunggah ke dalam DataFrame pandas dan membersihkannya."""
    try:
        string_data = uploaded_file.getvalue().decode("utf-8")
        df = pd.read_csv(io.StringIO(string_data))
        
        # Pembersihan data
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Engagements'] = pd.to_numeric(df['Engagements'], errors='coerce')
        df.dropna(subset=['Date', 'Engagements'], inplace=True)
        df['Engagements'] = df['Engagements'].astype(int)
        
        # Memastikan kolom lain ada
        required_cols = ['Platform', 'Sentiment', 'Media Type', 'Location', 'Headline']
        for col in required_cols:
            if col not in df.columns:
                df[col] = 'N/A' # Isi dengan N/A jika tidak ada
        df[required_cols] = df[required_cols].fillna('N/A')

        return df
    except Exception as e:
        st.error(f"Gagal memproses file CSV. Pastikan formatnya benar. Error: {e}")
        return None

# --- UI STREAMLIT ---
load_css()
api_configured = configure_gemini_api() # Panggil fungsi konfigurasi API di awal

# Header Utama
st.markdown("""
    <div class="main-header">
        <h1>Media Intelligence Dashboard</h1>
        <p>Didukung oleh AI Gemini</p>
    </div>
""", unsafe_allow_html=True)


# Inisialisasi session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'chart_insights' not in st.session_state:
    st.session_state.chart_insights = {}
if 'campaign_summary' not in st.session_state:
    st.session_state.campaign_summary = ""
if 'post_idea' not in st.session_state:
    st.session_state.post_idea = ""
if 'anomaly_insight' not in st.session_state:
    st.session_state.anomaly_insight = ""


# Tampilan unggah file
if st.session_state.data is None:
    with st.container():
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown("### ☁️ Unggah File CSV Anda")
            st.write("Pastikan file memiliki kolom 'Date', 'Engagements', 'Sentiment', 'Platform', 'Media Type', 'Location', dan (opsional) 'Headline'.")
            uploaded_file = st.file_uploader("Pilih file CSV", type="csv")
            if uploaded_file is not None:
                st.session_state.data = parse_csv(uploaded_file)
                # Streamlit akan otomatis rerun ketika session_state.data berubah
            st.markdown('</div>', unsafe_allow_html=True)


# Tampilan Dasbor Utama (setelah file diunggah)
if st.session_state.data is not None:
    df = st.session_state.data

    # --- Sidebar Filter ---
    with st.sidebar:
        st.markdown("<h3><i class='fas fa-filter'></i> Filter Data</h3>", unsafe_allow_html=True)

        platform = st.selectbox("Platform", ["All"] + list(df['Platform'].unique()), key='platform_filter')
        sentiment = st.selectbox("Sentiment", ["All"] + list(df['Sentiment'].unique()), key='sentiment_filter')
        media_type = st.selectbox("Media Type", ["All"] + list(df['Media Type'].unique()), key='media_type_filter')
        location = st.selectbox("Location", ["All"] + list(df['Location'].unique()), key='location_filter')

        min_date, max_date = df['Date'].min().date(), df['Date'].max().date()
        start_date = st.date_input("Tanggal Mulai", min_date, min_value=min_date, max_value=max_date, key='start_date_filter')
        end_date = st.date_input("Tanggal Akhir", max_date, min_value=min_date, max_value=max_date, key='end_date_filter')
        
        # Logika reset insight jika filter berubah
        filter_state = f"{platform}{sentiment}{media_type}{location}{start_date}{end_date}"
        if 'last_filter_state' not in st.session_state or st.session_state.last_filter_state != filter_state:
            st.session_state.chart_insights = {}
            st.session_state.campaign_summary = ""
            st.session_state.post_idea = ""
            st.session_state.anomaly_insight = ""
            st.session_state.last_filter_state = filter_state


    # Filter DataFrame
    filtered_df = df[
        (df['Date'].dt.date >= start_date) &
        (df['Date'].dt.date <= end_date)
    ]
    if platform != "All":
        filtered_df = filtered_df[filtered_df['Platform'] == platform]
    if sentiment != "All":
        filtered_df = filtered_df[filtered_df['Sentiment'] == sentiment] # Memperbaiki baris ini
    if media_type != "All":
        filtered_df = filtered_df[filtered_df['Media Type'] == media_type]
    if location != "All":
        filtered_df = filtered_df[filtered_df['Location'] == location]

    # --- Pusat Wawasan AI ---
    st.markdown('<div class="insight-hub">', unsafe_allow_html=True)
    st.markdown("<h3>🧠 Pusat Wawasan AI</h3>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<h4>⚡ Ringkasan Strategi Kampanye</h4>", unsafe_allow_html=True)
        if st.button("Buat Ringkasan", key="summary_btn", use_container_width=True): # Hapus `and api_configured` karena sudah dicek di get_ai_insight
            with st.spinner("Membuat ringkasan strategi..."):
                prompt = f"""
                Anda adalah seorang konsultan strategi media senior. Analisis data kampanye berikut secara komprehensif. Berikan ringkasan eksekutif (3-4 kalimat) diikuti oleh 3 rekomendasi strategis utama yang paling berdampak. 
                Gunakan data berikut:
                - Data yang difilter (5 baris pertama): {filtered_df.head().to_json()}
                - Jumlah total sebutan: {len(filtered_df)}
                - Rata-rata keterlibatan: {filtered_df['Engagements'].mean():.2f}
                - Distribusi Sentimen: {filtered_df['Sentiment'].value_counts().to_json()}
                - Keterlibatan per Platform: {filtered_df.groupby('Platform')['Engagements'].sum().to_json()}
                Fokus pada gambaran besar: Apa cerita utama yang disampaikan oleh data ini? Di mana peluang terbesar dan apa risiko utamanya? Format jawaban Anda dengan jelas.
                """
                summary = get_ai_insight(prompt)
                st.session_state.campaign_summary = summary
                
        st.markdown(f'<div class="insight-box">{st.session_state.campaign_summary or "Klik untuk membuat ringkasan strategis dari semua data."}</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("<h4>💡 Generator Ide Konten AI</h4>", unsafe_allow_html=True)
        if st.button("✨ Buat Ide Postingan", key="idea_btn", use_container_width=True): # Hapus `and api_configured`
            with st.spinner("Mencari ide terbaik..."):
                if not filtered_df.empty: # Tambahkan pengecekan agar tidak error jika filtered_df kosong
                    best_platform_series = filtered_df.groupby('Platform')['Engagements'].sum()
                    if not best_platform_series.empty:
                        best_platform = best_platform_series.idxmax()
                        top_posts = filtered_df[filtered_df['Platform'] == best_platform].nlargest(5, 'Engagements')
                        top_headlines = ', '.join(top_posts['Headline'].tolist())
                    else:
                        best_platform = "tidak diketahui"
                        top_headlines = "tidak ada data"
                else:
                    best_platform = "tidak diketahui"
                    top_headlines = "tidak ada data"


                prompt = f"""
                Anda adalah seorang ahli strategi media sosial yang kreatif. Berdasarkan data berikut, buatlah satu contoh postingan untuk platform **{best_platform}**.
                - Platform Berkinerja Terbaik: {best_platform}
                - Topik Berkinerja Tinggi (dari judul): {top_headlines}
                Postingan harus:
                1. Ditulis dalam Bahasa Indonesia.
                2. Memiliki nada yang menarik dan sesuai untuk {best_platform}.
                3. Memberikan saran konsep visual yang jelas.
                4. Menyertakan 3-5 tagar yang relevan.
                Format output dengan jelas: "Platform:", "Konten Postingan:", "Saran Visual:", dan "Tagar:".
                """
                idea = get_ai_insight(prompt)
                st.session_state.post_idea = idea
                
        st.markdown(f'<div class="insight-box">{st.session_state.post_idea or "Klik untuk menghasilkan ide postingan berdasarkan data kinerja terbaik Anda."}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Deteksi Anomali ---
    engagement_trend = filtered_df.groupby(filtered_df['Date'].dt.date)['Engagements'].sum().reset_index()
    if len(engagement_trend) > 7: # Membutuhkan setidaknya beberapa titik data untuk statistik
        mean = engagement_trend['Engagements'].mean()
        std = engagement_trend['Engagements'].std()
        # Hindari pembagian oleh nol jika std adalah nol (semua keterlibatan sama)
        anomaly_threshold = mean + (2 * std) if std > 0 else mean + 0.1 # Ambang batas minimal jika tidak ada variasi
        anomalies = engagement_trend[engagement_trend['Engagements'] > anomaly_threshold]
        
        if not anomalies.empty:
            anomaly = anomalies.iloc[0] # Ambil anomali pertama
            st.markdown('<div class="anomaly-card">', unsafe_allow_html=True)
            st.markdown("<h3>⚠️ Peringatan Anomali Terdeteksi!</h3>", unsafe_allow_html=True)
            st.write(f"Kami mendeteksi lonjakan keterlibatan yang tidak biasa pada **{anomaly['Date']}** dengan **{int(anomaly['Engagements']):,}** keterlibatan (rata-rata: {int(mean):,} ± {int(std):,}).")
            
            if st.button("✨ Jelaskan Anomali Ini", key="anomaly_btn"): # Hapus `and api_configured`
                with st.spinner("Menganalisis penyebab anomali..."):
                    # Ambil data spesifik untuk hari anomali
                    anomaly_day_data = filtered_df[filtered_df['Date'].dt.date == anomaly['Date']]
                    top_headlines_on_anomaly_day = ', '.join(anomaly_day_data.nlargest(3, 'Engagements')['Headline'].tolist())

                    prompt = f"""
                    Anda adalah seorang analis data intelijen media. Terdeteksi anomali keterlibatan pada {anomaly['Date']}.
                    - Keterlibatan pada hari itu: {anomaly['Engagements']}
                    - Rata-rata keterlibatan historis (dari data yang difilter): {mean:.2f}
                    - Judul berita teratas yang berkontribusi pada hari itu (jika ada): {top_headlines_on_anomaly_day if top_headlines_on_anomaly_day else "Tidak ada judul spesifik yang ditemukan."}
                    Berikan 3 kemungkinan penyebab anomali ini dan 2 rekomendasi tindakan. Format sebagai daftar bernomor.
                    """
                    insight = get_ai_insight(prompt)
                    st.session_state.anomaly_insight = insight

            if st.session_state.anomaly_insight:
                st.markdown(f'<div class="insight-box">{st.session_state.anomaly_insight}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)


    # --- Tampilan Grafik ---
    chart_cols = st.columns(2)
    
    # Daftar grafik untuk ditampilkan
    charts_to_display = [
        {"key": "sentiment", "title": "Analisis Sentimen", "col": chart_cols[0]},
        {"key": "trend", "title": "Tren Keterlibatan Seiring Waktu", "col": chart_cols[1]},
        {"key": "platform", "title": "Keterlibatan per Platform", "col": chart_cols[0]},
        {"key": "mediaType", "title": "Distribusi Jenis Media", "col": chart_cols[1]},
        {"key": "location", "title": "5 Lokasi Teratas", "col": chart_cols[0]},
    ]
    
    # Fungsi pembuat prompt untuk menghindari pengulangan
    def get_chart_prompt(key, data_json):
        prompts = {
            "sentiment": f"Berdasarkan data distribusi sentimen berikut: {data_json}, berikan 3 wawasan (insights) tajam dan dapat ditindaklanjuti untuk strategi komunikasi merek. Format sebagai daftar bernomor.",
            "trend": f"Berdasarkan 10 data tren keterlibatan harian terakhir ini: {data_json}, berikan 3 wawasan strategis tentang puncak, penurunan, dan pola umum. Apa artinya ini bagi ritme kampanye? Format sebagai daftar bernomor.",
            "platform": f"Berdasarkan data keterlibatan per platform ini: {data_json}, berikan 3 wawasan yang dapat ditindaklanjuti. Identifikasi platform 'juara' dan 'peluang'. Format sebagai daftar bernomor.",
            "mediaType": f"Berdasarkan data bauran jenis media ini: {data_json}, berikan 3 wawasan strategis. Analisis preferensi audiens berdasarkan format konten. Format sebagai daftar bernomor.",
            "location": f"Berdasarkan data keterlibatan per lokasi ini: {data_json}, berikan 3 wawasan geo-strategis. Identifikasi pasar utama dan pasar yang sedang berkembang. Format sebagai daftar bernomor."
        }
        return f"Anda adalah seorang konsultan intelijen media profesional. {prompts.get(key, '')}"

    for chart in charts_to_display:
        with chart["col"]:
            st.markdown(f'<div class="chart-container" key="chart-{chart["key"]}">', unsafe_allow_html=True)
            st.markdown(f'<h3>{chart["title"]}</h3>', unsafe_allow_html=True)
            
            fig = None
            chart_data_for_prompt = None

            if chart["key"] == "sentiment":
                sentiment_data = filtered_df['Sentiment'].value_counts().reset_index()
                sentiment_data.columns = ['Sentiment', 'count']
                if not sentiment_data.empty:
                    fig = px.pie(sentiment_data, names='Sentiment', values='count', color_discrete_sequence=px.colors.qualitative.Pastel)
                chart_data_for_prompt = sentiment_data.to_json()

            elif chart["key"] == "trend":
                # Pastikan 'Date' adalah kolom datetime sebelum mengelompokkan
                engagement_trend_chart = filtered_df.groupby(filtered_df['Date'].dt.date)['Engagements'].sum().reset_index()
                engagement_trend_chart['Date'] = pd.to_datetime(engagement_trend_chart['Date']) # Pastikan tipe data datetime untuk plotting
                if not engagement_trend_chart.empty:
                    fig = px.line(engagement_trend_chart, x='Date', y='Engagements', labels={'Date': 'Tanggal', 'Engagements': 'Total Keterlibatan'})
                    fig.update_traces(line=dict(color='#06B6D4', width=3))
                chart_data_for_prompt = engagement_trend_chart.tail(10).to_json() # Ambil 10 data terakhir untuk prompt
                
            elif chart["key"] == "platform":
                platform_data = filtered_df.groupby('Platform')['Engagements'].sum().sort_values(ascending=False).reset_index()
                if not platform_data.empty:
                    fig = px.bar(platform_data, x='Platform', y='Engagements', color='Platform')
                chart_data_for_prompt = platform_data.to_json()

            elif chart["key"] == "mediaType":
                media_type_data = filtered_df['Media Type'].value_counts().reset_index()
                media_type_data.columns = ['Media Type', 'count']
                if not media_type_data.empty:
                    fig = px.pie(media_type_data, names='Media Type', values='count', hole=.3)
                chart_data_for_prompt = media_type_data.to_json()

            elif chart["key"] == "location":
                location_data = filtered_df.groupby('Location')['Engagements'].sum().nlargest(5).reset_index()
                if not location_data.empty:
                    fig = px.bar(location_data, y='Location', x='Engagements', orientation='h', color='Location')
                chart_data_for_prompt = location_data.to_json()
            
            if fig: # Hanya tampilkan grafik jika ada data untuk dibuat
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#cbd5e1',
                    legend_title_text=''
                )
                st.plotly_chart(fig, use_container_width=True)

                # Tombol untuk membuat wawasan AI untuk setiap grafik
                if st.button(f"✨ Buat Wawasan AI", key=f"insight_btn_{chart['key']}"): # Hapus `and api_configured`
                    with st.spinner(f"Menganalisis {chart['title']}..."):
                        if chart_data_for_prompt: # Pastikan ada data untuk prompt
                            prompt = get_chart_prompt(chart['key'], chart_data_for_prompt)
                            insight = get_ai_insight(prompt)
                            st.session_state.chart_insights[chart['key']] = insight
                        else:
                            st.session_state.chart_insights[chart['key']] = "Tidak ada data yang cukup untuk menghasilkan wawasan."
                
                insight_text = st.session_state.chart_insights.get(chart['key'], "")
                if insight_text:
                    st.markdown(f'<div class="insight-box">{insight_text}</div>', unsafe_allow_html=True)
            else:
                st.write("Tidak ada data yang tersedia untuk grafik ini dengan filter yang dipilih.")
                # Tombol tetap ada meskipun tidak ada grafik, agar pengguna bisa mencoba menghasilkan wawasan
                if st.button(f"✨ Buat Wawasan AI", key=f"insight_btn_{chart['key']}_no_chart"):
                    st.session_state.chart_insights[chart['key']] = "Tidak ada data yang cukup untuk menghasilkan wawasan."
                insight_text = st.session_state.chart_insights.get(chart['key'], "")
                if insight_text:
                    st.markdown(f'<div class="insight-box">{insight_text}</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

