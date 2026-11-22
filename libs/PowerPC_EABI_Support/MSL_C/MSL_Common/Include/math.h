#ifndef MSL_MATH_H_
#define MSL_MATH_H_

#include <float.h>
#include <arith.h>

#define M_PI 3.14159265358979323846f
#define M_SQRT3 1.73205f

#define DEG_TO_RAD(degrees) (degrees * (M_PI / 180.0f))
#define RAD_TO_DEG(radians) (radians * (180.0f / M_PI))

#ifdef __cplusplus
extern "C" {
#endif

extern double __frsqrte(double);
extern float __fres(float);
extern double __fabs(double);
extern float __fabsf(float);

int abs(int);
double acos(double);
float acosf(float);
double asin(double);
double atan(double);
double atan2(double, double);
double ceil(double);
double copysign(double, double);
double cos(double);
float cosf(float);
double exp(double);
double floor(double);
double fmod(double, double);
double frexp(double, int*);
double ldexp(double, int);
double modf(double, double*);
double pow(double, double);
float powf(float, float);
double sin(double);
float sinf(float);
double sqrt(double);
double tan(double);
float tanf(float);
double log10(double);

inline int __fpclassifyf(float __value) {
    switch (*(int*)&__value & 0x7f800000) {
    case 0x7f800000:
        if ((*(int*)&__value & 0x7fffff) != 0) {
            return FP_QNAN;
        }
        return FP_INFINITE;

    case 0:
        if ((*(int*)&__value & 0x7fffff) != 0) {
            return FP_SUBNORMAL;
        }
        return FP_ZERO;
    }

    return FP_NORMAL;
}

inline int __fpclassifyd(double __value) {
    switch (__HI(__value) & 0x7ff00000) {
	case 0x7ff00000: {
		if ((__HI(__value) & 0x000fffff) || (__LO(__value) & 0xffffffff))
			return FP_QNAN;
		else
			return FP_INFINITE;
		break;
	}
	case 0: {
		if ((__HI(__value) & 0x000fffff) || (__LO(__value) & 0xffffffff))
			return FP_SUBNORMAL;
		else
			return FP_ZERO;
		break;
	}
	}
	return FP_NORMAL;
}

inline double fabs(double f) {
    return __fabs(f);
}

inline long double fabsl(long double x) {
    return fabs((double)x);
}

MSL_INLINE float acosf(float x) {
    return acos(x);
}

MSL_INLINE float atan2f(float y, float x) {
    return (float)atan2(y, x);
}

MSL_INLINE float ceilf(float num) {
    return ceil(num);
}

MSL_INLINE float cosf(float x) {
    return cos(x);
}

MSL_INLINE float expf(float x) {
    return exp(x);
}

MSL_INLINE float floorf(float num) {
    return floor(num);
}

MSL_INLINE float powf(float x, float y) {
    return pow(x, y);
}

MSL_INLINE float sinf(float x) {
    return sin(x);
}

MSL_INLINE float fabsf(float f) {
    return (float)fabs((double)f);
}

MSL_INLINE float fmodf(float f1, float f2) {
    return fmod(f1, f2);
}

MSL_INLINE float log10f(float x) {
    return log10(x);
}

#include "global.h"

MSL_INLINE float tanf(float x) {
    return tan(x);
}

#ifdef __cplusplus
};
#endif

#endif
