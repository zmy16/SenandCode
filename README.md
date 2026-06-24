# SenandCode ✨

> *Bahasa pemrograman puitis dalam Bahasa Indonesia*

**SenandCode** — dari *senandika* (dialog batin yang puitis) + *code* — adalah bahasa pemrograman yang indah seperti puisi. Setiap baris adalah puisi. Setiap program adalah antologi.

## Filosofi

Kode seharusnya indah. Bukan hanya berfungsi — ia harus berbicara. SenandCode lahir dari keyakinan bahwa **menulis program adalah menulis puisi**: setiap kata dipilih dengan hati-hati, setiap baris mengalir alami, dan setiap program menceritakan kisahnya sendiri.

> *"Simpan 5 dalam umur"* — bukan hanya assignment, ini adalah puisi mini.

## Instalasi

```bash
pip install senandika
```

Atau jalankan langsung dari source:

```bash
git clone https://github.com/username/SenandCode
cd SenandCode
python -m senandika program.sen
```

## Cara Menjalankan

Jalankan file `.sen`:

```bash
senandika program.sen
# atau
python -m senandika program.sen
```

REPL mode interaktif:

```bash
senandika
# atau
python -m senandika
```

## Sintaks

### Dasar
| Konsep | SenandCode | Arti |
|--------|------------|------|
| Cetak | `lukiskan "Halo";` | Mencetak ke layar |
| Variable | `simpan 5 dalam x;` | Simpan nilai dalam variabel |
| Gabung teks | `lukiskan "Halo " lalu nama;` | String concatenation |
| Input | `dengarkan nama;` | Input dari pengguna |
| Komentar | `// ini komentar` | Baris komentar |

### Percabangan
```
seandainya x > 5:
    lukiskan "Besar";
atau jika x == 5:
    lukiskan "Pas";
jika tidak:
    lukiskan "Kecil";
selesai
```

### Perulangan
```
// For loop
untuk i = 1 sampai 5 lakukan:
    lukiskan "Hitungan: " lalu i;
selesai

// While loop
selagi x > 0 lakukan:
    lukiskan x;
    simpan x - 1 dalam x;
selesai
```

### Fungsi
```
puisi luasLingkaran(r):
    simpan 3.14 dalam pi;
    kembalikan pi * r * r;
selesai

lukiskan luasLingkaran(7);
```

### OOP (Kelas)
```
wajah Orang:
    simpan "" dalam nama;
    simpan 0 dalam umur;

    puisi lahir(nama, umur):
        simpan nama dalam diri.nama;
        simpan umur dalam diri.umur;
    selesai

    puisi perkenalan():
        lukiskan "Aku " lalu diri.nama lalu ", " lalu diri.umur lalu " tahun.";
    selesai
selesai

simpan ciptakan Orang("Asep", 25) dalam asep;
asep.perkenalan();
```

### Penanganan Error
```
coba:
    simpan 10 / 0 dalam x;
raih e:
    lukiskan "Error: " lalu e;
akhirnya:
    lukiskan "Beres.";
selesai
```

### Boolean & Null
```
simpan benar dalam aktif;   // boolean true
simpan palsu dalam nonaktif; // boolean false
simpan hampa dalam kosong;   // null

seandainya aktif dan bukan nonaktif:
    lukiskan "Aktif!";
selesai
```

## Keyword Reference

| Keyword | Fungsi |
|---------|--------|
| `simpan` | Menyimpan nilai ke variabel |
| `dalam` | Bagian dari assignment |
| `lukiskan` | Mencetak output |
| `lalu` | Concatenation operator |
| `seandainya` | If (percabangan) |
| `atau jika` | Else if |
| `jika tidak` | Else |
| `untuk` | For loop |
| `sampai` | Range dalam for loop |
| `langkah` | Step dalam for loop |
| `lakukan` | Memulai body blok |
| `selagi` | While loop |
| `puisi` | Mendeklarasikan fungsi |
| `kembalikan` | Return value |
| `dengarkan` | Input dari user |
| `benar` / `palsu` | Boolean true/false |
| `hampa` | Null value |
| `dan` / `atau` / `bukan` | Logical and/or/not |
| `coba` / `raih` / `akhirnya` | Try/catch/finally |
| `lemparkan` | Throw exception |
| `wajah` | Deklarasi kelas |
| `diri` | This reference |
| `ciptakan` | Membuat objek baru |
| `warisi` | Inheritance |
| `selesai` | Akhir blok |
| `hening` | Break loop |
| `sambung` | Continue loop |

## Contoh Program

### Halo Dunia
```
lukiskan "Halo, Dunia!";
```

### Fungsi Sederhana
```
puisi sapa(nama):
    lukiskan "Halo, " lalu nama;
selesai

sapa("Asep");
```

### Perulangan
```
untuk i = 1 sampai 5 lakukan:
    lukiskan "Angka: " lalu i;
selesai
```

## Ekstensi File

Gunakan ekstensi `.sen` untuk file SenandCode.

## Kredit

Dibangun dengan cinta untuk bahasa Indonesia dan puisi.

## Lisensi

MIT
