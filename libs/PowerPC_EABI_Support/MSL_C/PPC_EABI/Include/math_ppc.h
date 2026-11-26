#ifndef PPC_EABI_SRC_MATH_PPC_H
#define PPC_EABI_SRC_MATH_PPC_H

#include "float.h"
#include "fdlibm.h"

// TODO: where should this go?
#ifndef DECL_WEAK
#if defined(__MWERKS__)
#define DECL_WEAK __declspec(weak)
#elif defined(__GNUC__)
#define DECL_WEAK __attribute__((weak))
#elif defined(_MSC_VER)
#define DECL_WEAK
#else
#error unknown compiler
#endif
#endif

DECL_WEAK int __fpclassifyf(float x)
{
    switch ((*(int*)&x) & 0x7f800000)
    {
    case 0x7f800000:
        if ((*(int*)&x) & 0x007fffff)
            return 1;
        else
            return 2;
    case 0:
        if ((*(int*)&x) & 0x007fffff)
            return 5;
        else
            return 3;
    }
    return 4;
}

double nan(const char* arg) {}

DECL_WEAK float atan2f(float x, float y) {
    return atan2(x, y);
}

DECL_WEAK float atanf(float x) {
    return atan(x);
}

DECL_WEAK float asinf(float x) {
    return asin(x);
}

DECL_WEAK float acosf(float x) {
    return acos(x);
}

DECL_WEAK float cosf(float x) {
    return cos(x);
}

DECL_WEAK float sinf(float x) {
    return sin(x);
}

DECL_WEAK float tanf(float x) {
    return tan(x);
}

#ifdef DECOMPCTX
// Hack to mitigate fake mismatches when building from decompctx output
// (which doesn't support precompiled headers).
//
// When built without a PCH, these constants would end up .rodata instead of .data
// which causes a variety of knock-on effects in individual functions' assembly.
//
// Making them into globals is a bit of a hack, but it generally fixes later
// .data and .rodata offsets and allows individual functions to match.
static double _half = 0.5;
static double _three = 3.0;
#endif
DECL_WEAK float sqrtf(float mag) {
#ifndef DECOMPCTX
    // part of the same hack, these are defined outside of the function when using decompctx
    static const double _half = 0.5;
    static const double _three = 3.0;
#endif
    if (mag > 0.0f) {
        double dmag = (double)mag;
        double tmpd = __frsqrte(dmag);
        tmpd = _half * tmpd * (_three - tmpd * tmpd * dmag);
        tmpd = _half * tmpd * (_three - tmpd * tmpd * dmag);
        tmpd = _half * tmpd * (_three - tmpd * tmpd * dmag);
        return (float)(dmag * tmpd);
    } else if (mag < 0.0) {
        return NAN;
    } else if (isnan(mag)) {
        return NAN;
    } else {
        return mag;
    }
}

DECL_WEAK float fmodf(float f1, float f2) {
    return fmod(f1, f2);
}

DECL_WEAK float powf(float f1, float f2) {
    return pow(f1, f2);
}

DECL_WEAK double fabs(double f) {
    return __fabs(f);
}

DECL_WEAK float logf(float f) {
    return log(f);
}

DECL_WEAK float expf(float f) {
    return exp(f);
}

#endif /* PPC_EABI_SRC_MATH_PPC_H */
