import cv2
import numpy as np

def make_bruise_texture(shape, base_color=(60, 0, 90), secondary_color=(90, 20, 130), heal_color=(120, 100, 60)):
    """Buat tekstur warna memar dengan gradasi dan noise."""
    h, w = shape[:2]
    bruise = np.zeros((h, w, 3), dtype=np.uint8)

    # Gradient radial dari tengah ke tepi
    cx, cy = w // 2, h // 2
    y, x = np.ogrid[:h, :w]
    mask = np.sqrt((x - cx)**2 + (y - cy)**2) / (0.5 * min(h, w))
    mask = np.clip(mask, 0, 1)

    for i in range(3):
        bruise[..., i] = (
            base_color[i] * (1 - mask)**2 +
            secondary_color[i] * (1 - mask) * mask * 1.5 +
            heal_color[i] * mask**2
        )

    # Tambahkan noise halus biar tidak terlalu rata
    noise = np.random.normal(0, 15, bruise.shape).astype(np.int16)
    bruise = np.clip(bruise.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    return bruise

def overlay_bruise(img, center, size, alpha=0.4):
    """Tempel efek memar semi-transparan dengan bentuk natural."""
    x, y = center
    w, h = size

    bruise_texture = make_bruise_texture((h, w))
    bruise_mask = cv2.getGaussianKernel(h, h / 3) @ cv2.getGaussianKernel(w, w / 3).T
    bruise_mask = bruise_mask / bruise_mask.max()
    bruise_mask = bruise_mask[..., None]

    # Hitung area di frame (pastikan tidak keluar batas)
    y1 = max(0, y - h // 2)
    y2 = min(img.shape[0], y + h // 2)
    x1 = max(0, x - w // 2)
    x2 = min(img.shape[1], x + w // 2)

    # Ukuran valid di area frame
    h_valid = y2 - y1
    w_valid = x2 - x1
    if h_valid <= 0 or w_valid <= 0:
        return img  # di luar frame

    # Crop sesuai area valid
    bruise_crop = bruise_texture[0:h_valid, 0:w_valid]
    mask_crop = bruise_mask[0:h_valid, 0:w_valid]
    roi = img[y1:y2, x1:x2]

    # Blend dengan aman
    blended = cv2.addWeighted(roi.astype(np.float32), 1 - alpha, bruise_crop.astype(np.float32), alpha, 0)
    blended = blended * mask_crop + roi.astype(np.float32) * (1 - mask_crop)
    img[y1:y2, x1:x2] = np.clip(blended, 0, 255).astype(np.uint8)
    return img

def apply_bruises_realtime():
    cap = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    if not cap.isOpened():
        print("❌ Tidak bisa membuka kamera.")
        return

    print("Tekan Q untuk keluar.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(100, 100))

        out = frame.copy()
        for (x, y, w, h) in faces:
            left_cheek = (x + int(0.3 * w), y + int(0.55 * h))
            right_cheek = (x + int(0.7 * w), y + int(0.1 * h))
            under_left_eye = (x + int(0.35 * w), y + int(0.4 * h))
            under_right_eye = (x + int(0.65 * w), y + int(0.4 * h))

            bruise_size = (int(0.25 * w), int(0.15 * h))

            out = overlay_bruise(out, left_cheek, bruise_size, alpha=0.3)
            out = overlay_bruise(out, right_cheek, bruise_size, alpha=0.3)
          #  out = overlay_bruise(out, under_left_eye, (int(0.2 * w), int(0.12 * h)), alpha=0.45)
          #  out = overlay_bruise(out, under_right_eye, (int(0.2 * w), int(0.12 * h)), alpha=0.45)

        cv2.imshow("Efek Babak Belur Natural - Tekan Q untuk keluar", out)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    apply_bruises_realtime()
