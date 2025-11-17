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

| Tanggal | Kegiatan | Hasil / Progress Pekerjaan |
| --- | --- | --- |
| 10/28/2025 | Pembuatan Repositori github Shadow Boxing, dan pembagian pekerjaan | Repositori github tugas besar dan koordinasi tim terkait pembagian scope pekerjaan |
| 11/9/2025 | Pemilihan Assets Fix & Rework FLow Game/Filter | Fiksasi assets (sound, filter, font), flow ui game |
| 11/10/2025 | Implementasi Core Game Systems, Game Mechanics, UI/UX, serta Difficulty System & Optimization | - **Core Systems:** System camera, MediaPipe detection, audio manager, visual effects <br/> - **Game Mechanics:** Punch detection, defense system, hitbox, combo system <br/> - **UI/UX:** Menu system, HUD, pause screen, transitions, game over screen <br/> - **Difficulty & Optimization:** 3 level kesulitan, text caching, fullscreen support |
| 11/17/2025 | Audio Processing, UI/UX Polish, dan Automation Script | - **Audio Processing:** Konversi wav ke WAV format MIREX (44100 Hz, mono, 16-bit PCM), analisis dan normalisasi LUFS ke -16 dB untuk konsistensi audio <br/> - **UI/UX Polish:** Penyesuaian ukuran font PressStart2P untuk proporsi lebih baik, perbaikan alignment highlight background pada menu items <br/> - **Automation:** Pembuatan launcher script (shadow_boxing.bat & shadow_boxing.sh) dengan auto-check dependencies dan instalasi otomatis |
| 11/18/2025 | Code Refactoring & Clean Code Implementation | - **Restructuring:** Flatten entities folder structure, hapus subfolder yang tidak perlu <br/> - **Dead Code Removal:** Hapus ai_controller.py yang tidak digunakan <br/> - **Documentation:** Tambah module docstring di semua file, inline comments untuk logika kompleks <br/> - **Import Optimization:** Bersihkan import yang tidak terpakai, simplify import paths <br/> - **Clean Code Principles:** Apply SRP, DRY, clear naming conventions |

---

## Cara Menggunakan

### Prerequisites
- Python 3.10+
- Webcam
- Windows/Linux/Mac

### Quick Start (Recommended)

Gunakan script launcher yang sudah disediakan untuk memudahkan instalasi dan menjalankan game:

**Windows:**
```bash
shadow_boxing.bat
```

**Linux/Mac:**
```bash
chmod +x shadow_boxing.sh
./shadow_boxing.sh
```

Script akan otomatis:
- Memeriksa instalasi Python
- Mengecek dan menginstall dependencies yang diperlukan
- Menjalankan game

### Manual Installation

Jika ingin instalasi manual:

1. **Clone repository:**
```bash
git clone https://github.com/Aziz097/shadow-boxing.git
cd shadow-boxing
```

2. **Buat virtual environment (opsional):**
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
| **ENTER** | Mulai game |
| **ESC** | Pause/Resume |
| **Q** | Keluar game |

---

## Mekanik Game

### Fase Serangan Player (3 detik)
- 2-4 kotak hitbox muncul secara random di area layar
- Pukul ke arah hitbox dengan kepalan tangan untuk mengenainya
- **Damage berdasarkan Combo:**
  - 4 hits = 25% damage 
  - 3 hits = 20% damage 
  - 2 hits = 15% damage
  - 1 hit = 10% damage 

### Fase Serangan Enemy (Combo 3-4 Attacks)
- **Target Icon (Red Dot)**: Muncul di area wajah player (prioritas face detection, fallback ke pose landmarks 0-10 untuk area kepala)
- **Warning Time**: Durasi sebelum serangan aktual:
  - Easy: 1.2 detik
  - Medium: 1.0 detik  
  - Hard: 0.8 detik
- **Defense System**:
  - **Block**: Tutup wajah dengan tangan untuk mengurangi damage 80% (damage × 0.2)
  - **Dodge**: Gerakkan kepala keluar dari target area untuk menghindari damage 100%
- **Damage per Attack**: Random 10-30 HP (dimodifikasi oleh difficulty multiplier)
- **Combo Attack**: Enemy menyerang 3-4 kali berturut-turut dengan delay 400ms antar serangan

### Kondisi Menang
- Health tertinggi setelah 3 ronde menang
- KO jika health mencapai 0

---

## Struktur Project

```
shadow-boxing/
├── main.py                      # Entry point dan game loop utama
├── requirements.txt             # Python dependencies
├── README.md                    # Dokumentasi lengkap
├── shadow_boxing.bat            # Launcher script Windows
├── shadow_boxing.sh             # Launcher script Linux/Mac
│
├── core/                        # Konfigurasi dan utilities inti
│   ├── config.py                # Centralized game settings
│   ├── constants.py             # Game constants dan difficulty
│   ├── math_utils.py            # Fungsi matematika (angle, distance)
│   ├── utils.py                 # Font manager dan image helpers
│   └── __init__.py
│
├── systems/                     # Sistem-sistem inti game
│   ├── vision_system.py         # MediaPipe integration (hands, pose, face)
│   ├── audio_system.py          # Sound effects dan background music
│   ├── render_system.py         # Graphics rendering dan visual effects
│   ├── input_processor.py       # Deteksi punch dan defense
│   └── __init__.py
│
├── entities/                    # Game entities
│   ├── player.py                # Player state, health, combo, scoring
│   ├── enemy.py                 # Enemy state, health, attack timing
│   └── __init__.py
│
├── game/                        # Game logic layer
│   ├── game_state.py            # State management, phase transitions
│   ├── hit_box_system.py        # Hitbox generation dan collision
│   ├── enemy_attack_system.py   # Enemy attack mechanics dan combo
│   └── __init__.py
│
├── ui/                          # User interface components
│   ├── menu_system.py           # Main menu dan navigation
│   ├── hud_renderer.py          # Health bars, timer, combo counter
│   ├── fight_overlay.py         # Round splash screens
│   ├── result_screen.py         # Game over screen
│   └── __init__.py
│
└── assets/                      # Game assets
    ├── font/                    # Custom fonts
    │   └── PressStart2P.ttf
    ├── sprites/                 # Game images (helm, gloves, ko, etc)
    ├── sfx/                     # Sound effects (punch, ko, rounds)
    └── music/                   # Background music (menu, fight, ko)
```

---

## Clean Code Principles

Proyek ini menerapkan prinsip-prinsip clean code untuk maintainability dan readability:

### 1. **Separation of Concerns**
- **Core**: Konfigurasi dan utilities yang reusable
- **Systems**: Sistem-sistem independen (vision, audio, render, input)
- **Entities**: Business logic untuk player dan enemy
- **Game**: Game-specific logic (state, hitbox, attack)
- **UI**: Presentation layer yang terpisah

### 2. **Single Responsibility Principle**
Setiap class memiliki satu tanggung jawab yang jelas:
- `VisionSystem`: Hanya handle MediaPipe detection
- `AudioSystem`: Hanya handle sound dan music
- `GameState`: Hanya manage game flow dan state transitions
- `HitBoxSystem`: Hanya manage hitbox generation dan collision

### 3. **DRY (Don't Repeat Yourself)**
- `FontManager`: Singleton untuk caching font, avoid duplicate loading
- `constants.py`: Centralized constants untuk avoid magic numbers
- Reusable utilities di `math_utils.py` dan `utils.py`

### 4. **Clear Naming Conventions**
- Deskriptif variable names: `player_health`, `enemy_attack_cooldown`
- Function names yang action-oriented: `start_attack()`, `register_hit()`
- Class names yang noun-based: `GameState`, `RenderSystem`

### 5. **Documentation**
- Module docstring di setiap file menjelaskan purpose
- Function docstring yang sederhana dan jelas
- Inline comments untuk logika yang kompleks

### 6. **Flat Structure**
- Eliminasi nested folders yang tidak perlu
- Direct import path: `from entities.player import Player`
- Menghindari deep nesting yang membingungkan

---

## Level Kesulitan

### Easy
- Serangan enemy lebih lambat (3-5s cooldown)
- 70% damage enemy
- 1.2 detik warning time

### Medium (Default)
- Serangan enemy normal (2-3.5s cooldown)
- 100% damage enemy
- 1.0 detik warning time

### Hard
- Serangan enemy cepat (1.5-2.5s cooldown)
- 130% damage enemy
- 0.8 detik warning time

**Catatan**: Fase serangan player tetap 3 detik untuk semua level kesulitan.

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

## References
- [MediaPipe Documentation](https://google.github.io/mediapipe/)
- [OpenCV Documentation](https://opencv.org/)
- [Pygame Documentation](https://www.pygame.org/docs/)
- [Github Copilot](https://github.com/features/copilot)
- [Qwen AI](https://qwen.ai/home)

### Assets
#### Music & Sound Effects
- [Myinstants](https://www.myinstants.com/en/index/us/)
#### Fonts
- [Press Start 2P](https://www.fontsquirrel.com/fonts/press-start-2p)
#### Sprites
- [Imagen by Gemini](https://gemini.google.com/app)


