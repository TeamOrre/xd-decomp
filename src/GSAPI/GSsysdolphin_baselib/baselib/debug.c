#include "GSAPI/GSsysdolphin_baselib/baselib/debug.h"

#include <stdio.h>

#include <dolphin/os.h>

OSContext debug_context;

static ReportCallback reportCallback;
static PanicCallback panic_func;
static __io_proc logFunc;

#ifdef MUST_MATCH
#pragma peephole off
#endif

static int report_func(__file_handle arg0, unsigned char* arg1, size_t* arg2,
                       __idle_proc arg3)
{
    if (reportCallback != NULL) {
        reportCallback(arg1, *arg2);
    }
    logFunc(arg0, arg1, arg2, arg3);
    return 0;
}

void HSD_LogInit(void)
{
    if (logFunc == NULL) {
        logFunc = stdout->write_fn;
    }
    stdout->write_fn = report_func;
    stdout->file_state.error = 0;
}

void __assert(const char* str, u32 arg1, const char* arg2)
{
    OSReport("assertion \"%s\" failed", arg2);
    HSD_Panic(str, arg1, "");
}

void HSD_Panic(const char* arg0, u32 line, const char* arg2)
{
    if (panic_func != NULL) {
        OSSaveContext(&debug_context);
        OSReport("%s in %s on line %d.\n", arg2, arg0, line);
        panic_func(&debug_context);
    }
    OSPanic(arg0, line, arg2);
}

void HSD_SetReportCallback(ReportCallback cb)
{
    reportCallback = cb;
}

void HSD_SetPanicCallback(PanicCallback cb)
{
    panic_func = cb;
}

void HSD_SaveContext()
{

}
