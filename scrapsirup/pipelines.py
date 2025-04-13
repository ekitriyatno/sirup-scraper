# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import psycopg2
import asyncpg
from asyncpg import ConnectionDoesNotExistError 
from datetime import datetime
from scrapy.exceptions import DropItem
from scrapy.exceptions import CloseSpider
import calendar
import json
# from dataclasses import dataclass, field, fields, InitVar, asdict

class ConvertDatePipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        bulan_indonesia_inggris = {
            "Januari": "January",
            "Februari": "February",
            "Maret": "March",
            "April": "April",
            "Mei": "May",
            "Juni": "June",
            "Juli": "July",
            "Agustus": "August",
            "September": "September",
            "Oktober": "October",
            "November": "November",
            "Desember": "December",
        }

        try:
            # Fungsi untuk mendapatkan tanggal akhir bulan
            def get_last_day_of_month(year, month):
                _, last_day = calendar.monthrange(year, month)
                return last_day

            # Pemanfaatan Barang/Jasa
            pbjm_bulan_indo, pbjtm = adapter["pemanfaatan_barang_jasa_mulai"].split()
            pbja_bulan_indo, pbjta = adapter["pemanfaatan_barang_jasa_akhir"].split()
            pbjm_bulan_inggris = bulan_indonesia_inggris[pbjm_bulan_indo]
            pbja_bulan_inggris = bulan_indonesia_inggris[pbja_bulan_indo]
            pbjm_inggris = f"{pbjm_bulan_inggris} {pbjtm}"
            pbja_inggris = f"{pbja_bulan_inggris} {pbjta}"

            pbjm_objek = datetime.strptime(pbjm_inggris, "%B %Y")
            pbja_objek = datetime.strptime(pbja_inggris, "%B %Y")

            adapter["pemanfaatan_barang_jasa_mulai"] = pbjm_objek.strftime("%Y-%m-01")
            adapter["pemanfaatan_barang_jasa_akhir"] = pbja_objek.strftime(f"%Y-%m-{get_last_day_of_month(pbja_objek.year, pbja_objek.month)}")

            # Jadwal Pelaksanaan Kontrak
            jpkm_bulan_indo, jpktm = adapter["jadwal_pelaksanaan_kontrak_mulai"].split()
            jpka_bulan_indo, jpkta = adapter["jadwal_pelaksanaan_kontrak_akhir"].split()
            jpkm_bulan_inggris = bulan_indonesia_inggris[jpkm_bulan_indo]
            jpka_bulan_inggris = bulan_indonesia_inggris[jpka_bulan_indo]
            jpkm_inggris = f"{jpkm_bulan_inggris} {jpktm}"
            jpka_inggris = f"{jpka_bulan_inggris} {jpkta}"

            jpkm_objek = datetime.strptime(jpkm_inggris, "%B %Y")
            jpka_objek = datetime.strptime(jpka_inggris, "%B %Y")

            adapter["jadwal_pelaksanaan_kontrak_mulai"] = jpkm_objek.strftime("%Y-%m-01")
            adapter["jadwal_pelaksanaan_kontrak_akhir"] = jpka_objek.strftime(f"%Y-%m-{get_last_day_of_month(jpka_objek.year, jpka_objek.month)}")

            # Jadwal Pemilihan Penyedia
            jppm_bulan_indo, jpptm = adapter["jadwal_pemilihan_penyedia_mulai"].split()
            jppa_bulan_indo, jppta = adapter["jadwal_pemilihan_penyedia_akhir"].split()
            jppm_bulan_inggris = bulan_indonesia_inggris[jppm_bulan_indo]
            jppa_bulan_inggris = bulan_indonesia_inggris[jppa_bulan_indo]
            jppm_inggris = f"{jppm_bulan_inggris} {jpptm}"
            jppa_inggris = f"{jppa_bulan_inggris} {jppta}"

            jppm_objek = datetime.strptime(jppm_inggris, "%B %Y")
            jppa_objek = datetime.strptime(jppa_inggris, "%B %Y")

            adapter["jadwal_pemilihan_penyedia_mulai"] = jppm_objek.strftime("%Y-%m-01")
            adapter["jadwal_pemilihan_penyedia_akhir"] = jppa_objek.strftime(f"%Y-%m-{get_last_day_of_month(jppa_objek.year, jppa_objek.month)}")
            adapter["sumber_dana"] = json.dumps(adapter["sumber_dana"])

            return item
        except (ValueError, KeyError) as e:
            print(f"Error konversi tanggal: {e}")
            return item

        
class SaveToPostgresPipeline:
    async def __init__(self, db_settings, spider):
        """Inisialisasi koneksi database"""
        self.db_settings = db_settings
        try:
            self.pool = await asyncpg.create_pool(user= self.db_settings['user'],
                                                password= self.db_settings['password'],
                                                database= self.db_settings['database'],
                                                host= self.db_settings['host'],
                                                port= self.db_settings['port'])
            self.conn = await self.pool.acquire()
        except ConnectionDoesNotExistError as e:
            spider.logger.error(f"Error koneksi ke PostgreSQL: {e}")
            raise DropItem(f"Error koneksi: {e}")
        except Exception as e:
            spider.logger.error(f"Error membuka koneksi ke PostgreSQL: {e}")
            raise CloseSpider(f"Error membuka koneksi: {e}")

    @classmethod
    async def from_crawler(cls, crawler):
        """Mengambil pengaturan dari settings.py"""
        db_settings = crawler.settings.get("DATABASE")
        return cls(db_settings)
    
    # async def open_spider(self, spider):
    #     """Membuka koneksi database saat spider dibuka"""
    #     try:
    #         self.pool = await asyncpg.create_pool(**self.db_settings)
    #         self.conn = await self.pool.acquire()
    #     except ConnectionDoesNotExistError as e:
    #         spider.logger.error(f"Error koneksi ke PostgreSQL: {e}")
    #         raise DropItem(f"Error koneksi: {e}")
    #     except Exception as e:
    #         spider.logger.error(f"Error membuka koneksi ke PostgreSQL: {e}")
    #         raise CloseSpider(f"Error membuka koneksi: {e}")
        
    async def process_item(self, item, spider):
        if self.conn is None:
            spider.logger.error("Koneksi database tidak tersedia.")
            raise DropItem(f"Koneksi database tidak tersedia: {item}")
        
        try:
            # Menggunakan asyncpg untuk menyimpan item ke PostgreSQL
            query_sirup = "INSERT INTO scraped_sirup (kode_rup, nama_paket, nama_klpd, satuan_kerja, tahun_anggaran, provinsi, kabupaten_kota, detail_lokasi, volume_pekerjaan, total_pagu, metode_pemilihan, tanggal_umumkan_paket, jenis_pengadaan,sumber_dana, aspek_ekonomi, aspek_sosial, aspek_lingkungan, pemanfaatan_barang_jasa_mulai, pemanfaatan_barang_jasa_akhir, jadwal_pelaksanaan_kontrak_mulai, jadwal_pelaksanaan_kontrak_akhir, jadwal_pemilihan_penyedia_mulai, jadwal_pemilihan_penyedia_akhir) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23)"
            await self.conn.execute(query_sirup,
                            item['kode_rup'],
                            item['nama_paket'],
                            item['nama_klpd'],
                            item['satuan_kerja'],
                            item['tahun_anggaran'],
                            item['provinsi'],
                            item['kabupaten_kota'],
                            item['detail_lokasi'],
                            item['volume_pekerjaan'],
                            item['total_pagu'],
                            item['metode_pemilihan'],
                            item['tanggal_umumkan_paket'],
                            item['jenis_pengadaan'],
                            item['sumber_dana'],
                            item['aspek_ekonomi'],
                            item['aspek_sosial'],
                            item['aspek_lingkungan'],
                            item['pemanfaatan_barang_jasa_mulai'],
                            item['pemanfaatan_barang_jasa_akhir'],
                            item['jadwal_pelaksanaan_kontrak_mulai'],
                            item['jadwal_pelaksanaan_kontrak_akhir'],
                            item['jadwal_pemilihan_penyedia_mulai'],
                            item['jadwal_pemilihan_penyedia_akhir']
                        )                
            # self.pool.commit()
            return item

        except Exception as e:
            spider.logger.error(f"Error menyimpan item ke PostgreSQL: {e}")
            raise DropItem(f"Error menyimpan item: {item}")
        

    async def close_spider(self, spider):
        """Menutup koneksi database setelah scraping selesai"""
        if self.pool:
            self.pool.close()

class ScrapsirupPipeline:
    def process_item(self, item, spider):
        return item
