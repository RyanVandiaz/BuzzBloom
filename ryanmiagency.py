import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
from io import StringIO
import textwrap

# --- KONFIGURASI HALAMAN DAN GAYA ---
# Setel konfigurasi halaman Streamlit. Harus menjadi perintah pertama yang dijalankan.
st.set_page_config(
    page_title="Media Intelligence Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Fungsi untuk memuat gaya kustom CSS untuk meniru tema gelap modern dari aplikasi React
def load_css():
    st.markdown("""
        <style>
            /* Tema gelap dasar */
            html, body, [class*="st-"] {
                background-color: #0f172a; /* slate-900 */
                color: #cbd5e1; /* slate-300 */
            }
            .st-emotion-cache-16txtl3 {
                padding-top: 2rem;
            }
            .st-emotion-cache-1y4p8pa {
                padding-top: 2rem;
                max-width: none;
            }
            /* Header */
            h1, h2, h3 {
                font-family: 'Orbitron', sans-serif;
                color: #e2e8f0; /* slate-200 */
            }
            h1 {
                background: -webkit-linear-gradient(45deg, #06B6D4, #6366F1);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-weight: 900;
            }
            h2 {
                color: #5eead4; /* teal-300 */
            }
            /* Sidebar */
            .st-emotion-cache-6q9sum {
                background-color: rgba(30, 41, 59, 0.4); /* slate-800/40 */
                backdrop-filter: blur(10px);
                border: 1px solid #475569; /* slate-700 */
            }
            /* Kontainer utama */
            .st-emotion-cache-z5fcl4 {
                 background-color: rgba(51, 65, 85, 0.5); /* slate-700/50 */
                 border: 1px solid #64748b; /* slate-600 */
                 border-radius: 1rem;
                 padding: 2rem;
                 margin-bottom: 2rem;
            }
            /* Tombol */
            .stButton>button {
                border-radius: 0.5rem;
                padding: 0.5rem 1rem;
                font-weight: bold;
                border: none;
                color: white;
                transition: all 0.2s ease-in-out;
            }
            /* Kotak wawasan (insights) AI */
            .insight-box {
                background-color: rgba(15, 23, 42, 0.7); /* slate-900/70 */
                border: 1px solid #334155; /* slate-700 */
                border-radius: 0.5rem;
                padding: 1.5rem;
                margin-top: 1rem;
                min-height: 150px;
                color: #cbd5e1; /* slate-300 */
            }
            .insight-box h4 {
                 color: #5eead4; /* teal-300 */
                 margin-bottom: 0.5rem;
            }
            /* Pesan "Tidak ada data" */
            .no-data {
                display: flex;
                align-items: center;
                justify-content: center;
                height: 350px;
                color: #94a3b8; /* slate-400 */
            }
        </style>
        <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400..900&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

# --- FUNGSI API GEMINI ---
# Fungsi untuk menginisialisasi dan memanggil model AI Gemini
def get_ai_insight(prompt):
    """Mengirim prompt ke Gemini dan mengembalikan respons teksnya."""
    try:
        # Kunci API diharapkan ada di Streamlit Secrets
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(prompt)
        # Menggunakan textwrap untuk memformat teks dengan lebih baik
        return textwrap.fill(response.text, width=120)
    except Exception as e:
        st.error(f"Error saat menghubungi Gemini AI: {e}")
        return None

# --- FUNGSI PEMROSESAN DATA ---
# Menggunakan cache untuk menghindari pemrosesan ulang file yang sama
@st.cache_data
def load_and_clean_data(uploaded_file):
    """Memuat dan membersihkan data dari file CSV yang diunggah."""
    if uploaded_file is None:
        return None
    try:
        # Membaca file yang diunggah sebagai string
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        df = pd.read_csv(stringio)
        
        # Membersihkan nama kolom dari spasi yang tidak diinginkan
        df.columns = df.columns.str.strip()
        
        # Memeriksa kolom yang diperlukan
        required_columns = {'Date', 'Engagements', 'Sentiment', 'Platform', 'Media Type', 'Location'}
        if not required_columns.issubset(df.columns):
            st.error(f"File CSV harus memiliki kolom: {', '.join(required_columns)}")
            return None

        # Membersihkan dan mengubah tipe data
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Engagements'] = pd.to_numeric(df['Engagements'], errors='coerce').fillna(0).astype(int)
        df.dropna(subset=['Date'], inplace=True)
        return df
    except Exception as e:
        st.error(f"Error saat memproses file CSV: {e}")
        return None

# --- FUNGSI-FUNGSI GRAFIK PLOTLY ---
# Skema warna yang modern
COLORS = ['#06B6D4', '#6366F1', '#EC4899', '#8B5CF6', '#F59E0B', '#10B981', '#3B82F6', '#EF4444']
TEMPLATE = "plotly_dark"

def create_pie_chart(df, column, title):
    data = df[column].value_counts().reset_index()
    data.columns = [column, 'count']
    fig = px.pie(data, names=column, values='count', title=title,
                 color_discrete_sequence=COLORS, hole=0.3)
    fig.update_layout(template=TEMPLATE, legend_title_text=column)
    return fig

def create_line_chart(df, title):
    df['DateOnly'] = df['Date'].dt.date
    trend_data = df.groupby('DateOnly')['Engagements'].sum().reset_index()
    fig = px.line(trend_data, x='DateOnly', y='Engagements', title=title,
                  labels={'DateOnly': 'Tanggal', 'Engagements': 'Total Keterlibatan'})
    fig.update_traces(line=dict(color=COLORS[0], width=2))
    fig.update_layout(template=TEMPLATE)
    return fig

def create_bar_chart(df, group_col, value_col, title, orientation='v'):
    data = df.groupby(group_col)[value_col].sum().reset_index().sort_values(by=value_col, ascending=False)
    if orientation == 'h':
        data = data.head(10).sort_values(by=value_col, ascending=True) # Urutkan untuk bar horizontal
    
    fig = px.bar(data, x=group_col if orientation == 'v' else value_col, 
                 y=value_col if orientation == 'v' else group_col, 
                 title=title, color_discrete_sequence=COLORS,
                 orientation=orientation,
                 labels={group_col: group_col.replace('_', ' '), value_col: 'Total Keterlibatan'})
    fig.update_layout(template=TEMPLATE)
    return fig

# --- UTAMA ---
def main():
    load_css()
    
    st.markdown("<h2 style='text-align: center; color: #94a3b8; font-family: Orbitron, sans-serif;'>RYAN MEDIA AGENCY</h2>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center;'>Media Intelligence Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("---")

    # Inisialisasi session state
    if 'insights' not in st.session_state:
        st.session_state.insights = {}
    
    # --- PENGUNGGAH FILE DI SIDEBAR ---
    st.sidebar.header("📤 Unggah Data")
    uploaded_file = st.sidebar.file_uploader(
        "Unggah file CSV Anda",
        type=['csv'],
        help="Pastikan file CSV memiliki kolom 'Date', 'Engagements', 'Sentiment', 'Platform', 'Media Type', dan 'Location'."
    )
    
    if uploaded_file is None:
        st.info("💡 Silakan unggah file CSV melalui sidebar untuk memulai analisis.")
        return

    # --- PEMROSESAN DATA ---
    original_df = load_and_clean_data(uploaded_file)
    if original_df is None:
        return # Hentikan jika data tidak valid

    # --- FILTER DI SIDEBAR ---
    st.sidebar.header("🔍 Filter Data")
    platform = st.sidebar.selectbox('Platform', ['All'] + sorted(original_df['Platform'].unique().tolist()))
    sentiment = st.sidebar.selectbox('Sentiment', ['All'] + sorted(original_df['Sentiment'].unique().tolist()))
    media_type = st.sidebar.selectbox('Media Type', ['All'] + sorted(original_df['Media Type'].unique().tolist()))
    location = st.sidebar.selectbox('Location', ['All'] + sorted(original_df['Location'].unique().tolist()))
    
    min_date = original_df['Date'].min().date()
    max_date = original_df['Date'].max().date()
    date_range = st.sidebar.date_input('Rentang Tanggal', [min_date, max_date], min_value=min_date, max_value=max_date)
    
    # Terapkan filter
    filtered_df = original_df.copy()
    if platform != 'All': filtered_df = filtered_df[filtered_df['Platform'] == platform]
    if sentiment != 'All': filtered_df = filtered_df[filtered_df['Sentiment'] == sentiment]
    if media_type != 'All': filtered_df = filtered_df[filtered_df['Media Type'] == media_type]
    if location != 'All': filtered_df = filtered_df[filtered_df['Location'] == location]
    if len(date_range) == 2:
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        filtered_df = filtered_df[(filtered_df['Date'] >= start_date) & (filtered_df['Date'] <= end_date)]

    if filtered_df.empty:
        st.warning("Tidak ada data yang cocok dengan filter yang dipilih.")
        return

    # --- TATA LETAK DASBOR ---
    
    # 1. Ringkasan Kampanye
    with st.container():
        st.header("✨ Ringkasan Strategi Kampanye")
        if st.button("Buat Ringkasan Strategi", key="summary_btn"):
            with st.spinner("Membuat ringkasan dengan Gemini AI..."):
                # Mengumpulkan semua wawasan yang sudah ada
                existing_insights = "\n".join([f"- {key.capitalize()} Insight: {val}" for key, val in st.session_state.insights.items() if val])
                prompt = f"""
                Anda adalah seorang konsultan strategi media. Berdasarkan wawasan berikut, tulis ringkasan eksekutif singkat (3-4 kalimat) dan 3 rekomendasi strategis utama. Jika tidak ada wawasan, nyatakan demikian.
                Data wawasan:
                {existing_insights if existing_insights else "Belum ada wawasan yang dibuat."}
                Fokus pada gambaran besar dan langkah selanjutnya yang paling berdampak.
                """
                summary = get_ai_insight(prompt)
                st.session_state.insights['summary'] = summary
        
        st.markdown(f"<div class='insight-box'><h4>Insight by Gemini AI:</h4><p>{st.session_state.insights.get('summary', 'Klik tombol untuk membuat ringkasan.')}</p></div>", unsafe_allow_html=True)
    
    st.markdown("---")

    # 2. Visualisasi Detail
    col1, col2 = st.columns(2)

    chart_definitions = [
        {'key': 'sentiment', 'col': col1, 'type': 'pie', 'column': 'Sentiment', 'title': 'Distribusi Sentimen'},
        {'key': 'media_type', 'col': col2, 'type': 'pie', 'column': 'Media Type', 'title': 'Kombinasi Jenis Media'},
        {'key': 'trend', 'col': col1, 'type': 'line', 'title': 'Tren Keterlibatan Harian'},
        {'key': 'platform', 'col': col2, 'type': 'bar_v', 'group_col': 'Platform', 'value_col': 'Engagements', 'title': 'Keterlibatan per Platform'},
        {'key': 'location', 'col': col1, 'type': 'bar_h', 'group_col': 'Location', 'value_col': 'Engagements', 'title': '10 Lokasi Teratas berdasarkan Keterlibatan'},
    ]

    for chart in chart_definitions:
        with chart['col'], st.container(border=True):
            if filtered_df.empty:
                 st.markdown("<div class='no-data'>Tidak ada data.</div>", unsafe_allow_html=True)
            elif chart['type'] == 'pie':
                fig = create_pie_chart(filtered_df, chart['column'], chart['title'])
                st.plotly_chart(fig, use_container_width=True)
            elif chart['type'] == 'line':
                fig = create_line_chart(filtered_df, chart['title'])
                st.plotly_chart(fig, use_container_width=True)
            elif chart['type'] == 'bar_v':
                fig = create_bar_chart(filtered_df, chart['group_col'], chart['value_col'], chart['title'])
                st.plotly_chart(fig, use_container_width=True)
            elif chart['type'] == 'bar_h':
                fig = create_bar_chart(filtered_df, chart['group_col'], chart['value_col'], chart['title'], orientation='h')
                st.plotly_chart(fig, use_container_width=True)

            # Tombol dan kotak wawasan AI untuk setiap grafik
            if st.button(f"🧠 Buat Wawasan AI untuk {chart['title']}", key=f"btn_{chart['key']}"):
                with st.spinner(f"Menganalisis {chart['title']}..."):
                    data_subset_json = filtered_df.head(50).to_json(orient='records', date_format='iso')
                    prompt = f"""
                    Anda adalah seorang konsultan intelijen media profesional. Berdasarkan cuplikan data berikut: {data_subset_json},
                    khususnya dengan fokus pada {chart['title']}, berikan 3 wawasan (insights) yang tajam dan dapat ditindaklanjuti untuk strategi komunikasi merek.
                    Fokus pada implikasi strategis dari data ini, bukan hanya deskripsi data. Format sebagai daftar bernomor.
                    """
                    insight = get_ai_insight(prompt)
                    st.session_state.insights[chart['key']] = insight
            
            if chart['key'] in st.session_state.insights:
                st.markdown(f"<div class='insight-box'><h4>Insight by Gemini AI:</h4><p>{st.session_state.insights[chart['key']]}</p></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
