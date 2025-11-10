# Shadow Boxing — Game Boxing Interactive Mediapipe

_“Boxing with mediapipe🥊”_

---

## Deskripsi Proyek

Shadow Boxing merupakan proyek filter interaktif berbasis multimedia yang menggabungkan computer vision, audio processing, dan video processing yang mensimulasikan pertandingan tinju melawan lawan virtual secara real-time. 

Sistem menggunakan MediaPipe untuk mendeteksi elemen-elemen tubuh penting seperti wajah, kepalan tangan, dan posisi tangan. Dari deteksi ini, aplikasi mampu mengenali gerakan menyerang (pukulan) dan bertahan (menutup wajah). Setiap aksi akan memicu efek visual (seperti efek “babak belur” pada wajah) serta efek suara (sound effects) sehingga menciptakan pengalaman bermain yang interaktif.

---

## Anggota Tim

| Nama Lengkap    | NIM       | ID GitHub                                    |
| --------------- | --------- | -------------------------------------------- |
| Aziz Kurniawan  | 122140097 | [@Aziz097](https://github.com/Aziz097)       |
| Harisya Miranti | 122140049 | [@harisya14](https://github.com/harisya14)   |
| Muhammad Yusuf  | 122140193 | [@muhamyusuf](https://github.com/muhamyusuf) |

---

## Laporan Logbook Mingguan

| Tanggal    | Kegiatan                                                           | Hasil / Progress Pekerjaan                                                         |
| ---------- | ------------------------------------------------------------------ | ---------------------------------------------------------------------------------- |
| 10/28/2025 | Pembuatan Repositori github Shadow Boxing, dan pembagian pekerjaan | Repositori github tugas besar dan koordinasi tim terkait pembagian scope pekerjaan |
| 11/9/2025  | Pemilihan Assets Fix & Rework FLow Game/Filter                     | Fiksasi assets (sound, filter, font), flow ui game                                 |
| 11/10/2024 | Implementasi Core Game Systems | System camera, MediaPipe detection, audio manager, visual effects |
| 11/10/2024 | Implementasi Game Mechanics | Punch detection, defense system (block & dodge), hitbox collision, combo system |
| 11/10/2024 | UI/UX Development | Menu system, HUD, pause screen, round transitions, game over screen dengan custom font |
| 11/10/2024 | Difficulty System & Optimization | 3 level kesulitan (Easy/Medium/Hard), text caching untuk performance, fullscreen support |

---

## Cara Menggunakan

### Prerequisites
- Python 3.10+
- Webcam
- Windows/Linux/Mac

### Instalasi

1. **Clone repository:**
```bash
git clone https://github.com/Aziz097/shadow-boxing.git
cd shadow-boxing
```

2. **Buat virtual environment:**
```bash
python -m venv shadow-boxing-venv
```

3. **Aktifkan virtual environment:**

**Windows:**
```powershell
.\shadow-boxing-venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
source shadow-boxing-venv/bin/activate
```

4. **Install dependencies:**
```bash
pip install -r requirements.txt
```

5. **Jalankan game:**
```bash
python main.py
```

---

## Kontrol Game

| Key | Action |
|-----|--------|
| **SPACE** | Mulai game |
| **ESC** | Pause/Resume |
| **Q** | Keluar game |

---

## Mekanik Game

### Fase Serangan Player (3 detik)
- 2-4 kotak hitbox muncul secara random
- Pukul ke arah hitbox untuk mengenainya
- **Damage berdasarkan Combo:**
  - 4 hits = 25% damage (Strong Punch sound)
  - 3 hits = 20% damage (Meme Punch sound)
  - 2 hits = 15% damage (Meme Punch sound)
  - 1 hit = 10% damage (Weak Punch sound)

### Fase Serangan Enemy
- Red dot target menunjukkan lokasi serangan (body landmarks 0-10)
- Warning time sebelum serangan aktual (tergantung difficulty)
- **Bertahan**: Tutup wajah dengan tangan untuk block
- **Damage jika tidak block**: Random 10-30% (dimodifikasi difficulty)

### Kondisi Menang
- Health tertinggi setelah 3 ronde menang
- KO jika health mencapai 0

---

## Struktur Project

```
shadow-boxing/
├── main.py                      # Entry point
├── config.py                    # Konfigurasi game
├── utils.py                     # Fungsi utility
├── requirements.txt             # Dependencies
│
├── game/                        # Core game logic
│   ├── game_manager.py          # Main game loop
│   └── __init__.py
│
├── player/                      # Komponen player
│   ├── player.py                # State player
│   ├── punch_detector.py        # Deteksi pukulan
│   ├── defense_detector.py      # Deteksi defense
│   └── __init__.py
│
├── enemy/                       # Enemy AI
│   ├── enemy.py                 # State enemy
│   ├── enemy_attack.py          # Pola serangan
│   └── __init__.py
│
├── systems/                     # Core systems
│   ├── camera_manager.py        # Webcam handling
│   ├── mediapipe_manager.py     # Motion tracking
│   ├── audio_manager.py         # Sound system
│   ├── visual_effects.py        # VFX rendering
│   └── __init__.py
│
├── ui/                          # UI components
│   ├── menu.py                  # Main menu
│   ├── hud.py                   # In-game HUD
│   ├── scoreboard.py            # End game screen
│   └── __init__.py
│
└── assets/                      # Game assets
    ├── font/
    ├── image/
    └── sfx/
```

---

## Level Kesulitan

### Easy
- Serangan enemy lebih lambat (3-5s cooldown)
- 70% damage enemy
- 3.5 detik untuk serangan player
- 1.5 detik warning time

### Medium (Default)
- Serangan enemy normal (2-3.5s cooldown)
- 100% damage enemy
- 3 detik untuk serangan player
- 1 detik warning time

### Hard
- Serangan enemy cepat (1.5-2.5s cooldown)
- 130% damage enemy
- 2.5 detik untuk serangan player
- 0.7 detik warning time

---

## Troubleshooting

### Masalah Kamera
```python
# Di config.py, ubah camera index:
CAMERA_INDEX = 0  # Coba 0, 1, atau 2
```

### Masalah Performa
- Turunkan resolusi kamera di `config.py`
- Kurangi confidence threshold MediaPipe
- Tutup aplikasi lain yang menggunakan kamera

### Masalah Deteksi MediaPipe
- Pastikan pencahayaan bagus
- Posisi dalam frame kamera
- Gunakan pakaian kontras

---

## Dependencies

```
opencv-python==4.10.0.84
mediapipe==0.10.14
numpy==1.26.4
pygame==2.5.2
```

---

## Credits

**Development Team:**
- **Aziz Kurniawan** - Base Game Logic, MediaPipe Tuning, Refactor, QA
- **Harisya Miranti** - UI/UX, Visual Effects & Assets
- **Muhammad Yusuf** - MediaPipe Integration & Flow Game

**Technologies:**
- MediaPipe by Google
- OpenCV
- Pygame Community
- Python Software Foundation

---

## License

This project is open source and available under the MIT License.

---

**Selamat bermain! 🥊 Latih keras, bertarung cerdas!**
