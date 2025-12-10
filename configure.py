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
config.binutils_tag = "2.42-1"
config.compilers_tag = "20250812"
config.dtk_tag = "v1.7.4"
config.objdiff_tag = "v3.4.0"
config.sjiswrap_tag = "v1.2.2"
config.wibo_tag = "1.0.0-beta.4"

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
    "-warn pragmas",
    "-requireprotos",
    "-D__GEKKO__",
    "-i include/libc",
    "-ir src/dolphin",
]

cflags_musyx = [
    "-proc gekko",
    "-nodefaults",
    "-nosyspath",
    "-i include",
    "-i extern/musyx/include",
    "-i include/libc",
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
    "-i extern/musyx/include",
    "-i include/libc",
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
def DolphinLib(lib_name: str, objects: List[Object], patch=2 if config.version == "NXXJ01" else 1) -> Dict[str, Any]:
    return {
        "lib": lib_name,
        "mw_version": "GC/1.2.5n",
        "cflags": [*cflags_dolphin, f"-DSDK_REVISION={patch}"],
        "progress_category": "sdk",
        "objects": objects,
    }


def MusyX(objects, mw_version="GC/1.3.2", debug=False, major=2, minor=0, patch=3 if version_num == 7 else 0):
    cflags = cflags_musyx if not debug else cflags_musyx_debug
    return {
        "lib": "musyx",
        "mw_version": mw_version,
        "src_dir": "extern/musyx/src",
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
        "base",
        [
            Object(MatchingFor("NXXJ01"), "dolphin/base/PPCArch.c"),
        ],
    ),
    DolphinLib(
        "os",
        [
            Object(NonMatching, "dolphin/os/OS.c"),
            Object(NonMatching, "dolphin/os/OSAlarm.c"),
            Object(NonMatching, "dolphin/os/OSArena.c"),
            Object(MatchingFor("NXXJ01"), "dolphin/os/OSAudioSystem.c"),
            Object(NonMatching, "dolphin/os/OSCache.c"),
            Object(NonMatching, "dolphin/os/OSContext.c"),
            Object(NonMatching, "dolphin/os/OSError.c"),
            Object(NonMatching, "dolphin/os/OSExec.c"),
            Object(NonMatching, "dolphin/os/OSFatal.c"),
            Object(NonMatching, "dolphin/os/OSFont.c"),
            Object(NonMatching, "dolphin/os/OSInterrupt.c"),
            Object(Equivalent, "dolphin/os/OSLink.c"),
            Object(MatchingFor("NXXJ01"), "dolphin/os/OSMemory.c"),
            Object(MatchingFor("NXXJ01"), "dolphin/os/OSMutex.c"),
            Object(MatchingFor("NXXJ01"), "dolphin/os/OSReboot.c"),
            Object(MatchingFor("NXXJ01"), "dolphin/os/OSReset.c"),
            Object(MatchingFor("NXXJ01"), "dolphin/os/OSResetSW.c"),
            Object(MatchingFor("NXXJ01"), "dolphin/os/OSRtc.c"),
            Object(MatchingFor("NXXJ01"), "dolphin/os/OSSync.c"),
            Object(NonMatching, "dolphin/os/OSThread.c"),
            Object(MatchingFor("NXXJ01"), "dolphin/os/OSTime.c"),
            Object(MatchingFor("NXXJ01"), "dolphin/os/__start.c"),
            Object(NonMatching, "dolphin/os/__ppc_eabi_init.cpp"),
        ],
    ),
    DolphinLib(
        "db",
        [
            Object(MatchingFor("NXXJ01"), "dolphin/db/db.c"),
        ],
    ),
    DolphinLib(
        "mtx",
        [
            Object(NonMatching, "dolphin/mtx/mtx.c", extra_cflags=["-char signed"]),
            Object(MatchingFor("NXXJ01"), "dolphin/mtx/mtxvec.c"),
            Object(NonMatching, "dolphin/mtx/mtx44.c", extra_cflags=["-char signed"]),
            Object(NonMatching, "dolphin/mtx/vec.c"),
            Object(NonMatching, "dolphin/mtx/quat.c"),
        ],
    ),
    DolphinLib(
        "dvd",
        [
            Object(NonMatching, "dolphin/dvd/dvdlow.c", extra_cflags=["-char signed"]),
            Object(NonMatching, "dolphin/dvd/dvdfs.c", extra_cflags=["-char signed"]),
            Object(NonMatching, "dolphin/dvd/dvd.c", extra_cflags=["-char signed"]),
            Object(MatchingFor("NXXJ01"), "dolphin/dvd/dvdqueue.c", extra_cflags=["-char signed"]),
            Object(MatchingFor("NXXJ01"), "dolphin/dvd/dvderror.c", extra_cflags=["-char signed"]),
            Object(MatchingFor("NXXJ01"), "dolphin/dvd/dvdidutils.c", extra_cflags=["-char signed"]),
            Object(MatchingFor("NXXJ01"), "dolphin/dvd/dvdFatal.c", extra_cflags=["-char signed"]),
            Object(NonMatching, "dolphin/dvd/fstload.c", extra_cflags=["-char signed"]),
        ],
    ),
    DolphinLib(
        "vi",
        [
            Object(NonMatching, "dolphin/vi/vi.c"),
        ],
    ),
    DolphinLib(
        "pad",
        [
            Object(NonMatching, "dolphin/pad/Pad.c"),
        ],
    ),
    DolphinLib(
        "ai",
        [
            Object(NonMatching, "dolphin/ai/ai.c"),
        ],
    ),
    DolphinLib(
        "ar",
        [
            Object(NonMatching, "dolphin/ar/ar.c"),
            Object(NonMatching, "dolphin/ar/arq.c"),
        ],
    ),
    DolphinLib(
        "dsp",
        [
            Object(NonMatching, "dolphin/dsp/dsp.c"),
            Object(MatchingFor("NXXJ01"), "dolphin/dsp/dsp_debug.c"),
            Object(NonMatching, "dolphin/dsp/dsp_task.c"),
        ],
    ),
    DolphinLib(
        "card",
        [
            Object(NonMatching, "dolphin/card/CARDBios.c"),
            Object(NonMatching, "dolphin/card/CARDUnlock.c"),
            Object(MatchingFor("NXXJ01"), "dolphin/card/CARDRdwr.c"),
            Object(MatchingFor("NXXJ01"), "dolphin/card/CARDBlock.c"),
            Object(MatchingFor("NXXJ01"), "dolphin/card/CARDDir.c"),
            Object(MatchingFor("NXXJ01"), "dolphin/card/CARDCheck.c"),
            Object(MatchingFor("NXXJ01"), "dolphin/card/CARDMount.c"),
            Object(MatchingFor("NXXJ01"), "dolphin/card/CARDFormat.c"),
            Object(MatchingFor("NXXJ01"), "dolphin/card/CARDOpen.c", extra_cflags=["-char signed"]),
            Object(MatchingFor("NXXJ01"), "dolphin/card/CARDCreate.c"),
            Object(MatchingFor("NXXJ01"), "dolphin/card/CARDRead.c"),
            Object(MatchingFor("NXXJ01"), "dolphin/card/CARDWrite.c"),
            Object(MatchingFor("NXXJ01"), "dolphin/card/CARDDelete.c"),
            Object(MatchingFor("NXXJ01"), "dolphin/card/CARDStat.c"),
            Object(MatchingFor("NXXJ01"), "dolphin/card/CARDStatEx.c"),
            Object(NonMatching, "dolphin/card/CARDNet.c"),
        ],
    ),
    DolphinLib(
        "gx",
        [
            Object(NonMatching, "dolphin/gx/GXInit.c"),
            Object(Equivalent, "dolphin/gx/GXFifo.c"),
            Object(NonMatching, "dolphin/gx/GXAttr.c"),
            Object(MatchingFor("NXXJ01"), "dolphin/gx/GXMisc.c"),
            Object(MatchingFor("NXXJ01"), "dolphin/gx/GXGeometry.c"),
            Object(NonMatching, "dolphin/gx/GXFrameBuf.c"),
            Object(NonMatching, "dolphin/gx/GXLight.c"),
            Object(NonMatching, "dolphin/gx/GXTexture.c"),
            Object(MatchingFor("NXXJ01"), "dolphin/gx/GXBump.c"),
            Object(NonMatching, "dolphin/gx/GXTev.c"),
            Object(NonMatching, "dolphin/gx/GXPixel.c"),
            Object(NonMatching, "dolphin/gx/GXDraw.c"),
            Object(MatchingFor("NXXJ01"), "dolphin/gx/GXDisplayList.c"),
            Object(NonMatching, "dolphin/gx/GXTransform.c"),
            Object(NonMatching, "dolphin/gx/GXPerf.c"),
        ],
    ),
    DolphinLib(
        "perf",
        [
            Object(NonMatching, "dolphin/perf/perf.c"),
            Object(NonMatching, "dolphin/perf/perfdraw.c"),
        ],
    ),
    DolphinLib(
        "amcstubs",
        [
            Object(MatchingFor("NXXJ01"), "dolphin/amcstubs/AmcExi2Stubs.c"),
        ],
    ),
    DolphinLib(
        "odenotstub",
        [
            Object(MatchingFor("NXXJ01"), "dolphin/odenotstub/odenotstub.c"),
        ],
    ),
    DolphinLib(
        "OdemuExi2",
        [
            Object(NonMatching, "dolphin/OdemuExi2Lib/DebuggerDriver.c"),
        ],
    ),
    DolphinLib(
        "exi",
        [
            Object(NonMatching, "dolphin/exi/EXIBios.c", extra_cflags=["-O3,p"]),
            Object(MatchingFor("NXXJ01"), "dolphin/exi/EXIUart.c"),
        ],
    ),
    DolphinLib(
        "si",
        [
            Object(NonMatching, "dolphin/si/SIBios.c"),
            Object(NonMatching, "dolphin/si/SISamplingRate.c"),
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
        "mw_version": config.linker_version,
        "cflags": cflags_runtime,
        "progress_category": "sdk",
        "host": False,
        "objects": [
            Object(NonMatching, "PowerPC_EABI_Support/Runtime/Src/__mem.c"),
            Object(NonMatching, "PowerPC_EABI_Support/Runtime/Src/__va_arg.c"),
            Object(NonMatching, "PowerPC_EABI_Support/Runtime/Src/global_destructor_chain.c"),
            Object(NonMatching, "PowerPC_EABI_Support/Runtime/Src/CPlusLibPPC.cp"),
            Object(NonMatching, "PowerPC_EABI_Support/Runtime/Src/NMWException.cp", extra_cflags=["-Cpp_exceptions on"]),
            Object(NonMatching, "PowerPC_EABI_Support/Runtime/Src/runtime.c"),
            Object(NonMatching, "PowerPC_EABI_Support/Runtime/Src/__init_cpp_exceptions.cpp"),
            Object(NonMatching, "PowerPC_EABI_Support/Runtime/Src/Gecko_ExceptionPPC.cp"),
            Object(NonMatching, "PowerPC_EABI_Support/Runtime/Src/GCN_mem_alloc.c", extra_cflags=["-str reuse,nopool,readonly"]),
        ],
    },
    {
        "lib": "MSL_C",
        "mw_version": config.linker_version,
        "cflags": cflags_runtime,
        "progress_category": "sdk",
        "host": False,
        "objects": [
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/abort_exit.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/alloc.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/errno.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/ansi_files.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Src/ansi_fp.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/arith.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/buffer_io.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/PPC_EABI/Src/critical_regions.gamecube.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/ctype.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/locale.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/direct_io.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/file_io.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/FILE_POS.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/mbstring.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/mem.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/mem_funcs.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/misc_io.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/printf.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/float.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/qsort.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/scanf.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/string.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/strtold.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/strtoul.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/wchar_io.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/PPC_EABI/Src/uart_console_io_gcn.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/e_acos.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/e_asin.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/e_atan2.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/e_exp.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/e_fmod.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/e_log.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/e_pow.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/e_rem_pio2.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/k_cos.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/k_rem_pio2.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/k_sin.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/k_tan.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/s_atan.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/s_ceil.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/s_copysign.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/s_cos.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/s_floor.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/s_frexp.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/s_ldexp.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/s_modf.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/s_sin.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/s_tan.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/w_acos.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/w_asin.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/w_atan2.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/w_exp.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/w_fmod.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/w_log.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/w_pow.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/e_sqrt.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/PPC_EABI/Src/math_ppc.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common_Embedded/Math/Double_precision/w_sqrt.c"),
            Object(NonMatching, "PowerPC_EABI_Support/MSL_C/MSL_Common/Src/extras.c"),
        ],
    },
    MusyX(
        # debug=True,
        # mw_version="GC/1.2.5n",
        major=2,
        minor=0,
        patch=0,
        objects=[
            Object(NonMatching, "musyx/runtime/seq.c"),
            Object(NonMatching, "musyx/runtime/synth.c"),
            Object(NonMatching, "musyx/runtime/seq_api.c"),
            Object(NonMatching, "musyx/runtime/snd_synthapi.c"),
            Object(NonMatching, "musyx/runtime/stream.c"),
            Object(NonMatching, "musyx/runtime/synthdata.c"),
            Object(NonMatching, "musyx/runtime/synthmacros.c"),
            Object(NonMatching, "musyx/runtime/synthvoice.c"),
            Object(NonMatching, "musyx/runtime/synth_ac.c"),
            Object(MatchingFor("NXXJ01"), "musyx/runtime/synth_dbtab.c"),
            Object(NonMatching, "musyx/runtime/synth_adsr.c"),
            Object(NonMatching, "musyx/runtime/synth_vsamples.c"),
            Object(NonMatching, "musyx/runtime/s_data.c"),
            Object(NonMatching, "musyx/runtime/hw_dspctrl.c"),
            Object(NonMatching, "musyx/runtime/hw_volconv.c"),
            Object(NonMatching, "musyx/runtime/snd3d.c"),
            Object(NonMatching, "musyx/runtime/snd_init.c"),
            Object(NonMatching, "musyx/runtime/snd_math.c"),
            Object(NonMatching, "musyx/runtime/snd_midictrl.c"),
            Object(NonMatching, "musyx/runtime/snd_service.c"),
            Object(NonMatching, "musyx/runtime/hardware.c"),
            Object(NonMatching, "musyx/runtime/dsp_import.c"),
            Object(NonMatching, "musyx/runtime/hw_aramdma.c"),
            Object(NonMatching, "musyx/runtime/hw_dolphin.c"),
            Object(NonMatching, "musyx/runtime/hw_memory.c"),
            Object(MatchingFor("NXXJ01"), "musyx/runtime/StdReverb/reverb_fx.c"),
            Object(NonMatching, "musyx/runtime/StdReverb/reverb.c"),
        ]
    ),
    {
        "lib": "gba",
        "mw_version": config.linker_version,
        "cflags": cflags_runtime,
        "progress_category": "sdk",
        "objects": [
            Object(NonMatching, "gba/GBA.c"),
            Object(NonMatching, "gba/GBARead.c"),
            Object(NonMatching, "gba/GBAWrite.c"),
            Object(NonMatching, "gba/GBAXfer.c"),
        ]
    },
    {
        "lib": "dbgMenu",
        "mw_version": config.linker_version,
        "cflags": cflags_runtime,
        "progress_category": "game",
        "objects": [
            Object(NonMatching, "game/dbgMenuCamera.cpp"),
            Object(NonMatching, "game/dbgMenuFight.cpp"),
            Object(NonMatching, "game/dbgMenuFlag.cpp"),
            Object(NonMatching, "game/dbgMenuPokemon.cpp"),
            Object(NonMatching, "game/dbgMenuHero.cpp"),
            Object(NonMatching, "game/dbgMenuFloor.cpp"),
            Object(NonMatching, "game/dbgMenuGSgfx.cpp"),
            Object(NonMatching, "game/dbgMenuGSvtr.cpp"),
            Object(NonMatching, "game/dbgMenuMemcard.cpp"),
            Object(NonMatching, "game/dbgMenuMsg.cpp"),
            Object(NonMatching, "game/dbgMenuPeople.cpp"),
            Object(NonMatching, "game/dbgMenuSoundTest.cpp"),
            Object(NonMatching, "game/dbgMenuWazaViewer.cpp"),
            Object(NonMatching, "game/dbgMenuWaza.cpp"),
            Object(NonMatching, "game/dbgMenuFightTrainer.cpp"),
            Object(NonMatching, "game/dbgMenuFightWaza.cpp"),
            Object(NonMatching, "game/dbgMenuLog.cpp"),
            Object(NonMatching, "game/dbgMenuFieldCamera.cpp"),
            Object(NonMatching, "game/dbgMenuItemCreate.cpp"),
            Object(NonMatching, "game/dbgMenuRelive.cpp"),
            Object(NonMatching, "game/dbgMenuToolBattle.cpp"),
            Object(NonMatching, "game/dbgMenuSub.cpp"),
            Object(NonMatching, "game/dbgMenuMenu.cpp"),
        ]
    },
    {
        "lib": "menu",
        "mw_version": config.linker_version,
        "cflags": cflags_runtime,
        "progress_category": "game",
        "objects": [
            Object(NonMatching, "game/menuData.c"),
            Object(NonMatching, "game/menuTool.cpp"),
            Object(NonMatching, "game/menuColosseumBattleConnection.cpp"),
            Object(NonMatching, "game/menuSeq.c"),
            Object(NonMatching, "game/menuSprite.c"),
            Object(NonMatching, "game/menuPokeCoupon.cpp"),
            Object(NonMatching, "game/menuKeyDisc.cpp"),
            Object(NonMatching, "game/menuPocketBattleDisk.cpp"),
            Object(NonMatching, "game/menuWorldMapMX.cpp"),
            Object(NonMatching, "game/menuItemMX.cpp"),
            Object(NonMatching, "game/menuPokemon.cpp"),
            Object(NonMatching, "game/menuFightStatus.cpp"),
            Object(NonMatching, "game/menuFight.cpp"),
            Object(NonMatching, "game/menuPocketTool.cpp"),
            Object(NonMatching, "game/menuPocket.cpp"),
            Object(NonMatching, "game/menuTop.cpp"),
            Object(NonMatching, "game/menuNameEntry.cpp"),
            Object(NonMatching, "game/menuPokemonStatus.cpp"),
            Object(NonMatching, "game/menuItemTool.cpp"),
            Object(NonMatching, "game/menuSaveLoad.cpp"),
            Object(NonMatching, "game/menuPda.cpp"),
            Object(NonMatching, "game/menuReliveHall.cpp"),
            Object(NonMatching, "game/menuPdaSearcher.cpp"),
            Object(NonMatching, "game/menuPdaMailXD.cpp"),
            Object(NonMatching, "game/menuPdaMailList.XD.cpp"),
            Object(NonMatching, "game/menuColosseumBattle.cpp"),
            Object(NonMatching, "game/menuCB_BattleResult.cpp"),
            Object(NonMatching, "game/menuCB_BattleStart.cpp"),
            Object(NonMatching, "game/menuCB_Bios.cpp"),
            Object(NonMatching, "game/menuCB_Common.cpp"),
            Object(NonMatching, "game/menuCB_Debug.cpp"),
            Object(NonMatching, "game/menuCB_ItemList.cpp"),
            Object(NonMatching, "game/menuCB_PokemonEntry.cpp"),
            Object(NonMatching, "game/menuCB_Rule.cpp"),
            Object(NonMatching, "game/menuCB_Battle.cpp"),
            Object(NonMatching, "game/menuToolBattle.cpp"),
            Object(NonMatching, "game/menuGBAC.cpp"),
            Object(NonMatching, "game/menuPdaDPMonitor.cpp"),
            Object(NonMatching, "game/menuPdaDPMonitorList.cpp"),
            Object(NonMatching, "game/menuPdaSub.cpp"),
            Object(NonMatching, "game/menuPdaMemoXD.cpp"),
            Object(NonMatching, "game/menuPdaMemoListXD.cpp"),
            Object(NonMatching, "game/menuPcBoxPokemon.cpp"),
            Object(NonMatching, "game/menuField.cpp"),
            Object(NonMatching, "game/menuScript.cpp"),
            Object(NonMatching, "game/menuReliveMeter.cpp"),
            Object(NonMatching, "game/menuShop.cpp"),
            Object(NonMatching, "game/menuPocketCologne.cpp"),
            Object(NonMatching, "game/menuItemPda.cpp"),
            Object(NonMatching, "game/menuSub.cpp"),
            Object(NonMatching, "game/menuPdaMemoWaveXD.cpp"),
            Object(NonMatching, "game/menuInterrupt.cpp"),
            Object(NonMatching, "game/menuPcBoxNew.cpp"),
            Object(NonMatching, "game/menuPcBoxDouguNew.cpp"),
            Object(NonMatching, "game/menuCB_externDB.cpp"),
            Object(NonMatching, "game/menuDataBios.cpp"),
            Object(NonMatching, "game/menuPanel.cpp"),
            Object(NonMatching, "game/menuCB_Sub1.cpp"),
            Object(NonMatching, "game/menuLogoDemo.cpp"),
            Object(NonMatching, "game/menuHologram.cpp"),
            Object(NonMatching, "game/menuBingo.cpp"),
            Object(NonMatching, "game/menuItemBT.c"),
            Object(NonMatching, "game/menuReliveHallTutorial.cpp"),
            Object(NonMatching, "game/menuPokemonChange.cpp"),
            Object(NonMatching, "game/menuWorldMapMoveDemo.cpp"),
            Object(NonMatching, "game/menuWorldMapModel.cpp"),
            Object(NonMatching, "game/menuItem.c"),
            Object(NonMatching, "game/menuBattleDisk.cpp"),
            Object(NonMatching, "game/menuItemXD.c"),
            Object(NonMatching, "game/menuOrreColosseum.cpp"),
            Object(NonMatching, "game/menuTitle.cpp"),
            Object(NonMatching, "game/menuUseItem.cpp"),
            Object(NonMatching, "game/menuItemDebugRelease.c"),
            Object(NonMatching, "game/menuMewWaza.cpp"),
            Object(NonMatching, "game/menuMoveDemo.cpp"),
            Object(NonMatching, "game/menuTitleOption.cpp"),
        ],
    },
    {
        "lib": "game_unsorted",
        "mw_version": config.linker_version,
        "cflags": cflags_runtime,
        "progress_category": "game",
        "objects": [
            Object(NonMatching, "game/character.cpp"),
            Object(NonMatching, "game/relglobal.c"),
            Object(NonMatching, "game/pause.cpp"),
            Object(NonMatching, "game/time.cpp"),
            Object(NonMatching, "game/main.cpp"),
            Object(NonMatching, "game/sysvars.cpp"),
            Object(NonMatching, "game/flashmenuTest.cpp"),
            Object(NonMatching, "game/gbaPokemon.cpp"),
            Object(NonMatching, "game/gbaCommand.cpp"),
            Object(NonMatching, "game/agbCommunication.cpp"),
            Object(NonMatching, "game/floorRead.cpp"),
            Object(NonMatching, "game/pokecolo.cpp"),
            Object(NonMatching, "game/pokeconv.cpp"),
            Object(NonMatching, "game/wazaconv.cpp"),
            Object(NonMatching, "game/floorLayerConfig.cpp"),
        ]
    },
    {
        "lib": "xd_GSAPI",
        "mw_version": config.linker_version,
        "cflags": cflags_runtime,
        "progress_category": "game",
        "objects": [
            # GSmemman
            Object(NonMatching, "game/pxdvs/GSAPI/GSmemman/GSmemman.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSmemman/memOverride.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSmemman/OSAlloc.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSmemman/sysdolmem.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSmemman/poolAlloc.cpp"),

            Object(NonMatching, "game/pxdvs/GSAPI/GScamera/GScamera.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSlight/GSlight.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSmaterial/GSmaterial.cpp"),

            # GSmath
            Object(NonMatching, "game/pxdvs/GSAPI/GSmath/GSmtx.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSmath/GSmtx44.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSmath/GSquat.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSmath/init.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSmath/GSbezier.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSmath/GSlerp.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSmath/GSutil.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSmath/GSvec.cpp"),

            # GSmodel
            Object(NonMatching, "game/pxdvs/GSAPI/GSmodel/effects.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSmodel/blend.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSmodel/bound.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSmodel/animation.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSmodel/GSmodel.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSmodel/GSmodelExt.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSmodel/parse.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSmodel/part.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSmodel/save_state.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSmodel/shadow.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSmodel/bank.cpp"),

            Object(NonMatching, "game/pxdvs/GSAPI/GSpart/GSpart.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSscratch/GSscratch.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GStexture/GStexture.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSthread/GSthread.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSinput/GSinput.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSres/GSres.cpp"),

            # GSmsg
            Object(NonMatching, "game/pxdvs/GSAPI/GSmsg/GSmsg.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSmsg/sprite.cpp"),

            Object(NonMatching, "game/pxdvs/GSAPI/GSgapp/GSgapp.cpp"),

            # GScolsys
            Object(NonMatching, "game/pxdvs/GSAPI/GScolsys/GScolsys2.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GScolsys/GScolsys2Draw.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GScolsys/GScolsys2Walk.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GScolsys/GScolsys2Hit.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GScolsys/GScolsys2Util.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GScolsys/GScolsys2Human.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GScolsys/GScolsys2Thru.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GScolsys/GScolsys2Check.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GScolsys/GScolsys2Sun.cpp"),

            # GSparticle
            Object(NonMatching, "game/pxdvs/GSAPI/GSparticle/GSparticle.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSparticle/peParticle.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSparticle/peNode.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSparticle/peBank.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSparticle/peEmitter.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSparticle/peModel.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSparticle/peContainer.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSparticle/peDistortion.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSparticle/peParticleStrip.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSparticle/peSpline.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSparticle/particleEngine.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSparticle/peShape.cpp"),

            Object(NonMatching, "game/pxdvs/GSAPI/GSeffect/GSeffect.cpp"),

            # GSsnd
            Object(NonMatching, "game/pxdvs/GSAPI/GSsnd/GSsnd.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSsnd/sndStream.cpp"),

            Object(NonMatching, "game/pxdvs/GSAPI/GSdvd/GSdvd.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSfilter/GSfilter.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSspline/GSspline.cpp"),

            # GSfsys
            Object(NonMatching, "game/pxdvs/GSAPI/GSfsys/fsysStream.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSfsys/fsysBlock.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSfsys/fsysCache.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSfsys/fsysRead.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSfsys/fsysAlloc.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSfsys/GSfsys2.cpp"),

            Object(NonMatching, "game/pxdvs/GSAPI/GSflag/GSflag.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSbound/GSbound.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSvtr/GSvtr.cpp"),

            # GSmovie
            Object(NonMatching, "game/pxdvs/GSAPI/GSmovie/movieStream.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSmovie/GSmovie.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSmovie/THPDraw.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSmovie/THPDec.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSmovie/THPAudio.cpp"),

            Object(NonMatching, "game/pxdvs/GSAPI/GSlensFlare/GSlensFlare.cpp"),

            # GSScript
            Object(NonMatching, "game/pxdvs/GSAPI/GSScript/tiga.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSScript/tvariant.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSScript/chank.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSScript/defobj.cpp"),

            Object(NonMatching, "game/pxdvs/GSAPI/GSnetwork/GSnetwork.cpp"),

            # GSprim
            Object(NonMatching, "game/pxdvs/GSAPI/GSprim/GSprim.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSprim/2d.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSprim/text.cpp"),

            # GSshape
            Object(NonMatching, "game/pxdvs/GSAPI/GSshape/shapeAnim.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSshape/shapeObject.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSshape/shapeRender.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSshape/GSshape.cpp"),

            Object(NonMatching, "game/pxdvs/GSAPI/GSstream/GSstream.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSlogM/GSlog.cpp"),

            # GSgfxM
            Object(NonMatching, "game/pxdvs/GSAPI/GSgfxM/backfb.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSgfxM/GSgfx.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSgfxM/layer.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSgfxM/render.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSgfxM/perfbar.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSgfxM/token.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSgfxM/project.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSgfxM/halt.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSgfxM/video.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSgfxM/gpu.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSgfxM/vf.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSgfxM/dl.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSgfxM/layerState.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSgfxM/matrixStack.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSgfxM/layerFunc.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSgfxM/renderModule.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSgfxM/c_func.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSgfxM/layerConfig.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSgfxM/light_gfxm.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSgfxM/layerEffect.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSgfxM/gamecube.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSgfxM/screenshot.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSgfxM/capture.cpp"),
            Object(NonMatching, "game/pxdvs/GSAPI/GSgfxM/reset.cpp"),
        ]
    },
    {
        "lib": "xd_app",
        "mw_version": config.linker_version,
        "cflags": cflags_runtime,
        "progress_category": "game",
        "objects": [
            # kaisuu
            Object(NonMatching, "game/pxdvs/app/kaisuu/kaisuuData.c"),
            Object(NonMatching, "game/pxdvs/app/kaisuu/kaisuu.cpp"),
            Object(NonMatching, "game/pxdvs/app/kaisuu/kaisuuBios.cpp"),

            # menu
            Object(NonMatching, "game/pxdvs/app/menu/winSprite.cpp"),
            Object(NonMatching, "game/pxdvs/app/menu/menu.cpp"),
            Object(NonMatching, "game/pxdvs/app/menu/menuFace.cpp"),
            Object(NonMatching, "game/pxdvs/app/menu/menuFaceBios.cpp"),
            Object(NonMatching, "game/pxdvs/app/menu/menuModel.cpp"),
            Object(NonMatching, "game/pxdvs/app/menu/menuOffScreen.cpp"),
            Object(NonMatching, "game/pxdvs/app/menu/window.cpp"),
            Object(NonMatching, "game/pxdvs/app/menu/cursorBios.cpp"),
            Object(NonMatching, "game/pxdvs/app/menu/winMsg.cpp"),

            # zokusei
            Object(NonMatching, "game/pxdvs/app/zokusei/zokusei.cpp"),
            Object(NonMatching, "game/pxdvs/app/zokusei/zokuseiBios.cpp"),

            # floor
            Object(NonMatching, "game/pxdvs/app/floor/floor.cpp"),
            Object(NonMatching, "game/pxdvs/app/floor/floorEvent.cpp"),
            Object(NonMatching, "game/pxdvs/app/floor/floorCharacterBios.cpp"),
            Object(NonMatching, "game/pxdvs/app/floor/floorDataBios.cpp"),
            Object(NonMatching, "game/pxdvs/app/floor/floorFieldCamera.cpp"),
            Object(NonMatching, "game/pxdvs/app/floor/floorFieldCameraEditor.cpp"),
            Object(NonMatching, "game/pxdvs/app/floor/floorOffscreen.cpp"),
            Object(NonMatching, "game/pxdvs/app/floor/floorManager.cpp"),
            Object(NonMatching, "game/pxdvs/app/floor/floorModule.cpp"),
            Object(NonMatching, "game/pxdvs/app/floor/floorStack.cpp"),
            Object(NonMatching, "game/pxdvs/app/floor/floorLoad.cpp"),
            Object(NonMatching, "game/pxdvs/app/floor/floorScript.cpp"),
            Object(NonMatching, "game/pxdvs/app/floor/floorsound.cpp"),

            # joutai
            Object(NonMatching, "game/pxdvs/app/joutai/joutaiData.c"),
            Object(NonMatching, "game/pxdvs/app/joutai/joutai.cpp"),
            Object(NonMatching, "game/pxdvs/app/joutai/joutaiBios.cpp"),

            # waza
            Object(NonMatching, "game/pxdvs/app/waza/waza.cpp"),
            Object(NonMatching, "game/pxdvs/app/waza/wazaFuncData.c"),
            Object(NonMatching, "game/pxdvs/app/waza/wazaBios.cpp"),
            Object(NonMatching, "game/pxdvs/app/waza/wazaDB.cpp"),

            # pokemon
            Object(NonMatching, "game/pxdvs/app/pokemon/pokemonGrowData.c"),
            Object(NonMatching, "game/pxdvs/app/pokemon/pokemonTokuseiData.c"),
            Object(NonMatching, "game/pxdvs/app/pokemon/pokemonFriendFilterData.c"),
            Object(NonMatching, "game/pxdvs/app/pokemon/pokemonNakigoeData.c"),
            Object(NonMatching, "game/pxdvs/app/pokemon/pokemonWaveDispData.c"),
            Object(NonMatching, "game/pxdvs/app/pokemon/pokemon.cpp"),
            Object(NonMatching, "game/pxdvs/app/pokemon/pokemonBios.cpp"),
            Object(NonMatching, "game/pxdvs/app/pokemon/pokemonDB.cpp"),
            Object(NonMatching, "game/pxdvs/app/pokemon/pokemonEvolution.cpp"),
            Object(NonMatching, "game/pxdvs/app/pokemon/pokemonStatusFightoutPokemon.cpp"),
            Object(NonMatching, "game/pxdvs/app/pokemon/pokemonStatusFightPokemon.cpp"),
            Object(NonMatching, "game/pxdvs/app/pokemon/pokemonStatusPokemon.cpp"),
            Object(NonMatching, "game/pxdvs/app/pokemon/darkPokemon.cpp"),
            Object(NonMatching, "game/pxdvs/app/pokemon/darkPokemonList.c"),
            Object(NonMatching, "game/pxdvs/app/pokemon/darkPokemonBios.cpp"),

            # hero
            Object(NonMatching, "game/pxdvs/app/hero/hero.cpp"),
            Object(NonMatching, "game/pxdvs/app/hero/heroBios.cpp"),
            Object(NonMatching, "game/pxdvs/app/hero/heroMove.cpp"),
            Object(NonMatching, "game/pxdvs/app/hero/heroPokemonGet.cpp"),
            Object(NonMatching, "game/pxdvs/app/hero/heroMemberFunctions.cpp"),

            # sex
            Object(NonMatching, "game/pxdvs/app/sex/sexdata.c"),
            Object(NonMatching, "game/pxdvs/app/sex/sex.cpp"),

            # msgctrl
            Object(NonMatching, "game/pxdvs/app/msgctrl/msgctrlcode.c"),
            Object(NonMatching, "game/pxdvs/app/msgctrl/msgctrl.cpp"),

            Object(NonMatching, "game/pxdvs/app/dbgMenu/dbgMenu.cpp"),
            Object(NonMatching, "game/pxdvs/app/pcbox/pcbox.cpp"),

            # gamedata
            Object(NonMatching, "game/pxdvs/app/gamedata/gamedatasaveBios.cpp"),
            Object(NonMatching, "game/pxdvs/app/gamedata/gamedataBios.cpp"),
            Object(NonMatching, "game/pxdvs/app/gamedata/gamedata.cpp"),

            Object(NonMatching, "game/pxdvs/app/status/status.cpp"),

            # kouka
            Object(NonMatching, "game/pxdvs/app/kouka/koukaData.c"),
            Object(NonMatching, "game/pxdvs/app/kouka/koukaLinkData.c"),
            Object(NonMatching, "game/pxdvs/app/kouka/kouka.cpp"),
            Object(NonMatching, "game/pxdvs/app/kouka/koukaBios.cpp"),

            # tenkou
            Object(NonMatching, "game/pxdvs/app/tenkou/tenkouData.c"),
            Object(NonMatching, "game/pxdvs/app/tenkou/tenkouBios.cpp"),

            # tikei
            Object(NonMatching, "game/pxdvs/app/tikei/tikeiData.c"),
            Object(NonMatching, "game/pxdvs/app/tikei/tikeiBios.cpp"),

            # effects
            Object(NonMatching, "game/pxdvs/app/effects/filter.cpp"),
            Object(NonMatching, "game/pxdvs/app/effects/envMap.cpp"),
            Object(NonMatching, "game/pxdvs/app/effects/blur.cpp"),
            Object(NonMatching, "game/pxdvs/app/effects/glow.cpp"),

            # item
            Object(NonMatching, "game/pxdvs/app/item/itemBallData.c"),
            Object(NonMatching, "game/pxdvs/app/item/itemSoubiData.c"),
            Object(NonMatching, "game/pxdvs/app/item/tasteData.c"),
            Object(NonMatching, "game/pxdvs/app/item/itemWazaMachineNo.c"),
            Object(NonMatching, "game/pxdvs/app/item/itemParam.c"),
            Object(NonMatching, "game/pxdvs/app/item/item.cpp"),
            Object(NonMatching, "game/pxdvs/app/item/itemBios.cpp"),
            Object(NonMatching, "game/pxdvs/app/item/itemDB.cpp"),
            Object(NonMatching, "game/pxdvs/app/item/itemUse2Pokemon.cpp"),
            Object(NonMatching, "game/pxdvs/app/item/itemFightItem.cpp"),

            Object(NonMatching, "game/pxdvs/app/sound/sound.cpp"),
            Object(NonMatching, "game/pxdvs/app/camera/camera.cpp"),

            # battleGrid
            Object(NonMatching, "game/pxdvs/app/battleGrid/battleGrid.cpp"),
            Object(NonMatching, "game/pxdvs/app/battleGrid/wazaSequenceCamera.cpp"),
            Object(NonMatching, "game/pxdvs/app/battleGrid/wazaSequenceCameraData.cpp"),
            Object(NonMatching, "game/pxdvs/app/battleGrid/battleCamera.cpp"),

            # fade
            Object(NonMatching, "game/pxdvs/app/fade/fade.cpp"),
            Object(NonMatching, "game/pxdvs/app/fade/fade_effect.cpp"),
            Object(NonMatching, "game/pxdvs/app/fade/fade_fluid.cpp"),

            # script
            Object(NonMatching, "game/pxdvs/app/script/appScript.cpp"),
            Object(NonMatching, "game/pxdvs/app/script/objCamera.cpp"),
            Object(NonMatching, "game/pxdvs/app/script/objFloor.cpp"),
            Object(NonMatching, "game/pxdvs/app/script/objHero.cpp"),
            Object(NonMatching, "game/pxdvs/app/script/objMenu.cpp"),
            Object(NonMatching, "game/pxdvs/app/script/objPeople.cpp"),
            Object(NonMatching, "game/pxdvs/app/script/script.cpp"),
            Object(NonMatching, "game/pxdvs/app/script/scriptModel.cpp"),
            Object(NonMatching, "game/pxdvs/app/script/contSave.cpp"),

            # memcard
            Object(NonMatching, "game/pxdvs/app/memcard/memcard.cpp"),
            Object(NonMatching, "game/pxdvs/app/memcard/savedata.cpp"),
            Object(NonMatching, "game/pxdvs/app/memcard/savedataBios.cpp"),

            # recovery
            Object(NonMatching, "game/pxdvs/app/recovery/recovery.cpp"),
            Object(NonMatching, "game/pxdvs/app/recovery/recoveryEvent.cpp"),

            # mail
            Object(NonMatching, "game/pxdvs/app/mail/mailMain.cpp"),
            Object(NonMatching, "game/pxdvs/app/mail/mail.cpp"),

            # wazaSequence
            Object(NonMatching, "game/pxdvs/app/wazaSequence/wazaViewer.c"),
            Object(NonMatching, "game/pxdvs/app/wazaSequence/wazaWZXData.c"),
            Object(NonMatching, "game/pxdvs/app/wazaSequence/trainerPKXData.c"),
            Object(NonMatching, "game/pxdvs/app/wazaSequence/pokemonPKXData.c"),
            Object(NonMatching, "game/pxdvs/app/wazaSequence/wazaGenericWZXData.c"),
            Object(NonMatching, "game/pxdvs/app/wazaSequence/wazaExtWZXData.c"),
            Object(NonMatching, "game/pxdvs/app/wazaSequence/pokemonWazaWZXData.c"),
            Object(NonMatching, "game/pxdvs/app/wazaSequence/unknownPokemonPKXData.c"),
            Object(NonMatching, "game/pxdvs/app/wazaSequence/rarePokemonPKXData.c"),
            Object(NonMatching, "game/pxdvs/app/wazaSequence/wazaSequence.cpp"),
            Object(NonMatching, "game/pxdvs/app/wazaSequence/wazaSequenceSys.cpp"),
            Object(NonMatching, "game/pxdvs/app/wazaSequence/modelSequence.cpp"),
            Object(NonMatching, "game/pxdvs/app/wazaSequence/nullSequence.cpp"),
            Object(NonMatching, "game/pxdvs/app/wazaSequence/wazaResourceData.c"),
            Object(NonMatching, "game/pxdvs/app/wazaSequence/wazaSequenceEntry.cpp"),
            Object(NonMatching, "game/pxdvs/app/wazaSequence/deoxyspokemonPKXData.c"),
            Object(NonMatching, "game/pxdvs/app/wazaSequence/rareDeoxysPokemonPKXData.c"),
            Object(NonMatching, "game/pxdvs/app/wazaSequence/pachiru.cpp"),
            Object(NonMatching, "game/pxdvs/app/wazaSequence/leaffx.cpp"),
            Object(NonMatching, "game/pxdvs/app/wazaSequence/billboard.cpp"),
            Object(NonMatching, "game/pxdvs/app/wazaSequence/wazaeffects.cpp"),
            Object(NonMatching, "game/pxdvs/app/wazaSequence/boneFill.cpp"),

            Object(NonMatching, "game/pxdvs/app/etctools/etctools.cpp"),
            Object(NonMatching, "game/pxdvs/app/sodateya/sodateya.cpp"),

            # fight
            Object(NonMatching, "game/pxdvs/app/fight/fightMain.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightKind.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightTarget.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightType.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightWaza.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightWazaBios.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightEncount.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightEncountBios.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightFloor.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightFloorBios.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightFloorDB.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightSideBios.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightSide.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightSideDB.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightTrainer.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightTrainerBios.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightTrainerDB.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightTrainerEnemy.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightItemBios.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightItem.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightPokemon.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightPokemonBios.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightPokemonEnemy.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightActionBios.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightAction.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightActionFlow.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightActionDisp.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightKouka.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightKoukaBios.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightJouken.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightJoukenBios.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightAbicnt.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fight.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightEncountWipeData.c"),

            # fightData
            Object(NonMatching, "game/pxdvs/app/fight/fightJoukenData.c"),
            Object(NonMatching, "game/pxdvs/app/fight/fightJoukenLinkData.c"),
            Object(NonMatching, "game/pxdvs/app/fight/fightTargetData.c"),
            Object(NonMatching, "game/pxdvs/app/fight/fightActionKindData.c"),
            Object(NonMatching, "game/pxdvs/app/fight/fightActionData_waza.c"),
            Object(NonMatching, "game/pxdvs/app/fight/fightKoukaData.c"),
            Object(NonMatching, "game/pxdvs/app/fight/fightWazaCriticalData.c"),
            Object(NonMatching, "game/pxdvs/app/fight/fightActionData_kaisi.c"),
            Object(NonMatching, "game/pxdvs/app/fight/fightAbicntData.c"),
            Object(NonMatching, "game/pxdvs/app/fight/fightActionData_turn.c"),
            Object(NonMatching, "game/pxdvs/app/fight/fightActionData_item.c"),
            Object(NonMatching, "game/pxdvs/app/fight/fightActionData_syuuryou.c"),
            Object(NonMatching, "game/pxdvs/app/fight/fightWazaHitKakurituData.c"),
            Object(NonMatching, "game/pxdvs/app/fight/fightTrainerAi_ComboId.c"),

            # fightAi2
            Object(NonMatching, "game/pxdvs/app/fight/fightTrainerAi2.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightTrainerAiWazaHit.cpp"),

            # fightSeq
            Object(NonMatching, "game/pxdvs/app/fight/fightSeq/fightSeqItem.c"),
            Object(NonMatching, "game/pxdvs/app/fight/fightSeq/fightSeqWaza.c"),
            Object(NonMatching, "game/pxdvs/app/fight/fightSeq/fightSeqWSWaza.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightSeq/fightSeqBasis.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightSeq/fightSeqItemseq.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightSeq/fightSeqMsg.c"),
            Object(NonMatching, "game/pxdvs/app/fight/fightSeq/fightSeqSpAction.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightSeq/fightSeqStatus.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightSeq/fightSeqWazaseq.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightSeq/fightSeq.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightSeq/fightWazaWzx.cpp"),

            Object(NonMatching, "game/pxdvs/app/toolentry/toolentry.cpp"),
            Object(NonMatching, "game/pxdvs/app/tableRes/tableResBios.cpp"),

            # pokemonRelive
            Object(NonMatching, "game/pxdvs/app/pokemon/pokemonRelive.cpp"),
            Object(NonMatching, "game/pxdvs/app/pokemon/pokemonWazaSequenceDisplay.cpp"),

            Object(NonMatching, "game/pxdvs/app/memo/memo.cpp"),
            Object(NonMatching, "game/pxdvs/app/evolution/evolution.cpp"),
            Object(NonMatching, "game/pxdvs/app/charName/charNameBios.cpp"),

            # fightGSfloor
            Object(NonMatching, "game/pxdvs/app/fight/fightGSfloor.cpp"),

            # fightMenu
            Object(NonMatching, "game/pxdvs/app/fight/fightMenu.cpp"),

            # fightTimer
            Object(NonMatching, "game/pxdvs/app/fight/fightTimer/fightTimer.cpp"),

            Object(NonMatching, "game/pxdvs/app/d2present/d2present.cpp"),
            Object(NonMatching, "game/pxdvs/app/effectEditor/effectEditor.cpp"),

            # flashmenu
            Object(NonMatching, "game/pxdvs/app/flashmenu/flashmenu.cpp"),
            Object(NonMatching, "game/pxdvs/app/flashmenu/flashcalc.cpp"),
            Object(NonMatching, "game/pxdvs/app/flashmenu/vecGraph.cpp"),
            Object(NonMatching, "game/pxdvs/app/flashmenu/flashsystem.cpp"),

            # deck
            Object(NonMatching, "game/pxdvs/app/deck/deck.cpp"),
            Object(NonMatching, "game/pxdvs/app/deck/deckGroupData.c"),
            Object(NonMatching, "game/pxdvs/app/deck/deckDataVirtualBios.cpp"),

            Object(NonMatching, "game/pxdvs/app/reliveHall/reliveHall.cpp"),
            Object(NonMatching, "game/pxdvs/app/ant/ant.cpp"),
            Object(NonMatching, "game/pxdvs/app/mball/mballBios.cpp"),

            # ribbon
            Object(NonMatching, "game/pxdvs/app/ribbon/ribbon.cpp"),
            Object(NonMatching, "game/pxdvs/app/ribbon/exribbon.cpp"),

            # light
            Object(NonMatching, "game/pxdvs/app/light/lightEditor.cpp"),
            Object(NonMatching, "game/pxdvs/app/light/light.cpp"),

            Object(NonMatching, "game/pxdvs/app/esaba/esaba.cpp"),

            # undertaker
            Object(NonMatching, "game/pxdvs/app/underTaker/undertaker.cpp"),
            Object(NonMatching, "game/pxdvs/app/underTaker/undertakerBios.cpp"),

            # people
            Object(NonMatching, "game/pxdvs/app/people/peopleInfoBios.cpp"),
            Object(NonMatching, "game/pxdvs/app/people/peopleBios.cpp"),
            Object(NonMatching, "game/pxdvs/app/people/people.cpp"),
            Object(NonMatching, "game/pxdvs/app/people/peopleViewer.cpp"),
            Object(NonMatching, "game/pxdvs/app/people/peoplePartAnimation.cpp"),
            Object(NonMatching, "game/pxdvs/app/people/peopleSave.cpp"),
            Object(NonMatching, "game/pxdvs/app/people/peopleTalk.cpp"),
            Object(NonMatching, "game/pxdvs/app/people/peopleWalkList.cpp"),
            Object(NonMatching, "game/pxdvs/app/people/peopleMemberFunc.cpp"),
            Object(NonMatching, "game/pxdvs/app/people/peopleColision.cpp"),

            # mewwaza
            Object(NonMatching, "game/pxdvs/app/mewwaza/mewwazadata.c"),
            Object(NonMatching, "game/pxdvs/app/mewwaza/mewwaza.cpp"),

            # fightAiM
            Object(NonMatching, "game/pxdvs/app/fight/fightTrainerAi.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightTrainerAiCombo.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightTrainerAiItem.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightTrainerAiIrekae.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightTrainerAiComboFunc.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightTrainerAiWaza.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightTrainerAiWazaDamage.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightTrainerAiWazaDamageFightPokemon.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightTrainerAiWazaValue.cpp"),
            Object(NonMatching, "game/pxdvs/app/fight/fightTrainerAi_ExpectWazaDat.c"),
            Object(NonMatching, "game/pxdvs/app/fight/fightTrainerAiComboContinueFunc.cpp"),
        ]
    },
    {
        "lib": "maximum_GSAPI",
        "mw_version": config.linker_version,
        "cflags": cflags_runtime,
        "progress_category": "game",
        "objects": [
            # hsdparticle_gs
            Object(NonMatching, "game/maximum/GSAPI/particle/pslist.cpp"),
            Object(NonMatching, "game/maximum/GSAPI/particle/particle.cpp"),
            Object(NonMatching, "game/maximum/GSAPI/particle/psappsrt.cpp"),
            Object(NonMatching, "game/maximum/GSAPI/particle/psdisp.cpp"),
            Object(NonMatching, "game/maximum/GSAPI/particle/psdisptev.cpp"),
            Object(NonMatching, "game/maximum/GSAPI/particle/psinterpret.cpp"),
            Object(NonMatching, "game/maximum/GSAPI/particle/generator.cpp"),

            # hsdbase_gs
            Object(NonMatching, "game/maximum/GSAPI/baselib/wobj.cpp"),
            Object(NonMatching, "game/maximum/GSAPI/baselib/archive.cpp"),
            Object(NonMatching, "game/maximum/GSAPI/baselib/bytecode.cpp"),
            Object(NonMatching, "game/maximum/GSAPI/baselib/class.cpp"),
            Object(NonMatching, "game/maximum/GSAPI/baselib/cobj.cpp"),
            Object(NonMatching, "game/maximum/GSAPI/baselib/debug.cpp"),
            Object(NonMatching, "game/maximum/GSAPI/baselib/displayfunc.cpp"),
            Object(NonMatching, "game/maximum/GSAPI/baselib/dobj.cpp"),
            Object(NonMatching, "game/maximum/GSAPI/baselib/fobj.cpp"),
            Object(NonMatching, "game/maximum/GSAPI/baselib/fog.cpp"),
            Object(NonMatching, "game/maximum/GSAPI/baselib/hash.cpp"),
            Object(NonMatching, "game/maximum/GSAPI/baselib/id.cpp"),
            Object(NonMatching, "game/maximum/GSAPI/baselib/initialize.cpp"),
            Object(NonMatching, "game/maximum/GSAPI/baselib/jobj.cpp"),
            Object(NonMatching, "game/maximum/GSAPI/baselib/list.cpp"),
            Object(NonMatching, "game/maximum/GSAPI/baselib/lobj.cpp"),
            Object(NonMatching, "game/maximum/GSAPI/baselib/memory.cpp"),
            Object(NonMatching, "game/maximum/GSAPI/baselib/mobj.cpp"),
            Object(NonMatching, "game/maximum/GSAPI/baselib/mtx_base.cpp"),
            Object(NonMatching, "game/maximum/GSAPI/baselib/objalloc.cpp"),
            Object(NonMatching, "game/maximum/GSAPI/baselib/object.cpp"),
            Object(NonMatching, "game/maximum/GSAPI/baselib/pobj.cpp"),
            Object(NonMatching, "game/maximum/GSAPI/baselib/quatlib.cpp"),
            Object(NonMatching, "game/maximum/GSAPI/baselib/random.cpp"),
            Object(NonMatching, "game/maximum/GSAPI/baselib/robj.cpp"),
            Object(NonMatching, "game/maximum/GSAPI/baselib/shadow_base.cpp"),
            Object(NonMatching, "game/maximum/GSAPI/baselib/spline.cpp"),
            Object(NonMatching, "game/maximum/GSAPI/baselib/state.cpp"),
            Object(NonMatching, "game/maximum/GSAPI/baselib/tev.cpp"),
            Object(NonMatching, "game/maximum/GSAPI/baselib/texp.cpp"),
            Object(NonMatching, "game/maximum/GSAPI/baselib/texpdag.cpp"),
            Object(NonMatching, "game/maximum/GSAPI/baselib/texpopt.cpp"),
            Object(NonMatching, "game/maximum/GSAPI/baselib/tobj.cpp"),
            Object(NonMatching, "game/maximum/GSAPI/baselib/util.cpp"),
            Object(NonMatching, "game/maximum/GSAPI/baselib/aobj.cpp"),
        ]
    },
    {
        "lib": "maximum_app",
        "mw_version": config.linker_version,
        "cflags": cflags_runtime,
        "progress_category": "game",
        "objects": [
            Object(NonMatching, "game/maximum/app/bingo/bingoBios.cpp"),
            Object(NonMatching, "game/maximum/app/gimmick/gimmickBox.cpp"),
        ]
    },
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
