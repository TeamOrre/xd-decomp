#ifndef _UTIL_H_
#define _UTIL_H_

#include <GSAPI/GSsysdolphin_baselib/platform.h>

#include <stdlib.h>

#include <dolphin/gx.h>
#include <dolphin/mtx.h>
#include <GSAPI/GSsysdolphin_baselib/baselib/mtx.h>

/// functions
void HSD_MulColor(GXColor* arg0, GXColor* arg1, GXColor* dest);
u32 HSD_GetNbBits(u32 arg0);
s32 HSD_Index2PosNrmMtx(u32 arg0);

/// variables
extern Mtx HSD_identityMtx;

#define DEG_TO_RAD_CALC 0.017453292519943295
#define RAD_TO_DEG_CALC 57.29577951308232

static inline int vec_normalize_check(Vec3* src, Vec3* dst)
{
    if (!src || !dst) {
        return -1;
    }
    if (fabs(src->x) <= FLT_MIN && fabs(src->y) <= FLT_MIN &&
        fabs(src->z) <= FLT_MIN)
    {
        return -1;
    }
    PSVECNormalize(src, dst);
    return 0;
}

static inline f32 atan2f_check(s8 y, s8 x)
{
    if (abs(x) == 0.0) {
        return y >= 0 ? 1.5707963267948966 : -1.5707963267948966;
    } else {
        return atan2f(y, x);
    }
}

#endif // _UTIL_H_
