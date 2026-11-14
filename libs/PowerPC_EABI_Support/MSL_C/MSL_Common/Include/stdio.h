#ifndef MSL_STDIO_H_
#define MSL_STDIO_H_

#include <char_io.h>
#include <file_io.h>
#include <printf.h>
#include <extras.h>
#include <scanf.h>
#include <stdarg.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

#define stdin (&__files._stdin)
#define stdout (&__files._stdout)
#define stderr (&__files._stderr)

#ifdef __cplusplus
};
#endif

#endif
