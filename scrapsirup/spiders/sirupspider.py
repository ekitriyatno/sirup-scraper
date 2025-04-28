import scrapy
from scrapsirup.items import ScrapsirupItem
from scrapsirup.settings import KEYWORDS


class SirupspiderSpider(scrapy.Spider):
    name = "sirupspider"
    allowed_domains = ["sirup.lkpp.go.id"]
    start_urls = ["https://sirup.lkpp.go.id/sirup/caripaketctr/index"]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                },
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "Referer": "https://sirup.lkpp.go.id",
                },
            )

    async def parse(self, response):
        page = response.meta['playwright_page']
         # Hilangkan atau sembunyikan elemen yang menghalangi
        
        close_button = page.locator(".modal-content-new button.close")
        if await close_button.is_visible(timeout=5000): # Cek apakah visible dalam 5 detik
            await close_button.click()
        else:
            print("Modal atau tombol close tidak muncul dalam waktu singkat.")

        await page.wait_for_selector("#searchResult tbody tr")

        try:
            keywords = KEYWORDS
            for keyword in keywords:
                # await page.locator('#bulan3').check()
                await page.locator('#bulan4').check()
                if keyword == "Makan":
                    await page.type('#minim', "200000000", delay=50)
                    await page.locator('button.js__btn-filter-pagu').click()
                await page.locator('#jenis1').check()
                await page.locator('#pdntrue').check()
                await page.type('#searchbox' , keyword, delay=100)
                # await page.locator('#searchbox').press("Tab")
                await page.wait_for_selector("#searchResult tbody tr")
                while True:
                    link_elements = await page.locator("a[data-toggle='modal']").all()
                    for link_element in link_elements:
                        if await link_element.is_visible():
                            href = await link_element.get_attribute("href")
                            if href:
                                url_join = response.urljoin(href)
                                yield scrapy.Request(
                                    url=url_join,
                                    meta={
                                        "playwright": True,
                                        "playwright_include_page": False,
                                    },
                                    callback=self.parse_detail,
                                )
                            else:
                                self.logger.warning("Link tidak ditemukan atau tidak valid.")
                        else:
                            self.logger.warning("Link element tidak visible.")

                    next_disable = await page.query_selector("li.paginate_button.next.disabled")
                    next_button = await page.query_selector("#searchResult_next a")
                    if next_disable is None and next_button:
                        await next_button.click()
                        # await page.wait_for_timeout(1000) #add delay
                    else:
                        break

                await page.reload()
                await page.wait_for_selector("#searchResult tbody tr")

        except TimeoutError:
            self.logger.error("Timeout terjadi saat menunggu elemen.")
        except Exception as e:
            self.logger.error(f"Error dalam memproses AJAX: {e}")


    async def parse_detail(self, response):
        # Ekstraksi data dari tabel utama
        sirup_item = ScrapsirupItem()

        kode_rup = response.css("td:contains('Kode RUP') + td::text").get()
        nama_paket = response.css("td:contains('Nama Paket') + td::text").get()
        nama_klpd = response.css("td:contains('Nama KLPD') + td::text").get()
        satuan_kerja = response.css("td:contains('Satuan Kerja') + td::text").get()
        tahun_anggaran = response.css("td:contains('Tahun Anggaran') + td::text").get()
        volume_pekerjaan = response.css("td:contains('Volume Pekerjaan') + td::text").get()
        total_pagu = response.css("td:contains('Total Pagu') + td::text").get()
        metode_pemilihan = response.css("td:contains('Metode Pemilihan') + td::text").get()
        tanggal_umumkan_paket = response.css("td:contains('Tanggal Umumkan Paket') + td::text").get()
        
        inner_table = response.css(".table-striped tr")
        
        # Ekstraksi data dari tabel Lokasi Pekerjaan
        provinsi = inner_table.css('td:nth-child(2)::text').get()
        kabupaten_kota = inner_table.css('td:nth-child(3)::text').get()
        detail_lokasi = inner_table.css('td:nth-child(4)::text').get()

        # Ekstraksi data dari tabel Sumber Dana
        sumber_dana = []
        sumber_dana_rows = response.css("td:contains('Sumber Dana') table tr")[1:-1] # Skip header and total
        for row in sumber_dana_rows:
            sumber = row.css("td:nth-child(2)::text").get()
            tahun = row.css("td:nth-child(3)::text").get()
            klpd = row.css("td:nth-child(4)::text").get()
            mak = row.css("td:nth-child(5)::text").get()
            pagu = row.css("span::text").get()
            sumber_dana.append({
                "sumber": sumber,
                "tahun": tahun,
                "klpd": klpd,
                "mak": mak,
                "pagu": pagu,
            })

        # Ekstraksi data dari tabel Jenis Pengadaan
        jenis_pengadaan = []
        jenis_pengadaan_rows = response.css("td:contains('Jenis Pengadaan') table tr")[1:] # Skip header
        for row in jenis_pengadaan_rows:
            jenis = row.css("td:nth-child(2)::text").get()
            pagu = row.css("td:nth-child(3)::text").get()
            jenis_pengadaan.append({
                "jenis": jenis,
                "pagu": pagu,
            })
        
        # Ekstraksi data dari tabel Pengadaan Berkelanjutan
        pengadaan_berkelanjutan = {}
        aspek = inner_table.css('td span:nth-child(1)::text').getall()
        if aspek:
            pengadaan_berkelanjutan["ekonomi"] = aspek[0]
            pengadaan_berkelanjutan["sosial"] = aspek[1]
            pengadaan_berkelanjutan["lingkungan"] = aspek[2]
        else:
            pengadaan_berkelanjutan["ekonomi"] = None
            pengadaan_berkelanjutan["sosial"] = None
            pengadaan_berkelanjutan["lingkungan"] = None

        # Ekstraksi data dari tabel Pemanfaatan Barang/Jasa
        tanggal = inner_table.css('.mid::text').getall()[2:]
        if tanggal:
            pemanfaatan_barang_jasa = {}
            pemanfaatan_barang_jasa["mulai"] = tanggal[0]
            pemanfaatan_barang_jasa["akhir"] = tanggal[1]

        # Ekstraksi data dari tabel Jadwal Pelaksanaan Kontrak
            jadwal_pelaksanaan_kontrak = {}
            jadwal_pelaksanaan_kontrak["mulai"] = tanggal[4]
            jadwal_pelaksanaan_kontrak["akhir"] = tanggal[5]
        
        # Ekstraksi data dari tabel Jadwal Pemilihan Penyedia
            jadwal_pemilihan_penyedia = {}
            jadwal_pemilihan_penyedia["mulai"] = tanggal[8]
            jadwal_pemilihan_penyedia["akhir"] = tanggal[9]
        else:
            pemanfaatan_barang_jasa = {}
            pemanfaatan_barang_jasa["mulai"] = None
            pemanfaatan_barang_jasa["akhir"] = None

            jadwal_pelaksanaan_kontrak = {}
            jadwal_pelaksanaan_kontrak["mulai"] = None
            jadwal_pelaksanaan_kontrak["akhir"] = None

            jadwal_pemilihan_penyedia = {}
            jadwal_pemilihan_penyedia["mulai"] = None
            jadwal_pemilihan_penyedia["akhir"] = None


        sirup_item["kode_rup"] = kode_rup
        sirup_item["nama_paket"] = nama_paket
        sirup_item["nama_klpd"] = nama_klpd
        sirup_item["satuan_kerja"] = satuan_kerja
        sirup_item["tahun_anggaran"] = tahun_anggaran
        sirup_item["provinsi"] = provinsi
        sirup_item["kabupaten_kota"] = kabupaten_kota
        sirup_item["detail_lokasi"] = detail_lokasi
        sirup_item["volume_pekerjaan"] = volume_pekerjaan
        sirup_item["total_pagu"] = total_pagu
        sirup_item["metode_pemilihan"] = metode_pemilihan
        sirup_item["tanggal_umumkan_paket"] = tanggal_umumkan_paket
        sirup_item["jenis_pengadaan"] = jenis_pengadaan[0]['jenis']
        sirup_item["sumber_dana"] = sumber_dana
        sirup_item["aspek_ekonomi"] = pengadaan_berkelanjutan.get('ekonomi')
        sirup_item["aspek_sosial"] = pengadaan_berkelanjutan.get('sosial')
        sirup_item["aspek_lingkungan"] = pengadaan_berkelanjutan.get('lingkungan')
        sirup_item["pemanfaatan_barang_jasa_mulai"] = pemanfaatan_barang_jasa.get('mulai')
        sirup_item["pemanfaatan_barang_jasa_akhir"] = pemanfaatan_barang_jasa.get('akhir')
        sirup_item["jadwal_pelaksanaan_kontrak_mulai"] = jadwal_pelaksanaan_kontrak.get('mulai')
        sirup_item["jadwal_pelaksanaan_kontrak_akhir"] = jadwal_pelaksanaan_kontrak.get('akhir')
        sirup_item["jadwal_pemilihan_penyedia_mulai"] = jadwal_pemilihan_penyedia.get('mulai')
        sirup_item["jadwal_pemilihan_penyedia_akhir"] =  jadwal_pemilihan_penyedia.get('akhir')
        
        yield sirup_item