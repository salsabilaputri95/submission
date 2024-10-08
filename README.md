# Panduan Penggunaan Dashboard Analisis Data E-Commerce

## Deskripsi Proyek
Proyek ini bertujuan untuk menganalisis data terkait pesanan, produk, pelanggan, dan item pesanan, serta memanfaatkan visualisasi data untuk mendapatkan wawasan bisnis yang berharga.

### Membuat file .ipynb untuk menjalankan streamlit
1. Upload direktori submission ke google drive
2. Masuk ke direktori dashboard lalu baut file .ipynb dengan nama Run_streamlit.ipynb
### Menjalankan Dashboard
1. install sreamlite
    !pip install streamlit -q
2. Dapatkan ip
    !wget -q -O - ipv4.icanhazip.com
3. Buat file dashboard.py
   %%writefile dashboard.py
    import streamlit as st
    import pandas as pd
    import matplotlib.pyplot as plt      
    ....
4. Run streamlite
    ! streamlit run dashboard.py & npx localtunnel --port 8501
5. Ketik y
6. KLik link yang di berikan
