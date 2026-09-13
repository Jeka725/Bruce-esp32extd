from os.path import join, isfile
from os import rename, remove, environ
import sys

Import("env")

# Пытаемся найти framework через pioarduino
FRAMEWORK_DIR = None
try:
    FRAMEWORK_DIR = env.PioPlatform().get_package_dir("framework-arduinoespressif32")
except:
    pass

# Если не нашли — ищем в ~/.platformio/packages/
if not FRAMEWORK_DIR or not isfile(join(FRAMEWORK_DIR, "package.json")):
    home = environ.get("HOME", "")
    candidate = join(home, ".platformio", "packages", "framework-arduinoespressif32")
    if isfile(join(candidate, "package.json")):
        FRAMEWORK_DIR = candidate
    else:
        # Ищем через glob
        import glob
        matches = glob.glob(join(home, ".platformio", "packages", "framework-arduinoespressif32*"))
        for m in matches:
            if isfile(join(m, "package.json")):
                FRAMEWORK_DIR = m
                break

if not FRAMEWORK_DIR or not isfile(join(FRAMEWORK_DIR, "package.json")):
    print("Framework not found — skipping patch")
    env.Exit(0)

patchflag_path = join(FRAMEWORK_DIR, ".patched")
board_mcu = env.BoardConfig()
mcu = board_mcu.get("build.mcu", "")

# patch file only if we didn't do it befored
if not isfile(join(FRAMEWORK_DIR, ".patched")):
    original_file = join(FRAMEWORK_DIR, "tools", "sdk", mcu, "lib", "libnet80211.a")
    patched_file = join(FRAMEWORK_DIR, "tools", "sdk", mcu, "lib", "libnet80211.a.patched")

    env.Execute("pio pkg exec -p toolchain-xtensa-%s -- xtensa-%s-elf-objcopy  --weaken-symbol=s %s %s" % (mcu, mcu, original_file, patched_file))
    if(isfile("%s.old"%(original_file))):
        remove("%s.old"%(original_file))
    rename(original_file,"%s.old"%(original_file))
    env.Execute("pio pkg exec -p toolchain-xtensa-%s -- xtensa-%s-elf-objcopy  --weaken-symbol=ieee80211_raw_frame_sanity_check %s %s" % (mcu, mcu, patched_file, original_file))

    def _touch(path):
        with open(path, "w") as fp:
            fp.write("")

    env.Execute(lambda *args, **kwargs: _touch(patchflag_path))
