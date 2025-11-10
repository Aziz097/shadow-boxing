"""
Script untuk memotong audio round-2.mp3
Dari 5 detik menjadi 2 detik pertama saja
Menggunakan subprocess dan ffmpeg (lebih ringan)
"""
import os
import subprocess
import shutil


def cut_audio_ffmpeg(input_file: str, output_file: str, duration_seconds: int = 2):
    """
    Memotong audio menggunakan ffmpeg.
    
    Args:
        input_file: Path file audio input
        output_file: Path file audio output
        duration_seconds: Durasi yang ingin diambil (dalam detik)
    """
    try:
        print(f"Loading audio: {input_file}")
        
        # Check if ffmpeg is available
        if not shutil.which("ffmpeg"):
            print("✗ ffmpeg not found! Installing via pip...")
            subprocess.run(["pip", "install", "ffmpeg-python"], check=True)
        
        # ffmpeg command to cut audio
        # -i input.mp3 -t 2 -acodec copy output.mp3
        command = [
            "ffmpeg",
            "-i", input_file,
            "-t", str(duration_seconds),  # Duration in seconds
            "-acodec", "copy",  # Copy audio codec (faster)
            "-y",  # Overwrite output file if exists
            output_file
        ]
        
        print(f"Cutting to {duration_seconds} seconds using ffmpeg...")
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✓ Successfully saved to: {output_file}")
            print(f"New duration: {duration_seconds} seconds")
        else:
            print(f"✗ Error: {result.stderr}")
            
    except FileNotFoundError:
        print("✗ ffmpeg not installed!")
        print("Please install ffmpeg:")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        print("  Or use: winget install ffmpeg")
    except Exception as e:
        print(f"✗ Error: {e}")


def cut_audio_manual(input_file: str, output_file: str, duration_seconds: int = 2):
    """
    Alternative: Manual cutting using basic Python (requires pydub).
    """
    try:
        from pydub import AudioSegment
        
        print(f"Loading audio: {input_file}")
        audio = AudioSegment.from_mp3(input_file)
        
        duration_ms = len(audio)
        duration_sec = duration_ms / 1000
        print(f"Original duration: {duration_sec:.2f} seconds")
        
        cut_duration_ms = duration_seconds * 1000
        audio_cut = audio[:cut_duration_ms]
        
        print(f"Cutting to {duration_seconds} seconds...")
        audio_cut.export(output_file, format="mp3")
        print(f"✓ Saved to: {output_file}")
        print(f"New duration: {duration_seconds} seconds")
        
    except ImportError:
        print("✗ pydub not installed!")
        print("Install with: pip install pydub")
        print("Or use ffmpeg method instead")
    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    base_path = os.getcwd()
    input_path = os.path.join(base_path, "assets", "sfx", "round", "round-2.mp3")
    output_path = os.path.join(base_path, "assets", "sfx", "round", "round-2-cut.mp3")
    
    print("=" * 50)
    print("Audio Cutter - Round 2")
    print("=" * 50)
    
    # Try ffmpeg first (recommended)
    print("\nMethod 1: Using ffmpeg")
    cut_audio_ffmpeg(input_path, output_path, duration_seconds=2)
    
    # If you want to replace the original file:
    if os.path.exists(output_path):
        replace = input("\nReplace original file? (y/n): ").lower()
        if replace == 'y':
            shutil.move(output_path, input_path)
            print(f"✓ Replaced original file: {input_path}")
        else:
            print(f"✓ Output saved as: {output_path}")
    else:
        print("\n✗ Output file was not created. Please install ffmpeg or use the manual method.")
        print("\nTrying Method 2: Using pydub...")
        cut_audio_manual(input_path, output_path, duration_seconds=2)
        
        if os.path.exists(output_path):
            replace = input("\nReplace original file? (y/n): ").lower()
            if replace == 'y':
                shutil.move(output_path, input_path)
                print(f"✓ Replaced original file: {input_path}")
            else:
                print(f"✓ Output saved as: {output_path}")
