import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai
import io

# --- KONFIGURASI HALAMAN & GAYA ---
# Mengatur konfigurasi halaman. Ini harus menjadi perintah pertama Streamlit.
st.set_page_config(
    page_title="Media Intelligence Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- FUNGSI UTAMA & LOGIKA ---

# --- Gemini API Call Function ---
def generate_campaign_summary_llm(prompt):
    """
    Calls the Gemini API to generate a campaign summary based on the provided prompt.
    """
    # YOUR API KEY IS NOW HARDCODED HERE
    api_key = "AIzaSyC0VUu6xTFIwH3aP2R7tbhyu4O8m1ICxn4" 

    if not api_key: # Added check for empty API key
        st.error("API Key tidak ditemukan. Pastikan API Key diatur dengan benar di lingkungan Canvas.")
        return "Gagal membuat ringkasan: API Key tidak diatur."

    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

    chat_history = [{"role": "user", "parts": [{"text": prompt}]}]
    payload = {"contents": chat_history}

    try:
        response = requests.post(api_url, headers={'Content-Type': 'application/json'}, json=payload)
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        result = response.json()

        if result.get('candidates') and len(result['candidates']) > 0 and \
           result['candidates'][0].get('content') and result['candidates'][0]['content'].get('parts') and \
           len(result['candidates'][0]['content']['parts']) > 0:
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            st.error("Gemini API response structure unexpected.")
            return "Gagal membuat ringkasan. Silakan coba lagi."
    except requests.exceptions.RequestException as e:
        st.error(f"Error calling Gemini API: {e}. Please ensure you have internet connectivity and a valid API key.")
        return "Error membuat ringkasan: Terjadi masalah koneksi atau API."
    except Exception as e:
        st.error(f"An unexpected error occurred during summary generation: {e}")
        return "Error membuat ringkasan: Terjadi kesalahan tak terduga."

# Fungsi untuk memuat dan menerapkan CSS kustom untuk meniru UI/UX React
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

# Fungsi untuk parsing CSV, diadaptasi untuk pandas
@st.cache_data
def parse_csv(uploaded_file):
    """Membaca file CSV yang diunggah ke dalam DataFrame pandas dan membersihkannya."""
    try:
        # Menggunakan io.StringIO untuk membaca file di memori
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
api_configured = configure_gemini_api()

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
                st.rerun() # Muat ulang aplikasi setelah data diunggah
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
        filtered_df = filtered_df[filtered_df['Sentiment'] == sentiment]
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
        if st.button("Buat Ringkasan", key="summary_btn", use_container_width=True) and api_configured:
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
        if st.button("✨ Buat Ide Postingan", key="idea_btn", use_container_width=True) and api_configured:
            with st.spinner("Mencari ide terbaik..."):
                best_platform = filtered_df.groupby('Platform')['Engagements'].sum().idxmax()
                top_posts = filtered_df[filtered_df['Platform'] == best_platform].nlargest(5, 'Engagements')

                prompt = f"""
                Anda adalah seorang ahli strategi media sosial yang kreatif. Berdasarkan data berikut, buatlah satu contoh postingan untuk platform **{best_platform}**.
                - Platform Berkinerja Terbaik: {best_platform}
                - Topik Berkinerja Tinggi (dari judul): {', '.join(top_posts['Headline'].tolist())}
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
    if len(engagement_trend) > 7:
        mean = engagement_trend['Engagements'].mean()
        std = engagement_trend['Engagements'].std()
        anomaly_threshold = mean + (2 * std)
        anomalies = engagement_trend[engagement_trend['Engagements'] > anomaly_threshold]
        
        if not anomalies.empty:
            anomaly = anomalies.iloc[0]
            st.markdown('<div class="anomaly-card">', unsafe_allow_html=True)
            st.markdown("<h3>⚠️ Peringatan Anomali Terdeteksi!</h3>", unsafe_allow_html=True)
            st.write(f"Kami mendeteksi lonjakan keterlibatan yang tidak biasa pada **{anomaly['Date']}** dengan **{int(anomaly['Engagements']):,}** keterlibatan (rata-rata: {int(mean):,}).")
            
            if st.button("✨ Jelaskan Anomali Ini", key="anomaly_btn") and api_configured:
                 with st.spinner("Menganalisis penyebab anomali..."):
                    prompt = f"""
                    Anda adalah seorang analis data intelijen media. Terdeteksi anomali keterlibatan pada {anomaly['Date']}.
                    - Keterlibatan pada hari itu: {anomaly['Engagements']}
                    - Rata-rata keterlibatan: {mean:.2f}
                    - Judul berita teratas pada hari itu (jika ada): {', '.join(filtered_df[filtered_df['Date'].dt.date == anomaly['Date']].nlargest(3, 'Engagements')['Headline'].tolist())}
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
        {"key": "mediaType", "title": "Kombinasi Jenis Media", "col": chart_cols[1]},
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
                fig = px.pie(sentiment_data, names='Sentiment', values='count', color_discrete_sequence=px.colors.qualitative.Pastel)
                chart_data_for_prompt = sentiment_data.to_json()

            elif chart["key"] == "trend":
                fig = px.line(engagement_trend, x='Date', y='Engagements', labels={'Date': 'Tanggal', 'Engagements': 'Total Keterlibatan'})
                fig.update_traces(line=dict(color='#06B6D4', width=3))
                chart_data_for_prompt = engagement_trend.tail(10).to_json()
            
            elif chart["key"] == "platform":
                platform_data = filtered_df.groupby('Platform')['Engagements'].sum().sort_values(ascending=False).reset_index()
                fig = px.bar(platform_data, x='Platform', y='Engagements', color='Platform')
                chart_data_for_prompt = platform_data.to_json()

            elif chart["key"] == "mediaType":
                media_type_data = filtered_df['Media Type'].value_counts().reset_index()
                media_type_data.columns = ['Media Type', 'count']
                fig = px.pie(media_type_data, names='Media Type', values='count', hole=.3)
                chart_data_for_prompt = media_type_data.to_json()

            elif chart["key"] == "location":
                location_data = filtered_df.groupby('Location')['Engagements'].sum().nlargest(5).reset_index()
                fig = px.bar(location_data, y='Location', x='Engagements', orientation='h', color='Location')
                chart_data_for_prompt = location_data.to_json()
            
            if fig:
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#cbd5e1',
                    legend_title_text=''
                )
                st.plotly_chart(fig, use_container_width=True)

                if st.button(f"✨ Buat Wawasan AI", key=f"insight_btn_{chart['key']}") and api_configured:
                    with st.spinner(f"Menganalisis {chart['title']}..."):
                        prompt = get_chart_prompt(chart['key'], chart_data_for_prompt)
                        insight = get_ai_insight(prompt)
                        st.session_state.chart_insights[chart['key']] = insight
                
                insight_text = st.session_state.chart_insights.get(chart['key'], "")
                if insight_text:
                    st.markdown(f'<div class="insight-box">{insight_text}</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

