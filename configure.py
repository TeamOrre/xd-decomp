#!/usr/bin/env python3

###
# Generates build files for the project.
# This file also includes the project configuration,
# such as compiler flags and the object matching status.
#
# Usage:
#   python3 configure.py
#   ninja
#
# Append --help to see available options.
###

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List

from tools.project import (
    Object,
    ProgressCategory,
    ProjectConfig,
    calculate_progress,
    generate_build,
    is_windows,
)

# Game versions
DEFAULT_VERSION = 0
VERSIONS = [
    "GXXE01",  # 0
    "NXXJ01"
]

parser = argparse.ArgumentParser()
parser.add_argument(
    "mode",
    choices=["configure", "progress"],
    default="configure",
    help="script mode (default: configure)",
    nargs="?",
)
parser.add_argument(
    "-v",
    "--version",
    choices=VERSIONS,
    type=str.upper,
    default=VERSIONS[DEFAULT_VERSION],
    help="version to build",
)
parser.add_argument(
    "--build-dir",
    metavar="DIR",
    type=Path,
    default=Path("build"),
    help="base build directory (default: build)",
)
parser.add_argument(
    "--binutils",
    metavar="BINARY",
    type=Path,
    help="path to binutils (optional)",
)
parser.add_argument(
    "--compilers",
    metavar="DIR",
    type=Path,
    help="path to compilers (optional)",
)
parser.add_argument(
    "--map",
    action="store_true",
    help="generate map file(s)",
)
parser.add_argument(
    "--debug",
    action="store_true",
    help="build with debug info (non-matching)",
)
if not is_windows():
    parser.add_argument(
        "--wrapper",
        metavar="BINARY",
        type=Path,
        help="path to wibo or wine (optional)",
    )
parser.add_argument(
    "--dtk",
    metavar="BINARY | DIR",
    type=Path,
    help="path to decomp-toolkit binary or source (optional)",
)
parser.add_argument(
    "--objdiff",
    metavar="BINARY | DIR",
    type=Path,
    help="path to objdiff-cli binary or source (optional)",
)
parser.add_argument(
    "--sjiswrap",
    metavar="EXE",
    type=Path,
    help="path to sjiswrap.exe (optional)",
)
parser.add_argument(
    "--ninja",
    metavar="BINARY",
    type=Path,
    help="path to ninja binary (optional)"
)
parser.add_argument(
    "--verbose",
    action="store_true",
    help="print verbose output",
)
parser.add_argument(
    "--non-matching",
    dest="non_matching",
    action="store_true",
    help="builds equivalent (but non-matching) or modded objects",
)
parser.add_argument(
    "--warn",
    dest="warn",
    type=str,
    choices=["all", "off", "error"],
    help="how to handle warnings",
)
parser.add_argument(
    "--no-progress",
    dest="progress",
    action="store_false",
    help="disable progress calculation",
)
args = parser.parse_args()

config = ProjectConfig()
config.version = str(args.version)
version_num = VERSIONS.index(config.version)

# Apply arguments
config.build_dir = args.build_dir
config.dtk_path = args.dtk
config.objdiff_path = args.objdiff
config.binutils_path = args.binutils
config.compilers_path = args.compilers
config.generate_map = args.map
config.non_matching = args.non_matching
config.sjiswrap_path = args.sjiswrap
config.ninja_path = args.ninja
config.progress = args.progress
if not is_windows():
    config.wrapper = args.wrapper
# Don't build asm unless we're --non-matching
if not config.non_matching:
    config.asm_dir = None

# Tool versions
config.binutils_tag = "2.42-2"
config.compilers_tag = "20251118"
config.dtk_tag = "v1.9.1"
config.objdiff_tag = "v3.6.1"
config.sjiswrap_tag = "v1.2.2"
config.wibo_tag = "1.0.3"

# Project
config.config_path = Path("config") / config.version / "config.yml"
config.check_sha_path = Path("config") / config.version / "build.sha1"
config.asflags = [
    "-mgekko",
    "--strip-local-absolute",
    "-I include",
    f"-I build/{config.version}/include",
    f"--defsym BUILD_VERSION={version_num}",
]
config.ldflags = [
    "-fp hardware",
    "-nodefaults",
]
if args.debug:
    config.ldflags.append("-g")  # Or -gdwarf-2 for Wii linkers
if args.map:
    config.ldflags.append("-mapunused")
    # config.ldflags.append("-listclosure") # For Wii linkers

# Use for any additional files that should cause a re-configure when modified
config.reconfig_deps = []

# Optional numeric ID for decomp.me preset
# Can be overridden in libraries or objects
config.scratch_preset_id = None

# Base flags, common to most GC/Wii games.
# Generally leave untouched, with overrides added below.
cflags_base = [
    "-nodefaults",
    "-proc gekko",
    "-align powerpc",
    "-enum int",
    "-fp hardware",
    "-Cpp_exceptions off",
    # "-W all",
    "-O4,p",
    "-inline auto",
    '-pragma "cats off"',
    '-pragma "warn_notinlined off"',
    "-maxerrors 1",
    "-nosyspath",
    "-RTTI off",
    "-fp_contract on",
    "-str reuse",
    "-multibyte",  # For Wii compilers, replace with `-enc SJIS`
    "-i include",
    f"-i build/{config.version}/include",
    f"-DBUILD_VERSION={version_num}",
    f"-DVERSION_{config.version}",
    "-i libs/dolphin/include",
    "-i libs/PowerPC_EABI_Support/MSL_C/MSL_Common/Include",
    "-i libs/PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Include",
    "-i libs/PowerPC_EABI_Support/MSL_C/PPC_EABI/Include",
    "-i libs/PowerPC_EABI_Support/Runtime/Inc",
]

# Debug flags
if args.debug:
    # Or -sym dwarf-2 for Wii compilers
    cflags_base.extend(["-sym on", "-DDEBUG=1"])
else:
    cflags_base.append("-DNDEBUG=1")

# Warning flags
if args.warn == "all":
    cflags_base.append("-W all")
elif args.warn == "off":
    cflags_base.append("-W off")
elif args.warn == "error":
    cflags_base.append("-W error")

# Metrowerks library flags
cflags_runtime = [
    *cflags_base,
    "-use_lmw_stmw on",
    "-str reuse,pool,readonly",
    "-gccinc",
    "-common off",
    "-inline auto",
]

#pokemon object
cflags_xd_app_pokemon = [
    *cflags_runtime,
    "-O4",
    "-inline noauto",
]
cflags_xd_app_pokemon.remove("-O4,p")
cflags_xd_app_pokemon.remove("-inline auto")

# REL flags
cflags_rel = [
    *cflags_base,
    "-sdata 0",
    "-sdata2 0",
]

cflags_trk = [
    *cflags_base,
    "-use_lmw_stmw on",
    "-rostr",
    "-str reuse",
    "-gccinc",
    "-common off",
    "-inline deferred,auto",
    "-char signed",
    "-sdata 0",
    "-sdata2 0",
]

cflags_dolphin = [
    *cflags_base,
    "-char unsigned",
    "-sym on",
    "-fp_contract off",
    "-warn pragmas",
    "-requireprotos",
    "-D__GEKKO__",
    "-DDOLPHIN_SDK",
    "-i libs/dolphin/include",
]

cflags_dolphin_exibios = cflags_dolphin[:]
cflags_dolphin_exibios.remove("-O4,p")  # need to remove this flag for EXIBios.c

cflags_musyx = [
    "-proc gekko",
    "-nodefaults",
    "-nosyspath",
    "-i include",
    "-i libs/musyx/include",
    "-i libs/dolphin/include",
    "-i libs/dolphin/include/libc",
    "-inline auto,depth=4",
    "-O4,p",
    "-fp hard",
    "-enum int",
    "-sym on",
    "-Cpp_exceptions off",
    "-str reuse,pool,readonly",
    "-fp_contract off",
    "-DMUSY_TARGET=MUSY_TARGET_DOLPHIN",
]

cflags_musyx_debug = [
    "-proc gecko",
    "-fp hard",
    "-nodefaults",
    "-nosyspath",
    "-i include",
    "-i libs/musyx/include",
    "-i libs/dolphin/include",
    "-i libs/dolphin/include/libc",
    "-g",
    "-sym on",
    "-D_DEBUG=1",
    "-fp hard",
    "-enum int",
    "-Cpp_exceptions off",
    "-DMUSY_TARGET=MUSY_TARGET_DOLPHIN",
]

config.linker_version = "GC/2.6"


# Helper function for Dolphin libraries
def DolphinLib(lib_name: str, cflags: Any, objects: List[Object], patch=2 if config.version == "NXXJ01" else 1) -> Dict[str, Any]:
    return {
        "lib": lib_name,
        "src_dir": "libs/dolphin/src",
        "strip_prefix": "dolphin/",
        "mw_version": "GC/1.2.5n",
        "cflags": [*cflags, f"-DSDK_REVISION={patch}"],
        "progress_category": "sdk",
        "objects": objects,
    }

def SysdolphinLib(objects: List[Object]):
    return {
        "lib": "sysdolphin",
        "src_dir": "src",
        "mw_version": "GC/1.3.2",
        "cflags": [*cflags_base, "-inline deferred", "-str readonly"],
        "progress_category": "GSAPI",
        "objects": objects,
    }


def MusyX(objects, mw_version="GC/1.3.2", debug=False, major=2, minor=0, patch=3 if version_num == 7 else 0):
    cflags = cflags_musyx if not debug else cflags_musyx_debug
    return {
        "lib": "musyx",
        "mw_version": mw_version,
        "src_dir": "libs/musyx/src",
        "host": False,
        "cflags": [
            *cflags,
            f"-DMUSY_VERSION_MAJOR={major}",
            f"-DMUSY_VERSION_MINOR={minor}",
            f"-DMUSY_VERSION_PATCH={patch}",
        ],
        "progress_category": "sdk",
        "objects": objects,
        "shift_jis": False,
    }


# Helper function for REL script objects
def Rel(lib_name: str, objects: List[Object]) -> Dict[str, Any]:
    return {
        "lib": lib_name,
        "mw_version": "GC/1.3.2",
        "cflags": cflags_rel,
        "progress_category": "game",
        "objects": objects,
    }


Matching = True                   # Object matches and should be linked
NonMatching = False               # Object does not match and should not be linked
Equivalent = config.non_matching  # Object should be linked when configured with --non-matching


# Object is only matching for specific versions
def MatchingFor(*versions):
    return config.version in versions


config.warn_missing_config = True
config.warn_missing_source = False
config.libs = [
    DolphinLib(
        "ai",
        [*cflags_dolphin, "-i libs/dolphin/src/gx"],
        [
            Object(Matching, "dolphin/ai/ai.c"),
        ],
    ),
    DolphinLib(
        "amcstubs",
        cflags_dolphin,
        [
            Object(Matching, "dolphin/amcstubs/AmcExi2Stubs.c"),
        ],
    ),
    DolphinLib(
        "ar",
        [*cflags_dolphin, "-i libs/dolphin/src/ar"],
        [
            Object(Matching, "dolphin/ar/ar.c"),
            Object(Matching, "dolphin/ar/arq.c"),
        ],
    ),
    DolphinLib(
        "base",
        cflags_dolphin,
        [
            Object(Matching, "dolphin/base/PPCArch.c"),
        ],
    ),
    DolphinLib(
        "card",
        [
            *cflags_dolphin,
            "-char signed",
            "-i libs/dolphin/src",
            "-i libs/dolphin/src/card",
            "-i libs/dolphin/src/os",
        ],
        [
            Object(Matching, "dolphin/card/CARDBios.c"),
            Object(Matching, "dolphin/card/CARDUnlock.c"),
            Object(Matching, "dolphin/card/CARDRdwr.c"),
            Object(Matching, "dolphin/card/CARDBlock.c"),
            Object(Matching, "dolphin/card/CARDDir.c"),
            Object(Matching, "dolphin/card/CARDCheck.c"),
            Object(Matching, "dolphin/card/CARDMount.c"),
            Object(Matching, "dolphin/card/CARDFormat.c"),
            Object(Matching, "dolphin/card/CARDOpen.c", extra_cflags=["-char signed"]),
            Object(Matching, "dolphin/card/CARDCreate.c"),
            Object(Matching, "dolphin/card/CARDRead.c"),
            Object(Matching, "dolphin/card/CARDWrite.c"),
            Object(Matching, "dolphin/card/CARDDelete.c"),
            Object(Matching, "dolphin/card/CARDStat.c"),
            Object(Matching, "dolphin/card/CARDStatEx.c"),
            Object(Matching, "dolphin/card/CARDNet.c"),
        ],
    ),
    DolphinLib(
        "db",
        cflags_dolphin,
        [
            Object(Matching, "dolphin/db/db.c"),
        ],
    ),
    DolphinLib(
        "dsp",
        [*cflags_dolphin, "-i libs/dolphin/src/dsp"],
        [
            Object(Matching, "dolphin/dsp/dsp.c"),
            Object(Matching, "dolphin/dsp/dsp_debug.c"),
            Object(Matching, "dolphin/dsp/dsp_task.c"),
        ],
    ),
    DolphinLib(
        "dvd",
        [
            *cflags_dolphin,
            "-char signed",
            "-i libs/dolphin/src",
            "-i libs/dolphin/src/dvd",
            "-i libs/dolphin/src/os",
        ],
        [
            Object(Matching, "dolphin/dvd/dvdlow.c"),
            Object(Matching, "dolphin/dvd/dvdfs.c"),
            Object(Matching, "dolphin/dvd/dvd.c"),
            Object(Matching, "dolphin/dvd/dvdqueue.c"),
            Object(Matching, "dolphin/dvd/dvderror.c"),
            Object(Matching, "dolphin/dvd/dvdidutils.c"),
            Object(Matching, "dolphin/dvd/dvdFatal.c"),
            Object(Matching, "dolphin/dvd/fstload.c"),
        ],
    ),
    {
        "lib": "Dolphin EXIBios",
        "src_dir": "libs/dolphin/src",
        "strip_prefix": "dolphin/",
        "mw_version": "GC/1.2.5n",
        "cflags": [*cflags_dolphin_exibios, "-i libs/dolphin/src/os"],
        "progress_category": "sdk",
        "objects": [
            Object(Matching, "dolphin/exi/EXIBios.c", extra_cflags=["-O3,p"]),
        ],
    },
    DolphinLib(
        "exi",
        [*cflags_dolphin, "-i libs/dolphin/src/os"],
        [
            Object(Matching, "dolphin/exi/EXIUart.c"),
        ],
    ),
    DolphinLib(
        "gba",
        [
            *cflags_dolphin,
            "-i libs/dolphin/src/gba",
            "-i libs/dolphin/src/os",
            "-i libs/dolphin/src/dsp"
        ],
        [
            Object(Matching, "dolphin/gba/GBA.c"),
            Object(Matching, "dolphin/gba/GBAGetProcessStatus.c"),
            Object(Matching, "dolphin/gba/GBAJoyBoot.c"),
            Object(Matching, "dolphin/gba/GBARead.c"),
            Object(Matching, "dolphin/gba/GBAWrite.c"),
            Object(Matching, "dolphin/gba/GBAXfer.c"),
            Object(Matching, "dolphin/gba/GBAKey.c"),
        ],
    ),
    DolphinLib(
        "gx",
        [*cflags_dolphin, "-i libs/dolphin/src/gx"],
        [
            Object(Matching, "dolphin/gx/GXInit.c"),
            Object(Matching, "dolphin/gx/GXFifo.c"),
            Object(Matching, "dolphin/gx/GXAttr.c"),
            Object(Matching, "dolphin/gx/GXMisc.c"),
            Object(Matching, "dolphin/gx/GXGeometry.c"),
            Object(Matching, "dolphin/gx/GXFrameBuf.c"),
            Object(Matching, "dolphin/gx/GXLight.c"),
            Object(Matching, "dolphin/gx/GXTexture.c"),
            Object(Matching, "dolphin/gx/GXBump.c"),
            Object(Matching, "dolphin/gx/GXTev.c"),
            Object(Matching, "dolphin/gx/GXPixel.c"),
            Object(Matching, "dolphin/gx/GXDraw.c"),
            Object(Matching, "dolphin/gx/GXDisplayList.c"),
            Object(Matching, "dolphin/gx/GXTransform.c"),
            Object(Matching, "dolphin/gx/GXPerf.c"),
        ], patch=2
    ),
    DolphinLib(
        "mtx",
        cflags_dolphin,
        [
            Object(Matching, "dolphin/mtx/mtx.c", extra_cflags=["-char signed"]),
            Object(Matching, "dolphin/mtx/mtxvec.c"),
            Object(Matching, "dolphin/mtx/mtx44.c", extra_cflags=["-char signed"]),
            Object(Matching, "dolphin/mtx/vec.c"),
            Object(Matching, "dolphin/mtx/quat.c"),
        ],
    ),
    DolphinLib(
        "OdemuExi2",
        cflags_dolphin,
        [
            Object(Matching, "dolphin/OdemuExi2/DebuggerDriver.c", extra_cflags=["-inline auto,deferred"]),
        ],
    ),
    DolphinLib(
        "odenotstub",
        cflags_dolphin,
        [
            Object(Matching, "dolphin/odenotstub/odenotstub.c"),
        ],
    ),
    DolphinLib(
        "os",
        [
            *cflags_dolphin,
            "-D__GEKKO__",
            "-i libs/dolphin/src/dvd",
            "-i libs/dolphin/src/os",
        ],
        [
            Object(Matching, "dolphin/os/OS.c"),
            Object(Matching, "dolphin/os/OSAlarm.c"),
            Object(Matching, "dolphin/os/OSArena.c"),
            Object(Matching, "dolphin/os/OSAudioSystem.c"),
            Object(Matching, "dolphin/os/OSCache.c"),
            Object(Matching, "dolphin/os/OSContext.c"),
            Object(Matching, "dolphin/os/OSError.c"),
            Object(Matching, "dolphin/os/OSExec.c"),
            Object(Matching, "dolphin/os/OSFatal.c"),
            Object(Matching, "dolphin/os/OSFont.c"),
            Object(Matching, "dolphin/os/OSInterrupt.c"),
            Object(Equivalent, "dolphin/os/OSLink.c"),
            Object(Matching, "dolphin/os/OSMemory.c"),
            Object(Matching, "dolphin/os/OSMutex.c"),
            Object(Matching, "dolphin/os/OSReboot.c"),
            Object(Matching, "dolphin/os/OSReset.c"),
            Object(Matching, "dolphin/os/OSResetSW.c"),
            Object(Matching, "dolphin/os/OSRtc.c"),
            Object(Matching, "dolphin/os/OSSync.c"),
            Object(Matching, "dolphin/os/OSThread.c"),
            Object(Matching, "dolphin/os/OSTime.c"),
            Object(Matching, "dolphin/os/__start.c"),
            Object(Matching, "dolphin/os/__ppc_eabi_init.c"),
        ],
    ),
    DolphinLib(
        "pad",
        [
            *cflags_dolphin,
            "-i libs/dolphin/src/si",
        ],
        [
            Object(Matching, "dolphin/pad/Pad.c"),
        ],
    ),
    DolphinLib(
        "perf",
        [
            *cflags_dolphin,
            "-i libs/dolphin/src/gx",
            "-i libs/dolphin/src/perf"
        ],
        [
            Object(Matching, "dolphin/perf/perf.c"),
            Object(Equivalent, "dolphin/perf/perfdraw.c"),
        ],
    ),
    DolphinLib(
        "si",
        [*cflags_dolphin, "-i libs/dolphin/src/os"],
        [
            Object(Matching, "dolphin/si/SIBios.c"),
            Object(Matching, "dolphin/si/SISamplingRate.c"),
        ],
    ),
    DolphinLib(
        "vi",
        [
            *cflags_dolphin,
            "-i libs/dolphin/src/gx",
            "-i libs/dolphin/src/os",
            "-i libs/dolphin/src/vi",
        ],
        [
            Object(Matching, "dolphin/vi/vi.c"),
        ],
    ),
    {
        "lib": "TRK_MINNOW_DOLPHIN",
        "mw_version": config.linker_version,
        "cflags": cflags_trk,
        "progress_category": "sdk",
        "host": False,
        "objects": [
            # debugger
            Object(NonMatching, "runtime_libs/debugger/embedded/MetroTRK/Portable/mainloop.c"),
            Object(NonMatching, "runtime_libs/debugger/embedded/MetroTRK/Portable/nubevent.c"),
            Object(NonMatching, "runtime_libs/debugger/embedded/MetroTRK/Portable/nubinit.c"),
            Object(NonMatching, "runtime_libs/debugger/embedded/MetroTRK/Portable/msg.c"),
            Object(NonMatching, "runtime_libs/debugger/embedded/MetroTRK/Portable/msgbuf.c"),
            Object(NonMatching, "runtime_libs/debugger/embedded/MetroTRK/Portable/serpoll.c", extra_cflags=["-sdata 8"]),
            Object(NonMatching, "runtime_libs/debugger/embedded/MetroTRK/Os/dolphin/usr_put.c"),
            Object(NonMatching, "runtime_libs/debugger/embedded/MetroTRK/Portable/dispatch.c"),
            Object(NonMatching, "runtime_libs/debugger/embedded/MetroTRK/Portable/msghndlr.c"),
            Object(NonMatching, "runtime_libs/debugger/embedded/MetroTRK/Portable/support.c"),
            Object(NonMatching, "runtime_libs/debugger/embedded/MetroTRK/Portable/mutex_TRK.c"),
            Object(NonMatching, "runtime_libs/debugger/embedded/MetroTRK/Portable/notify.c"),
            Object(NonMatching, "runtime_libs/debugger/embedded/MetroTRK/Processor/ppc/Generic/flush_cache.c"),
            Object(NonMatching, "runtime_libs/debugger/embedded/MetroTRK/Portable/mem_TRK.c"),
            Object(NonMatching, "runtime_libs/debugger/embedded/MetroTRK/Processor/ppc/Generic/targimpl.c"),
            Object(NonMatching, "runtime_libs/debugger/embedded/MetroTRK/Processor/ppc/Export/targsupp.s"),
            Object(NonMatching, "runtime_libs/debugger/embedded/MetroTRK/Processor/ppc/Generic/mpc_7xx_603e.c"),
            Object(NonMatching, "runtime_libs/debugger/embedded/MetroTRK/Processor/ppc/Generic/__exception.s"),
            Object(NonMatching, "runtime_libs/debugger/embedded/MetroTRK/Os/dolphin/dolphin_trk.c"),
            Object(NonMatching, "runtime_libs/debugger/embedded/MetroTRK/Portable/main_TRK.c"),
            Object(NonMatching, "runtime_libs/debugger/embedded/MetroTRK/Os/dolphin/dolphin_trk_glue.c"),
            Object(NonMatching, "runtime_libs/debugger/embedded/MetroTRK/Os/dolphin/targcont.c"),
            Object(NonMatching, "runtime_libs/debugger/embedded/MetroTRK/Os/dolphin/target_options.c"),
            Object(NonMatching, "runtime_libs/debugger/embedded/MetroTRK/Export/mslsupp.c"),
            Object(NonMatching, "runtime_libs/debugger/embedded/MetroTRK/Os/dolphin/UDP_Stubs.c"),

            # gamedev
            Object(NonMatching, "runtime_libs/gamedev/cust_connection/cc/exi2/GCN/EXI2_DDH_GCN/main_ddh.c", extra_cflags=["-sdata 8"]),
            Object(NonMatching, "runtime_libs/gamedev/cust_connection/utils/common/CircleBuffer.c"),
            Object(NonMatching, "runtime_libs/gamedev/cust_connection/cc/exi2/GCN/EXI2_GDEV_GCN/main_gdev.c", extra_cflags=["-sdata 8"]),
            Object(NonMatching, "runtime_libs/gamedev/cust_connection/utils/common/MWTrace.c"),
            Object(NonMatching, "runtime_libs/gamedev/cust_connection/utils/gc/MWCriticalSection_gc.c"),
        ],
    },
    {
        "lib": "Runtime.PPCEABI.H",
        "src_dir": "libs",
        "mw_version": config.linker_version,
        "cflags": [*cflags_runtime, "-inline deferred"],
        "progress_category": "sdk",
        "host": False,
        "objects": [
            Object(Matching, "PowerPC_EABI_Support/Runtime/Src/__mem.c"),
            Object(Matching, "PowerPC_EABI_Support/Runtime/Src/__va_arg.c"),
            Object(Matching, "PowerPC_EABI_Support/Runtime/Src/global_destructor_chain.c"),
            Object(Matching, "PowerPC_EABI_Support/Runtime/Src/CPlusLibPPC.cp"),
            Object(Matching, "PowerPC_EABI_Support/Runtime/Src/NMWException.cp", extra_cflags=["-Cpp_exceptions on"]),
            Object(Matching, "PowerPC_EABI_Support/Runtime/Src/runtime.c"),
            Object(Matching, "PowerPC_EABI_Support/Runtime/Src/__init_cpp_exceptions.cpp"),
            Object(Matching, "PowerPC_EABI_Support/Runtime/Src/Gecko_ExceptionPPC.cp"),
            Object(Matching, "PowerPC_EABI_Support/Runtime/Src/GCN_mem_alloc.c", extra_cflags=["-str reuse,nopool,readonly"]),
        ],
    },
    {
        "lib": "MSL_C",
        "src_dir": "libs",
        "mw_version": config.linker_version,
        "cflags": [*cflags_runtime, "-inline deferred"],
        "progress_category": "sdk",
        "host": False,
        "objects": [
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/abort_exit.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/alloc.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/errno.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/ansi_files.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Src/ansi_fp.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/arith.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/buffer_io.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/PPC_EABI/Src/critical_regions.gamecube.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/ctype.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/locale.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/direct_io.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/file_io.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/FILE_POS.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/mbstring.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/mem.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/mem_funcs.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/misc_io.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/printf.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/float.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/qsort.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/scanf.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/string.c"),
            Object(Equivalent, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/strtold.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/strtoul.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/wchar_io.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/PPC_EABI/Src/uart_console_io_gcn.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/e_acos.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/e_asin.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/e_atan2.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/e_exp.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/e_fmod.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/e_log.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/e_pow.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/e_rem_pio2.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/k_cos.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/k_rem_pio2.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/k_sin.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/k_tan.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/s_atan.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/s_ceil.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/s_copysign.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/s_cos.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/s_floor.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/s_frexp.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/s_ldexp.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/s_modf.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/s_sin.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/s_tan.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/w_acos.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/w_asin.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/w_atan2.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/w_exp.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/w_fmod.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/w_log.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/w_pow.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/e_sqrt.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/PPC_EABI/Src/math_ppc.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/w_sqrt.c"),
            Object(Matching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/extras.c"),
        ],
    },
    MusyX(
        # debug=True,
        # mw_version="GC/1.2.5n",
        major=2,
        minor=0,
        patch=3,
        objects=[
            Object(Matching, "musyx/runtime/seq.c"),
            Object(Matching, "musyx/runtime/synth.c"),
            Object(Matching, "musyx/runtime/seq_api.c"),
            Object(Matching, "musyx/runtime/snd_synthapi.c"),
            Object(Matching, "musyx/runtime/stream.c"),
            Object(NonMatching, "musyx/runtime/synthdata.c"),
            Object(Matching, "musyx/runtime/synthmacros.c"),
            Object(Matching, "musyx/runtime/synthvoice.c"),
            Object(Matching, "musyx/runtime/synth_ac.c"),
            Object(Matching, "musyx/runtime/synth_dbtab.c"),
            Object(Matching, "musyx/runtime/synth_adsr.c"),
            Object(Matching, "musyx/runtime/synth_vsamples.c"),
            Object(Matching, "musyx/runtime/s_data.c"),
            Object(Matching, "musyx/runtime/hw_dspctrl.c"),
            Object(Matching, "musyx/runtime/hw_volconv.c"),
            Object(Matching, "musyx/runtime/snd3d.c"),
            Object(Matching, "musyx/runtime/snd_init.c"),
            Object(Matching, "musyx/runtime/snd_math.c"),
            Object(Matching, "musyx/runtime/snd_midictrl.c"),
            Object(NonMatching, "musyx/runtime/snd_service.c"),
            Object(Matching, "musyx/runtime/hardware.c"),
            Object(Matching, "musyx/runtime/dsp_import.c"),
            Object(Matching, "musyx/runtime/hw_aramdma.c"),
            Object(Matching, "musyx/runtime/hw_dolphin.c"),
            Object(Matching, "musyx/runtime/hw_memory.c"),
            Object(Matching, "musyx/runtime/StdReverb/reverb_fx.c"),
            Object(Matching, "musyx/runtime/StdReverb/reverb.c"),
        ]
    ),
    {
        "lib": "dbgMenu",
        "mw_version": config.linker_version,
        "cflags": cflags_runtime,
        "progress_category": "game",
        "objects": [
            Object(NonMatching, "dbgMenuCamera.cpp"),
            Object(NonMatching, "dbgMenuFight.cpp"),
            Object(NonMatching, "dbgMenuFlag.cpp"),
            Object(NonMatching, "dbgMenuPokemon.cpp"),
            Object(NonMatching, "dbgMenuHero.cpp"),
            Object(NonMatching, "dbgMenuFloor.cpp"),
            Object(NonMatching, "dbgMenuGSgfx.cpp"),
            Object(NonMatching, "dbgMenuGSvtr.cpp"),
            Object(NonMatching, "dbgMenuMemcard.cpp"),
            Object(NonMatching, "dbgMenuMsg.cpp"),
            Object(NonMatching, "dbgMenuPeople.cpp"),
            Object(NonMatching, "dbgMenuSoundTest.cpp"),
            Object(NonMatching, "dbgMenuWazaViewer.cpp"),
            Object(NonMatching, "dbgMenuWaza.cpp"),
            Object(NonMatching, "dbgMenuFightTrainer.cpp"),
            Object(NonMatching, "dbgMenuFightWaza.cpp"),
            Object(NonMatching, "dbgMenuLog.cpp"),
            Object(NonMatching, "dbgMenuFieldCamera.cpp"),
            Object(NonMatching, "dbgMenuItemCreate.cpp"),
            Object(NonMatching, "dbgMenuRelive.cpp"),
            Object(NonMatching, "dbgMenuToolBattle.cpp"),
            Object(NonMatching, "dbgMenuSub.cpp"),
            Object(NonMatching, "dbgMenuMenu.cpp"),
        ]
    },
    {
        "lib": "menu",
        "mw_version": config.linker_version,
        "cflags": cflags_runtime,
        "progress_category": "game",
        "objects": [
            Object(NonMatching, "menuData.c"),
            Object(NonMatching, "menuTool.cpp"),
            Object(NonMatching, "menuColosseumBattleConnection.cpp"),
            Object(NonMatching, "menuSeq.c"),
            Object(NonMatching, "menuSprite.c"),
            Object(NonMatching, "menuPokeCoupon.cpp"),
            Object(NonMatching, "menuKeyDisc.cpp"),
            Object(NonMatching, "menuPocketBattleDisk.cpp"),
            Object(NonMatching, "menuWorldMapMX.cpp"),
            Object(NonMatching, "menuItemMX.cpp"),
            Object(NonMatching, "menuPokemon.cpp"),
            Object(NonMatching, "menuFightStatus.cpp"),
            Object(NonMatching, "menuFight.cpp"),
            Object(NonMatching, "menuPocketTool.cpp"),
            Object(NonMatching, "menuPocket.cpp"),
            Object(NonMatching, "menuTop.cpp"),
            Object(NonMatching, "menuNameEntry.cpp"),
            Object(NonMatching, "menuPokemonStatus.cpp"),
            Object(NonMatching, "menuItemTool.cpp"),
            Object(NonMatching, "menuSaveLoad.cpp"),
            Object(NonMatching, "menuPda.cpp"),
            Object(NonMatching, "menuReliveHall.cpp"),
            Object(NonMatching, "menuPdaSearcher.cpp"),
            Object(NonMatching, "menuPdaMailXD.cpp"),
            Object(NonMatching, "menuPdaMailList.XD.cpp"),
            Object(NonMatching, "menuColosseumBattle.cpp"),
            Object(NonMatching, "menuCB_BattleResult.cpp"),
            Object(NonMatching, "menuCB_BattleStart.cpp"),
            Object(NonMatching, "menuCB_Bios.cpp"),
            Object(NonMatching, "menuCB_Common.cpp"),
            Object(NonMatching, "menuCB_Debug.cpp"),
            Object(NonMatching, "menuCB_ItemList.cpp"),
            Object(NonMatching, "menuCB_PokemonEntry.cpp"),
            Object(NonMatching, "menuCB_Rule.cpp"),
            Object(NonMatching, "menuCB_Battle.cpp"),
            Object(NonMatching, "menuToolBattle.cpp"),
            Object(NonMatching, "menuGBAC.cpp"),
            Object(NonMatching, "menuPdaDPMonitor.cpp"),
            Object(NonMatching, "menuPdaDPMonitorList.cpp"),
            Object(NonMatching, "menuPdaSub.cpp"),
            Object(NonMatching, "menuPdaMemoXD.cpp"),
            Object(NonMatching, "menuPdaMemoListXD.cpp"),
            Object(NonMatching, "menuPcBoxPokemon.cpp"),
            Object(NonMatching, "menuField.cpp"),
            Object(NonMatching, "menuScript.cpp"),
            Object(NonMatching, "menuReliveMeter.cpp"),
            Object(NonMatching, "menuShop.cpp"),
            Object(NonMatching, "menuPocketCologne.cpp"),
            Object(NonMatching, "menuItemPda.cpp"),
            Object(NonMatching, "menuSub.cpp"),
            Object(NonMatching, "menuPdaMemoWaveXD.cpp"),
            Object(NonMatching, "menuInterrupt.cpp"),
            Object(NonMatching, "menuPcBoxNew.cpp"),
            Object(NonMatching, "menuPcBoxDouguNew.cpp"),
            Object(NonMatching, "menuCB_externDB.cpp"),
            Object(NonMatching, "menuDataBios.cpp"),
            Object(NonMatching, "menuPanel.cpp"),
            Object(NonMatching, "menuCB_Sub1.cpp"),
            Object(NonMatching, "menuLogoDemo.cpp"),
            Object(NonMatching, "menuHologram.cpp"),
            Object(NonMatching, "menuBingo.cpp"),
            Object(NonMatching, "menuItemBT.c"),
            Object(NonMatching, "menuReliveHallTutorial.cpp"),
            Object(NonMatching, "menuPokemonChange.cpp"),
            Object(NonMatching, "menuWorldMapMoveDemo.cpp"),
            Object(NonMatching, "menuWorldMapModel.cpp"),
            Object(NonMatching, "menuItem.c"),
            Object(NonMatching, "menuBattleDisk.cpp"),
            Object(NonMatching, "menuItemXD.c"),
            Object(NonMatching, "menuOrreColosseum.cpp"),
            Object(NonMatching, "menuTitle.cpp"),
            Object(NonMatching, "menuUseItem.cpp"),
            Object(NonMatching, "menuItemDebugRelease.c"),
            Object(NonMatching, "menuMewWaza.cpp"),
            Object(NonMatching, "menuMoveDemo.cpp"),
            Object(NonMatching, "menuTitleOption.cpp"),
        ],
    },
    {
        "lib": "game_unsorted",
        "mw_version": config.linker_version,
        "cflags": cflags_runtime,
        "progress_category": "game",
        "objects": [
            Object(NonMatching, "character.cpp"),
            Object(NonMatching, "relglobal.c"),
            Object(NonMatching, "pause.cpp"),
            Object(NonMatching, "time.cpp"),
            Object(NonMatching, "main.cpp"),
            Object(NonMatching, "sysvars.cpp"),
            Object(NonMatching, "flashmenuTest.cpp"),
            Object(NonMatching, "gbaPokemon.cpp"),
            Object(NonMatching, "gbaCommand.cpp"),
            Object(NonMatching, "agbCommunication.cpp"),
            Object(NonMatching, "floorRead.cpp"),
            Object(NonMatching, "pokecolo.cpp"),
            Object(NonMatching, "pokeconv.cpp"),
            Object(NonMatching, "wazaconv.cpp"),
            Object(NonMatching, "floorLayerConfig.cpp"),
        ]
    },
    {
        "lib": "xd_GSAPI",
        "mw_version": config.linker_version,
        "cflags": cflags_runtime,
        "progress_category": "GSAPI",
        "objects": [
            # GSmemman
            Object(NonMatching, "GSAPI/GSmemman/GSmemman.cpp"),
            Object(NonMatching, "GSAPI/GSmemman/memOverride.cpp"),
            Object(NonMatching, "GSAPI/GSmemman/OSAlloc.cpp"),
            Object(NonMatching, "GSAPI/GSmemman/sysdolmem.cpp"),
            Object(NonMatching, "GSAPI/GSmemman/poolAlloc.cpp"),

            Object(NonMatching, "GSAPI/GScamera/GScamera.cpp"),
            Object(NonMatching, "GSAPI/GSlight/GSlight.cpp"),
            Object(NonMatching, "GSAPI/GSmaterial/GSmaterial.cpp"),

            # GSmath
            Object(NonMatching, "GSAPI/GSmath/GSmtx.cpp"),
            Object(NonMatching, "GSAPI/GSmath/GSmtx44.cpp"),
            Object(NonMatching, "GSAPI/GSmath/GSquat.cpp"),
            Object(NonMatching, "GSAPI/GSmath/init.cpp"),
            Object(NonMatching, "GSAPI/GSmath/GSbezier.cpp"),
            Object(NonMatching, "GSAPI/GSmath/GSlerp.cpp"),
            Object(NonMatching, "GSAPI/GSmath/GSutil.cpp"),
            Object(NonMatching, "GSAPI/GSmath/GSvec.cpp"),

            # GSmodel
            Object(NonMatching, "GSAPI/GSmodel/effects.cpp"),
            Object(NonMatching, "GSAPI/GSmodel/blend.cpp"),
            Object(NonMatching, "GSAPI/GSmodel/bound.cpp"),
            Object(NonMatching, "GSAPI/GSmodel/animation.cpp"),
            Object(NonMatching, "GSAPI/GSmodel/GSmodel.cpp"),
            Object(NonMatching, "GSAPI/GSmodel/GSmodelExt.cpp"),
            Object(NonMatching, "GSAPI/GSmodel/parse.cpp"),
            Object(NonMatching, "GSAPI/GSmodel/part.cpp"),
            Object(NonMatching, "GSAPI/GSmodel/save_state.cpp"),
            Object(NonMatching, "GSAPI/GSmodel/shadow.cpp"),
            Object(NonMatching, "GSAPI/GSmodel/bank.cpp"),

            Object(NonMatching, "GSAPI/GSpart/GSpart.cpp"),
            Object(NonMatching, "GSAPI/GSscratch/GSscratch.cpp"),
            Object(NonMatching, "GSAPI/GStexture/GStexture.cpp"),
            Object(NonMatching, "GSAPI/GSthread/GSthread.cpp"),
            Object(NonMatching, "GSAPI/GSinput/GSinput.cpp"),
            Object(NonMatching, "GSAPI/GSres/GSres.cpp"),

            # GSmsg
            Object(NonMatching, "GSAPI/GSmsg/GSmsg.cpp"),
            Object(NonMatching, "GSAPI/GSmsg/sprite.cpp"),

            Object(NonMatching, "GSAPI/GSgapp/GSgapp.cpp"),

            # GScolsys
            Object(NonMatching, "GSAPI/GScolsys/GScolsys2.cpp"),
            Object(NonMatching, "GSAPI/GScolsys/GScolsys2Draw.cpp"),
            Object(NonMatching, "GSAPI/GScolsys/GScolsys2Walk.cpp"),
            Object(NonMatching, "GSAPI/GScolsys/GScolsys2Hit.cpp"),
            Object(NonMatching, "GSAPI/GScolsys/GScolsys2Util.cpp"),
            Object(NonMatching, "GSAPI/GScolsys/GScolsys2Human.cpp"),
            Object(NonMatching, "GSAPI/GScolsys/GScolsys2Thru.cpp"),
            Object(NonMatching, "GSAPI/GScolsys/GScolsys2Check.cpp"),
            Object(NonMatching, "GSAPI/GScolsys/GScolsys2Sun.cpp"),

            # GSparticle
            Object(NonMatching, "GSAPI/GSparticle/GSparticle.cpp"),
            Object(NonMatching, "GSAPI/GSparticle/peParticle.cpp"),
            Object(NonMatching, "GSAPI/GSparticle/peNode.cpp"),
            Object(NonMatching, "GSAPI/GSparticle/peBank.cpp"),
            Object(NonMatching, "GSAPI/GSparticle/peEmitter.cpp"),
            Object(NonMatching, "GSAPI/GSparticle/peModel.cpp"),
            Object(NonMatching, "GSAPI/GSparticle/peContainer.cpp"),
            Object(NonMatching, "GSAPI/GSparticle/peDistortion.cpp"),
            Object(NonMatching, "GSAPI/GSparticle/peParticleStrip.cpp"),
            Object(NonMatching, "GSAPI/GSparticle/peSpline.cpp"),
            Object(NonMatching, "GSAPI/GSparticle/particleEngine.cpp"),
            Object(NonMatching, "GSAPI/GSparticle/peShape.cpp"),

            Object(NonMatching, "GSAPI/GSeffect/GSeffect.cpp"),

            # GSsnd
            Object(NonMatching, "GSAPI/GSsnd/GSsnd.cpp"),
            Object(NonMatching, "GSAPI/GSsnd/sndStream.cpp"),

            Object(NonMatching, "GSAPI/GSdvd/GSdvd.cpp"),
            Object(NonMatching, "GSAPI/GSfilter/GSfilter.cpp"),
            Object(NonMatching, "GSAPI/GSspline/GSspline.cpp"),

            # GSfsys
            Object(NonMatching, "GSAPI/GSfsys/fsysStream.cpp"),
            Object(NonMatching, "GSAPI/GSfsys/fsysBlock.cpp"),
            Object(NonMatching, "GSAPI/GSfsys/fsysCache.cpp"),
            Object(NonMatching, "GSAPI/GSfsys/fsysRead.cpp"),
            Object(NonMatching, "GSAPI/GSfsys/fsysAlloc.cpp"),
            Object(NonMatching, "GSAPI/GSfsys/GSfsys2.cpp"),

            Object(NonMatching, "GSAPI/GSflag/GSflag.cpp"),
            Object(NonMatching, "GSAPI/GSbound/GSbound.cpp"),
            Object(NonMatching, "GSAPI/GSvtr/GSvtr.cpp"),

            # GSmovie
            Object(NonMatching, "GSAPI/GSmovie/movieStream.cpp"),
            Object(NonMatching, "GSAPI/GSmovie/GSmovie.cpp"),
            Object(NonMatching, "GSAPI/GSmovie/THPDraw.cpp"),
            Object(NonMatching, "GSAPI/GSmovie/THPDec.cpp"),
            Object(NonMatching, "GSAPI/GSmovie/THPAudio.cpp"),

            Object(NonMatching, "GSAPI/GSlensFlare/GSlensFlare.cpp"),

            # GSScript
            Object(NonMatching, "GSAPI/GSScript/tiga.cpp"),
            Object(NonMatching, "GSAPI/GSScript/tvariant.cpp"),
            Object(NonMatching, "GSAPI/GSScript/chank.cpp"),
            Object(NonMatching, "GSAPI/GSScript/defobj.cpp"),

            Object(NonMatching, "GSAPI/GSnetwork/GSnetwork.cpp"),

            # GSprim
            Object(NonMatching, "GSAPI/GSprim/GSprim.cpp"),
            Object(NonMatching, "GSAPI/GSprim/2d.cpp"),
            Object(NonMatching, "GSAPI/GSprim/text.cpp"),

            # GSshape
            Object(NonMatching, "GSAPI/GSshape/shapeAnim.cpp"),
            Object(NonMatching, "GSAPI/GSshape/shapeObject.cpp"),
            Object(NonMatching, "GSAPI/GSshape/shapeRender.cpp"),
            Object(NonMatching, "GSAPI/GSshape/GSshape.cpp"),

            Object(NonMatching, "GSAPI/GSstream/GSstream.cpp"),
            Object(NonMatching, "GSAPI/GSlogM/GSlog.cpp"),

            # GSgfxM
            Object(NonMatching, "GSAPI/GSgfxM/backfb.cpp"),
            Object(NonMatching, "GSAPI/GSgfxM/GSgfx.cpp"),
            Object(NonMatching, "GSAPI/GSgfxM/layer.cpp"),
            Object(NonMatching, "GSAPI/GSgfxM/render.cpp"),
            Object(NonMatching, "GSAPI/GSgfxM/perfbar.cpp"),
            Object(NonMatching, "GSAPI/GSgfxM/token.cpp"),
            Object(NonMatching, "GSAPI/GSgfxM/project.cpp"),
            Object(NonMatching, "GSAPI/GSgfxM/halt.cpp"),
            Object(NonMatching, "GSAPI/GSgfxM/video.cpp"),
            Object(NonMatching, "GSAPI/GSgfxM/gpu.cpp"),
            Object(NonMatching, "GSAPI/GSgfxM/vf.cpp"),
            Object(NonMatching, "GSAPI/GSgfxM/dl.cpp"),
            Object(NonMatching, "GSAPI/GSgfxM/layerState.cpp"),
            Object(NonMatching, "GSAPI/GSgfxM/matrixStack.cpp"),
            Object(NonMatching, "GSAPI/GSgfxM/layerFunc.cpp"),
            Object(NonMatching, "GSAPI/GSgfxM/renderModule.cpp"),
            Object(NonMatching, "GSAPI/GSgfxM/c_func.cpp"),
            Object(NonMatching, "GSAPI/GSgfxM/layerConfig.cpp"),
            Object(NonMatching, "GSAPI/GSgfxM/light_gfxm.cpp"),
            Object(NonMatching, "GSAPI/GSgfxM/layerEffect.cpp"),
            Object(NonMatching, "GSAPI/GSgfxM/gamecube.cpp"),
            Object(NonMatching, "GSAPI/GSgfxM/screenshot.cpp"),
            Object(NonMatching, "GSAPI/GSgfxM/capture.cpp"),
            Object(NonMatching, "GSAPI/GSgfxM/reset.cpp"),
        ]
    },
    {
        "lib": "xd_app",
        "mw_version": config.linker_version,
        "cflags": cflags_runtime,
        "progress_category": "game",
        "objects": [
            # kaisuu
            Object(Matching, "app/kaisuu/kaisuuData.c"),
            Object(Matching, "app/kaisuu/kaisuu.cpp"),
            Object(Matching, "app/kaisuu/kaisuuBios.cpp"),

            # menu
            Object(NonMatching, "app/menu/winSprite.cpp"),
            Object(NonMatching, "app/menu/menu.cpp"),
            Object(NonMatching, "app/menu/menuFace.cpp"),
            Object(NonMatching, "app/menu/menuFaceBios.cpp"),
            Object(NonMatching, "app/menu/menuModel.cpp"),
            Object(NonMatching, "app/menu/menuOffScreen.cpp"),
            Object(NonMatching, "app/menu/window.cpp"),
            Object(NonMatching, "app/menu/cursorBios.cpp"),
            Object(NonMatching, "app/menu/winMsg.cpp"),

            # zokusei
            Object(NonMatching, "app/zokusei/zokusei.cpp"),
            Object(NonMatching, "app/zokusei/zokuseiBios.cpp"),

            # floor
            Object(NonMatching, "app/floor/floor.cpp"),
            Object(NonMatching, "app/floor/floorEvent.cpp"),
            Object(NonMatching, "app/floor/floorCharacterBios.cpp"),
            Object(NonMatching, "app/floor/floorDataBios.cpp"),
            Object(NonMatching, "app/floor/floorFieldCamera.cpp"),
            Object(NonMatching, "app/floor/floorFieldCameraEditor.cpp"),
            Object(NonMatching, "app/floor/floorOffscreen.cpp"),
            Object(NonMatching, "app/floor/floorManager.cpp"),
            Object(NonMatching, "app/floor/floorModule.cpp"),
            Object(NonMatching, "app/floor/floorStack.cpp"),
            Object(NonMatching, "app/floor/floorLoad.cpp"),
            Object(NonMatching, "app/floor/floorScript.cpp"),
            Object(NonMatching, "app/floor/floorsound.cpp"),

            # joutai
            Object(NonMatching, "app/joutai/joutaiData.c"),
            Object(NonMatching, "app/joutai/joutai.cpp"),
            Object(NonMatching, "app/joutai/joutaiBios.cpp"),

            # waza
            Object(NonMatching, "app/waza/waza.cpp"),
            Object(NonMatching, "app/waza/wazaFuncData.c"),
            Object(NonMatching, "app/waza/wazaBios.cpp"),
            Object(NonMatching, "app/waza/wazaDB.cpp"),

            # hero
            Object(NonMatching, "app/hero/hero.cpp"),
            Object(NonMatching, "app/hero/heroBios.cpp"),
            Object(NonMatching, "app/hero/heroMove.cpp"),
            Object(NonMatching, "app/hero/heroPokemonGet.cpp"),
            Object(NonMatching, "app/hero/heroMemberFunctions.cpp"),

            # sex
            Object(NonMatching, "app/sex/sexdata.c"),
            Object(NonMatching, "app/sex/sex.cpp"),

            # msgctrl
            Object(NonMatching, "app/msgctrl/msgctrlcode.c"),
            Object(NonMatching, "app/msgctrl/msgctrl.cpp"),

            Object(NonMatching, "app/dbgMenu/dbgMenu.cpp"),
            Object(NonMatching, "app/pcbox/pcbox.cpp"),

            # gamedata
            Object(NonMatching, "app/gamedata/gamedatasaveBios.cpp"),
            Object(NonMatching, "app/gamedata/gamedataBios.cpp"),
            Object(NonMatching, "app/gamedata/gamedata.cpp"),

            Object(NonMatching, "app/status/status.cpp"),

            # kouka
            Object(NonMatching, "app/kouka/koukaData.c"),
            Object(NonMatching, "app/kouka/koukaLinkData.c"),
            Object(NonMatching, "app/kouka/kouka.cpp"),
            Object(NonMatching, "app/kouka/koukaBios.cpp"),

            # tenkou
            Object(NonMatching, "app/tenkou/tenkouData.c"),
            Object(NonMatching, "app/tenkou/tenkouBios.cpp"),

            # tikei
            Object(NonMatching, "app/tikei/tikeiData.c"),
            Object(NonMatching, "app/tikei/tikeiBios.cpp"),

            # effects
            Object(NonMatching, "app/effects/filter.cpp"),
            Object(NonMatching, "app/effects/envMap.cpp"),
            Object(NonMatching, "app/effects/blur.cpp"),
            Object(NonMatching, "app/effects/glow.cpp"),

            # item
            Object(NonMatching, "app/item/itemBallData.c"),
            Object(NonMatching, "app/item/itemSoubiData.c"),
            Object(NonMatching, "app/item/tasteData.c"),
            Object(NonMatching, "app/item/itemWazaMachineNo.c"),
            Object(NonMatching, "app/item/itemParam.c"),
            Object(NonMatching, "app/item/item.cpp"),
            Object(NonMatching, "app/item/itemBios.cpp"),
            Object(NonMatching, "app/item/itemDB.cpp"),
            Object(NonMatching, "app/item/itemUse2Pokemon.cpp"),
            Object(NonMatching, "app/item/itemFightItem.cpp"),

            Object(NonMatching, "app/sound/sound.cpp"),
            Object(NonMatching, "app/camera/camera.cpp"),

            # battleGrid
            Object(NonMatching, "app/battleGrid/battleGrid.cpp"),
            Object(NonMatching, "app/battleGrid/wazaSequenceCamera.cpp"),
            Object(NonMatching, "app/battleGrid/wazaSequenceCameraData.cpp"),
            Object(NonMatching, "app/battleGrid/battleCamera.cpp"),

            # fade
            Object(NonMatching, "app/fade/fade.cpp"),
            Object(NonMatching, "app/fade/fade_effect.cpp"),
            Object(NonMatching, "app/fade/fade_fluid.cpp"),

            # script
            Object(NonMatching, "app/script/appScript.cpp"),
            Object(NonMatching, "app/script/objCamera.cpp"),
            Object(NonMatching, "app/script/objFloor.cpp"),
            Object(NonMatching, "app/script/objHero.cpp"),
            Object(NonMatching, "app/script/objMenu.cpp"),
            Object(NonMatching, "app/script/objPeople.cpp"),
            Object(NonMatching, "app/script/script.cpp"),
            Object(NonMatching, "app/script/scriptModel.cpp"),
            Object(NonMatching, "app/script/contSave.cpp"),

            # memcard
            Object(NonMatching, "app/memcard/memcard.cpp"),
            Object(NonMatching, "app/memcard/savedata.cpp"),
            Object(NonMatching, "app/memcard/savedataBios.cpp"),

            # recovery
            Object(NonMatching, "app/recovery/recovery.cpp"),
            Object(NonMatching, "app/recovery/recoveryEvent.cpp"),

            # mail
            Object(NonMatching, "app/mail/mailMain.cpp"),
            Object(NonMatching, "app/mail/mail.cpp"),

            # wazaSequence
            Object(NonMatching, "app/wazaSequence/wazaViewer.c"),
            Object(NonMatching, "app/wazaSequence/wazaWZXData.c"),
            Object(NonMatching, "app/wazaSequence/trainerPKXData.c"),
            Object(NonMatching, "app/wazaSequence/pokemonPKXData.c"),
            Object(NonMatching, "app/wazaSequence/wazaGenericWZXData.c"),
            Object(NonMatching, "app/wazaSequence/wazaExtWZXData.c"),
            Object(NonMatching, "app/wazaSequence/pokemonWazaWZXData.c"),
            Object(NonMatching, "app/wazaSequence/unknownPokemonPKXData.c"),
            Object(NonMatching, "app/wazaSequence/rarePokemonPKXData.c"),
            Object(NonMatching, "app/wazaSequence/wazaSequence.cpp"),
            Object(NonMatching, "app/wazaSequence/wazaSequenceSys.cpp"),
            Object(NonMatching, "app/wazaSequence/modelSequence.cpp"),
            Object(NonMatching, "app/wazaSequence/nullSequence.cpp"),
            Object(NonMatching, "app/wazaSequence/wazaResourceData.c"),
            Object(NonMatching, "app/wazaSequence/wazaSequenceEntry.cpp"),
            Object(NonMatching, "app/wazaSequence/deoxyspokemonPKXData.c"),
            Object(NonMatching, "app/wazaSequence/rareDeoxysPokemonPKXData.c"),
            Object(NonMatching, "app/wazaSequence/pachiru.cpp"),
            Object(NonMatching, "app/wazaSequence/leaffx.cpp"),
            Object(NonMatching, "app/wazaSequence/billboard.cpp"),
            Object(NonMatching, "app/wazaSequence/wazaeffects.cpp"),
            Object(NonMatching, "app/wazaSequence/boneFill.cpp"),

            Object(NonMatching, "app/etctools/etctools.cpp"),
            Object(NonMatching, "app/sodateya/sodateya.cpp"),

            # fight
            Object(NonMatching, "app/fight/fightMain.cpp"),
            Object(NonMatching, "app/fight/fightKind.cpp"),
            Object(NonMatching, "app/fight/fightTarget.cpp"),
            Object(NonMatching, "app/fight/fightType.cpp"),
            Object(NonMatching, "app/fight/fightWaza.cpp"),
            Object(NonMatching, "app/fight/fightWazaBios.cpp"),
            Object(NonMatching, "app/fight/fightEncount.cpp"),
            Object(NonMatching, "app/fight/fightEncountBios.cpp"),
            Object(NonMatching, "app/fight/fightFloor.cpp"),
            Object(NonMatching, "app/fight/fightFloorBios.cpp"),
            Object(NonMatching, "app/fight/fightFloorDB.cpp"),
            Object(NonMatching, "app/fight/fightSideBios.cpp"),
            Object(NonMatching, "app/fight/fightSide.cpp"),
            Object(NonMatching, "app/fight/fightSideDB.cpp"),
            Object(NonMatching, "app/fight/fightTrainer.cpp"),
            Object(NonMatching, "app/fight/fightTrainerBios.cpp"),
            Object(NonMatching, "app/fight/fightTrainerDB.cpp"),
            Object(NonMatching, "app/fight/fightTrainerEnemy.cpp"),
            Object(NonMatching, "app/fight/fightItemBios.cpp"),
            Object(NonMatching, "app/fight/fightItem.cpp"),
            Object(NonMatching, "app/fight/fightPokemon.cpp"),
            Object(NonMatching, "app/fight/fightPokemonBios.cpp"),
            Object(NonMatching, "app/fight/fightPokemonEnemy.cpp"),
            Object(NonMatching, "app/fight/fightActionBios.cpp"),
            Object(NonMatching, "app/fight/fightAction.cpp"),
            Object(NonMatching, "app/fight/fightActionFlow.cpp"),
            Object(NonMatching, "app/fight/fightActionDisp.cpp"),
            Object(NonMatching, "app/fight/fightKouka.cpp"),
            Object(NonMatching, "app/fight/fightKoukaBios.cpp"),
            Object(NonMatching, "app/fight/fightJouken.cpp"),
            Object(NonMatching, "app/fight/fightJoukenBios.cpp"),
            Object(NonMatching, "app/fight/fightAbicnt.cpp"),
            Object(NonMatching, "app/fight/fight.cpp"),
            Object(NonMatching, "app/fight/fightEncountWipeData.c"),

            # fightData
            Object(NonMatching, "app/fight/fightJoukenData.c"),
            Object(NonMatching, "app/fight/fightJoukenLinkData.c"),
            Object(NonMatching, "app/fight/fightTargetData.c"),
            Object(NonMatching, "app/fight/fightActionKindData.c"),
            Object(NonMatching, "app/fight/fightActionData_waza.c"),
            Object(NonMatching, "app/fight/fightKoukaData.c"),
            Object(NonMatching, "app/fight/fightWazaCriticalData.c"),
            Object(NonMatching, "app/fight/fightActionData_kaisi.c"),
            Object(NonMatching, "app/fight/fightAbicntData.c"),
            Object(NonMatching, "app/fight/fightActionData_turn.c"),
            Object(NonMatching, "app/fight/fightActionData_item.c"),
            Object(NonMatching, "app/fight/fightActionData_syuuryou.c"),
            Object(NonMatching, "app/fight/fightWazaHitKakurituData.c"),
            Object(NonMatching, "app/fight/fightTrainerAi_ComboId.c"),

            # fightAi2
            Object(NonMatching, "app/fight/fightTrainerAi2.cpp"),
            Object(NonMatching, "app/fight/fightTrainerAiWazaHit.cpp"),

            # fightSeq
            Object(NonMatching, "app/fight/fightSeq/fightSeqItem.c"),
            Object(NonMatching, "app/fight/fightSeq/fightSeqWaza.c"),
            Object(NonMatching, "app/fight/fightSeq/fightSeqWSWaza.cpp"),
            Object(NonMatching, "app/fight/fightSeq/fightSeqBasis.cpp"),
            Object(NonMatching, "app/fight/fightSeq/fightSeqItemseq.cpp"),
            Object(NonMatching, "app/fight/fightSeq/fightSeqMsg.c"),
            Object(NonMatching, "app/fight/fightSeq/fightSeqSpAction.cpp"),
            Object(NonMatching, "app/fight/fightSeq/fightSeqStatus.cpp"),
            Object(NonMatching, "app/fight/fightSeq/fightSeqWazaseq.cpp"),
            Object(NonMatching, "app/fight/fightSeq/fightSeq.cpp"),
            Object(NonMatching, "app/fight/fightSeq/fightWazaWzx.cpp"),

            Object(NonMatching, "app/toolentry/toolentry.cpp"),
            Object(NonMatching, "app/tableRes/tableResBios.cpp"),

            # pokemonRelive
            Object(NonMatching, "app/pokemon/pokemonRelive.cpp"),
            Object(NonMatching, "app/pokemon/pokemonWazaSequenceDisplay.cpp"),

            Object(NonMatching, "app/memo/memo.cpp"),
            Object(NonMatching, "app/evolution/evolution.cpp"),
            Object(NonMatching, "app/charName/charNameBios.cpp"),

            # fightGSfloor
            Object(NonMatching, "app/fight/fightGSfloor.cpp"),

            # fightMenu
            Object(NonMatching, "app/fight/fightMenu.cpp"),

            # fightTimer
            Object(NonMatching, "app/fight/fightTimer/fightTimer.cpp"),

            Object(NonMatching, "app/d2present/d2present.cpp"),
            Object(NonMatching, "app/effectEditor/effectEditor.cpp"),

            # flashmenu
            Object(NonMatching, "app/flashmenu/flashmenu.cpp"),
            Object(NonMatching, "app/flashmenu/flashcalc.cpp"),
            Object(NonMatching, "app/flashmenu/vecGraph.cpp"),
            Object(NonMatching, "app/flashmenu/flashsystem.cpp"),

            # deck
            Object(NonMatching, "app/deck/deck.cpp"),
            Object(NonMatching, "app/deck/deckGroupData.c"),
            Object(NonMatching, "app/deck/deckDataVirtualBios.cpp"),

            Object(NonMatching, "app/reliveHall/reliveHall.cpp"),
            Object(NonMatching, "app/ant/ant.cpp"),
            Object(NonMatching, "app/mball/mballBios.cpp"),

            # ribbon
            Object(NonMatching, "app/ribbon/ribbon.cpp"),
            Object(NonMatching, "app/ribbon/exribbon.cpp"),

            # light
            Object(NonMatching, "app/light/lightEditor.cpp"),
            Object(NonMatching, "app/light/light.cpp"),

            Object(NonMatching, "app/esaba/esaba.cpp"),

            # undertaker
            Object(NonMatching, "app/underTaker/undertaker.cpp"),
            Object(NonMatching, "app/underTaker/undertakerBios.cpp"),

            # people
            Object(NonMatching, "app/people/peopleInfoBios.cpp"),
            Object(NonMatching, "app/people/peopleBios.cpp"),
            Object(NonMatching, "app/people/people.cpp"),
            Object(NonMatching, "app/people/peopleViewer.cpp"),
            Object(NonMatching, "app/people/peoplePartAnimation.cpp"),
            Object(NonMatching, "app/people/peopleSave.cpp"),
            Object(NonMatching, "app/people/peopleTalk.cpp"),
            Object(NonMatching, "app/people/peopleWalkList.cpp"),
            Object(NonMatching, "app/people/peopleMemberFunc.cpp"),
            Object(NonMatching, "app/people/peopleColision.cpp"),

            # mewwaza
            Object(NonMatching, "app/mewwaza/mewwazadata.c"),
            Object(NonMatching, "app/mewwaza/mewwaza.cpp"),

            # fightAiM
            Object(NonMatching, "app/fight/fightTrainerAi.cpp"),
            Object(NonMatching, "app/fight/fightTrainerAiCombo.cpp"),
            Object(NonMatching, "app/fight/fightTrainerAiItem.cpp"),
            Object(NonMatching, "app/fight/fightTrainerAiIrekae.cpp"),
            Object(NonMatching, "app/fight/fightTrainerAiComboFunc.cpp"),
            Object(NonMatching, "app/fight/fightTrainerAiWaza.cpp"),
            Object(NonMatching, "app/fight/fightTrainerAiWazaDamage.cpp"),
            Object(NonMatching, "app/fight/fightTrainerAiWazaDamageFightPokemon.cpp"),
            Object(NonMatching, "app/fight/fightTrainerAiWazaValue.cpp"),
            Object(NonMatching, "app/fight/fightTrainerAi_ExpectWazaDat.c"),
            Object(NonMatching, "app/fight/fightTrainerAiComboContinueFunc.cpp"),

            # bingoBios
            Object(NonMatching, "app/bingo/bingoBios.cpp"),

            # gimmickBox
            Object(NonMatching, "app/gimmick/gimmickBox.cpp"),
        ]
    },
    {
        "lib": "xd_app_pokemon",
        "mw_version": config.linker_version,
        "cflags": cflags_xd_app_pokemon,
        "progress_category": "game",
        "objects": [
            # pokemon
            Object(NonMatching, "app/pokemon/pokemonGrowData.c"),
            Object(NonMatching, "app/pokemon/pokemonTokuseiData.c"),
            Object(NonMatching, "app/pokemon/pokemonFriendFilterData.c"),
            Object(NonMatching, "app/pokemon/pokemonNakigoeData.c"),
            Object(NonMatching, "app/pokemon/pokemonWaveDispData.c"),
            Object(NonMatching, "app/pokemon/pokemon.cpp"),
            Object(NonMatching, "app/pokemon/pokemonBios.cpp"),
            Object(NonMatching, "app/pokemon/pokemonDB.cpp"),
            Object(NonMatching, "app/pokemon/pokemonEvolution.cpp"),
            Object(NonMatching, "app/pokemon/pokemonStatusFightoutPokemon.cpp"),
            Object(NonMatching, "app/pokemon/pokemonStatusFightPokemon.cpp"),
            Object(NonMatching, "app/pokemon/pokemonStatusPokemon.cpp"),
            Object(NonMatching, "app/pokemon/darkPokemon.cpp"),
            Object(NonMatching, "app/pokemon/darkPokemonList.c"),
            Object(NonMatching, "app/pokemon/darkPokemonBios.cpp"),
        ]
    },
    SysdolphinLib(
        objects=[
            # hsdparticle_gs
            Object(NonMatching, "GSAPI/GSsysdolphin_baselib/particle/pslist.c"),
            Object(NonMatching, "GSAPI/GSsysdolphin_baselib/particle/particle.c"),
            Object(NonMatching, "GSAPI/GSsysdolphin_baselib/particle/psappsrt.c"),
            Object(NonMatching, "GSAPI/GSsysdolphin_baselib/particle/psdisp.c"),
            Object(NonMatching, "GSAPI/GSsysdolphin_baselib/particle/psdisptev.c"),
            Object(NonMatching, "GSAPI/GSsysdolphin_baselib/particle/psinterpret.c"),
            Object(NonMatching, "GSAPI/GSsysdolphin_baselib/particle/generator.c"),

            # hsdbase_gs
            Object(NonMatching, "GSAPI/GSsysdolphin_baselib/baselib/wobj.c"),
            Object(NonMatching, "GSAPI/GSsysdolphin_baselib/baselib/archive.c"),
            Object(NonMatching, "GSAPI/GSsysdolphin_baselib/baselib/bytecode.c", extra_cflags=["-use_lmw_stmw=on"]),
            Object(NonMatching, "GSAPI/GSsysdolphin_baselib/baselib/class.c"),
            Object(NonMatching, "GSAPI/GSsysdolphin_baselib/baselib/cobj.c"),
            Object(NonMatching, "GSAPI/GSsysdolphin_baselib/baselib/debug.c"),
            Object(NonMatching, "GSAPI/GSsysdolphin_baselib/baselib/displayfunc.c"),
            Object(NonMatching, "GSAPI/GSsysdolphin_baselib/baselib/dobj.c"),
            Object(NonMatching, "GSAPI/GSsysdolphin_baselib/baselib/fobj.c"),
            Object(NonMatching, "GSAPI/GSsysdolphin_baselib/baselib/fog.c"),
            Object(NonMatching, "GSAPI/GSsysdolphin_baselib/baselib/hash.c"),
            Object(NonMatching, "GSAPI/GSsysdolphin_baselib/baselib/id.c"),
            Object(NonMatching, "GSAPI/GSsysdolphin_baselib/baselib/initialize.c"),
            Object(NonMatching, "GSAPI/GSsysdolphin_baselib/baselib/jobj.c"),
            Object(NonMatching, "GSAPI/GSsysdolphin_baselib/baselib/list.c"),
            Object(NonMatching, "GSAPI/GSsysdolphin_baselib/baselib/lobj.c"),
            Object(NonMatching, "GSAPI/GSsysdolphin_baselib/baselib/memory.c"),
            Object(NonMatching, "GSAPI/GSsysdolphin_baselib/baselib/mobj.c"),
            Object(NonMatching, "GSAPI/GSsysdolphin_baselib/baselib/mtx.c"),
            Object(NonMatching, "GSAPI/GSsysdolphin_baselib/baselib/objalloc.c"),
            Object(Matching, "GSAPI/GSsysdolphin_baselib/baselib/object.c"),
            Object(NonMatching, "GSAPI/GSsysdolphin_baselib/baselib/pobj.c"),
            Object(NonMatching, "GSAPI/GSsysdolphin_baselib/baselib/quatlib.c"),
            Object(NonMatching, "GSAPI/GSsysdolphin_baselib/baselib/random.c"),
            Object(NonMatching, "GSAPI/GSsysdolphin_baselib/baselib/robj.c"),
            Object(NonMatching, "GSAPI/GSsysdolphin_baselib/baselib/shadow.c"),
            Object(NonMatching, "GSAPI/GSsysdolphin_baselib/baselib/spline.c"),
            Object(NonMatching, "GSAPI/GSsysdolphin_baselib/baselib/state.c"),
            Object(NonMatching, "GSAPI/GSsysdolphin_baselib/baselib/tev.c"),
            Object(NonMatching, "GSAPI/GSsysdolphin_baselib/baselib/texp.c"),
            Object(NonMatching, "GSAPI/GSsysdolphin_baselib/baselib/texpdag.c"),
            Object(NonMatching, "GSAPI/GSsysdolphin_baselib/baselib/texpopt.c"),
            Object(NonMatching, "GSAPI/GSsysdolphin_baselib/baselib/tobj.c"),
            Object(NonMatching, "GSAPI/GSsysdolphin_baselib/baselib/util.c"),
            Object(NonMatching, "GSAPI/GSsysdolphin_baselib/baselib/aobj.c"),
        ]
    ),
]


# Optional callback to adjust link order. This can be used to add, remove, or reorder objects.
# This is called once per module, with the module ID and the current link order.
#
# For example, this adds "dummy.c" to the end of the DOL link order if configured with --non-matching.
# "dummy.c" *must* be configured as a Matching (or Equivalent) object in order to be linked.
def link_order_callback(module_id: int, objects: List[str]) -> List[str]:
    # Don't modify the link order for matching builds
    if not config.non_matching:
        return objects
    if module_id == 0:  # DOL
        return objects + ["dummy.c"]
    return objects

# Uncomment to enable the link order callback.
# config.link_order_callback = link_order_callback


# Optional extra categories for progress tracking
# Adjust as desired for your project
config.progress_categories = [
    ProgressCategory("game", "Game Code"),
    ProgressCategory("sdk", "SDK Code"),
    ProgressCategory("GSAPI", "GSAPI Code")
]
config.progress_each_module = args.verbose
# Optional extra arguments to `objdiff-cli report generate`
config.progress_report_args = [
    # Marks relocations as mismatching if the target value is different
    # Default is "functionRelocDiffs=none", which is most lenient
    # "--config functionRelocDiffs=data_value",
]

if args.mode == "configure":
    # Write build.ninja and objdiff.json
    generate_build(config)
elif args.mode == "progress":
    # Print progress information
    calculate_progress(config)
else:
    sys.exit("Unknown mode: " + args.mode)
