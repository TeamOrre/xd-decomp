#include <locale>
#include <ctype.h>
#include <wctype_api.h>
#include <mbstring.h>

#pragma options align=native
#pragma warn_padding off

struct lconv __lconv = {
    ".",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    0x7F,
    0x7F,
    0x7F,
    0x7F,
    0x7F,
    0x7F,
    0x7F,
    "",
    0x7F,
    0x7F,
    0x7F,
    0x7F,
    0x7F,
    0x7F,
    0x7F
};
#pragma warn_padding reset
#pragma options align=reset

const char* dummy = "C";
