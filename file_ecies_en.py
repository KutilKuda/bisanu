#!/usr/bin/env python3
"""
Script untuk mengenkripsi dan mendekripsi file di path tertentu menggunakan ECIES
"""

import os
import sys
import argparse
from pathlib import Path
from ecies.keys import PrivateKey
from ecies import encrypt, decrypt
from ecies.config import ECIES_CONFIG
import hashlib
import json

class FileEncryptor:
    def __init__(self, curve='secp256k1'):
        """Inisialisasi encryptor dengan kurva tertentu"""
        self.curve = curve
        self.private_key = None
        self.public_key = None
        
    def generate_keys(self):
        """Generate kunci baru"""
        print(f"🔑 Generating {self.curve} keys...")
        self.private_key = PrivateKey(self.curve)
        self.public_key = self.private_key.public_key
        
        # Simpan ke file
        self._save_keys()
        print("✅ Keys generated and saved!")
        return self.private_key, self.public_key
    
    def _save_keys(self, key_dir="~/.ecies_keys"):
        """Simpan kunci ke file"""
        key_dir = Path(key_dir).expanduser()
        key_dir.mkdir(exist_ok=True, mode=0o700)
        
        # Simpan private key (hex)
        private_key_file = key_dir / "private_key.pem"
        with open(private_key_file, 'w') as f:
            f.write(self.private_key.to_hex())
        os.chmod(private_key_file, 0o600)
        
        # Simpan public key (hex)
        public_key_file = key_dir / "public_key.pem"
        with open(public_key_file, 'w') as f:
            if self.curve == 'secp256k1':
                f.write(self.public_key.to_hex(compressed=True))
            else:
                f.write(self.public_key.to_hex())
        os.chmod(public_key_file, 0o644)
        
        # Simpan metadata
        meta = {
            "curve": self.curve,
            "private_key_path": str(private_key_file),
            "public_key_path": str(public_key_file)
        }
        
        meta_file = key_dir / "key_meta.json"
        with open(meta_file, 'w') as f:
            json.dump(meta, f, indent=2)
    
    def load_keys(self, key_dir="~/.ecies_keys"):
        """Load kunci dari file"""
        key_dir = Path(key_dir).expanduser()
        
        # Load metadata
        meta_file = key_dir / "key_meta.json"
        if not meta_file.exists():
            raise FileNotFoundError(f"Key files not found in {key_dir}")
        
        with open(meta_file, 'r') as f:
            meta = json.load(f)
        
        self.curve = meta['curve']
        
        # Load private key
        with open(meta['private_key_path'], 'r') as f:
            private_key_hex = f.read().strip()
        self.private_key = PrivateKey.from_hex(private_key_hex, self.curve)
        
        # Load public key
        with open(meta['public_key_path'], 'r') as f:
            public_key_hex = f.read().strip()
        
        print(f"✅ Loaded {self.curve} keys from {key_dir}")
        return self.private_key
    
    def encrypt_file(self, input_path, output_path=None, public_key_hex=None):
        """Enkripsi file tunggal"""
        input_path = Path(input_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"File {input_path} not found")
        
        # Baca file
        with open(input_path, 'rb') as f:
            data = f.read()
        
        # Gunakan public key dari parameter atau yang sudah ada
        if public_key_hex:
            pk_bytes = bytes.fromhex(public_key_hex.replace('0x', ''))
        elif self.public_key:
            if self.curve == 'secp256k1':
                pk_bytes = self.public_key.to_bytes(compressed=True)
            else:
                pk_bytes = self.public_key.to_bytes()
        else:
            raise ValueError("No public key provided")
        
        # Enkripsi data
        encrypted_data = encrypt(pk_bytes, data)
        
        # Tentukan output path
        if output_path is None:
            output_path = input_path.with_suffix(input_path.suffix + '.enc')
        
        # Tulis file terenkripsi
        with open(output_path, 'wb') as f:
            f.write(encrypted_data)
        
        # Simpan hash untuk verifikasi
        original_hash = hashlib.sha256(data).hexdigest()
        hash_file = output_path.with_suffix('.sha256')
        with open(hash_file, 'w') as f:
            f.write(f"original_hash={original_hash}\n")
            f.write(f"original_file={input_path}\n")
            f.write(f"encrypted_file={output_path}\n")
        
        print(f"🔒 Encrypted: {input_path} -> {output_path}")
        print(f"   Hash: {original_hash}")
        
        return output_path
    
    def decrypt_file(self, input_path, output_path=None):
        """Dekripsi file tunggal"""
        input_path = Path(input_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"File {input_path} not found")
        
        if not self.private_key:
            raise ValueError("Private key not loaded")
        
        # Baca file terenkripsi
        with open(input_path, 'rb') as f:
            encrypted_data = f.read()
        
        # Dekripsi data
        if self.curve == 'secp256k1':
            sk_bytes = self.private_key.secret
        else:
            sk_bytes = self.private_key.to_bytes()
        
        decrypted_data = decrypt(sk_bytes, encrypted_data)
        
        # Tentukan output path
        if output_path is None:
            if input_path.suffix == '.enc':
                output_path = input_path.with_suffix('')
            else:
                output_path = input_path.with_suffix('.decrypted')
        
        # Tulis file terdekripsi
        with open(output_path, 'wb') as f:
            f.write(decrypted_data)
        
        # Verifikasi hash jika ada
        hash_file = input_path.with_suffix('.sha256')
        if hash_file.exists():
            with open(hash_file, 'r') as f:
                lines = f.readlines()
                original_hash = None
                for line in lines:
                    if line.startswith('original_hash='):
                        original_hash = line.split('=')[1].strip()
            
            decrypted_hash = hashlib.sha256(decrypted_data).hexdigest()
            
            if original_hash == decrypted_hash:
                print(f"✅ Hash verified: {original_hash}")
            else:
                print(f"⚠️  Hash mismatch! Original: {original_hash}, Decrypted: {decrypted_hash}")
        
        print(f"🔓 Decrypted: {input_path} -> {output_path}")
        
        return output_path
    
    def encrypt_directory(self, directory_path, recursive=True, extension=None):
        """Enkripsi seluruh file dalam direktori"""
        directory_path = Path(directory_path)
        
        if not directory_path.is_dir():
            raise NotADirectoryError(f"{directory_path} is not a directory")
        
        encrypted_files = []
        
        # Pattern untuk mencari file
        if extension:
            pattern = f"**/*{extension}" if recursive else f"*{extension}"
        else:
            pattern = "**/*" if recursive else "*"
        
        for file_path in directory_path.glob(pattern):
            if file_path.is_file() and not file_path.suffix == '.enc':
                try:
                    encrypted_file = self.encrypt_file(file_path)
                    encrypted_files.append(encrypted_file)
                except Exception as e:
                    print(f"❌ Error encrypting {file_path}: {e}")
        
        print(f"\n📊 Summary: Encrypted {len(encrypted_files)} files")
        return encrypted_files
    
    def decrypt_directory(self, directory_path, recursive=True):
        """Dekripsi seluruh file dalam direktori"""
        directory_path = Path(directory_path)
        
        if not directory_path.is_dir():
            raise NotADirectoryError(f"{directory_path} is not a directory")
        
        decrypted_files = []
        
        for file_path in directory_path.glob("**/*.enc" if recursive else "*.enc"):
            if file_path.is_file():
                try:
                    decrypted_file = self.decrypt_file(file_path)
                    decrypted_files.append(decrypted_file)
                except Exception as e:
                    print(f"❌ Error decrypting {file_path}: {e}")
        
        print(f"\n📊 Summary: Decrypted {len(decrypted_files)} files")
        return decrypted_files

def main():
    parser = argparse.ArgumentParser(
        description="🔐 File Encryption Tool using ECIES",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --generate --curve secp256k1
  %(prog)s --encrypt /path/to/file.txt --public-key public_key.pem
  %(prog)s --decrypt /path/to/file.txt.enc
  %(prog)s --encrypt-dir /home/user/Documents --recursive
  %(prog)s --decrypt-dir /home/user/encrypted_files
        """
    )
    
    # Mode operasi
    mode_group = parser.add_argument_group('Mode')
    mode_group.add_argument('--generate', '-g', action='store_true',
                          help='Generate new key pair')
    mode_group.add_argument('--encrypt', '-e', type=str,
                          help='Encrypt a single file')
    mode_group.add_argument('--decrypt', '-d', type=str,
                          help='Decrypt a single file')
    mode_group.add_argument('--encrypt-dir', type=str,
                          help='Encrypt all files in directory')
    mode_group.add_argument('--decrypt-dir', type=str,
                          help='Decrypt all files in directory')
    
    # Kunci
    key_group = parser.add_argument_group('Keys')
    key_group.add_argument('--public-key', '-pk', type=str,
                         help='Public key file (for encryption)')
    key_group.add_argument('--private-key', '-sk', type=str,
                         help='Private key file (for decryption)')
    key_group.add_argument('--key-dir', type=str, default="~/.ecies_keys",
                         help='Directory to store/load keys (default: ~/.ecies_keys)')
    
    # Konfigurasi
    config_group = parser.add_argument_group('Configuration')
    config_group.add_argument('--curve', '-c', type=str, default='secp256k1',
                            choices=['secp256k1', 'x25519', 'ed25519'],
                            help='Elliptic curve to use (default: secp256k1)')
    config_group.add_argument('--recursive', '-r', action='store_true',
                            help='Process directories recursively')
    config_group.add_argument('--extension', type=str,
                            help='Only process files with this extension')
    config_group.add_argument('--output', '-o', type=str,
                            help='Output file/directory path')
    
    args = parser.parse_args()
    
    # Validasi input
    if not any([args.generate, args.encrypt, args.decrypt, 
                args.encrypt_dir, args.decrypt_dir]):
        parser.print_help()
        sys.exit(1)
    
    # Inisialisasi encryptor
    encryptor = FileEncryptor(curve=args.curve)
    
    try:
        # Mode generate keys
        if args.generate:
            encryptor.generate_keys()
            
            # Tampilkan info kunci
            print("\n" + "="*50)
            print("🔑 KEY INFORMATION")
            print("="*50)
            print(f"Curve: {args.curve}")
            print(f"Private Key: {encryptor.private_key.to_hex()}")
            if args.curve == 'secp256k1':
                print(f"Public Key: {encryptor.public_key.to_hex(compressed=True)}")
                print(f"Address: {encryptor.public_key.to_address()}")
            else:
                print(f"Public Key: {encryptor.public_key.to_hex()}")
            print(f"Keys saved to: {Path(args.key_dir).expanduser()}")
            print("="*50)
        
        # Mode encrypt file
        elif args.encrypt:
            if args.public_key:
                with open(args.public_key, 'r') as f:
                    public_key_hex = f.read().strip()
                encryptor.encrypt_file(args.encrypt, args.output, public_key_hex)
            else:
                encryptor.load_keys(args.key_dir)
                encryptor.encrypt_file(args.encrypt, args.output)
        
        # Mode decrypt file
        elif args.decrypt:
            encryptor.load_keys(args.key_dir)
            encryptor.decrypt_file(args.decrypt, args.output)
        
        # Mode encrypt directory
        elif args.encrypt_dir:
            if args.public_key:
                with open(args.public_key, 'r') as f:
                    public_key_hex = f.read().strip()
                encryptor.public_key = public_key_hex
            else:
                encryptor.load_keys(args.key_dir)
            
            encryptor.encrypt_directory(
                args.encrypt_dir, 
                recursive=args.recursive,
                extension=args.extension
            )
        
        # Mode decrypt directory
        elif args.decrypt_dir:
            encryptor.load_keys(args.key_dir)
            encryptor.decrypt_directory(
                args.decrypt_dir,
                recursive=args.recursive
            )
    
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()