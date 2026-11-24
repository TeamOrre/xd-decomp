#include "app/kaisuu/kaisuu.hpp"
#include "app/kaisuu/kaisuuBios.hpp"
#include <GSAPI/GSsysdolphin_baselib/baselib/random.h>

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
