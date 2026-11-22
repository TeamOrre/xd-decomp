#ifndef _MSL_COMMON_FLOAT_H
#define _MSL_COMMON_FLOAT_H

#include <fdlibm.h>
#include "global.h"

#define NAN (*(float*) __float_nan)
#define HUGE_VALF (*(float*) __float_huge)
#define HUGE_VAL (*(double*)__double_huge)

#define FP_SNAN 0
#define FP_QNAN 1
#define FP_INFINITE 2
#define FP_ZERO 3
#define FP_NORMAL 4
#define FP_SUBNORMAL 5

#define FP_NAN FP_QNAN

#define fpclassify(x) \
	((sizeof(x) == sizeof(float)) ? __fpclassifyf((float)(x)) : \
	__fpclassifyd((double)(x)) )

#define signbit(x) ((sizeof(x) == sizeof(float)) ? __signbitf(x) : __signbitd(x))
#define isfinite(x) ((fpclassify(x) > FP_INFINITE))
#define isnan(x) (fpclassify(x) == FP_NAN)
#define isinf(x) (fpclassify(x) == FP_INFINITE)

#define __signbitf(x) ((int)(__HI(x) & 0x80000000))

// TODO: OK?
#define __signbitd(x) ((int)(__HI(x) & 0x80000000))

extern int __float_nan[];
extern int __float_huge[];
extern int __double_huge[];
extern int __double_min[];
extern int __double_max[];
extern int __float_max[];
extern int __float_epsilon[];
extern int __extended_min[];
extern int __extended_max[];

#define FLT_MANT_DIG   24
#define FLT_DIG        6
#define FLT_MIN_EXP    (-125)
#define FLT_MIN_10_EXP (-37)
#define FLT_MAX_EXP    128
#define FLT_MAX_10_EXP 38

#define FLT_MAX (*(float*) __float_max)
#define FLT_EPSILON 1.1920928955078125e-07f

#define DBL_MANT_DIG   53
#define DBL_DIG        15
#define DBL_MIN_EXP    (-1021)
#define DBL_MIN_10_EXP (-308)
#define DBL_MAX_EXP    1024
#define DBL_MAX_10_EXP 308

#define DBL_MIN (*(double*)__double_min)
#define DBL_MAX (*(double*)__double_max)

#define LDBL_MANT_DIG 53
#define LDBL_DIG 15
#define LDBL_MIN_EXP (-1021)
#define LDBL_MIN_10_EXP (-308)
#define LDBL_MAX_EXP 1024
#define LDBL_MAX_10_EXP 308

#define LDBL_MAX (*(f128*)__extended_max)
#define LDBL_EPSILON 0x1.0000000000000P-52L
#define LDBL_MIN (*(f128*)__extended_min)

#endif /* _MSL_COMMON_FLOAT_H */
