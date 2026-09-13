from os.path import join, isfile, exists
from os import rename, remove, environ
import glob
import sys

Import("env")

# Ищем libnet80211.a по ВСЕМ возможным путям
board_mcu = env.BoardConfig()
mcu = board_mcu.get("build.mcu", "")

search_paths = [
    # проект .pio
    join(env.subst("$PROJECT_DIR"), ".pio", "packages", "framework-arduinoespressif32", "tools", "sdk", mcu, "lib", "libnet80211.a"),
    # глобальный ~/.platformio
    join(environ.get("HOME", ""), ".platformio", "packages", "framework-arduinoespressif32", "tools", "sdk", mcu, "lib", "libnet80211.a"),
]

# плюс любые framework-arduinoespressif32* в обоих местах
for base in [
    join(env.subst("$PROJECT_DIR"), ".pio", "packages"),
    join(environ.get("HOME", ""), ".platformio", "packages"),
]:
    for d in glob.glob(join(base, "framework-arduinoespressif32*")):
        search_paths.append(join(d, "tools", "sdk", mcu, "lib", "libnet80211.a"))

original_file = None
FRAMEWORK_DIR = None
for p in search_paths:
    if isfile(p):
        original_file = p
        # FRAMEWORK_DIR = три уровня вверх от libnet80211.a
        FRAMEWORK_DIR = p.split("/tools/sdk/")[0]
        break

if original_file is None:
    print("libnet80211.a NOT FOUND — skipping patch")
    env.Exit(0)

print("FOUND: " + original_file)
patchflag_path = join(FRAMEWORK_DIR, ".patched")
