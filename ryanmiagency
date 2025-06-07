import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Social Pulse Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- FUNGSI BANTU & SIMULASI AI ---

def generate_insight(chart_title: str, filtered_df: pd.DataFrame):
    """
    Simulasi fungsi AI untuk menghasilkan insight dari data.
    Dalam aplikasi nyata, ini akan memanggil model LLM.
    """
    insights = {
        "Sentiment Breakdown": [
            "**Dominasi Sentimen Positif:** Sebagian besar percakapan (lebih dari 50%) memiliki sentimen positif, menandakan citra merek yang kuat.",
            "**Sentimen Negatif Terkendali:** Sentimen negatif berada di bawah 20%, namun perlu dianalisis lebih lanjut untuk mengidentifikasi keluhan spesifik.",
            "**Peluang di Sentimen Netral:** Sentimen netral cukup signifikan, ini adalah audiens yang bisa digiring menjadi positif melalui kampanye yang tepat."
        ],
        "Engagement Trend over Time": [
            "**Pola Pertumbuhan Stabil:** Terlihat tren kenaikan engagement yang konsisten dari waktu ke waktu, menunjukkan strategi konten berjalan baik.",
            "**Identifikasi Puncak Engagement:** Terdapat lonjakan engagement pada tanggal tertentu, yang kemungkinan besar berkorelasi dengan event atau postingan viral.",
            "**Analisis Penurunan:** Perhatikan periode di mana engagement menurun; ini bisa menjadi indikasi kelelahan audiens atau konten yang kurang relevan."
        ],
        "Platform Engagements": [
            "**Instagram Memimpin:** Instagram adalah platform dengan engagement tertinggi, jadikan sebagai fokus utama alokasi sumber daya.",
            "**Facebook Sebagai Penopang:** Facebook menunjukkan engagement yang solid dan stabil, efektif untuk menjangkau demografi yang lebih luas.",
            "**Potensi di TikTok:** Meskipun engagement lebih rendah, TikTok memiliki potensi pertumbuhan viral yang cepat jika kontennya sesuai tren."
        ],
        "Media Type Mix": [
            "**Video Paling Menarik:** Konten video menghasilkan engagement paling tinggi, menandakan preferensi audiens terhadap format visual dinamis.",
            "**Gambar Tetap Relevan:** Gambar masih menjadi format yang kuat, terutama di platform visual seperti Instagram.",
            "**Teks Perlu Diperkuat:** Engagement pada postingan teks murni cenderung rendah; kombinasikan dengan visual untuk meningkatkan daya tarik."
        ],
        "Top 5 Locations by Engagement": [
            "**Jakarta Pusat Kekuatan:** Jakarta menjadi basis audiens paling aktif, penting untuk konten yang relevan dengan tren dan event lokal di sana.",
            "**Pasar Surabaya Berkembang:** Surabaya menunjukkan engagement yang kuat, menjadikannya target ekspansi kampanye regional yang menjanjikan.",
            "**Kehadiran Kuat di Kota Besar:** Dominasi kota-kota besar lainnya seperti Bandung dan Medan mengkonfirmasi bahwa fokus strategi harus tetap di area urban."
        ]
    }
    return insights.get(chart_title, ["Insight tidak tersedia."])

def generate_key_action_summary(filtered_df: pd.DataFrame):
    """Simulasi AI untuk ringkasan strategi kampanye."""
    if filtered_df.empty:
        return "Tidak ada data untuk dianalisis."
        
    top_platform = filtered_df.groupby('Platform')['Engagements'].sum().idxmax()
    top_media_type = filtered_df.groupby('Media Type')['Engagements'].sum().idxmax()
    dominant_sentiment = filtered_df['Sentiment'].value_counts().idxmax()

    summary = f"""
    ### Ringkasan Strategi Kampanye (Key Action Summary)
    Berdasarkan data yang dianalisis, berikut adalah rekomendasi tindakan utama:
    
    1.  **Fokuskan Sumber Daya pada {top_platform}:** Platform ini secara konsisten memberikan engagement tertinggi. Prioritaskan pembuatan konten orisinal dan alokasi budget iklan di sini.
    2.  **Optimalkan Konten Berbasis {top_media_type}:** Audiens paling merespons format {top_media_type}. Tingkatkan produksi konten jenis ini dengan kualitas yang lebih baik dan narasi yang menarik.
    3.  **Manfaatkan Sentimen {dominant_sentiment}:** Dengan mayoritas sentimen bersifat **{dominant_sentiment}**, gunakan testimoni positif dalam materi pemasaran. Untuk sentimen negatif, segera tangani dengan respons yang solutif.
    4.  **Targetkan Ulang Kampanye di Lokasi Unggulan:** Perkuat kampanye di kota-kota dengan engagement teratas seperti Jakarta dan Surabaya melalui konten yang dilokalisasi.
    """
    return summary

def answer_natural_language_query(query: str, df: pd.DataFrame):
    """Simulasi AI untuk menjawab pertanyaan bahasa alami."""
    query = query.lower()
    if "engagement tertinggi" in query:
        if "platform" in query:
            top_platform = df.groupby('Platform')['Engagements'].sum().idxmax()
            total_engagement = df.groupby('Platform')['Engagements'].sum().max()
            return f"Platform dengan engagement tertinggi adalah **{top_platform}** dengan total **{int(total_engagement)}** engagements."
        elif "tanggal" in query:
            top_date = df.groupby('Date')['Engagements'].sum().idxmax().strftime('%d %B %Y')
            total_engagement = df.groupby('Date')['Engagements'].sum().max()
            return f"Tanggal dengan engagement tertinggi adalah **{top_date}** dengan total **{int(total_engagement)}** engagements."
    elif "sentimen" in query and "negatif" in query:
        negative_count = df[df['Sentiment'] == 'Negative'].shape[0]
        return f"Terdapat **{negative_count}** postingan dengan sentimen negatif."
    else:
        return "Maaf, saya belum bisa menjawab pertanyaan tersebut. Coba pertanyaan lain seperti 'Platform apa dengan engagement tertinggi?'"

# --- MEMBUAT DATA CONTOH ---
@st.cache_data
def load_data():
    """Membuat DataFrame contoh untuk simulasi."""
    np.random.seed(42)
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(365)]
    data = {
        'Date': np.random.choice(dates, 500),
        'Platform': np.random.choice(['Instagram', 'Facebook', 'TikTok', 'Twitter'], 500, p=[0.4, 0.3, 0.2, 0.1]),
        'Engagements': np.random.randint(50, 2000, 500),
        'Sentiment': np.random.choice(['Positive', 'Negative', 'Neutral'], 500, p=[0.6, 0.15, 0.25]),
        'Media Type': np.random.choice(['Video', 'Image', 'Text', 'Carousel'], 500, p=[0.4, 0.35, 0.1, 0.15]),
        'Location': np.random.choice(['Jakarta', 'Surabaya', 'Bandung', 'Medan', 'Makassar', 'Lainnya'], 500, p=[0.3, 0.2, 0.15, 0.1, 0.1, 0.15])
    }
    df = pd.DataFrame(data)
    
    # Menambahkan beberapa nilai kosong untuk simulasi cleaning
    df.loc[df.sample(frac=0.05).index, 'Engagements'] = np.nan
    
    return df

df_original = load_data()

# --- PROSES DATA CLEANING ---
df = df_original.copy()
# 1. Konversi kolom Date ke format datetime
df['Date'] = pd.to_datetime(df['Date'])
# 2. Isi nilai Engagements yang kosong dengan 0
df['Engagements'] = df['Engagements'].fillna(0).astype(int)


# --- SIDEBAR & FILTER ---
st.sidebar.title("🚀 Social Pulse Team")
st.sidebar.markdown("**Kelompok 7**")
st.sidebar.header("Filter Interaktif")

# Filter Rentang Tanggal
min_date = df['Date'].min().date()
max_date = df['Date'].max().date()
date_range = st.sidebar.date_input(
    "Pilih Rentang Tanggal",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

start_date, end_date = date_range

# Filter lainnya
platforms = st.sidebar.multiselect("Pilih Platform", options=df['Platform'].unique(), default=df['Platform'].unique())
sentiments = st.sidebar.multiselect("Pilih Sentimen", options=df['Sentiment'].unique(), default=df['Sentiment'].unique())
media_types = st.sidebar.multiselect("Pilih Media Type", options=df['Media Type'].unique(), default=df['Media Type'].unique())
locations = st.sidebar.multiselect("Pilih Lokasi", options=df['Location'].unique(), default=df['Location'].unique())

# Filter DataFrame berdasarkan input pengguna
df_filtered = df[
    (df['Date'].dt.date >= start_date) &
    (df['Date'].dt.date <= end_date) &
    (df['Platform'].isin(platforms)) &
    (df['Sentiment'].isin(sentiments)) &
    (df['Media Type'].isin(media_types)) &
    (df['Location'].isin(locations))
]

# --- MAIN DASHBOARD LAYOUT ---
st.title("📊 Dashboard Analitik Media Sosial")
st.markdown("Analisis performa kampanye media sosial secara komprehensif.")

if df_filtered.empty:
    st.warning("Tidak ada data yang cocok dengan filter yang dipilih. Silakan ubah pilihan filter Anda.")
else:
    # --- METRIK UTAMA ---
    total_engagements = int(df_filtered['Engagements'].sum())
    total_posts = df_filtered.shape[0]
    avg_engagement_per_post = int(total_engagements / total_posts) if total_posts > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Engagement", f"{total_engagements:,}")
    col2.metric("Total Postingan", f"{total_posts:,}")
    col3.metric("Rata-rata Engagement/Post", f"{avg_engagement_per_post:,}")
    
    st.markdown("---")

    # --- KEMAMPUAN AI: RINGKASAN & PREDIKSI ---
    with st.container():
        st.subheader("💡 AI-Powered Insights & Strategy")
        
        # Ringkasan Strategi
        st.markdown(generate_key_action_summary(df_filtered))
        
        # Fitur AI lainnya
        expander_ai = st.expander("Lihat Fitur AI Lanjutan")
        with expander_ai:
            # Natural Language Query
            st.write("**Tanya Data Anda**")
            nl_query = st.text_input("Contoh: 'Platform apa dengan engagement tertinggi?'", key="nl_query")
            if nl_query:
                st.info(answer_natural_language_query(nl_query, df_filtered))

            # Rekomendasi Waktu Unggah
            st.write("**Rekomendasi Waktu Unggah Optimal (Simulasi)**")
            st.success("Rekomendasi: **Rabu & Jumat, pukul 19:00 - 21:00**. Ini adalah waktu di mana audiens Anda paling aktif.")
            
            # Prediksi Tren Engagement
            st.write("**Prediksi Tren Engagement (Simulasi)**")
            st.info("Prediksi: Engagement diperkirakan akan **naik sebesar 15%** pada kuartal berikutnya jika strategi konten video di Instagram dipertahankan.")

    st.markdown("---")

    # --- VISUALISASI DATA ---
    st.subheader("Visualisasi Kinerja Kampanye")

    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)

    with row1_col1:
        # Pie Chart: Sentiment Breakdown
        sentiment_data = df_filtered['Sentiment'].value_counts().reset_index()
        sentiment_data.columns = ['Sentiment', 'Count']
        fig_sentiment = px.pie(sentiment_data, names='Sentiment', values='Count', title='Sentiment Breakdown',
                               color_discrete_map={'Positive':'#2ECC71', 'Negative':'#E74C3C', 'Neutral':'#3498DB'},
                               hole=0.3)
        fig_sentiment.update_layout(legend_title_text='Sentimen')
        st.plotly_chart(fig_sentiment, use_container_width=True)
        
        with st.expander("Lihat Insight Grafik"):
            insights = generate_insight("Sentiment Breakdown", df_filtered)
            for insight in insights:
                st.markdown(f"- {insight}")

    with row1_col2:
        # Line Chart: Engagement Trend over Time
        engagement_trend = df_filtered.groupby(df_filtered['Date'].dt.date)['Engagements'].sum().reset_index()
        fig_trend = px.line(engagement_trend, x='Date', y='Engagements', title='Engagement Trend over Time', markers=True)
        fig_trend.update_layout(xaxis_title='Tanggal', yaxis_title='Total Engagement')
        st.plotly_chart(fig_trend, use_container_width=True)

        with st.expander("Lihat Insight Grafik"):
            insights = generate_insight("Engagement Trend over Time", df_filtered)
            for insight in insights:
                st.markdown(f"- {insight}")
    
    with row2_col1:
        # Bar Chart: Platform Engagements
        platform_engagement = df_filtered.groupby('Platform')['Engagements'].sum().sort_values(ascending=False).reset_index()
        fig_platform = px.bar(platform_engagement, x='Platform', y='Engagements', title='Platform Engagements', color='Platform')
        fig_platform.update_layout(xaxis_title='Platform', yaxis_title='Total Engagement', showlegend=False)
        st.plotly_chart(fig_platform, use_container_width=True)

        with st.expander("Lihat Insight Grafik"):
            insights = generate_insight("Platform Engagements", df_filtered)
            for insight in insights:
                st.markdown(f"- {insight}")

    with row2_col2:
        # Pie Chart: Media Type Mix
        media_type_data = df_filtered.groupby('Media Type')['Engagements'].sum().reset_index()
        fig_media = px.pie(media_type_data, names='Media Type', values='Engagements', title='Media Type Mix by Engagement', hole=0.3)
        fig_media.update_layout(legend_title_text='Tipe Media')
        st.plotly_chart(fig_media, use_container_width=True)

        with st.expander("Lihat Insight Grafik"):
            insights = generate_insight("Media Type Mix", df_filtered)
            for insight in insights:
                st.markdown(f"- {insight}")

    # Bar Chart: Top 5 Locations
    location_engagement = df_filtered.groupby('Location')['Engagements'].sum().nlargest(5).reset_index()
    fig_location = px.bar(location_engagement, x='Location', y='Engagements', title='Top 5 Locations by Engagement',
                          color='Location', text_auto=True)
    fig_location.update_layout(xaxis_title='Lokasi', yaxis_title='Total Engagement', showlegend=False)
    st.plotly_chart(fig_location, use_container_width=True)

    with st.expander("Lihat Insight Grafik"):
        insights = generate_insight("Top 5 Locations by Engagement", df_filtered)
        for insight in insights:
            st.markdown(f"- {insight}")


    # --- FITUR EKSPOR ---
    # Catatan: Ekspor PDF langsung dari sisi server di Streamlit itu kompleks.
    # Cara paling praktis adalah menggunakan fungsi "Print to PDF" dari browser.
    st.sidebar.markdown("---")
    st.sidebar.info(
        "**Cara Mengekspor ke PDF:**\n"
        "1. Klik kanan di mana saja di halaman ini.\n"
        "2. Pilih **Cetak...** (Print...).\n"
        "3. Atur tujuan (Destination) menjadi **Simpan sebagai PDF** (Save as PDF).\n"
        "4. Klik **Simpan** (Save)."
    )

    # --- MENAMPILKAN DATA MENTAH ---
    with st.expander("Lihat Data Mentah yang Difilter"):
        st.dataframe(df_filtered)

