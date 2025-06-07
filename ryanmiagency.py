# app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import json

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Media Intelligence Dashboard",
    page_icon="🧠",
    layout="wide",
)

# --- FUNGSI BANTUAN ---

def get_gemini_insights(prompt_text, api_key):
    """
    Mengirimkan prompt ke Google Gemini API dan mengembalikan responsnya.
    """
    if not api_key:
        return "Kunci API Gemini tidak diberikan. Masukkan kunci API Anda di bilah sisi untuk mengaktifkan wawasan AI."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        full_prompt = (
            "You are an expert media analyst. Your task is to provide three brief, actionable, and insightful bullet points "
            "based on the data summary provided. Focus on strategic recommendations.\n\n"
            "Data Summary:\n"
            f"{prompt_text}"
        )

        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Terjadi kesalahan saat menghubungi Gemini API: {e}"

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
st.sidebar.header("Pengaturan")
st.sidebar.subheader("Pengaturan AI")
gemini_api_key = st.sidebar.text_input("Masukkan Kunci API Google Gemini Anda", type="password", help="Diperlukan untuk menghasilkan wawasan otomatis.")

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

                with st.expander("🤖 AI Insights (Gemini API)"):
                    with st.spinner("Menganalisis sentimen..."):
                        prompt = f"Chart: Sentiment Distribution.\nData: {sentiment_counts.to_json(orient='split')}"
                        st.markdown(get_gemini_insights(prompt, gemini_api_key))

            with col_chart2:
                st.subheader("Tren Keterlibatan dari Waktu ke Waktu")
                engagement_trend = df_filtered.groupby(df_filtered['Date'].dt.to_period('D'))['Engagements'].sum().reset_index()
                engagement_trend['Date'] = engagement_trend['Date'].dt.to_timestamp()
                fig_trend = px.line(engagement_trend, x='Date', y='Engagements', markers=True)
                fig_trend.update_traces(line=dict(color='#39FF14'))
                fig_trend.update_layout(template="plotly_dark", xaxis_title='Tanggal', yaxis_title='Total Keterlibatan')
                st.plotly_chart(fig_trend, use_container_width=True)

                with st.expander("🤖 AI Insights (Gemini API)"):
                     with st.spinner("Menganalisis tren..."):
                        prompt = f"Chart: Engagement Trend Over Time.\nData: {engagement_trend.to_json(orient='split')}"
                        st.markdown(get_gemini_insights(prompt, gemini_api_key))
            
            st.markdown("<br>", unsafe_allow_html=True)
            col_chart3, col_chart4 = st.columns(2)

            with col_chart3:
                st.subheader("Keterlibatan per Platform")
                platform_engagement = df_filtered.groupby('Platform')['Engagements'].sum().sort_values(ascending=False).reset_index()
                fig_platform = px.bar(platform_engagement, x='Platform', y='Engagements', color='Platform', color_discrete_sequence=px.colors.qualitative.Pastel)
                fig_platform.update_layout(template="plotly_dark", showlegend=False)
                st.plotly_chart(fig_platform, use_container_width=True)

                with st.expander("🤖 AI Insights (Gemini API)"):
                    with st.spinner("Menganalisis platform..."):
                        prompt = f"Chart: Platform Engagements.\nData: {platform_engagement.to_json(orient='split')}"
                        st.markdown(get_gemini_insights(prompt, gemini_api_key))

            with col_chart4:
                st.subheader("Distribusi Jenis Media")
                media_type_counts = df_filtered['Media_Type'].value_counts().reset_index()
                fig_media = px.pie(media_type_counts, names='Media_Type', values='count', hole=.3, color_discrete_sequence=px.colors.sequential.Aggrnyl)
                fig_media.update_layout(template="plotly_dark", legend_title_text='Jenis Media')
                st.plotly_chart(fig_media, use_container_width=True)

                with st.expander("🤖 AI Insights (Gemini API)"):
                    with st.spinner("Menganalisis jenis media..."):
                        prompt = f"Chart: Media Type Mix.\nData: {media_type_counts.to_json(orient='split')}"
                        st.markdown(get_gemini_insights(prompt, gemini_api_key))

            st.markdown("<br>", unsafe_allow_html=True)
            col_chart5, col_chart6 = st.columns(2)
            
            with col_chart5:
                st.subheader("5 Lokasi Teratas")
                top_locations = df_filtered.groupby('Location')['Engagements'].sum().nlargest(5).sort_values(ascending=True).reset_index()
                fig_location = px.bar(top_locations, y='Location', x='Engagements', orientation='h', color='Engagements', color_continuous_scale='Greens')
                fig_location.update_layout(template="plotly_dark", yaxis_title='Lokasi')
                st.plotly_chart(fig_location, use_container_width=True)

                with st.expander("🤖 AI Insights (Gemini API)"):
                    with st.spinner("Menganalisis lokasi..."):
                        prompt = f"Chart: Top 5 Locations by Engagement.\nData: {top_locations.to_json(orient='split')}"
                        st.markdown(get_gemini_insights(prompt, gemini_api_key))
            
            with col_chart6:
                st.subheader("5 Influencer/Brand Teratas")
                top_influencers = df_filtered.groupby('Influencer_Brand')['Engagements'].sum().nlargest(5).sort_values(ascending=True).reset_index()
                fig_influencer = px.bar(top_influencers, y='Influencer_Brand', x='Engagements', orientation='h', color='Engagements', color_continuous_scale='Purples')
                fig_influencer.update_layout(template="plotly_dark", yaxis_title='Influencer / Brand')
                st.plotly_chart(fig_influencer, use_container_width=True)

                with st.expander("🤖 AI Insights (Gemini API)"):
                    with st.spinner("Menganalisis influencer..."):
                        prompt = f"Chart: Top 5 Influencers/Brands by Engagement.\nData: {top_influencers.to_json(orient='split')}"
                        st.markdown(get_gemini_insights(prompt, gemini_api_key))

            # --- FITUR STRATEGI LANJUTAN ---
            st.markdown("---")
            st.header("🧠 Analisis & Rekomendasi Strategi")
            if st.button("Hasilkan Ringkasan Strategi Kampanye", key="generate_summary"):
                if gemini_api_key:
                    with st.spinner("AI sedang menyusun ringkasan strategi... Ini mungkin memakan waktu sebentar."):
                        summary_data = df_filtered.sample(min(100, len(df_filtered))).to_dict(orient='records')
                        
                        strategy_prompt = f"""
                        You are a world-class digital media strategist. Based on the following data summary from a media campaign, create a comprehensive strategy report.
                        Structure your response in markdown with clear headings.

                        Address the following key areas:
                        1.  **Overall Performance Summary:** What are the general sentiment and engagement trends?
                        2.  **Platform Focus:** Which platforms should be the main focus and why? Recommend budget/effort allocation percentages.
                        3.  **Content & Creative Recommendations:** What media types (Video, Image, etc.) and content topics are resonating most with the audience? Suggest specific creative ideas.
                        4.  **Audience Targeting:** Which locations and influencers/brands should be prioritized? How can they be leveraged?
                        5.  **Opportunities for Improvement:** What areas are underperforming and what specific actions can be taken to fix them?

                        Data Sample:
                        {json.dumps(summary_data, indent=2)}
                        """
                        
                        strategy_summary = get_gemini_insights(strategy_prompt, gemini_api_key)
                        st.markdown(strategy_summary)
                else:
                    st.error("Harap masukkan Kunci API Google Gemini Anda di bilah sisi untuk menggunakan fitur canggih ini.")
