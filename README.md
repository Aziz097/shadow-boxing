# Shadow Boxing - Interactive Boxing Game# Shadow Boxing — Game Boxing Interactive MediaPipe# Shadow Boxing — Game Boxing Interactive Mediapipe



Game tinju interaktif yang mensimulasikan pertandingan real-time melawan AI menggunakan deteksi gerakan MediaPipe._"Fight Your Virtual Opponent with Real Punches!"\_\_“”_



---![Status](https://img.shields.io/badge/status-active-success.svg)---



## Deskripsi Proyek![Python](https://img.shields.io/badge/python-3.8+-blue.svg)



Shadow Boxing adalah aplikasi multimedia interaktif yang menggabungkan computer vision, audio processing, dan video processing. Sistem mendeteksi wajah, kepalan tangan, dan posisi tangan untuk mengenali gerakan menyerang (pukulan) dan bertahan (blocking). Setiap aksi memicu efek visual dan audio untuk pengalaman bermain yang responsif.![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.14-orange.svg)## Deskripsi Proyek



------Shadow Boxing merupakan proyek filter interaktif berbasis multimedia yang menggabungkan computer vision, audio processing, dan video processing yang mensimulasikan pertandingan tinju melawan lawan virtual secara real-time.



## Fitur Sistem## 🎮 Deskripsi ProyekSistem menggunakan MediaPipe untuk mendeteksi elemen-elemen tubuh penting seperti wajah, kepalan tangan, dan posisi tangan. Dari deteksi ini, aplikasi mampu mengenali gerakan menyerang (pukulan) dan bertahan (menutup wajah). Setiap aksi akan memicu efek visual (seperti efek “babak belur” pada wajah) serta efek suara (sound effects) sehingga menciptakan pengalaman bermain yang interaktif.



### Player System (Aziz Kurniawan)**Shadow Boxing** adalah game tinju interaktif yang mensimulasikan pertandingan tinju real-time melawan lawan virtual (AI). Pemain menyerang dengan gerakan pukulan ke kamera dan bertahan dengan menutup wajah menggunakan tangan. ---

- Punch Detection: Deteksi pukulan berbasis velocity dan arah gerakan

- Fist Detection: Deteksi kepalan tangan dengan analisis sudut dan jarakSistem mendeteksi wajah, kepalan tangan, dan posisi tangan via **MediaPipe**, lalu memberikan umpan balik visual (efek grafis) dan audio (sound effects).## Anggota Tim

- Defense System: Deteksi blocking berdasarkan posisi tangan di area wajah

### ✨ Fitur Utama| Nama Lengkap | NIM | ID GitHub |

### Enemy AI System (Muhammad Yusuf)

- Telegraph System: Peringatan visual sebelum serangan| --------------- | --------- | -------------------------------------------- |

- Difficulty Levels: EASY, MEDIUM, HARD dengan parameter berbeda

- Combo Attacks: Kombinasi 2-3 pukulan berurutan#### 🥊 Player Features (by Aziz)| Aziz Kurniawan | 122140097 | [@Aziz097](https://github.com/Aziz097) |

- Stamina System: Manajemen stamina untuk serangan

- Vulnerability Windows: Kesempatan counter-attack setelah enemy menyerang- **Punch Detection**: Deteksi pukulan berbasis velocity dan arah gerakan| Harisya Miranti | 122140049 | [@harisya14](https://github.com/harisya14) |

- Adaptive AI: Penyesuaian strategi berdasarkan pola bermain player

- Attack Patterns: CENTER, LEFT, RIGHT attack types- **Fist Detection**: Deteksi kepalan tangan dengan kombinasi sudut dan jarak| Muhammad Yusuf | 122140193 | [@muhamyusuf](https://github.com/muhamyusuf) |



### Game System (Harisya Miranti)- **Defense System**: Deteksi blocking dengan posisi tangan di depan wajah

- Round Manager: 3 ronde x 20 detik dengan rest period 5 detik

- HP System: Health points untuk player dan enemy---

- Score Tracking: Statistik punches landed, accuracy, blocks

- Visual Effects: Telegraph warnings, HP bars, stamina bar, damage indicators, motion trails, combo indicators#### 👊 Enemy AI System (by Ucup)

- Sound Manager: Audio feedback untuk game events

- **Telegraph System**: Warning visual sebelum enemy menyerang## Laporan Logbook Mingguan

---

- **3 Difficulty Levels**: EASY, MEDIUM, HARD dengan parameter berbeda

## Gameplay

- **Combo Attacks**: Enemy bisa melakukan kombinasi 2-3 pukulan| Tanggal | Kegiatan | Hasil / Progress Pekerjaan |

### Controls

- **SPACE**: Start round / Continue- **Stamina System**: Enemy perlu stamina untuk menyerang| ---------- | ------------------------------------------------------------------ | ---------------------------------------------------------------------------------- |

- **Q**: Quit game

- **D**: Change difficulty- **Vulnerability Windows**: Player bisa counter-attack saat enemy recovering| 10/28/2025 | Pembuatan Repositori github Shadow Boxing, dan pembagian pekerjaan | Repositori github tugas besar dan koordinasi tim terkait pembagian scope pekerjaan |

- **S**: Toggle sound

- **Adaptive AI**: Enemy belajar dari pola bermain player

### Cara Bermain

1. Tekan SPACE untuk memulai round- **3 Attack Types**: CENTER, LEFT, RIGHT attack patterns---

2. Buat kepalan dan pukul cepat ke arah kamera untuk menyerang

3. Tutup wajah dengan tangan untuk block serangan enemy#### 🎯 Game System (by Ica)@lisence nya belum tau

4. Serang saat enemy vulnerable (setelah menyerang)

5. Menang dengan KO (HP enemy = 0) atau poin tertinggi setelah 3 ronde- **Round Manager**: 3 ronde × 20 detik dengan rest period 5 detik

- **HP System**: Player dan Enemy memiliki health points

---- **Score Tracking**: Track punches landed, accuracy, blocks

- **Visual Effects**:

## Instalasi  - Telegraph warnings dengan pulse effect

  - HP bars dengan color gradient

### Prerequisites  - Stamina bar untuk enemy

- Python 3.8+  - Damage indicators

- Webcam  - Motion trails untuk punch effects

- Windows / macOS / Linux  - Hit flash effects

  - Combo indicators

### Setup- **Sound Manager**: Audio feedback untuk punch, hit, block events



```bash---

# Clone repository

git clone https://github.com/Aziz097/shadow-boxing.git## 🎯 Gameplay Mechanics

cd shadow-boxing

### Controls

# Install dependencies

pip install -r requirements.txt- **SPACE**: Start round / Continue to next round

- **Q**: Quit game

# Run game- **D**: Change difficulty (EASY → MEDIUM → HARD)

python main.py- **S**: Toggle sound on/off

```

### How to Play

---

1. **Start Game**: Press SPACE untuk memulai round pertama

## Struktur Project2. **Attack**: Buat kepalan tangan dan pukul cepat ke arah kamera

3. **Defend**: Tutup wajah dengan tangan untuk block serangan enemy

```4. **Counter**: Serang saat enemy vulnerable (setelah enemy menyerang)

shadow-boxing/5. **Win**: Kurangi HP enemy hingga 0 atau menang poin di akhir round

├── main.py                      # Main game loop

├── utils.py                     # Helper functions### Winning Conditions

├── requirements.txt             # Dependencies

│- **KO**: Reduce enemy HP to 0

├── player/                      # Player detection (Aziz)- **Points**: Win more rounds based on punches landed vs hits taken

│   ├── fist_detector.py

│   ├── punch_detector.py---

│   └── defense_detector.py

│## 🔗 Referensi

├── enemy/                       # Enemy AI (Yusuf)

│   ├── enemy_hit_tester.py- [Video Referensi 1: Thailand Boxing](https://www.tiktok.com/@thailandboxing6/video/7370984266391489808)

│   └── enhanced_enemy_ai.py- [Video Referensi 2: Boxing Simulator](https://lenslist.co/boxing-simulator)

│

├── game/                        # Game systems (Ica)---

│   ├── game_state.py

│   ├── round_manager.py## 👥 Anggota Tim

│   ├── sound_manager.py

│   └── visual_effects.py| Nama Lengkap    | NIM       | ID GitHub                                    | Tanggung Jawab |

│| --------------- | --------- | -------------------------------------------- | -------------- |

└── assets/| Aziz Kurniawan  | 122140097 | [@Aziz097](https://github.com/Aziz097)       | Player System  |

    ├── sfx/| Harisya Miranti | 122140049 | [@harisya14](https://github.com/harisya14)   | Game System    |

    └── vfx/| Muhammad Yusuf  | 122140193 | [@muhamyusuf](https://github.com/muhamyusuf) | Enemy System   |

```

---

---

## 🚀 Instalasi & Setup

## Technical Stack

### Prerequisites

- **OpenCV**: Video capture & image processing

- **MediaPipe**: Hand, face, and pose detection- Python 3.8 atau lebih tinggi

- **NumPy**: Numerical computations- Webcam

- **Pygame**: Audio playback- OS: Windows / macOS / Linux



### Detection Systems### Langkah Instalasi

- Hand Detection: 21 landmarks per hand, 30+ FPS tracking

- Face Detection: 468 facial landmarks untuk hit detection1. **Clone Repository**

- Pose Detection: Body landmarks sebagai fallback

```bash

### Enemy AI Algorithmgit clone https://github.com/Aziz097/shadow-boxing.git

cd shadow-boxing

State Machine:```

```

IDLE → TELEGRAPH → ATTACKING → RECOVERING → IDLE2. **Install Dependencies**

```

```bash

Adaptive Learning: Menyesuaikan agresivitas dan feint chance berdasarkan defense rate player.pip install -r requirements.txt

```

---

3. **Run Game**

## Anggota Tim

```bash

| Nama            | NIM       | GitHub                                       | Tanggung Jawab |python main.py

| --------------- | --------- | -------------------------------------------- | -------------- |```

| Aziz Kurniawan  | 122140097 | [@Aziz097](https://github.com/Aziz097)      | Player System  |

| Harisya Miranti | 122140049 | [@harisya14](https://github.com/harisya14)  | Game System    |---

| Muhammad Yusuf  | 122140193 | [@muhamyusuf](https://github.com/muhamyusuf)| Enemy System   |

## 📁 Struktur Project

---

```

## Laporan Progressshadow-boxing/

├── main.py                 # Main game loop & integration

| Tanggal    | Kegiatan                             | Progress                                                    |├── utils.py                # Helper functions

| ---------- | ------------------------------------ | ----------------------------------------------------------- |├── requirements.txt        # Python dependencies

| 10/28/2025 | Setup repository & pembagian tugas   | Inisialisasi project dan koordinasi tim                     |├── README.md              # Documentation

| 11/03/2025 | Enhanced Enemy AI System             | Telegraph, difficulty, combo, stamina, adaptive AI          |│

| 11/03/2025 | Game State & Round Manager           | HP system, scoring, round management                        |├── player/                # Player detection modules (Aziz)

| 11/03/2025 | Visual & Sound Effects               | Complete VFX dan audio integration                          |│   ├── __init__.py

│   ├── fist_detector.py   # Fist detection algorithm

---│   ├── punch_detector.py  # Punch detection with velocity

│   └── defense_detector.py # Defense/blocking detection

## Referensi│

├── enemy/                 # Enemy AI modules (Ucup)

- [Thailand Boxing TikTok](https://www.tiktok.com/@thailandboxing6/video/7370984266391489808)│   ├── __init__.py

- [Boxing Simulator LensList](https://lenslist.co/boxing-simulator)│   ├── enemy_hit_tester.py      # Original enemy system

│   └── enhanced_enemy_ai.py     # Enhanced AI with new features

---│

├── game/                  # Game systems (Ica)

## Known Issues & Future Plans│   ├── __init__.py

│   ├── game_state.py      # HP, damage, scoring system

### Limitations│   ├── round_manager.py   # Round & timing management

- Sound files untuk hit, block, bell belum tersedia│   ├── sound_manager.py   # Audio system

- Punch hit detection perlu peningkatan akurasi│   └── visual_effects.py  # VFX rendering

- Performa bergantung pada kondisi pencahayaan│

└── assets/               # Game assets

### Planned Features    ├── sfx/              # Sound effects

- Sound effects lengkap    │   └── strongpunch.mp3

- Multiplayer mode    └── vfx/              # Visual effects

- Training mode        ├── bruised_face.py

- Leaderboard system        └── pow.png

- Additional characters```

- Power-ups & special moves

---

---

## 🛠️ Technical Details

## License

### Technologies Used

License belum ditentukan.

- **OpenCV**: Video capture & image processing

---- **MediaPipe**: Hand, face, and pose detection

- **NumPy**: Numerical computations

## Contact- **Pygame**: Audio playback



- Aziz Kurniawan: [@Aziz097](https://github.com/Aziz097)### Detection Systems

- Muhammad Yusuf: [@muhamyusuf](https://github.com/muhamyusuf)

- Harisya Miranti: [@harisya14](https://github.com/harisya14)#### Hand Detection



---- Uses MediaPipe Hands for landmark detection

- 21 hand landmarks per hand

**Shadow Boxing Team - Sistem Multimedia Project**- Real-time tracking at 30+ FPS


#### Face Detection

- MediaPipe Face Mesh with 468 facial landmarks
- Bounding box calculation for hit detection

#### Pose Detection

- MediaPipe Pose for body landmark tracking
- Fallback when face not visible

### AI Algorithm

**Enemy AI State Machine:**

```
IDLE → TELEGRAPH → ATTACKING → RECOVERING → IDLE
         ↓              ↓
      (feint)    (combo branch)
```

**Adaptive Learning:**

- Tracks player defense rate
- Adjusts aggression based on player behavior
- Increases feint chance if player defends often

---

## 📊 Laporan Logbook Mingguan

| Tanggal    | Kegiatan                                                           | Hasil / Progress Pekerjaan                                                                                    |
| ---------- | ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------- |
| 10/28/2025 | Pembuatan Repositori github Shadow Boxing, dan pembagian pekerjaan | Repositori github tugas besar dan koordinasi tim terkait pembagian scope pekerjaan                            |
| 11/03/2025 | Implementasi Enhanced Enemy AI System                              | Enhanced AI dengan telegraph, difficulty levels, combo attacks, stamina, vulnerability, dan adaptive learning |
| 11/03/2025 | Implementasi Game State & Round Manager                            | HP system, damage tracking, scoring, dan 3-round system dengan rest periods                                   |
| 11/03/2025 | Implementasi Visual & Sound Effects                                | Complete VFX system dan audio integration                                                                     |

---

## 🎨 Screenshots

_(Coming soon - tambahkan screenshots gameplay di sini)_

---

## 🐛 Known Issues & Future Improvements

### Current Limitations

- Sound files untuk hit, block, dan bell belum tersedia (hanya punch.mp3)
- Punch hit detection bisa lebih akurat dengan zone-based detection
- Lighting conditions affect MediaPipe detection quality

### Planned Features

- [ ] Tambah sound effects lengkap
- [ ] Multiplayer mode
- [ ] Training mode dengan punch bag
- [ ] Leaderboard system
- [ ] More enemy characters
- [ ] Power-ups & special moves

---

## 📝 License

[License type belum ditentukan]

---

## 🙏 Acknowledgments

- MediaPipe by Google
- OpenCV Community
- Referensi video TikTok & LensList
- Dosen & Asisten Mata Kuliah Sistem Multimedia

---

## 📧 Contact

Untuk pertanyaan atau kontribusi, silakan hubungi:

- Aziz Kurniawan: [@Aziz097](https://github.com/Aziz097)
- Muhammad Yusuf: [@muhamyusuf](https://github.com/muhamyusuf)
- Harisya Miranti: [@harisya14](https://github.com/harisya14)

---

**Made with 🥊 by Team Shadow Boxing**
