# 🕸️ Scraping Data Tender Pemerintah dari SiRUP LKPP

Project ini mengumpulkan data tender dari portal SiRUP LKPP (https://sirup.lkpp.go.id) menggunakan Scrapy. Data digunakan untuk analisis pasar potensial, monitoring kegiatan pengadaan, dan insight bisnis — terutama untuk tender yang relevan dengan produk atau jasa yang ingin kita tawarkan.

## 🚀 Teknologi yang Digunakan

- Python 3.10+
- Scrapy
- PostgreSQL (via asyncpg)
- Pandas, Matplotlib
- Jupyter Notebook

## 📄 Data yang Dikumpulkan

Contoh field:
- 'kode_rup'
- 'nama_paket'
- 'nama_klpd'
- 'satuan_kerja'
- 'tahun_anggaran'
- 'provinsi', 'kabupaten_kota'
- 'volume_pekerjaan', 'total_pagu'
- 'metode_pemilihan'
- Aspek keberlanjutan: 'ekonomi', 'sosial', 'lingkungan'
- Tanggal & jadwal pemanfaatan mendetail

## 📊 Analisis Data

Notebook 'notebook/analisis_singkat.ipynb' berisi:
- Contoh cleansing data sederhana
- Distribusi tender per provinsi
- Export data ke csv

## 🔧 Cara Menggunakan

1. **Clone repositori:**
   '''bash
   git clone https://github.com/ekitriyatno/sirup-scraper.git
   cd scrapsirup
   '''

2. **Install dependencies:**
   '''bash
   pip install -r requirements.txt
   '''

3. **Konfigurasi 'settings.py':**
   - Set 'ROBOTSTXT_OBEY = False'
   - Tambahkan pipeline ke 'ITEM_PIPELINES'
   - Tambahkan:
     '''python
     DOWNLOAD_HANDLERS = {
         "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
         "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
     }
     '''
   - Tambahkan:
     ITEM_PIPELINES = {
      "scrapsirup.pipelines.ConvertDatePipeline": 300,
      "scrapsirup.pipelines.SaveToMysqlPipeline": 400,
      } 
   - Set 'USER_AGENT' agar tidak diblokir:
     '''python
     USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
     '''
   - Tentukan:
     '''python
     KEYWORDS = ['minuman segar', 'susu bayi', ...]  # sesuaikan dengan kebutuhan
     '''
   - Lengkapi pengaturan koneksi MySql:
     '''python
     DATABASE = {
         'host': 'localhost',
         'user': 'your_user',
         'password': 'your_password',
         'database': 'your_database',
         'port': '5432',
     }
     '''

4. **Jalankan spider:**
   '''bash
   scrapy crawl sirupspider
   '''
