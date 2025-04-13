# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapsirupItem(scrapy.Item):
    kode_rup = scrapy.Field()
    nama_paket = scrapy.Field()
    nama_klpd = scrapy.Field()
    satuan_kerja = scrapy.Field()
    tahun_anggaran = scrapy.Field()
    provinsi  = scrapy.Field()
    kabupaten_kota  = scrapy.Field()
    detail_lokasi  = scrapy.Field()
    volume_pekerjaan = scrapy.Field()
    total_pagu = scrapy.Field()
    metode_pemilihan = scrapy.Field()
    tanggal_umumkan_paket = scrapy.Field()
    jenis_pengadaan = scrapy.Field()
    sumber_dana  = scrapy.Field()
    aspek_ekonomi = scrapy.Field()
    aspek_sosial = scrapy.Field()
    aspek_lingkungan = scrapy.Field()
    pemanfaatan_barang_jasa_mulai = scrapy.Field()
    pemanfaatan_barang_jasa_akhir = scrapy.Field()
    jadwal_pelaksanaan_kontrak_mulai = scrapy.Field()
    jadwal_pelaksanaan_kontrak_akhir = scrapy.Field()
    jadwal_pemilihan_penyedia_mulai = scrapy.Field()
    jadwal_pemilihan_penyedia_akhir = scrapy.Field()
