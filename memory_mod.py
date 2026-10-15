import struct
import pymem
import pymem.pattern
import pymem.process


def safe_pattern(pattern_bytes: bytes) -> bytes:
  """Mengamankan byte pattern agar karakter ASCII regex seperti '[' (0x5B)

  tidak dianggap sebagai regex character set oleh scanner.
  """
  regex_special = set(b"[]()*+?\\^${}")
  out = bytearray()
  for b in pattern_bytes:
    if b in regex_special:
      out.extend(b"\\" + bytes([b]))
    else:
      out.append(b)
  return bytes(out)


class DW6Trainer:

  def __init__(self):
    self.pm = None
    self.base_address = None
    self.process_name = "DW6_WIN.exe"
    self.injections = {}

    # Database AOB & Payload Injection
    self.CHEATS = {
        "hp": {
            "name": "Infinite HP",
            "pattern": (
                b"\x0F\x2F\x86\x04\x01\x00\x00\x77.\x5B\x8D\x86\x98\x00\x00\x00"
            ),
            "size": 7,
            "payload": (
                b"\xF3\x0F\x10\x86\x00\x01\x00\x00\xF3\x0F\x11\x86\x04\x01\x00\x00\x0F\x2F\x86\x04\x01\x00\x00"
            ),
        },
        "musou": {
            "name": "Infinite Musou",
            "pattern": (
                b"\xF3\x0F\x10\x84\x02....\xF3\x0F\x10\x8C\x02....\x8D\x84\x02...."
            ),
            "size": 9,
            "payload": (
                b"\xF3\x0F\x10\x84\x02\x3C\x0F\x00\x00\xF3\x0F\x11\x84\x02\x40\x0F\x00\x00"
            ),
        },
        "renbu": {
            "name": "Full Renbu Gauge",
            "pattern": b"\xF3\x0F\x10\x85\x18\x01\x00\x00\x75.\xF3\x0F\x2C\xC0",
            "size": 8,
            "payload": (
                b"\xC7\x85\x18\x01\x00\x00\x00\x00\x7A\x44\xF3\x0F\x10\x85\x18\x01\x00\x00"
            ),
        },
        "level": {
            "name": "Instant Max Level / EXP",
            "pattern": b"\x89\x86\x98\x00\x00\x00\x5E\x5B",
            "size": 6,
            "payload": b"\xB8\x9F\x86\x01\x00\x89\x86\x98\x00\x00\x00",
        },
        "weapon": {
            "name": "Max Highlighted Weapon",
            "pattern": b"\x8B\x8E\x60\x0E\x00\x00\x8B\x19\x0F\x85",
            "size": 6,
            # PERBAIKAN PAYLOAD:
            # 1. mov ecx,[esi+0x0E60]           (6 byte)
            # 2. test ecx,ecx                   (2 byte)
            # 3. jz +0x15                       (2 byte -> lompat 21 byte jika pointer NULL)
            # 4. mov dword ptr [ecx+0x04], 100  (7 byte -> Atk Max Cap 100)
            # 5. mov dword ptr [ecx+0x08], 1    (7 byte -> Element Ice)
            # 6. mov dword ptr [ecx+0x0C], 0x1F (7 byte -> 5 Efek Max = Bitmask 31)
            "payload": (
                b"\x8B\x8E\x60\x0E\x00\x00"
                b"\x85\xC9"
                b"\x74\x15"
                b"\xC7\x41\x04\x64\x00\x00\x00"
                b"\xC7\x41\x08\x01\x00\x00\x00"
                b"\xC7\x41\x0C\x1F\x00\x00\x00"
            ),
        },
        "horse": {
            "name": "Max Highlighted Horse",
            "pattern": b"\x8B\x4A\x18\xF2\x0F\x5A\xC0\x33\xC0",
            "size": 7,
            "payload": (
                b"\x8B\x4A\x18\xC7\x42\x18\x9F\x86\x01\x00\xC7\x42\x28\xF4\x01\x00\x00\xC7\x42\x2C\xF4\x01\x00\x00\xC7\x42\x30\xF4\x01\x00\x00\xC7\x42\x34\xF4\x01\x00\x00\xC7\x42\x38\xF4\x01\x00\x00\xC7\x42\x24\xFF\x00\x00\x00"
            ),
        },
    }

  def connect(self) -> bool:
    try:
      self.pm = pymem.Pymem(self.process_name)
      module = pymem.process.module_from_name(
          self.pm.process_handle, self.process_name
      )
      self.base_address = module.lpBaseOfDll
      return True
    except Exception:
      self.pm = None
      self.base_address = None
      return False

  def toggle_cheat(self, key: str) -> str:
    if not self.pm and not self.connect():
      return "Gagal: DW6_WIN.exe belum berjalan / Jalankan CMD as Admin!"

    if key not in self.CHEATS:
      return "Fitur tidak valid."

    cheat = self.CHEATS[key]

    if key in self.injections:
      info = self.injections[key]
      try:
        self.pm.write_bytes(
            info["target_addr"], info["orig_bytes"], cheat["size"]
        )
        self.pm.free(info["cave_addr"])
        del self.injections[key]
        return f"{cheat['name']}: OFF"
      except Exception as e:
        return f"Error Disable: {e}"

    try:
      module = pymem.process.module_from_name(
          self.pm.process_handle, self.process_name
      )

      scanned_pattern = safe_pattern(cheat["pattern"])
      target_addr = pymem.pattern.pattern_scan_module(
          self.pm.process_handle, module, scanned_pattern
      )

      if not target_addr:
        return f"Gagal: AOB Pattern {cheat['name']} tidak ditemukan!"

      cave_addr = self.pm.allocate(128)
      orig_bytes = self.pm.read_bytes(target_addr, cheat["size"])

      return_addr = target_addr + cheat["size"]
      payload = cheat["payload"]

      jmp_back_offset = return_addr - (cave_addr + len(payload) + 5)
      full_cave_code = payload + b"\xE9" + struct.pack("<i", jmp_back_offset)

      self.pm.write_bytes(cave_addr, full_cave_code, len(full_cave_code))

      jmp_to_cave_offset = cave_addr - (target_addr + 5)
      inject_jmp = b"\xE9" + struct.pack("<i", jmp_to_cave_offset)
      if cheat["size"] > 5:
        inject_jmp += b"\x90" * (cheat["size"] - 5)

      self.pm.write_bytes(target_addr, inject_jmp, cheat["size"])

      self.injections[key] = {
          "target_addr": target_addr,
          "cave_addr": cave_addr,
          "orig_bytes": orig_bytes,
      }

      return f"{cheat['name']}: ON"

    except Exception as e:
      return f"Error Inject: {e}"

  def toggle_hp(self):
    return self.toggle_cheat("hp")

  def toggle_musou(self):
    return self.toggle_cheat("musou")

  def toggle_renbu(self):
    return self.toggle_cheat("renbu")

  def toggle_level(self):
    return self.toggle_cheat("level")

  def toggle_weapon(self):
    return self.toggle_cheat("weapon")

  def toggle_horse(self):
    return self.toggle_cheat("horse")