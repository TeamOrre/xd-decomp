#ifndef _MSL_COMMON_CTYPE_H
#define _MSL_COMMON_CTYPE_H

#include "global.h"

#ifdef __cplusplus
extern "C" {
#endif

#define EOF -1L

extern unsigned char __ctype_map[];
extern unsigned char __lower_map[];
extern unsigned char __upper_map[];

#define __control_char 0x01
#define __motion_char 0x02
#define __space_char 0x04
#define __punctuation 0x08
#define __digit 0x10
#define __hex_digit 0x20
#define __lower_case 0x40
#define __upper_case 0x80

#define __letter (__lower_case | __upper_case)
#define __alphanumeric (__letter | __digit)
#define __graphic (__alphanumeric | __punctuation)
#define __printable (__graphic | __space_char)
#define __whitespace (__motion_char | __space_char)
#define __control (__motion_char | __control_char)
#define __zero_fill(c) ((int)(unsigned char)(c))

int isalpha(int c);
int isdigit(int c);
int isupper(int c);
int isxdigit(int c);
int isspace(int c);
int tolower(int c);
int toupper(int c);

MSL_INLINE int isalpha(int c) {
    return (int)(__ctype_map[(unsigned char)c] & __letter);
}

MSL_INLINE int isdigit(int c) {
    return (int)(__ctype_map[(unsigned char)c] & __digit);
}

MSL_INLINE int isupper(int c) {
    return (int)(__ctype_map[(unsigned char)c] & __upper_case);
}

MSL_INLINE int isxdigit(int c) {
    return (int)(__ctype_map[(unsigned char)c] & __hex_digit);
}

MSL_INLINE int isspace(int c) {
    return (int)(__ctype_map[(unsigned char)c] & __whitespace);
}

MSL_INLINE int _tolower(int c) {
    return (c == -1) ? -1 : (int) (__lower_map[(unsigned char)c]);
}

MSL_INLINE int toupper(int c) {
    return (c == -1 ? -1 : (int)__upper_map[(unsigned char)c]);
}

#ifdef __cplusplus
}
#endif

#endif /* _MSL_COMMON_CTYPE_H */
