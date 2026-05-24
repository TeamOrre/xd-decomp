#include "game/pxdvs/app/kaisuu/kaisuu.hpp"
#include "game/pxdvs/app/kaisuu/kaisuuBios.hpp"
#include "game/maximum/GSAPI/baselib/random.h"

extern "C" s32 kaisuuGetKaisuu(u32 idx) {
    s32 maxVal = kaisuuBiosGetMax(idx);
    s32 minVal = kaisuuBiosGetMin(idx);

    if (maxVal == minVal) {
        return minVal;
    }

    s32 delta = maxVal - minVal + 1;
    s32 pickedVal = HSD_Rand() % delta;

    return minVal + pickedVal;
}
