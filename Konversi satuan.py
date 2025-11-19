import sys
import math
import time
import random

DATA = {
    "Fisika": {
        "Tekanan": ["Pa", "kPa", "MPa", "bar", "atm", "mmHg", "psi"],
        "Suhu": ["C", "K", "F"],
        "Kalor & Energi": ["J", "kJ", "cal"],
        "Panjang": ["mm", "cm", "m", "km", "inch", "ft"],
        "Kecepatan": ["m/s", "km/h"]
    },
    "Kimia": {
        "Gas Ideal (PVT)": ["Pa", "kPa", "atm", "mmHg", "L", "mL", "m^3", "C", "K"],
        "Larutan & Konsentrasi": ["mol/L", "M", "%", "ppm", "L", "mL"],
        "Termokimia": ["J", "kJ", "cal", "C", "K"],
        "Massa & Mol": ["mg", "g", "kg", "mol"]
    },
    "Matematika": {
        "Panjang & Luas": ["mm", "cm", "m", "km", "cm^2", "m^2", "km^2", "inch"],
        "Volume": ["cm^3", "m^3", "L", "mL"],
        "Sudut": ["deg", "rad"],
        "Kecepatan": ["m/s", "km/h"],
        "Persentase": ["%", "desimal"]
    }
}

LENGTH = {'mm': 0.001, 'cm': 0.01, 'm': 1.0, 'km': 1000.0, 'inch': 0.0254, 'ft': 0.3048}
AREA   = {'cm^2': 0.0001, 'm^2': 1.0, 'km^2': 1_000_000.0}
VOLUME = {'cm^3': 1e-6, 'm^3': 1.0, 'L': 0.001, 'mL': 1e-6}
MASS   = {'mg': 1e-6, 'g': 1e-3, 'kg': 1.0}
PRESS  = {'Pa':1.0, 'kPa':1000.0, 'MPa':1e6, 'bar':100000.0, 'atm':101325.0, 'mmHg':133.322, 'psi':6894.76}
ENERGY = {'J':1.0, 'kJ':1000.0, 'cal':4.184}
SPEED_FACT = {('m/s','km/h'):3.6, ('km/h','m/s'):1/3.6}
PERCENT = {'%':'percent','desimal':'decimal'} 
ANGLE = {'deg':'deg','rad':'rad'}

HISTORY = []

def pretty(n):
    """Format number: up to 10 significant digits, fall back to exponential if too large/small."""
    if n is None or (isinstance(n, float) and (math.isnan(n) or math.isinf(n))):
        return "NaN"
    try:
        if abs(n) != 0 and (abs(n) < 1e-6 or abs(n) > 1e9):
            return f"{n:.6e}"
        
        s = f"{n:.10g}"
        return s
    except Exception:
        return str(n)

def input_number(prompt):
    """Safe numeric input; repeats until user inputs a valid number or types 'back'."""
    while True:
        s = input(prompt).strip()
        if s.lower() in ('back','b'):
            return None
        s = s.replace(',','.')
        try:
            val = float(s)
            return val
        except ValueError:
            print("  ❌ Input bukan angka. Ketik angka seperti 12.5 atau ketik 'back' untuk kembali.")


def convert_generic(value, from_u, to_u, extra=None):
    """Try to convert value from from_u to to_u. extra is a dict for molar_mass, etc."""
    # identical
    if from_u == to_u:
        return value

    # Length
    if from_u in LENGTH and to_u in LENGTH:
        return value * LENGTH[from_u] / LENGTH[to_u]

    # Area
    if from_u in AREA and to_u in AREA:
        return value * AREA[from_u] / AREA[to_u]

    # Volume
    if from_u in VOLUME and to_u in VOLUME:
        return value * VOLUME[from_u] / VOLUME[to_u]

    # Mass
    if from_u in MASS and to_u in MASS:
        return value * MASS[from_u] / MASS[to_u]

    # Pressure
    if from_u in PRESS and to_u in PRESS:
        return value * PRESS[from_u] / PRESS[to_u]

    # Energy
    if from_u in ENERGY and to_u in ENERGY:
        return value * ENERGY[from_u] / ENERGY[to_u]

    # Speed
    if (from_u, to_u) in SPEED_FACT:
        return value * SPEED_FACT[(from_u,to_u)]

    # Temperature conversions
    if from_u == 'C' and to_u == 'K':
        return value + 273.15
    if from_u == 'K' and to_u == 'C':
        return value - 273.15
    if from_u == 'C' and to_u == 'F':
        return value * 9/5 + 32
    if from_u == 'F' and to_u == 'C':
        return (value - 32) * 5/9
    if from_u == 'K' and to_u == 'F':
        return (value - 273.15) * 9/5 + 32
    if from_u == 'F' and to_u == 'K':
        return (value - 32) * 5/9 + 273.15

    # Percent <-> decimal
    if from_u == '%' and to_u == 'desimal':
        return value / 100.0
    if from_u == 'desimal' and to_u == '%':
        return value * 100.0

    # Angle deg <-> rad
    if from_u == 'deg' and to_u == 'rad':
        return math.radians(value)
    if from_u == 'rad' and to_u == 'deg':
        return math.degrees(value)

    # mol <-> g using molar mass (g/mol)
    if (from_u == 'g' and to_u == 'mol') or (from_u == 'mol' and to_u == 'g'):
        mm = None
        if extra and 'molar_mass' in extra:
            mm = extra['molar_mass']
        if not mm:
            return None  # needs molar mass
        try:
            mm = float(mm)
        except Exception:
            return None
        if from_u == 'g':
            return value / mm
        else:
            return value * mm

    # Fallback: unsupported
    return None

# -----------------------
# UI helpers
# -----------------------
def clear_screen():
    print("\n" * 2)

def banner():
    print("="*48)
    print("  KONVERTER SATUAN — Fisika • Kimia • Matematika")
    print("="*48)

def motivational():
    msgs = [
        "Good job! Keep going 💪",
        "Nice — semoga kamu makin pinter! ✨",
        "Mantap, lanjut lagi! 🚀",
        "Hebat! Jangan lupa istirahat juga ya 😌"
    ]
    print("\n" + random.choice(msgs) + "\n")

def welcome():
    msgs = [
        "Welcome to Converter",
        "Selamat menggunakan 🙌",
        "Ayo kita mulai 🚀",
        "Mari Kubantu kerjakan tugas 😌"
    ]
    print("\n" + random.choice(msgs) + "\n")


def page_select_subject():
    clear_screen()
    banner()
    welcome()
    subjects = list(DATA.keys())
    for i, s in enumerate(subjects, 1):
        print(f"{i}. {s}")
    print("0. Keluar")

    while True:
        choice = input("Pilih mata pelajaran (ketik nomor): ").strip()
        if choice == '0':
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(subjects):
            return subjects[int(choice)-1]
        print("  ❌ Pilihan tidak valid. Coba lagi.")

def page_subject_actions(subject):
    """Page 2: choose chapter -> do conversions. Provide back option."""
    while True:
        clear_screen()
        banner()
        print(f"Mapel: {subject}")
        chapters = list(DATA[subject].keys())
        for i, ch in enumerate(chapters, 1):
            print(f"{i}. {ch}")
        print("b. Kembali ke pemilihan mapel")
        print("h. Lihat history")
        print("q. Keluar")

        choice = input("Pilih bab (nomor) atau perintah: ").strip().lower()
        if choice == 'b':
            return  
        if choice == 'h':
            show_history()
            input("Tekan Enter untuk lanjut...")
            continue
        if choice == 'q':
            if confirm_quit() is False:
                continue

        if choice.isdigit() and 1 <= int(choice) <= len(chapters):
            chapter = chapters[int(choice)-1]
            handle_conversion_page(subject, chapter)
            continue
        print("  ❌ Pilihan tidak valid.")

def show_history():
    clear_screen()
    print("=== HISTORY KONVERSI ===")
    if not HISTORY:
        print(" - Belum ada riwayat konversi -")
    else:
        for i, item in enumerate(HISTORY, 1):
            print(f"{i}. {item}")
    print("="*28)

def handle_conversion_page(subject, chapter):
    units = DATA[subject][chapter]
    while True:
        clear_screen()
        print(f"Mapel: {subject}  →  Bab: {chapter}")
        print("-"*40)
        print("Units available:", ", ".join(units))
        print("Commands: swap | back | history | menu | quit")
        print("-"*40)

        # from unit
        from_u = input("Masukkan satuan awal (teks persis seperti di atas): ").strip()
        if from_u.lower() in ('back','b'):
            return
        if from_u.lower() in ('menu','m'):
            
            raise SystemExit("Returning to menu")
        if from_u.lower() == 'history':
            show_history(); input("Enter to continue..."); continue
        if from_u.lower() == 'quit' or from_u.lower() == 'q':
            if confirm_quit() is False:
                continue

        if from_u == 'swap':
            print("Ketik swap hanya setelah memilih kedua unit. Lanjut ulang.")
            continue
        if from_u not in units:
            print("  ❌ Satuan awal tidak ada di list. Coba lagi.")
            time.sleep(1.0)
            continue

        to_u = input("Masukkan satuan akhir: ").strip()
        if to_u.lower() in ('back','b'):
            return
        if to_u not in units:
            print("  ❌ Satuan akhir tidak ada di list. Coba lagi.")
            time.sleep(1.0)
            continue

        # swap functionality
        if from_u == 'swap' or to_u == 'swap':
            from_u, to_u = to_u, from_u

        # extra input: molar mass if needed
        extra = {}
        if (from_u == 'g' and to_u == 'mol') or (from_u == 'mol' and to_u == 'g'):
            mm = input("Masukkan molar mass (g/mol) — misal 18.015 (ketik 'back' untuk batal): ").strip()
            if mm.lower() in ('back','b'):
                continue
            try:
                extra['molar_mass'] = float(mm)
            except ValueError:
                print("  ❌ Molar mass harus angka. Kembali ke awal bab.")
                time.sleep(1)
                continue

        # input value
        val = input_number("Masukkan nilai (atau ketik 'back' untuk batal): ")
        if val is None:
            continue

        # perform convert
        out = convert_generic(val, from_u, to_u, extra=extra)
        if out is None:
            print("  ❌ Konversi tidak didukung atau butuh input tambahan.")
            time.sleep(1.3)
            continue

        # show result
        print("\n✨ Hasil Konversi:")
        print(f"  {pretty(val)} {from_u}  →  {pretty(out)} {to_u}")
        HISTORY.insert(0, f"{time.strftime('%H:%M:%S')} | {val} {from_u} -> {pretty(out)} {to_u}")
        if len(HISTORY) > 50:
            HISTORY.pop()

        motivational()
        
        while True:
            nxt = input("Mau konversi lagi di bab ini? (y) / ganti bab (b) / menu mapel (m) / keluar (q): ").strip().lower()
            if nxt == 'y' or nxt == '':
                break 
            elif nxt == 'b':
                return  
            elif nxt == 'm':
                raise SystemExit("back to menu")
            elif nxt == 'q':
                if confirm_quit() is False:
                    continue


            else:
                print("Pilihan nggak valid. Ketik y/b/m/q.")

def confirm_quit():
    while True:
        c = input("❓ Kamu yakin ingin keluar? (y/n): ").strip().lower()
        if c == 'y':
            print("Terima kasih sudah pakai konverter! Semangat belajarnya ya 💛")
            sys.exit()

        elif c == 'n':
            print("Sip, kita lanjut lagi 😎\n")
            return False
        else:
            print("Ketik 'y' atau 'n' ya!")

def main():
    while True:
        try:
            subj = page_select_subject()
            if subj is None:
                print("Makasih udah pake konverter. Semangat belajar! ✨")
                break
            page_subject_actions(subj)
        except SystemExit as e:
            msg = str(e)
            if msg == "Returning to menu":
                continue
            if msg == "back to menu":
                continue
            break
        except KeyboardInterrupt:
            print("\nKeluar. Jaga kesehatan ya! 💛")
            break
        except KeyboardInterrupt:
            if confirm_quit() is False:
                continue

if __name__ == "__main__":
    main()