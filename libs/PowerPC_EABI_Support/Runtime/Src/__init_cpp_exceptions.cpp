#include "__ppc_eabi_linker.h"

#if __MWERKS__
#pragma exceptions off
#pragma internal on
#endif

#ifdef __cplusplus
extern "C" {
#endif

extern void __init_cpp_exceptions(void);
extern void __fini_cpp_exceptions(void);

extern void __destroy_global_chain(void);
extern void __unregister_fragment(int);
extern int __register_fragment(struct __eti_init_info* info, char* TOC);

#ifdef __cplusplus
}
#endif

static int fragmentID = -2;

extern void GetR2(char** R2) {
	register char* temp;
	asm {
		mr temp, r2
	}
	*R2 = temp;
}

void __init_cpp_exceptions(void) {
    char* R2;

    if (fragmentID == -2) {
        GetR2(&R2);
        fragmentID = __register_fragment(_eti_init_info, R2);
    }
}

void __fini_cpp_exceptions(void) {
    char* R2;
    if (fragmentID != -2) {
        __unregister_fragment(fragmentID);
        fragmentID = -2;
    }
}

__declspec(section ".ctors") extern void* const __init_cpp_exceptions_reference = __init_cpp_exceptions;

__declspec(section ".dtors") extern void* const __fini_cpp_exceptions_reference = __fini_cpp_exceptions;
