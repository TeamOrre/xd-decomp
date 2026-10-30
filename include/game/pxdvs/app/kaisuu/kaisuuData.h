#ifndef KAISUU_DATA_H
#define KAISUU_DATA_H

#include <global.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    s32 min;
    s32 max;
} KaisuuData;

extern KaisuuData kaisuu_data[];
extern u32 kaisuu_data_number;


#ifdef __cplusplus
}
#endif

#endif
