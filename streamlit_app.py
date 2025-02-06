import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Dashboard Visualisasi Data Barang Keluar",
    page_icon="l.web.jpg",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================
# Fungsi untuk Memuat dan Menggabungkan Data dari Beberapa Tahun
# =====================================

@st.cache_data
def load_data(years, file_template='{}_db.xlsx', sheet_name='Sheet1'):
    df_list = []
    for year in years:
        file_path = file_template.format(year)
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            df['year'] = year  # Menambahkan kolom tahun
            df_list.append(df)
        except FileNotFoundError:
            st.error(f"File untuk tahun {year} tidak ditemukan: {file_path}")
        except Exception as e:
            st.error(f"Terjadi kesalahan saat memuat file {file_path}: {e}")
    if df_list:
        combined_df = pd.concat(df_list, ignore_index=True)
        return combined_df
    else:
        st.stop()

# Daftar tahun yang akan dimuat
years = [2020, 2021, 2022, 2023, 2024]
data = load_data(years)

# Rename columns sesuai kebutuhan
data.rename(columns={
    'nama divisi': 'nm_div',
    'divisi': 'anm_div',
    'sub divisi': 'subdivisi'
}, inplace=True)

# Convert 'tanggal' to datetime
data['tanggal'] = pd.to_datetime(data['tanggal'], format='%d/%m/%Y', errors='coerce')

# Menghapus baris dengan tanggal yang tidak valid
data = data.dropna(subset=['tanggal'])

# Tambahkan kolom 'month_year' untuk agregasi per bulan
months = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
          'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']

bulan_dict = {
    'Januari':1, 'Februari':2, 'Maret':3, 'April':4,
    'Mei':5, 'Juni':6, 'Juli':7, 'Agustus':8,
    'September':9, 'Oktober':10, 'November':11, 'Desember':12
}

data['month_year'] = data['tanggal'].apply(lambda x: f"{months[x.month - 1]} {x.year}")

# Sidebar
st.sidebar.image("654db0b264142 (1).webp", width=120)
st.sidebar.title("📊 PT Bakrie Pipe Industries")
st.sidebar.subheader("Dashboard Visualisasi Data Barang Keluar")

# =====================================
# Pindahkan Pencarian Nomor Barang ke Sidebar
# =====================================

st.sidebar.header("🔍 Pencarian Nomor Barang")

# Input untuk nomor barang
masukkan_nomor_barang = st.sidebar.text_input("Masukkan Nomor Barang:")

# Tombol Search
search_button = st.sidebar.button("Search")

# Sidebar filters
st.sidebar.header("🔍 Filter Data")

# Mode selector
mode = st.sidebar.radio(
    "Pilih Mode Tampilan:",
    options=["Dark", "Light"],
    index=1
)

# Set template berdasarkan mode
template = "plotly_white" if mode == "Light" else "plotly_dark"
background_color = "#ffffff" if mode == "Light" else "#222222"
font_color = "#000000" if mode == "Light" else "#ffffff"

# ============================
# Pengaturan Filter Tahun dan Bulan
# ============================

# Definisikan daftar tahun
unique_years = data['year'].unique()
sorted_years = sorted(unique_years)
year_options = ['All Years'] + list(sorted_years)

# Dropdown untuk memilih tahun
selected_year = st.sidebar.selectbox(
    "Pilih Tahun:",
    options=year_options
)

# Definisikan daftar bulan per tahun
if selected_year != 'All Years':
    # Filter data berdasarkan tahun yang dipilih
    data_filtered_year = data[data['year'] == selected_year]
else:
    data_filtered_year = data.copy()

unique_month_year = data_filtered_year['month_year'].unique()
sorted_month_year = sorted(unique_month_year, key=lambda x: (int(x.split()[1]), bulan_dict[x.split()[0]]))
month_year_options = ['All Months'] + sorted_month_year

# Multiselect untuk memilih bulan
selected_months = st.sidebar.multiselect(
    "Pilih Bulan:",
    options=month_year_options,
    default=['All Months']
)

# nm_div filter
nm_div_options = ['Semua Divisi'] + list(data['nm_div'].dropna().unique())
selected_nm_div = st.sidebar.selectbox(
    "Pilih Nama Divisi:",
    options=nm_div_options
)

# anm_div and subdivisi filters (depend on selected nm_div)
if selected_nm_div == 'Semua Divisi':
    filtered_nm_div_data = data
else:
    filtered_nm_div_data = data[data['nm_div'] == selected_nm_div]

anm_div_options = filtered_nm_div_data['anm_div'].dropna().unique()
selected_anm_div = st.sidebar.multiselect(
    "Alokasi Nama Divisi:",
    options=anm_div_options,
    default=list(anm_div_options)
)

subdivisi_options = filtered_nm_div_data[filtered_nm_div_data['anm_div'].isin(selected_anm_div)]['subdivisi'].dropna().unique()
selected_subdivisi = st.sidebar.multiselect(
    "Pilih Sub Divisi:",
    options=subdivisi_options,
    default=list(subdivisi_options)
)

# CSS Kustom
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

/* Header Utama dengan Gradient */
.main-header {
    background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
    padding: 30px;
    border-radius: 10px;
    text-align: center;
    color: #ffffff; /* Ubah warna teks menjadi putih untuk kontras */
    margin-bottom: 40px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

/* Container Kartu */
.card-container {
    background-color: #ffffff;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}

/* DataFrame Styling */
.dataframe {
    margin: auto;
    border-collapse: collapse;
    width: 100%;
}

.dataframe th {
    background-color: #2c3e50;
    color: #ffffff;
    text-align: center;
    font-weight: 600;
    padding: 10px;
}

.dataframe tr:hover {
    background-color: #f1f1f1;
    transition: all 0.2s ease-in-out;
}

.dataframe td {
    padding: 10px;
    text-align: center;
}

/* Judul Bagian dengan Gradient */
.title-section-bg {
    background: linear-gradient(45deg, #ff7e5f, #feb47b);
    padding: 10px;
    border-radius: 8px;
    text-align: center;
    margin-bottom: 15px;
}

.title-section-bg h2 {
    margin: 0;
    font-weight: 600;
    display: inline-block;
    padding: 5px 10px;
    color: #ffffff; /* Warna teks putih untuk kontras */
}

/* Judul Bagian tanpa Background */
.title-section-no-bg {
    text-align: center;
    margin-bottom: 15px;
}

.title-section-no-bg h3, .title-section-no-bg h4 {
    margin: 0;
    font-weight: 600;
    display: inline-block;
    padding: 5px 10px;
    color: #333333;
}

.title-section-no-bg h3:hover, .title-section-no-bg h4:hover {
    color: #555555;
}

/* Note Section */
.note-section p {
    background-color: #fff3cd;
    color: #856404;
    padding: 10px;
    border-left: 5px solid #ffeeba;
    border-radius: 5px;
    font-weight: 500;
}

/* Informasi Tambahan Section */
.info-section p {
    background-color: #d4edda;
    color: #155724;
    padding: 10px;
    border-left: 5px solid #c3e6cb;
    border-radius: 5px;
    font-weight: 500;
}

/* Footer */
.footer-section {
    text-align: center;
    margin-top: 30px;
    color: #999999;
}

.footer-section hr {
    margin: 20px 0;
    border: none;
    border-top: 1px solid #ddd;
}

/* Subtitle Styling */
.subtitle {
    font-size: 14px;
    color: #666666;
    margin-bottom: 15px;
}

/* Welcome Section */
.welcome-section {
    background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
    padding: 30px;
    border-radius: 10px;
    text-align: center;
    color: #ffffff; /* Ubah warna teks menjadi putih untuk kontras */
    margin-bottom: 40px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

.welcome-section h1 {
    color: #ffffff; /* Teks putih untuk kontras */
    font-size: 2.5em;
    margin-bottom: 10px;
}

.welcome-section p, .welcome-section ul {
    color: #ffffff; /* Teks putih untuk kontras */
    font-size: 1.2em;
}

/* Search Result Section */
.search-result-section {
    background: linear-gradient(45deg, #ff7e5f, #feb47b);
    padding: 10px;
    border-radius: 8px;
    text-align: center;
    margin-bottom: 15px;
}

.search-result-section h2 {
    margin: 0;
    font-weight: 600;
    display: inline-block;
    padding: 5px 10px;
    color: #ffffff; /* Ubah warna teks menjadi putih untuk kontras */
}

/* Responsive Title Sizes */
@media (max-width: 768px) {
    .title-section-bg h2 {
        font-size: 1.5em;
    }
    .title-section-no-bg h3 {
        font-size: 1.3em;
    }
    .title-section-no-bg h4 {
        font-size: 1.1em;
    }
    .welcome-section h1 {
        font-size: 2em;
    }
    .search-result-section h2 {
        font-size: 1.5em;
    }
}
</style>
"""

# Terapkan CSS kustom
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Logika untuk Search
if search_button:
    if masukkan_nomor_barang.strip() == "":
        st.sidebar.error("Silakan masukkan Nomor Barang terlebih dahulu sebelum melakukan pencarian.")
        st.session_state['search_clicked'] = False
    else:
        st.session_state['search_clicked'] = True
        st.session_state['top_items_limit'] = 3  # Reset ke batas awal pada pencarian baru
else:
    if 'search_clicked' not in st.session_state:
        st.session_state['search_clicked'] = False

# Default view jika search belum diklik
if not st.session_state['search_clicked']:
    st.markdown(
        f"""
        <div class="welcome-section">
            <h1>🌟 Selamat Datang di Dashboard Visualisasi Data Barang Keluar</h1>
            <p>Warehouse PT Bakrie Pipe Industries</p>
            <p><b>Hari ini:</b> {datetime.now().strftime('%A, %d %B %Y')}</p>
        </div>
        """, unsafe_allow_html=True)

    st.write("Gunakan filter di sebelah kiri, masukkan **Nomor Barang**, lalu klik tombol 'Search' untuk melihat hasil **visualisasi data**")
else:
    st.markdown("""
    <div class="search-result-section">
        <h2>🎯 Berikut hasil visualisasi data berdasarkan pencarian Anda!</h2>
    </div>
    """, unsafe_allow_html=True)

    # Apply filters
    filtered_data = data[
        ((selected_nm_div == 'Semua Divisi') | (data['nm_div'] == selected_nm_div)) &
        (data['anm_div'].isin(selected_anm_div)) &
        (data['subdivisi'].isin(selected_subdivisi))
    ]

    # Filter berdasarkan tahun jika bukan "All Years"
    if selected_year != 'All Years':
        filtered_data = filtered_data[filtered_data['year'] == selected_year]

    # Filter berdasarkan bulan jika bukan "All Months"
    if 'All Months' not in selected_months and selected_months:
        filtered_data = filtered_data[filtered_data['month_year'].isin(selected_months)]
    # Jika "All Months" dipilih atau tidak memilih apapun, tidak ada filter bulan

    # Filter berdasarkan nomor barang
    filtered_nomor_barang_data = filtered_data[filtered_data['nomor barang'].str.contains(masukkan_nomor_barang, case=False, na=False)]

    if not filtered_nomor_barang_data.empty:
        # Tampilkan informasi barang berdasarkan nomor barang yang diinput
        item_info = filtered_nomor_barang_data[['nomor barang', 'nama barang', 'satuan']].drop_duplicates()

        st.markdown("### 📦 Informasi Barang")
        st.table(item_info)

        # Update filtered_data untuk hanya menyertakan 'nomor barang' yang dipilih
        filtered_data = filtered_nomor_barang_data
    else:
        st.warning("Nomor Barang tidak ditemukan dalam data.")
        st.stop()  # Menghentikan eksekusi selanjutnya jika tidak ada data yang cocok

    # ========================================
    # Tambahkan Tabel "📋 Data Pemakaian" (Total Tahunan)
    # ========================================

    st.markdown(f"<h3 style='color:{font_color};'>📋 Data Pemakaian (Total Tahunan)</h3>", unsafe_allow_html=True)

    # Agregasi total pemakaian per tahun untuk barang yang dicari
    usage_data = filtered_data.groupby('year')['jumlah'].sum().reset_index()
    usage_data = usage_data.sort_values('year')

    # Tampilkan tabel total tahunan
    st.table(usage_data)

    # ========================================
    # Visualisasi Data
    # ========================================

    st.markdown("<h2 style='text-align: center;'>📈 Visualisasi Data</h2>", unsafe_allow_html=True)
    st.markdown(
        f"""<div style='text-align: justify; margin-top: 10px; margin-bottom: 20px; font-size: 16px;'>
        Bagian ini menyajikan berbagai visualisasi data yang dirancang untuk memberikan pemahaman mendalam tentang pola, tren, dan distribusi data barang keluar. Dengan memanfaatkan grafik ini, Anda dapat menganalisis informasi penting, seperti tren permintaan, distribusi jumlah barang, hingga kontribusi setiap divisi atau sub divisi. Tujuannya adalah membantu Anda dalam pengambilan keputusan berbasis data secara lebih efektif dan efisien.
        </div>""",
        unsafe_allow_html=True
    )

    # Mendapatkan daftar tahun yang tersedia dalam data yang difilter
    available_years = filtered_data['year'].unique()
    available_years = sorted(available_years)

    if len(available_years) == 0:
        st.warning("Tidak ada data yang tersedia untuk visualisasi.")
    else:
        # Buat tabs untuk setiap tahun
        tabs = st.tabs([f"Tahun {year}" for year in available_years])

        for idx, year in enumerate(available_years):
            with tabs[idx]:
                st.markdown(f"<h3 style='color:{font_color};'>📊 Visualisasi Tahun {year}</h3>", unsafe_allow_html=True)
                
                # Filter data untuk tahun tersebut
                data_year = filtered_data[filtered_data['year'] == year]

                # 1. Line Chart: Tren Permintaan Barang per Bulan
                st.markdown(f"<div style='border: 1px solid #000000; padding: 10px; margin-bottom: 20px; border-radius: 10px;'>", unsafe_allow_html=True)
                st.markdown(f"<h4 style='color:{font_color};'>✨ Tren Permintaan Barang per Bulan</h4>", unsafe_allow_html=True)
                st.markdown(
                    f"""<div style='text-align: justify; margin-top: 10px; margin-bottom: 10px; font-size: 14px;'>
                    Grafik ini menampilkan tren permintaan barang per bulan tahun {year}. Dengan visualisasi ini, Anda dapat melihat bagaimana permintaan barang berubah seiring waktu dan mengidentifikasi tren atau pola musiman.
                    </div>""",
                    unsafe_allow_html=True
                )

                # Menggabungkan data untuk tahun tersebut
                aggregated_trend_data = data_year.groupby(['month_year'])['jumlah'].sum().reset_index()

                # Pastikan month_year terurut dengan benar
                aggregated_trend_data['month_year'] = pd.Categorical(aggregated_trend_data['month_year'], categories=sorted_month_year, ordered=True)
                aggregated_trend_data = aggregated_trend_data.sort_values('month_year')

                line_chart = px.line(
                    aggregated_trend_data,
                    x='month_year',
                    y='jumlah',
                    title=None,
                    labels={'jumlah': 'Jumlah Permintaan', 'month_year': 'Bulan'},
                    template=template,
                    markers=True
                )
                st.plotly_chart(line_chart, use_container_width=True)
                st.markdown(
                    f"""<div style='background-color:{background_color}; padding:5px; border-radius:5px; margin-top:10px;'>
                    <b style='color:{font_color};'>Penjelasan:</b> Grafik garis ini menunjukkan tren permintaan barang per bulan tahun {year}. Warna yang berbeda mewakili masing-masing tahun, memungkinkan Anda untuk membandingkan tren antar tahun.
                    </div>""",
                    unsafe_allow_html=True
                )
                st.markdown(f"</div>", unsafe_allow_html=True)

                # 2. Bar Chart: Jumlah Barang per Bulan dan Alokasi Nama Divisi
                st.markdown(f"<div style='border: 1px solid #000000; padding: 10px; margin-bottom: 20px; border-radius: 10px;'>", unsafe_allow_html=True)
                st.markdown(f"<h4 style='color:{font_color};'>📊 Jumlah Barang per Bulan dan Alokasi Nama Divisi</h4>", unsafe_allow_html=True)
                st.markdown(
                    f"""<div style='text-align: justify; margin-top: 10px; margin-bottom: 10px; font-size: 14px;'>
                    Grafik batang ini menunjukkan jumlah barang yang keluar per bulan dan alokasi nama divisi tahun {year}. Dengan visualisasi ini, Anda dapat memahami distribusi jumlah barang berdasarkan divisi dan melihat bagaimana alokasi barang berubah setiap bulannya.
                    </div>""",
                    unsafe_allow_html=True
                )

                # Menggabungkan data untuk tahun tersebut
                aggregated_bar_data = data_year.groupby(['month_year', 'anm_div'])['jumlah'].sum().reset_index()

                bar_chart = px.bar(
                    aggregated_bar_data,
                    x='month_year',
                    y='jumlah',
                    color='anm_div',
                    barmode='group',
                    title=None,
                    labels={'jumlah': 'Total Jumlah', 'anm_div': 'Alokasi Nama Divisi', 'month_year': 'Bulan'},
                    template=template
                )
                st.plotly_chart(bar_chart, use_container_width=True)
                st.markdown(
                    f"""<div style='background-color:{background_color}; padding:5px; border-radius:5px; margin-top:10px;'>
                    <b style='color:{font_color};'>Penjelasan:</b> Grafik batang ini menunjukkan jumlah barang yang digunakan oleh divisi pada bulan tertentu tahun {year}. Warna yang berbeda mewakili masing-masing divisi, memudahkan perbandingan antar divisi.
                    </div>""",
                    unsafe_allow_html=True
                )
                st.markdown(f"</div>", unsafe_allow_html=True)

                # 3. Pie Chart: Persentase Jumlah per Bulan
                st.markdown(f"<div style='border: 1px solid #000000; padding: 10px; margin-bottom: 20px; border-radius:10px;'>", unsafe_allow_html=True)
                st.markdown(f"<h4 style='color:{font_color};'>🍰 Persentase Jumlah per Bulan</h4>", unsafe_allow_html=True)
                st.markdown(
                    f"""<div style='text-align: justify; margin-top: 10px; margin-bottom: 10px; font-size: 14px;'>
                    Diagram lingkaran ini menggambarkan persentase jumlah barang yang keluar setiap bulan tahun {year}. Dengan visualisasi ini, Anda dapat melihat kontribusi setiap bulan terhadap total permintaan barang.
                    </div>""",
                    unsafe_allow_html=True
                )

                # Menggabungkan data untuk tahun tersebut
                aggregated_pie_data = data_year.groupby(['month_year'])['jumlah'].sum().reset_index()

                pie_chart = px.pie(
                    aggregated_pie_data,
                    names='month_year',
                    values='jumlah',
                    title=None,
                    labels={'jumlah': 'Jumlah', 'month_year': 'Bulan'},
                    template=template,
                    hole=0.3
                )
                st.plotly_chart(pie_chart, use_container_width=True)
                st.markdown(
                    f"""<div style='background-color:{background_color}; padding:5px; border-radius:5px; margin-top:10px;'>
                    <b style='color:{font_color};'>Penjelasan:</b> Diagram lingkaran ini menunjukkan persentase kontribusi setiap bulan terhadap total permintaan barang tahun {year}. Warna yang berbeda mewakili masing-masing bulan, memungkinkan analisis perbandingan antar bulan.
                    </div>""",
                    unsafe_allow_html=True
                )
                st.markdown(f"</div>", unsafe_allow_html=True)

                # 4. Heatmap: Penggunaan Barang per Bulan dan Sub Divisi
                st.markdown(f"<div style='border: 1px solid #000000; padding: 10px; margin-bottom: 20px; border-radius:10px;'>", unsafe_allow_html=True)
                st.markdown(f"<h4 style='color:{font_color};'>🌡️ Heatmap Penggunaan Barang per Bulan dan Sub Divisi</h4>", unsafe_allow_html=True)
                st.markdown(
                    f"""<div style='text-align: justify; margin-top: 10px; margin-bottom: 10px; font-size: 14px;'>
                    Heatmap ini menunjukkan intensitas penggunaan barang pada setiap bulan dan sub divisi tahun {year}. Dengan visualisasi ini, Anda dapat mengidentifikasi subdivisi yang memiliki permintaan tertinggi dan pola penggunaan barang yang mungkin terjadi.
                    </div>""",
                    unsafe_allow_html=True
                )

                # Menggabungkan data untuk tahun tersebut
                aggregated_heatmap_data = data_year.groupby(['month_year', 'subdivisi'])['jumlah'].sum().reset_index()

                heatmap = px.density_heatmap(
                    aggregated_heatmap_data,
                    x='month_year',
                    y='subdivisi',
                    z='jumlah',
                    title=None,
                    labels={
                        'jumlah': 'Jumlah',
                        'month_year': 'Bulan',
                        'subdivisi': 'Sub Divisi'
                    },
                    color_continuous_scale='Viridis',
                    template=template
                )
                st.plotly_chart(heatmap, use_container_width=True)
                st.markdown(
                    f"""<div style='background-color:{background_color}; padding:5px; border-radius:5px; margin-top:10px;'>
                    <b style='color:{font_color};'>Penjelasan:</b> Heatmap ini menunjukkan intensitas jumlah barang yang digunakan pada bulan tertentu oleh subdivisi tahun {year}. Warna mewakili jumlah barang, memudahkan identifikasi subdivisi dengan permintaan tinggi.
                    </div>""",
                    unsafe_allow_html=True
                )
                st.markdown(f"</div>", unsafe_allow_html=True)

                # 5. Scatterplot: Bulan vs Jumlah Permintaan
                st.markdown(f"<div style='border: 1px solid #000000; padding: 10px; margin-bottom: 20px; border-radius:10px;'>", unsafe_allow_html=True)
                st.markdown(f"<h4 style='color:{font_color};'>🔹 Scatterplot Bulan vs Jumlah Permintaan</h4>", unsafe_allow_html=True)
                st.markdown(
                    f"""<div style='text-align: justify; margin-top: 10px; margin-bottom: 10px; font-size: 14px;'>
                    Scatterplot ini menampilkan hubungan antara bulan dan jumlah permintaan barang tahun {year}. Dengan visualisasi ini, Anda dapat mendeteksi pola dan tren musiman dalam permintaan barang serta membandingkan tren antar tahun.
                    </div>""",
                    unsafe_allow_html=True
                )

                # Menggabungkan data untuk tahun tersebut
                aggregated_scatter_data = data_year.groupby(['month_year'])['jumlah'].sum().reset_index()

                scatter_plot = px.scatter(
                    aggregated_scatter_data,
                    x='month_year',
                    y='jumlah',
                    title=None,
                    labels={'month_year': 'Bulan', 'jumlah': 'Jumlah Permintaan'},
                    template=template,
                    size='jumlah',
                    hover_data=[]
                )
                st.plotly_chart(scatter_plot, use_container_width=True)
                st.markdown(
                    f"""<div style='background-color:{background_color}; padding:5px; border-radius:5px; margin-top:10px;'>
                    <b style='color:{font_color};'>Penjelasan:</b> Scatterplot ini menunjukkan hubungan antara bulan dan jumlah permintaan barang tahun {year}. Warna yang berbeda mewakili masing-masing tahun, memungkinkan analisis perbandingan tren dan pola musiman.
                    </div>""",
                    unsafe_allow_html=True
                )
                st.markdown(f"</div>", unsafe_allow_html=True)

                # 6. Boxplot: Distribusi Jumlah per Bulan
                st.markdown(f"<div style='border: 1px solid #000000; padding: 10px; margin-bottom: 20px; border-radius:10px;'>", unsafe_allow_html=True)
                st.markdown(f"<h4 style='color:{font_color};'>📦 Distribusi Jumlah per Bulan</h4>", unsafe_allow_html=True)
                st.markdown(
                    f"""<div style='text-align: justify; margin-top: 10px; margin-bottom: 10px; font-size: 14px;'>
                    Boxplot ini menganalisis distribusi jumlah permintaan barang pada berbagai bulan tahun {year}. Dengan visualisasi ini, Anda dapat melihat rentang distribusi, median, serta nilai ekstrem dalam permintaan barang dan membandingkan distribusi antar tahun.
                    </div>""",
                    unsafe_allow_html=True
                )

                # Menggabungkan data untuk tahun tersebut
                aggregated_box_data = data_year.groupby(['month_year'])['jumlah'].sum().reset_index()

                box_plot = px.box(
                    aggregated_box_data,
                    x='month_year',
                    y='jumlah',
                    title=None,
                    labels={'month_year': 'Bulan', 'jumlah': 'Jumlah Permintaan'},
                    template=template
                )
                st.plotly_chart(box_plot, use_container_width=True)
                st.markdown(
                    f"""<div style='background-color:{background_color}; padding:5px; border-radius:5px; margin-top:10px;'>
                    <b style='color:{font_color};'>Penjelasan:</b> Boxplot ini menganalisis distribusi permintaan barang pada berbagai bulan tahun {year}. Warna yang berbeda mewakili masing-masing tahun, memudahkan perbandingan distribusi antar tahun.
                    </div>""",
                    unsafe_allow_html=True
                )
                st.markdown(f"</div>", unsafe_allow_html=True)

                # 7. Histogram: Distribusi Jumlah Permintaan per Bulan
                st.markdown(f"<div style='border: 1px solid #000000; padding: 10px; margin-bottom: 20px; border-radius:10px;'>", unsafe_allow_html=True)
                st.markdown(f"<h4 style='color:{font_color};'>📊 Distribusi Jumlah Permintaan per Bulan</h4>", unsafe_allow_html=True)
                st.markdown(
                    f"""<div style='text-align: justify; margin-top: 10px; margin-bottom: 10px; font-size: 14px;'>
                    Histogram ini menunjukkan pola distribusi jumlah permintaan barang pada setiap bulan tahun {year}. Dengan visualisasi ini, Anda dapat mengidentifikasi distribusi frekuensi permintaan dan potensi puncak permintaan antar tahun.
                    </div>""",
                    unsafe_allow_html=True
                )

                # Menggabungkan data untuk tahun tersebut
                aggregated_histogram_data = data_year.groupby(['month_year'])['jumlah'].sum().reset_index()

                histogram = px.histogram(
                    aggregated_histogram_data,
                    x='month_year',
                    y='jumlah',
                    title=None,
                    labels={'month_year': 'Bulan', 'jumlah': 'Jumlah Permintaan'},
                    template=template
                )
                st.plotly_chart(histogram, use_container_width=True)
                st.markdown(
                    f"""<div style='background-color:{background_color}; padding:5px; border-radius:5px; margin-top:10px;'>
                    <b style='color:{font_color};'>Penjelasan:</b> Histogram ini menunjukkan distribusi jumlah permintaan barang pada setiap bulan tahun {year}. Warna yang berbeda mewakili masing-masing tahun, memungkinkan identifikasi tren distribusi dan puncak permintaan antar tahun.
                    </div>""",
                    unsafe_allow_html=True
                )
                st.markdown(f"</div>", unsafe_allow_html=True)

                # 8. Violin Plot: Jumlah Permintaan per Bulan
                st.markdown(f"<div style='border: 1px solid #000000; padding: 10px; margin-bottom: 20px; border-radius:10px;'>", unsafe_allow_html=True)
                st.markdown(f"<h4 style='color:{font_color};'>🎻 Violin Plot Jumlah Permintaan per Bulan</h4>", unsafe_allow_html=True)
                st.markdown(
                    f"""<div style='text-align: justify; margin-top: 10px; margin-bottom: 10px; font-size: 14px;'>
                    Violin Plot ini memberikan distribusi mendetail dari jumlah permintaan barang per bulan tahun {year}. Dengan visualisasi ini, Anda dapat melihat distribusi simetris atau asimetris permintaan serta mengidentifikasi potensi outlier dan tren musiman.
                    </div>""",
                    unsafe_allow_html=True
                )

                # Menggabungkan data untuk tahun tersebut
                aggregated_violin_data = data_year.groupby(['month_year'])['jumlah'].sum().reset_index()

                violin_plot = px.violin(
                    aggregated_violin_data,
                    x='month_year',
                    y='jumlah',
                    title=None,
                    labels={'month_year': 'Bulan', 'jumlah': 'Jumlah Permintaan'},
                    template=template,
                    box=True,
                    points="all"
                )
                st.plotly_chart(violin_plot, use_container_width=True)
                st.markdown(
                    f"""<div style='background-color:{background_color}; padding:5px; border-radius:5px; margin-top:10px;'>
                    <b style='color:{font_color};'>Penjelasan:</b> Violin Plot ini menunjukkan distribusi jumlah permintaan barang pada berbagai bulan tahun {year}. Warna yang berbeda mewakili masing-masing tahun, memungkinkan analisis distribusi dan identifikasi tren serta outlier antar tahun.
                    </div>""",
                    unsafe_allow_html=True
                )
                st.markdown(f"</div>", unsafe_allow_html=True)

        # (Opsional) Footer
        st.markdown("""
        <div class="footer-section">
            <hr>
            <p>© 2025 - PT Bakrie Pipe Industries. All rights reserved.</p>
        </div>
        """, unsafe_allow_html=True)
