# SenandCode ✨

<p align="center">
  <img src="docs/favicon.svg" alt="SenandCode Logo" width="80">
</p>

> *Bahasa pemrograman puitis dalam Bahasa Indonesia*

**SenandCode** — dari *senandika* (dialog batin yang puitis) + *code* — adalah bahasa pemrograman yang indah seperti puisi. Setiap baris adalah puisi. Setiap program adalah antologi.

![License](https://img.shields.io/github/license/zmy16/SenandCode)
![Stars](https://img.shields.io/github/stars/zmy16/SenandCode)

## Filosofi

Kode seharusnya indah. Bukan hanya berfungsi — ia harus berbicara. SenandCode lahir dari keyakinan bahwa **menulis program adalah menulis puisi**: setiap kata dipilih dengan hati-hati, setiap baris mengalir alami, dan setiap program menceritakan kisahnya sendiri.

> *"Simpan 5 dalam umur"* — bukan sekadar assignment, ini adalah puisi mini.

## Instalasi

Clone dan jalankan langsung dari source:

```bash
git clone https://github.com/zmy16/SenandCode.git
cd SenandCode
```

Pastikan Python 3.7+ sudah terinstal. Tidak perlu dependensi eksternal.

## Cara Menjalankan

**Jalankan file `.sen`:**

```bash
python -m senandika examples/hello.sen
```

**REPL mode interaktif:**

```bash
python -m senandika
```

Di dalam REPL, semicolon (`;`) opsional. Tekan `Ctrl+D` atau `Ctrl+Z` untuk keluar.

**Windows — double click `run.bat`:**

```
run.bat                # Masuk REPL
run.bat program.sen    # Jalankan file
```

## Sintaks

### Dasar

| Konsep | SenandCode | Arti |
|--------|------------|------|
| Cetak | `lukiskan "Halo";` | Mencetak ke layar |
| Variabel | `simpan 5 dalam x;` | Simpan nilai dalam variabel |
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

**For loop:**

```
untuk i = 1 sampai 5 lakukan:
    lukiskan "Hitungan: " lalu i;
selesai
```

**While loop:**

```
simpan 5 dalam x;
selagi x > 0 lakukan:
    lukiskan x;
    simpan x - 1 dalam x;
selesai
```

**Break & Continue:**

```
untuk i = 1 sampai 10 lakukan:
    seandainya i == 3:
        hening;    // berhenti di i = 3
    selesai
    seandainya i == 5:
        sambung;   // lewati i = 5
    selesai
    lukiskan i;
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
// Output: Aku Asep, 25 tahun.
```

**Inheritance:**

```
wajah Hewan:
    puisi suara():
        lukiskan "...";
    selesai
selesai

wajah Kucing warisi Hewan:
    puisi suara():
        lukiskan "Meow!";
    selesai
selesai

simpan ciptakan Kucing() dalam kucing;
kucing.suara();
// Output: Meow!
```

### Array

```
simpan [1, 2, 3, 4, 5] dalam angka;
lukiskan panjang(angka);       // Output: 5
lukiskan angka[0];             // Output: 1
simpan "Halo" dalam teks;
lukiskan panjang(teks);        // Output: 4
lukiskan teks[0];              // Output: H
```

### Penanganan Error

```
coba:
    simpan 10 / 0 dalam x;
raih e:
    lukiskan "Tercatat: " lalu e;
akhirnya:
    lukiskan "Selesai.";
selesai
// Output:
// Tercatat: division by zero
// Selesai.
```

### Boolean & Null

```
simpan benar dalam aktif;
simpan palsu dalam nonaktif;
simpan hampa dalam kosong;

seandainya aktif dan bukan nonaktif:
    lukiskan "Sistem berjalan!";
selesai
```

## Keyword Reference

### Variabel & Output
| Keyword | Fungsi |
|---------|--------|
| `simpan` | Menyimpan nilai ke variabel |
| `dalam` | Bagian dari assignment (`simpan <nilai> dalam <variabel>`) |
| `lukiskan` | Mencetak output ke layar |
| `lalu` | Concatenation operator (gabung string/nilai) |
| `dengarkan` | Membaca input dari pengguna |

### Percabangan
| Keyword | Fungsi |
|---------|--------|
| `seandainya` | If — kondisi pertama |
| `atau jika` | Else if — kondisi alternatif |
| `jika tidak` | Else — fallback |

### Perulangan
| Keyword | Fungsi |
|---------|--------|
| `untuk` | For loop — iterasi range |
| `sampai` | Batas atas dalam for loop |
| `lakukan` | Memulai body blok |
| `selagi` | While loop — iterasi selama kondisi benar |
| `hening` | Break — hentikan loop |
| `sambung` | Continue — lewati iterasi saat ini |

### Fungsi
| Keyword | Fungsi |
|---------|--------|
| `puisi` | Mendeklarasikan fungsi |
| `kembalikan` | Return value dari fungsi |

### OOP
| Keyword | Fungsi |
|---------|--------|
| `wajah` | Deklarasi kelas |
| `diri` | Referensi ke instance saat ini (this/self) |
| `ciptakan` | Membuat objek baru (new/instance) |
| `warisi` | Inheritance — pewarisan kelas |
| `lahir` | Constructor — fungsi pembangkit objek |

### Error Handling
| Keyword | Fungsi |
|---------|--------|
| `coba` | Try block |
| `raih` | Catch block — tangkap error |
| `akhirnya` | Finally block — selalu dijalankan |
| `lemparkan` | Throw exception |

### Lainnya
| Keyword | Fungsi |
|---------|--------|
| `benar` / `palsu` | Boolean true / false |
| `hampa` | Null value |
| `dan` / `atau` / `bukan` | Logical and / or / not |
| `selesai` | Penutup blok |
| `panjang` | Built-in: panjang array atau string |

## Struktur Proyek

```
SenandCode/
├── senandika/
│   ├── __init__.py         # Package init
│   ├── __main__.py         # CLI entry point + REPL
│   ├── lexer.py            # Tokenizer (regex-based)
│   ├── parser.py           # Recursive descent parser
│   └── interpreter.py      # Tree-walk interpreter
├── examples/               # 9 contoh program .sen
│   ├── hello.sen           # Hello world
│   ├── sapa.sen            # Fungsi & parameter
│   ├── hitung.sen          # Percabangan if/elif/else
│   ├── lingkaran.sen       # Fungsi dengan return
│   ├── hitung_mundur.sen   # For loop countdown
│   ├── biodata.sen         # OOP & kelas
│   ├── error.sen           # Try/catch/finally
│   ├── array.sen           # Array & indexing
│   └── string_ops.sen      # String operations
├── LICENSE                 # MIT License
├── README.md
├── pyproject.toml
├── run.bat
├── MANIFEST.in
└── .gitignore
```

## Ekstensi File

Gunakan ekstresi `.sen` untuk file SenandCode.

## Arsitektur

SenandCode mengikuti arsitektur interpreter klasik tiga tahap:

1. **Lexer** — Mengubah source code menjadi token (kata kunci, variabel, operator)
2. **Parser** — Menyusun token menjadi Abstract Syntax Tree (AST)
3. **Interpreter** — Menjalankan AST secara langsung (tree-walk)

Tidak ada kompilasi ke bytecode. Tidak ada dependency eksternal. Murni Python.

## Kredit

**Penulis:** [Muhammad Raid Zakwan](https://github.com/zmy16)

Dibangun dengan cinta untuk bahasa Indonesia dan puisi.

## Lisensi

[MIT License](LICENSE) — bebas digunakan, dimodifikasi, dan didistribusikan.
