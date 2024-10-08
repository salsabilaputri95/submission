import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import folium
from streamlit_folium import folium_static

# Memuat dataset
merged_df = pd.read_csv('merged_dataset.csv')
merged_df['order_purchase_timestamp'] = pd.to_datetime(merged_df['order_purchase_timestamp'])

# Judul dan sidebar untuk filter
st.title('Dashboard Analisis Data E-Commerce')

st.sidebar.header('Opsi Filter')
product_category = st.sidebar.selectbox('Pilih Kategori Produk:', merged_df['product_category_name'].unique())
date_range = st.sidebar.date_input("Pilih Rentang Tanggal", [])

# Filter dataset berdasarkan pilihan
filtered_df = merged_df[merged_df['product_category_name'] == product_category]

if date_range:
    start_date, end_date = date_range[0], date_range[-1]
    filtered_df = filtered_df[(filtered_df['order_purchase_timestamp'] >= start_date) & 
                              (filtered_df['order_purchase_timestamp'] <= end_date)]

# Analisis korelasi antara jenis produk dan frekuensi pembelian
st.subheader('Korelasi antara Jenis Produk dan Frekuensi Pembelian')

# Menghitung frekuensi pembelian per pelanggan dan per kategori produk
freq_df = merged_df.groupby(['customer_id', 'product_category_name']).agg({
    'order_id': 'count'
}).reset_index()
freq_df.columns = ['customer_id', 'product_category_name', 'purchase_frequency']

# Visualisasi hubungan jenis produk dengan frekuensi pembelian
fig_corr = px.scatter(freq_df, 
                      x='product_category_name', 
                      y='purchase_frequency', 
                      title='Korelasi antara Jenis Produk dan Frekuensi Pembelian',
                      labels={'product_category_name': 'Kategori Produk', 'purchase_frequency': 'Frekuensi Pembelian'},
                      height=400,
                      color_discrete_sequence=px.colors.qualitative.Vivid)
st.plotly_chart(fig_corr)

st.write("""
Grafik scatter di atas menggambarkan hubungan antara jenis produk dan frekuensi pembelian pelanggan.
""")

# Rasio repeat order vs single order
st.subheader('Rasio Repeat Order vs Single Order')

# Menghitung total pesanan yang dilakukan oleh setiap pelanggan
customer_order_summary = merged_df.groupby('customer_unique_id')['order_id'].count().reset_index(name='Order Count')

# Mengidentifikasi pelanggan yang melakukan pemesanan berulang
repeat_customers = customer_order_summary[customer_order_summary['Order Count'] > 1].shape[0]

# Mengidentifikasi pelanggan yang melakukan pemesanan sekali
one_time_customers = customer_order_summary[customer_order_summary['Order Count'] == 1].shape[0]

# Menghitung total pelanggan
total_customers_in_summary = customer_order_summary.shape[0]

# Menghitung rasio pemesanan berulang dan pemesanan sekali
repeat_ratio = repeat_customers / total_customers_in_summary * 100
one_time_ratio = one_time_customers / total_customers_in_summary * 100

# Visualisasi rasio pelanggan pemesanan berulang vs pemesanan sekali dengan pie chart
customer_labels = ['Pelanggan Berulang', 'Pelanggan Satu Kali']
customer_sizes = [repeat_ratio, one_time_ratio]
customer_colors = ['#ffcccb', '#add8e6']

fig, ax = plt.subplots(figsize=(5, 5))
ax.pie(customer_sizes, labels=customer_labels, colors=customer_colors, autopct='%1.1f%%', startangle=90)
ax.set_title('Rasio Pelanggan Berulang vs Pelanggan Satu Kali', fontsize=16)
ax.axis('equal')  # Equal aspect ratio ensures that pie chart is drawn as a circle

# Tampilkan pie chart di Streamlit
st.pyplot(fig)

# Ringkasan dalam bentuk teks di Streamlit
st.write(f"""
Rasio pelanggan yang melakukan repeat order adalah {repeat_ratio:.2f}% 
dibandingkan dengan {one_time_ratio:.2f}% yang hanya melakukan satu kali pembelian.
""")

# Analisis RFM
rfm_df = filtered_df.groupby('customer_id').agg({
    'order_purchase_timestamp': lambda x: (pd.Timestamp.now() - x.max()).days,
    'order_id': 'count',
    'price': 'sum'
}).reset_index()

rfm_df.columns = ['customer_id', 'Recency', 'Frequency', 'Monetary']

# Segmentasi pelanggan berdasarkan nilai RFM
def rfm_segmentation(row):
    if row['Recency'] <= 30 and row['Frequency'] > 5:
        return 'Nilai Tinggi'
    elif row['Recency'] > 30 and row['Frequency'] > 1:
        return 'Churning'
    else:
        return 'Nilai Rendah'

rfm_df['Segment'] = rfm_df.apply(rfm_segmentation, axis=1)

# Visualisasi segmen RFM
st.subheader('Segmen RFM')
fig_rfm = px.scatter(rfm_df, 
                      x='Recency', 
                      y='Monetary', 
                      size='Frequency', 
                      color='Segment',  # Menggunakan segmen sebagai warna
                      title='Analisis RFM: Segmen Pelanggan',
                      labels={'Recency': 'Recency (hari)', 'Monetary': 'Monetary (Total Belanja)', 'Frequency': 'Frekuensi'},
                      hover_name='customer_id',
                      height=400,
                      color_discrete_sequence=px.colors.qualitative.Set3)
st.plotly_chart(fig_rfm)

st.write("""
Grafik sebar di atas memvisualisasikan metrik RFM, di mana setiap titik mewakili seorang pelanggan. 
Sumbu menggambarkan nilai Recency dan Monetary, sementara ukuran setiap titik menunjukkan 
Frekuensi pembelian. Pelanggan dikelompokkan berdasarkan perilaku pembelian mereka.
""")



# Pesanan dari waktu ke waktu
st.subheader('Pesanan dari Waktu ke Waktu')
orders_over_time = filtered_df.groupby(filtered_df['order_purchase_timestamp'].dt.to_period('M')).size()

plt.figure(figsize=(10, 6))
orders_over_time.plot(kind='line', marker='o')
plt.title('Pesanan Bulanan')
plt.xlabel('Bulan')
plt.ylabel('Jumlah Pesanan')
plt.xticks(rotation=45)
st.pyplot(plt)

st.write("""
Grafik garis di atas menunjukkan jumlah pesanan setiap bulan. 
Ini sangat membantu kita dalam memahami tren pembelian dari waktu ke waktu dan mengidentifikasi periode puncak.
""")

# Pendapatan total dari waktu ke waktu
st.subheader('Pendapatan Total dari Waktu ke Waktu')
revenue_over_time = filtered_df.groupby(filtered_df['order_purchase_timestamp'].dt.to_period('M'))['price'].sum()

plt.figure(figsize=(10, 6))
revenue_over_time.plot(kind='bar', color='orange')
plt.title('Pendapatan Bulanan')
plt.xlabel('Bulan')
plt.ylabel('Total Pendapatan')
plt.xticks(rotation=45)
st.pyplot(plt)

st.write("""
Grafik batang di atas menunjukkan total pendapatan setiap bulan. 
Ini memberikan gambaran tentang kinerja finansial e-commerce seiring berjalannya waktu, 
dan membantu dalam analisis perbandingan.
""")

# 10 Produk teratas berdasarkan pendapatan
st.subheader('10 Produk Teratas berdasarkan Pendapatan')
top_products = filtered_df.groupby('product_id')['price'].sum().nlargest(10).reset_index()
top_products['short_product_id'] = top_products['product_id'].str[:5]  # Mengambil 5 karakter pertama

plt.figure(figsize=(10, 6))
sns.barplot(x='short_product_id', y='price', data=top_products, palette='magma')
plt.title('10 Produk Teratas berdasarkan Pendapatan')
plt.xlabel('Product ID (Singkat)')
plt.ylabel('Total Pendapatan')
st.pyplot(plt)

st.write("""
Grafik di atas menunjukkan 10 produk teratas berdasarkan total pendapatan. 
**Product ID** ditampilkan dalam format pendek (5 karakter pertama dalam product_id) untuk memudahkan pemahaman. 
**Total Pendapatan** merepresentasikan jumlah pendapatan yang dihasilkan dari masing-masing produk. 
Warna pada grafik memberikan visualisasi yang menarik untuk mengidentifikasi peringkat produk.
""")

# Geoanalisis (contoh jika ada data geografis)
if 'geolocation_city' in merged_df.columns:
    geo_df = filtered_df.groupby('geolocation_city')['order_id'].count().reset_index()
    geo_df.columns = ['Kota', 'Total Pesanan']

    st.subheader('Geoanalisis: Distribusi Pesanan berdasarkan Kota')
    m = folium.Map(location=[-2.548926, 118.0148634], zoom_start=5)  # Berpusat di Indonesia
    for index, row in geo_df.iterrows():
        folium.CircleMarker([row['Kota'], row['Total Pesanan']], radius=row['Total Pesanan'] / 10).add_to(m)
    folium_static(m)

# Metrik kunci
st.subheader('Metrik Kunci')
total_orders = filtered_df['order_id'].nunique()
total_revenue = filtered_df['price'].sum()
total_customers = filtered_df['customer_id'].nunique()

st.metric(label="Total Pesanan", value=total_orders)
st.metric(label="Total Pendapatan", value=f"${total_revenue:,.2f}")
st.metric(label="Total Pelanggan Unik", value=total_customers)

# Bagian kesimpulan
st.subheader('Kesimpulan')
st.write("""
Dashboard ini memberikan gambaran umum tentang kinerja e-commerce berdasarkan kategori produk yang dipilih dan 
rentang tanggal. Metrik kunci dan visualisasi memungkinkan untuk mendapatkan wawasan cepat 
tentang perilaku pelanggan, tren pendapatan, dan kinerja produk.
""")

st.caption('Copyright (c) SALSABILA PUTRI 2024')
