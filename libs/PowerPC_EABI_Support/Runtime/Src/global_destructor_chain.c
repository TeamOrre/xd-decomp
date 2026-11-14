#include "NMWException.h"
#include "MWCPlusLib.h"

DestructorChain* __global_destructor_chain;

void __destroy_global_chain(void) {
    DestructorChain* iter;
    while ((iter = __global_destructor_chain) != 0) {
        __global_destructor_chain = iter->next;
        DTORCALL_COMPLETE(iter->destructor, iter->object);
    }
}
