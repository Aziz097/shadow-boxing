# 🥊 QUICK START GUIDE

## Langkah Cepat Memulai Game

### 1. Pastikan Virtual Environment Aktif
```powershell
.\shadow-boxing-venv\Scripts\Activate.ps1
```

### 2. Test Sistem (Opsional tapi Direkomendasikan)
```powershell
python test_imports.py
```

Jika semua ✓ hijau, lanjut ke step 3!

### 3. Jalankan Game!
```powershell
python main.py
```

---

## 🎮 Controls Saat Bermain

| Tombol | Fungsi |
|--------|--------|
| **SPACE** | Mulai game dari menu |
| **ESC** | Pause/Resume |
| **Q** | Quit/Keluar |

---

## 🎯 Cara Bermain

### Fase Player Attack (3 detik)
1. Kotak-kotak warna akan muncul di layar (2-4 kotak)
2. **Pukul ke arah kotak** dengan tangan Anda
3. Semakin banyak kotak yang kena, semakin besar damage ke enemy!
   - 4 kotak = 25% damage ⚡
   - 3 kotak = 20% damage 💥
   - 2 kotak = 15% damage 👊
   - 1 kotak = 10% damage 🤜

### Fase Enemy Attack
1. **Red dot** (target merah) akan muncul di body Anda
2. Ini warning bahwa enemy akan menyerang!
3. **CEPAT tutup wajah dengan tangan** untuk block!
4. Kalau tidak block = damage 10-30% 💔

### Win Condition
- Health tertinggi setelah 3 round menang! 🏆
- Atau KO lawan sebelum round habis! 💪

---

## 💡 Tips & Tricks

### Punch Detection
✅ **DO:**
- Gerakan cepat dan tegas
- Pastikan tangan terlihat jelas di kamera
- Pencahayaan harus bagus

❌ **DON'T:**
- Gerakan terlalu lambat
- Tangan tertutup badan
- Posisi terlalu jauh dari kamera

### Defense
✅ **DO:**
- Tutup wajah dengan KEDUA tangan
- Cover seluruh area wajah
- React cepat saat red dot muncul

❌ **DON'T:**
- Cuma pakai satu tangan
- Tangan terlalu jauh dari wajah
- Lambat react

### Strategy
- **Fokus akurasi** > kecepatan
- **Prioritaskan combo 4** untuk max damage
- **Selalu siap defend** setelah attack phase
- **Jaga stamina** - jangan panic punch!

---

## 🐛 Troubleshooting

### Camera tidak terdeteksi?
```python
# Edit config.py, line ~15
CAMERA_INDEX = 1  # Coba 0, 1, atau 2
```

### Punch tidak terdeteksi?
1. Cek pencahayaan ruangan
2. Posisi lebih dekat ke kamera
3. Pastikan tangan tidak tertutup
4. Gerakan lebih cepat dan tegas

### Defense tidak work?
1. Tutup wajah dengan KEDUA tangan
2. Cover seluruh area wajah
3. Tangan harus di depan wajah, tidak samping

### Game lag?
```python
# Edit config.py
CAMERA_WIDTH = 640   # Lower resolution
CAMERA_HEIGHT = 480

# Lower detection confidence
HAND_MIN_DETECTION_CONFIDENCE = 0.5
POSE_MIN_DETECTION_CONFIDENCE = 0.5
```

---

## 📊 Difficulty Levels

Setelah familiar, coba ubah difficulty di `config.py`:

```python
DEFAULT_DIFFICULTY = "EASY"    # Untuk pemula
DEFAULT_DIFFICULTY = "MEDIUM"  # Normal (default)
DEFAULT_DIFFICULTY = "HARD"    # Untuk expert!
```

**Easy:**
- Enemy lambat (3-5 detik cooldown)
- Damage enemy 70%
- Warning time 1.5 detik

**Medium:**
- Enemy normal (2-3.5 detik cooldown)
- Damage enemy 100%
- Warning time 1 detik

**Hard:**
- Enemy cepat (1.5-2.5 detik cooldown)
- Damage enemy 130%
- Warning time 0.7 detik

---

## 🎥 Posisi Ideal Bermain

```
     [CAMERA]
        |
        |
      2-3 m
        |
        v
    [YOU HERE]
```

- **Jarak**: 2-3 meter dari kamera
- **Posisi**: Berdiri tegak, seluruh badan terlihat
- **Pencahayaan**: Terang, lampu di depan/samping (jangan dari belakang)
- **Background**: Polos lebih baik (untuk deteksi optimal)

---

## 🏆 High Score Challenge

Track your best game! Catat:
- ⚡ Max Combo Hit
- 🎯 Accuracy (% punch yang hit)
- 🛡️ Successful Blocks
- 💪 Fastest KO Time
- 👑 Highest Health Remaining

---

## 🚨 Jika Ada Error

1. **Check test_imports.py** terlebih dahulu
2. **Baca error message** dengan teliti
3. **Check config.py** settings
4. **Pastikan semua assets ada** di folder assets/
5. **Restart game** - kadang fix simple issues

Jika masih error, check `DEVELOPMENT.md` untuk troubleshooting lengkap!

---

## 📞 Need Help?

- 📖 Baca `README.md` untuk info lengkap
- 🔧 Baca `DEVELOPMENT.md` untuk technical details
- 💾 Check `config.py` untuk customization
- 🧪 Run `test_imports.py` untuk diagnostics

---

**Ready? Let's Box! 🥊💥**

```
     ╔═══════════════════════════╗
     ║   FIGHT!                  ║
     ║   ▓▓▓▓▓▓ vs ▓▓▓▓▓▓      ║
     ║   PLAYER    ENEMY        ║
     ╚═══════════════════════════╝
```
