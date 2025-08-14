import math
import pandas as pd
import streamlit as st
import altair as alt
import plotly.express as px
from db_config import get_engine
from utils import protect_page

# Proteksi halaman login
protect_page()

# Judul halaman
st.title("📊 Analisa Penjualan Kopi")

# Profil user
role = st.session_state.get("role", "user")
username = st.session_state.get("username", "User")

# === Fungsi Format Rupiah ===
def format_rupiah_singkat(angka):
    if angka >= 1_000_000_000:
        return f"Rp {angka / 1_000_000_000:.2f} M"
    elif angka >= 1_000_000:
        return f"Rp {angka / 1_000_000:.2f} Juta"
    elif angka >= 1_000:
        return f"Rp {angka / 1_000:.0f} Ribu"
    else:
        return f"Rp {angka:,.0f}".replace(",", ".")

def singkat_angka(value):
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f} M"
    elif value >= 1_000_000:
        return f"{value / 1_000_000:.2f} Juta"
    elif value >=1_000:
        return f"{value / 1_000:.0f} Ribu"
    else:
        return f"{value:,.0f}".replace(",", ".")

# Ambil data dari MySQL
engine = get_engine()
df = pd.read_sql("SELECT * FROM coffee_sales", engine)

# === Sidebar Kurs & Konversi Mata Uang ===
st.sidebar.subheader("💱 Konversi Mata Uang")
exchange_rate = st.sidebar.number_input(
    "Kurs BRL ke IDR", min_value=1000, max_value=10000, value=3200, step=100
)
df["money"] = df["money"] * exchange_rate
st.info(f"💱 Nilai 'money' dikonversi dari Brazilian Real (BRL) ke Rupiah (IDR) dengan kurs: 1 BRL = Rp {exchange_rate:,}")

# === Filter Rentang Tanggal ===
st.subheader("📅 Filter Rentang Tanggal")
min_date_available = df["date"].min().date() 
max_date_available = df["date"].max().date() 

# Filter rentang tanggal
date_range = st.date_input(
    "Pilih rentang tanggal:",
    value=[min_date_available, max_date_available],
    min_value=min_date_available,
    max_value=max_date_available
)

# Copy full dataset
filtered_df = df.copy()

if len(date_range) == 2:
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])
    end_date = end_date + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

    filtered_df = filtered_df[(filtered_df["date"] >= start_date) & (filtered_df["date"] <= end_date)]

# Beri peringatan jika kosong setelah filter
if filtered_df.empty:
    st.warning("⚠️ Tidak ada data pada rentang tanggal yang dipilih. Sesuaikan rentang tanggal.")
    st.stop()

# === Tampilkan Metrik Penjualan ===
total_penjualan = filtered_df["money"].sum()
jumlah_transaksi = len(filtered_df)
rata_rata = filtered_df["money"].mean()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        "💰 Total Penjualan (Rp)",
        format_rupiah_singkat(total_penjualan),
        help=f"Total: Rp {total_penjualan:,.0f}"
    )
with col2:
    st.metric(
        "🧾 Jumlah Transaksi",
        f"{jumlah_transaksi:,}",
        help=f"Total Transaksi: {jumlah_transaksi:,} kali"
    )
with col3:
    st.metric(
        "📊 Rata-rata per Transaksi",
        format_rupiah_singkat(rata_rata),
        help=f"Rata-rata: Rp {rata_rata:,.0f}"
    )


# === Visualisasi Grafik Analisis ===
st.markdown("## 📊 Visualisasi Penjualan")

# === Grafik: ☕ Penjualan per Jenis Kopi ===
st.subheader("☕ Penjualan per Jenis Kopi")

# Hitung total penjualan per jenis kopi
df_kopi = filtered_df.groupby("coffee_name")["money"].sum().reset_index().sort_values("money", ascending=False)

# Tambahkan kolom dalam satuan juta dan label teks
df_kopi["money_juta"] = df_kopi["money"] / 1_000_000
df_kopi["label"] = df_kopi["money_juta"].apply(lambda x: f"Rp {x:,.2f} Juta")

# Pilih skema warna profesional
color_sequence = px.colors.sequential.Viridis  # Bisa diganti dengan Plasma, Blues, Tealgrn, dll.

# Buat grafik
fig_kopi = px.bar(
    df_kopi,
    x="coffee_name",
    y="money_juta",
    text="label",
    color="coffee_name",
    color_discrete_sequence=color_sequence,
    labels={
        "coffee_name": "Jenis Kopi",
        "money_juta": "Total Penjualan (Juta Rp)"
    }
)

# === Set sumbu Y ke kelipatan 10 Juta ===
max_val = df_kopi["money_juta"].max()
upper_limit = math.ceil(max_val / 10) * 10
tick_vals = list(range(0, int(upper_limit) + 10, 10))
tick_texts = [f"{val} Juta" for val in tick_vals]

# Update tampilan grafik
fig_kopi.update_traces(
    hovertemplate="<b>Jenis Kopi:</b> %{x}<br><b>Total Penjualan:</b> Rp %{y:,.2f} Juta",
    textposition="outside",
    textfont_size=12
)

fig_kopi.update_layout(
    yaxis=dict(
        tickvals=tick_vals,
        ticktext=tick_texts,
        title="Total Penjualan"
    ),
    xaxis_title="Jenis Kopi",
    uniformtext_minsize=8,
    uniformtext_mode='hide',
    showlegend=False,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(size=12),
    margin=dict(t=30, b=80),
)
st.plotly_chart(fig_kopi, use_container_width=True, key="grafik_kopi")


# === Grafik: 📆 Jumlah Transaksi per Hari ===
st.subheader("📆 Jumlah Transaksi per Hari")
transaksi_per_hari = (
    filtered_df.groupby(filtered_df["date"].dt.date)
    .size()
    .reset_index(name="jumlah_transaksi")
)

fig_trx_per_hari = px.line(
    transaksi_per_hari,
    x="date",
    y="jumlah_transaksi",
    markers=True,
    labels={"date": "Tanggal", "jumlah_transaksi": "Jumlah Transaksi"},
    title="Jumlah Transaksi Harian"
)
fig_trx_per_hari.update_layout(
    xaxis_title="Tanggal",
    yaxis_title="Jumlah Transaksi",
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)'
)
st.plotly_chart(fig_trx_per_hari, use_container_width=True, key="trx_harian")


# === Grafik: 💳 Penjualan Berdasarkan Metode Pembayaran ===
st.subheader("💳 Penjualan Berdasarkan Metode Pembayaran")

# Tampilkan informasi rentang tanggal di judul
tanggal_info = f"{start_date.strftime('%d %b %Y')} - {end_date.strftime('%d %b %Y')}"

fig_payment = px.pie(
    filtered_df,
    values="money",
    names="cash_type",
    title=f"Distribusi Penjualan per Metode Pembayaran ({tanggal_info})",
    color_discrete_sequence=px.colors.qualitative.Pastel,
    hole=0.4
)

fig_payment.update_traces(
    textinfo="label+percent",
    hovertemplate="<b>%{label}</b><br>Rp %{value:,.0f}<extra></extra>"
)

fig_payment.update_layout(
    showlegend=True,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    margin=dict(t=40, b=40)
)

st.plotly_chart(fig_payment, use_container_width=True, key="metode_pembayaran")


# === Grafik: 📅 Penjualan per Hari dalam Seminggu ===
st.subheader("📅 Penjualan per Hari dalam Seminggu")

# Ambil nama hari dari kolom tanggal
filtered_df["day_name"] = pd.to_datetime(filtered_df["date"]).dt.day_name()

# Atur urutan hari agar dimulai dari Senin
ordered_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
filtered_df["day_name"] = pd.Categorical(filtered_df["day_name"], categories=ordered_days, ordered=True)

# Total penjualan per hari
penjualan_per_hari = (
    filtered_df.groupby("day_name")["money"]
    .sum()
    .reset_index()
    .sort_values("day_name")
)
penjualan_per_hari["money_juta"] = penjualan_per_hari["money"] / 1_000_000

# Buat grafik batang
fig_hari = px.bar(
    penjualan_per_hari,
    x="day_name",
    y="money_juta",
    labels={"day_name": "Hari", "money_juta": "Total Penjualan (Juta Rp)"},
    color="day_name",
    color_discrete_sequence=px.colors.qualitative.Set2,
    text=penjualan_per_hari["money_juta"].apply(lambda x: f"{x:.2f} Juta")
)

fig_hari.update_traces(
    textposition="outside",
    hovertemplate="<b>%{x}</b><br>Total Penjualan: Rp %{y:.2f} Juta<extra></extra>"
)
fig_hari.update_layout(
    xaxis_title="Hari",
    yaxis_title="Penjualan (Juta Rp)",
    showlegend=False,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)'
)
st.plotly_chart(fig_hari, use_container_width=True, key="penjualan_hari_dalam_minggu")


# === Grafik: ⏰ Penjualan Berdasarkan Jam (dalam Juta Rupiah) ===
st.subheader("⏰ Penjualan Berdasarkan Jam")

# Hitung total penjualan per jam
df_per_jam = filtered_df.groupby("hour_of_day")["money"].sum().reset_index()
df_per_jam["money_juta"] = df_per_jam["money"] / 1_000_000

# Buat list tickvals dan ticktext
max_juta = df_per_jam["money_juta"].max()
step = 5
tick_vals = list(range(0, math.ceil(max_juta)+step, step))
tick_texts = [f"{val} Juta" for val in tick_vals]

# Buat grafik line
fig_hour = px.line(
    df_per_jam,
    x="hour_of_day",
    y="money_juta",
    markers=True,
    labels={
        "hour_of_day": "Jam",
        "money_juta": "Total Penjualan"
    },
    title="Penjualan per Jam"
)

fig_hour.update_traces(
    line=dict(width=3),
    marker=dict(size=10),
    hovertemplate="<b>Jam %{x}:00</b><br>Total Penjualan: %{y:.2f} Juta<extra></extra>"
)

fig_hour.update_layout(
    xaxis=dict(dtick=1),
    yaxis=dict(
        title="Penjualan",
        tickvals=tick_vals,
        ticktext=tick_texts
    ),
    xaxis_title="Jam (0 - 23)",
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(size=12),
    margin=dict(t=30, b=40),
)

st.plotly_chart(fig_hour, use_container_width=True, key="penjualan_per_jam")

# === Info: ⏰ Jam Tersibuk ===
if not filtered_df.empty:
    busiest_hour = filtered_df["hour_of_day"].value_counts().idxmax()
    formatted_busiest_hour = f"{busiest_hour:02d}"
    st.info(f"⏰ **Jam Tersibuk:** {formatted_busiest_hour}:00")
else:
    st.info("⏰ **Jam Tersibuk:** Tidak ada data penjualan dalam rentang waktu ini.")


# === Grafik: 📈 Jumlah Transaksi per Jam ===
st.subheader("📈 Jumlah Transaksi per Jam")

# Hitung jumlah transaksi per jam
df_transaksi_jam = filtered_df.groupby("hour_of_day").size().reset_index(name="jumlah_transaksi")
df_transaksi_jam["label_jam"] = df_transaksi_jam["hour_of_day"].apply(lambda x: f"Jam {x:02d}")

# Buat bar chart vertikal dengan tema gelap
fig_transaksi_hour = px.bar(
    df_transaksi_jam,
    x="label_jam",
    y="jumlah_transaksi",
    text="jumlah_transaksi",
    labels={
        "label_jam": "Jam",
        "jumlah_transaksi": "Jumlah Transaksi"
    },
    title="Jumlah Transaksi per Jam",
    color="jumlah_transaksi",
    color_continuous_scale="Tealgrn",  # Bisa ganti: "Blues", "Inferno", "Viridis"
    template="plotly_dark"
)

# Atur tampilan tambahan
fig_transaksi_hour.update_traces(
    textposition="outside",
    textfont=dict(size=12),
    marker_line_color='rgba(255,255,255,0.6)',
    marker_line_width=1.5
)

fig_transaksi_hour.update_layout(
    plot_bgcolor="#1e1e1e",
    paper_bgcolor="#1e1e1e",
    font=dict(color="white", size=13),
    title_font=dict(size=15, color="white"),
    xaxis_title="Jam",
    yaxis_title="Jumlah Transaksi",
    showlegend=False
)

# Tampilkan grafik
st.plotly_chart(fig_transaksi_hour, use_container_width=True, key="transaksi_per_jam")


# === Grafik: 🏆 Top 5 Produk Terlaris ===
st.subheader("🏆 Top 5 Produk Terlaris")

top5_sales = (
    filtered_df.groupby("coffee_name", as_index=False)["money"]
    .sum()
    .rename(columns={"money": "total_sales"})
    .sort_values(by="total_sales", ascending=False)
    .head(5)
)

# Konversi ke juta
top5_sales["total_sales_juta"] = top5_sales["total_sales"] / 1e6
top5_sales["label"] = top5_sales["total_sales_juta"].apply(lambda x: f"Rp {x:,.2f} Juta")

# Sort descending supaya yang terbesar muncul di atas (karena horizontal bar)
top5_sorted = top5_sales.sort_values(by="total_sales_juta", ascending=False)

# Buat grafik
fig_top5 = px.bar(
    top5_sorted,
    x="total_sales_juta",
    y="coffee_name",
    orientation="h",
    text="label",
    color="coffee_name",
    labels={
        "coffee_name": "Jenis Kopi",
        "total_sales_juta": "Total Penjualan (Juta Rp)"
    }
)

# Hitung kelipatan 10 juta untuk sumbu X
max_val = top5_sorted["total_sales_juta"].max()
upper_limit = math.ceil(max_val / 10) * 10
tick_vals = list(range(0, int(upper_limit) + 10, 10))
tick_texts = [f"{val} Juta" for val in tick_vals]

# Update tampilan
fig_top5.update_traces(
    textposition="inside",
    textfont_size=12,
    hovertemplate='%{y}<br>Rp %{x:,.2f} Juta<extra></extra>'
)

fig_top5.update_layout(
    showlegend=False,
    xaxis=dict(
        tickvals=tick_vals,
        ticktext=tick_texts,
        title="Total Penjualan"
    )
)

st.plotly_chart(fig_top5, use_container_width=True, key="top5_kopi")


# === Grafik: 🥧 Komposisi Penjualan per Time of Day) ===
st.subheader("🥧 Komposisi Penjualan per Time of Day")

# Hitung total penjualan per Time of Day
df_timeofday = filtered_df.groupby("Time_of_Day")["money"].sum().reset_index()
df_timeofday["money_juta"] = df_timeofday["money"] / 1_000_000
df_timeofday["label"] = df_timeofday["money_juta"].apply(lambda x: f"Rp {x:,.2f} Juta")

# Buat Pie Chart
fig_pie = px.pie(
    df_timeofday,
    names="Time_of_Day",
    values="money_juta",
    color_discrete_sequence=px.colors.qualitative.Pastel,
    hole=0.4,
)

# Tambahkan format hover dan label
fig_pie.update_traces(
    textinfo="percent+label",
    hovertemplate="<b>%{label}</b><br>Total: Rp %{value:,.2f} Juta",
    textfont_size=14
)

fig_pie.update_layout(
    title="Komposisi Penjualan Berdasarkan Time of Day",
    title_font_size=18,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)"
)

# Tampilkan di Streamlit
st.plotly_chart(fig_pie, use_container_width=True, key="penjualan_timeofday")


# === Grafik: 📊 Jumlah Transaksi per Time of Day ===
st.subheader("📊 Jumlah Transaksi per Time of Day")

# Hitung jumlah transaksi per Time_of_Day
count_data = filtered_df["Time_of_Day"].value_counts().reset_index()
count_data.columns = ["Time_of_Day", "Jumlah Transaksi"]

# Warna khusus untuk tiap kategori Time_of_Day
custom_colors = {
    "Morning": "#FFA07A",     # Salmon
    "Afternoon": "#20B2AA",   # LightSeaGreen
    "Night": "#9370DB"        # MediumPurple
}

# Buat grafik batang
fig_bar_count = px.bar(
    count_data,
    x="Time_of_Day",
    y="Jumlah Transaksi",
    color="Time_of_Day",
    text="Jumlah Transaksi",
    title="Frekuensi Transaksi Berdasarkan Time of Day",
    color_discrete_map=custom_colors,
    category_orders={"Time_of_Day": ["Morning", "Afternoon", "Night"]}
)

# Tambahan gaya visual
fig_bar_count.update_traces(
    textposition="outside",
    textfont_size=11,
    marker_line_color='white',
    marker_line_width=1
)

# Atur layout tema gelap
fig_bar_count.update_layout(
    plot_bgcolor="#2D2D2D",
    paper_bgcolor="#1F1F1F",
    font=dict(color="white", size=13),
    title_font=dict(size=15, color="white"),
    xaxis=dict(title="Time of Day", showgrid=False, color="white"),
    yaxis=dict(title="Jumlah Transaksi", showgrid=True, gridcolor="#444", color="white"),
    showlegend=False
)

st.plotly_chart(fig_bar_count, use_container_width=True, key="transaksi_timeofday")


# === Grafik: 📊 Rata-rata Penjualan per Transaksi per Jenis Kopi ===
st.subheader("💹 Rata-rata Penjualan per Transaksi per Jenis Kopi")

avg_per_kopi = (
    filtered_df.groupby("coffee_name")["money"]
    .mean()
    .reset_index()
    .sort_values(by="money", ascending=False)
)

avg_per_kopi["money_text"] = avg_per_kopi["money"].apply(format_rupiah_singkat)

fig_avg_kopi = px.bar(
    avg_per_kopi,
    x="coffee_name",
    y="money",
    color="coffee_name",
    labels={"money": "Rata-rata per Transaksi (Rp)", "coffee_name": "Jenis Kopi"},
    color_discrete_sequence=px.colors.qualitative.Prism,
    text=avg_per_kopi["money"].apply(lambda x: f"Rp {x:,.0f}".replace(",", ".")),
)

fig_avg_kopi.update_traces(
    textposition="outside",
    textfont=dict(size=11),
    hovertemplate='<b>%{x}</b><br>Rata-rata: %{customdata}<extra></extra>',
    customdata=avg_per_kopi["money_text"]
)

fig_avg_kopi.update_layout(
    plot_bgcolor="#2D2D2D",
    paper_bgcolor="#1F1F1F",
    font=dict(color="white", size=13),
    title_font_size=18,
    xaxis=dict(title="", tickangle=-45, color="white"),
    yaxis=dict(title="Rata-rata Penjualan (Rp)", color="white"),
    showlegend=False,
    margin=dict(t=60, b=100)
)

st.plotly_chart(fig_avg_kopi, use_container_width=True, key="rata_penjualan_jenis_kopi")


# === Grafik: 📈 Tren Pendapatan Harian per Time of Day ===
st.subheader("📈 Tren Pendapatan Harian per Time of Day")

# Hitung total pendapatan per hari per Time_of_Day
daily_trend = (
    filtered_df.groupby(["date", "Time_of_Day"])["money"]
    .sum()
    .reset_index()
    .sort_values(by="date")
)

# Buat grafik garis
fig_trend = px.line(
    daily_trend,
    x="date",
    y="money",
    color="Time_of_Day",
    markers=True,
    labels={
        "date": "Tanggal",
        "money": "Pendapatan (Rp)",
        "Time_of_Day": "Waktu"
    },
    color_discrete_sequence=px.colors.qualitative.Bold,
)

# Hover hanya tanggal dan nilai (tanpa waktu)
fig_trend.update_traces(
    hovertemplate="%{x|%d %b %Y}<br>Pendapatan: Rp %{y:,.0f}",
    line=dict(width=2),
    marker=dict(size=10)
)

fig_trend.update_layout(
    plot_bgcolor="#1A1B1E",
    paper_bgcolor="#121212",
    font=dict(color="#E0E0E0", size=13),
    xaxis=dict(color="#CCCCCC", showgrid=False),
    yaxis=dict(
        title="Pendapatan (Rp)",
        color="#CCCCCC",
        gridcolor="rgba(255,255,255,0.1)",
        tickformat=",",
        tickprefix="Rp ",
    ),
    margin=dict(t=40, b=80),
    legend=dict(title=None),
    hovermode="x unified"
)

st.plotly_chart(fig_trend, use_container_width=True, key="pendapatan_harian_timeofday")


# === Grafik: 💰📆 Penjualan Bulanan ===
st.subheader("💰📆 Penjualan Bulanan")

# Ambil bulan & tahun
filtered_df["Bulan"] = filtered_df["date"].dt.month
filtered_df["Tahun"] = filtered_df["date"].dt.year

# Mapping nama bulan ke Bahasa Indonesia
nama_bulan = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
    5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
    9: "September", 10: "Oktober", 11: "November", 12: "Desember"
}
filtered_df["Nama_Bulan"] = filtered_df["Bulan"].map(nama_bulan)

# Gabungkan bulan dan tahun untuk ditampilkan
filtered_df["Periode"] = filtered_df["Nama_Bulan"] + " " + filtered_df["Tahun"].astype(str)

# Use the Period for consistent grouping and sorting
filtered_df["Periode_dt_period"] = filtered_df["date"].dt.to_period("M")
df_sorted = filtered_df.sort_values("Periode_dt_period")

# Agregasi penjualan bulanan
penjualan_bulanan = (
    df_sorted.groupby(df_sorted["Periode_dt_period"])["money"]
    .sum()
    .reset_index()
)

# Convert Period to string for plotting
penjualan_bulanan["Periode"] = penjualan_bulanan["Periode_dt_period"].astype(str)
penjualan_bulanan["Total_Juta"] = (penjualan_bulanan["money"] / 1_000_000).round(2)

# Periksa apakah ada lebih dari satu bulan unik dalam data agregat
if penjualan_bulanan["Periode"].nunique() > 1:
    fig_penjualan = px.bar(
        penjualan_bulanan,
        x="Periode",
        y="Total_Juta",
        text="Total_Juta",
        color="Periode",
        color_discrete_sequence=px.colors.sequential.Viridis,
        labels={
            "Periode": "Bulan",
            "Total_Juta": "Total Penjualan (Rp Juta)"
        },
    )

    # Update teks & hover
    fig_penjualan.update_traces(
        texttemplate="Rp %{text} Juta",
        textposition="outside",
        hovertemplate="<b>Bulan:</b> %{x}<br><b>Total Penjualan:</b> Rp %{y} Juta<extra></extra>"
    )

    fig_penjualan.update_layout(
        xaxis_tickangle=-45,
        yaxis_title="Total Penjualan (Rp Juta)",
        xaxis_title="Periode"
    )

    st.plotly_chart(fig_penjualan, use_container_width=True)
else:
    st.info("ℹ️ Grafik penjualan bulanan tidak ditampilkan karena data hanya mencakup satu bulan.")



# === Profil Sidebar ===
with st.sidebar:
    st.markdown("### 👤 Profil")
    st.markdown(f"**{username.title()}**")
    st.markdown(f"Role: `{role}`")
    
with st.sidebar:
    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.switch_page("Dashboard_Analisis_Penjualan_Kopi.py")

# === Footer ===
st.markdown("---")
st.caption("© 2025 Coffee Shop Analyst Dashboard Created By Arjun Yuda Firwanda")
