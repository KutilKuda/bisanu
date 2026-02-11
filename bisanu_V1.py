#!/usr/bin/env python3
"""
Program untuk mengubah icon aplikasi dan wallpaper di Linux
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path
import random
import string


def get_download_path():
    """Mendapatkan path folder Downloads"""
    home = Path.home()
    download_paths = [
        home / "Downloads",
        home / "Unduhan",  # Untuk beberapa bahasa
    ]

    for path in download_paths:
        if path.exists():
            return path
    return home / "Downloads"  # Fallback

def change_icon(icon_file):
    """Mengubah icon aplikasi"""
    icon_path = Path(icon_file)

    if not icon_path.exists():
        print(f"❌ File icon tidak ditemukan: {icon_file}")
        return False

    # Lokasi untuk icon sistem (berbeda tergantung DE)
    desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()

    try:
        if "gnome" in desktop or "ubuntu" in desktop:
            # Untuk GNOME/Unity
            icon_dir = Path.home() / ".local" / "share" / "icons"
            icon_dir.mkdir(parents=True, exist_ok=True)

            # Copy icon ke lokasi sistem
            dest_icon = icon_dir / "custom-logo.ico"
            shutil.copy2(icon_file, dest_icon)
            print(f"✅ Icon disalin ke: {dest_icon}")

            # Set icon untuk aplikasi (contoh: untuk terminal)
            subprocess.run([
                "gsettings", "set", "org.gnome.desktop.interface",
                "icon-theme", "custom-logo"
            ], check=False)

        elif "kde" in desktop:
            # Untuk KDE Plasma
            print("⚠️  Untuk KDE, ubah icon melalui System Settings > Icons")

        elif "xfce" in desktop:
            # Untuk XFCE
            icon_dir = Path.home() / ".icons"
            icon_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(icon_file, icon_dir / "custom-logo.ico")

        return True

    except Exception as e:
        print(f"❌ Error mengubah icon: {e}")
        return False

def change_wallpaper(wallpaper_file):
    """Mengubah wallpaper"""
    wallpaper_path = Path(wallpaper_file)

    if not wallpaper_path.exists():
        print(f"❌ File wallpaper tidak ditemukan: {wallpaper_file}")
        return False

    desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()

    try:
        if "gnome" in desktop or "ubuntu" in desktop:
            # Untuk GNOME/Unity
            wallpaper_dest = Path.home() / "Pictures" / wallpaper_path.name
            shutil.copy2(wallpaper_file, wallpaper_dest)

            # Set wallpaper menggunakan gsettings
            uri = f"file://{wallpaper_dest.absolute()}"
            subprocess.run([
                "gsettings", "set", "org.gnome.desktop.background",
                "picture-uri", uri
            ], check=True)

            # Juga set untuk lockscreen
            subprocess.run([
                "gsettings", "set", "org.gnome.desktop.screensaver",
                "picture-uri", uri
            ], check=False)

            print(f"✅ Wallpaper GNOME diubah ke: {wallpaper_dest}")

        elif "kde" in desktop:
            # Untuk KDE Plasma
            script = f"""
            var allDesktops = desktops();
            for (var i=0; i<allDesktops.length; i++) {{
                var d = allDesktops[i];
                d.wallpaperPlugin = "org.kde.image";
                d.currentConfigGroup = Array("Wallpaper", "org.kde.image", "General");
                d.writeConfig("Image", "file://{wallpaper_file}")
            }}
            """
            subprocess.run(["qdbus", "org.kde.plasmashell", "/PlasmaShell",
                          "org.kde.PlasmaShell.evaluateScript", script], check=False)
            print("✅ Wallpaper KDE diubah")

        elif "xfce" in desktop:
            # Untuk XFCE
            subprocess.run([
                "xfconf-query", "-c", "xfce4-desktop",
                "-p", "/backdrop/screen0/monitor0/image-path",
                "-s", wallpaper_file
            ], check=True)
            print("✅ Wallpaper XFCE diubah")

        elif "mate" in desktop:
            # Untuk MATE
            subprocess.run([
                "gsettings", "set", "org.mate.background",
                "picture-filename", wallpaper_file
            ], check=True)
            print("✅ Wallpaper MATE diubah")

        else:
            # Fallback untuk desktop environment lain
            print("⚠️  Desktop Environment tidak dikenali, mencoba metode umum...")

            # Coba gunando feh (ringan, sering digunakan)
            try:
                subprocess.run(["feh", "--bg-fill", wallpaper_file], check=True)
                print("✅ Wallpaper diubah menggunakan feh")
            except:
                # Coba nitrogen
                try:
                    subprocess.run(["nitrogen", "--set-zoom-fill", wallpaper_file], check=True)
                    print("✅ Wallpaper diubah menggunakan nitrogen")
                except:
                    print("❌ Tidak dapat mengubah wallpaper. Install feh atau nitrogen:")
                    print("   sudo apt install feh   # Debian/Ubuntu")
                    print("   sudo pacman -S feh     # Arch")
                    print("   sudo dnf install feh   # Fedora")
                    return False

        return True

    except Exception as e:
        print(f"❌ Error mengubah wallpaper: {e}")
        return False

def check_dependencies():
    """Memeriksa dependencies yang diperlukan"""
    required_commands = []

    desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()

    if "gnome" in desktop or "ubuntu" in desktop:
        required_commands.append("gsettings")
    elif "kde" in desktop:
        required_commands.append("qdbus")
    elif "xfce" in desktop:
        required_commands.append("xfconf-query")

    missing = []
    for cmd in required_commands:
        if shutil.which(cmd) is None:
            missing.append(cmd)

    return missing

def generate_random_id(length=20):
    """Generate random ID dengan kombinasi huruf dan angka"""
    characters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def create_readme_file():
    """Membuat file bisanu_here.txt """
    # Buat 2 paragraf dengan ID random
    ID random: {generate_random_id()}
    paragraf1 = f"""Tidak ada teks lengkap publik yang tersedia secara bebas karena alasan keamanan, 
    tapi berdasarkan analisis, catatan biasanya dimulai dengan peringatan seperti "Files encrypted" 
    atau serupa, diikuti detail kontak dan konsekuensi. Beberapa varian disebut 
    "Decryption Instructions.txt" 

"""
    paragraf2 = f"""For education only wallet: {generate_random_id()}
"""
    
    # Gabungkan kedua paragraf
    isi_file = paragraf1 + paragraf2
    
    # Tentukan lokasi file di Desktop
    desktop = Path.home() / "Desktop"
    file_path = desktop / "bisanu_here.txt"
    
    # Tulis ke file
    file_path.write_text(isi_file, encoding='utf-8')
    
    return file_path, isi_file

def main():
    """Fungsi utama"""
    print("=" * 50)
    print("PROGRAM UBAH LOGO DAN WALLPAPER LINUX")
    print("=" * 50)

    # Dapatkan path Downloads
    download_path = get_download_path()
    print(f"📁 Folder Downloads: {download_path}")

    # File yang dicari
    icon_file = download_path / "nubis.ico"
    wallpaper_file = download_path / "wallp.jpg"

    # Periksa file
    print("\n🔍 Mencari file...")
    print(f"   Icon:     {icon_file} {'✅' if icon_file.exists() else '❌ Tidak ditemukan'}")
    print(f"   Wallpaper: {wallpaper_file} {'✅' if wallpaper_file.exists() else '❌ Tidak ditemukan'}")

    if not icon_file.exists() and not wallpaper_file.exists():
        print("\n❌ Tidak ada file yang ditemukan di Downloads!")
        print("   Pastikan file 'icon.ico' dan 'wall.jpg' ada di folder Downloads")
        sys.exit(1)

    # Periksa dependencies
    print("\n🔧 Memeriksa dependencies...")
    missing_deps = check_dependencies()
    if missing_deps:
        print(f"   ⚠️  Perintah berikut tidak ditemukan: {', '.join(missing_deps)}")
        print("   Beberapa fitur mungkin tidak berfungsi.")
    else:
        print("   ✅ Semua dependencies terpenuhi")

    # Tampilkan desktop environment
    desktop = os.environ.get("XDG_CURRENT_DESKTOP", "Tidak dikenali")
    print(f"   Desktop Environment: {desktop}")

    # Konfirmasi
    print("\n" + "=" * 50)
    response = input("Lanjutkan perubahan? (y/n): ").lower()

    if response != 'y':
        print("❌ Dibatalkan oleh pengguna")
        sys.exit(0)

    print("\n🚀 Memulai perubahan...")

    # Ubah icon jika file ada
    success_count = 0
    if icon_file.exists():
        print(f"\n🎨 Mengubah icon dari: {icon_file}")
        if change_icon(icon_file):
            success_count += 1
    else:
        print("\n⚠️  Lewat: File icon tidak ditemukan")

    # Ubah wallpaper jika file ada
    if wallpaper_file.exists():
        print(f"\n🖼️  Mengubah wallpaper dari: {wallpaper_file}")
        if change_wallpaper(wallpaper_file):
            success_count += 1
    else:
        print("\n⚠️  Lewat: File wallpaper tidak ditemukan")

    # Hasil
    print("\n" + "=" * 50)
    print("📊 HASIL:")
    print(f"   ✅ Berhasil: {success_count}/2 perubahan")

    if success_count > 0:
        print("\n✨ Perubahan akan berlaku segera!")
        print("   Mungkin perlu restart session/login ulang untuk efek lengkap.")
    else:
        print("\n❌ Tidak ada perubahan yang berhasil.")
        print("   Periksa file dan permissions.")

    print("\n💡 Tips:")
    print("   - Untuk icon, mungkin perlu pilih manual di system settings")
    print("   - Pastikan format file didukung (.ico untuk icon, .jpg untuk wallpaper)")

    print("Membuat file bisanu_here.txt...")
    
    try:
        file_path, isi_file = create_readme_file()
        
        print(f"File berhasil dibuat: {file_path}")
        print("\nIsi file:")
        print("=" * 50)
        print(isi_file)
        print("=" * 50)
        
    except Exception as e:
        print(f"Error: {e}")
        
if __name__ == "__main__":
    # Cek jika dijalankan sebagai root
    if os.geteuid() == 0:
        print("⚠️  Warning: Jangan jalankan sebagai root/sudo!")
        print("   Program ini untuk konfigurasi user.")
        sys.exit(1)

    main()