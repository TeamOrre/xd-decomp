#include "game/pxdvs/app/kaisuu/kaisuuBios.hpp"
#include "game/pxdvs/app/kaisuu/kaisuuData.h"

extern "C" s32 kaisuuBiosGetMax(u32 idx) {
    if (idx >= kaisuu_data_number) {
        return 0;
    }
    return kaisuu_data[idx].max;
}

extern "C" s32 kaisuuBiosGetMin(u32 idx) {
    if (idx >= kaisuu_data_number) {
        return 0;
    }
    return kaisuu_data[idx].min;
}
