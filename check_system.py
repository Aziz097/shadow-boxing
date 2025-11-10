"""
Quick start script to test if all dependencies are installed
"""
import sys

def check_dependencies():
    """Check if all required dependencies are installed."""
    required_modules = {
        'cv2': 'opencv-python',
        'mediapipe': 'mediapipe',
        'numpy': 'numpy',
        'pygame': 'pygame'
    }
    
    missing = []
    print("Checking dependencies...")
    print("-" * 50)
    
    for module_name, package_name in required_modules.items():
        try:
            __import__(module_name)
            print(f"✓ {package_name:20} - OK")
        except ImportError:
            print(f"✗ {package_name:20} - MISSING")
            missing.append(package_name)
    
    print("-" * 50)
    
    if missing:
        print("\n❌ Missing dependencies:")
        for pkg in missing:
            print(f"  - {pkg}")
        print("\nInstall them with:")
        print(f"  pip install {' '.join(missing)}")
        return False
    else:
        print("\n✅ All dependencies are installed!")
        return True


def check_assets():
    """Check if required assets exist."""
    import os
    
    print("\nChecking assets...")
    print("-" * 50)
    
    required_assets = [
        'assets/font/daydream.otf',
        'assets/sfx/round/round-1.mp3',
        'assets/sfx/round/round-2.mp3',
        'assets/sfx/round/round-3.mp3',
        'assets/sfx/weak-punch.mp3',
        'assets/sfx/strongpunch.mp3',
        'assets/image/boxing-helm.png',
        'assets/image/target-icon.png'
    ]
    
    missing = []
    for asset in required_assets:
        if os.path.exists(asset):
            print(f"✓ {asset:40} - OK")
        else:
            print(f"✗ {asset:40} - MISSING")
            missing.append(asset)
    
    print("-" * 50)
    
    if missing:
        print("\n⚠️  Some assets are missing:")
        for asset in missing:
            print(f"  - {asset}")
        print("\nThe game may not work correctly without these assets.")
        return False
    else:
        print("\n✅ All assets are present!")
        return True


def check_camera():
    """Check if camera is accessible."""
    print("\nChecking camera...")
    print("-" * 50)
    
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print("✓ Camera is accessible")
                print(f"  Resolution: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
                cap.release()
                print("\n✅ Camera check passed!")
                return True
            else:
                print("✗ Camera opened but cannot read frames")
                cap.release()
                return False
        else:
            print("✗ Cannot open camera")
            print("  Make sure your webcam is connected and not used by other apps")
            return False
    except Exception as e:
        print(f"✗ Camera check failed: {e}")
        return False


def main():
    """Run all checks."""
    print("="*50)
    print("  SHADOW BOXING - SYSTEM CHECK")
    print("="*50)
    print()
    
    deps_ok = check_dependencies()
    assets_ok = check_assets()
    camera_ok = check_camera()
    
    print("\n" + "="*50)
    if deps_ok and camera_ok:
        print("  ✅ SYSTEM READY!")
        print("  Run: python main.py")
    else:
        print("  ❌ SYSTEM NOT READY")
        print("  Please fix the issues above")
    print("="*50)


if __name__ == "__main__":
    main()
