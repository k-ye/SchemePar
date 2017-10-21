#include "gc.h"

#include <assert.h>
#include <stdlib.h>
#include <string.h>

int64_t* free_ptr = NULL;
int64_t* fromspace_begin = NULL;
int64_t* fromspace_end = NULL;
int64_t** rootstack_begin = NULL;

static int64_t* tospace_begin = NULL;
static int64_t* tospace_end = NULL;

///////////////////////////////////////////////////////////////

static uint64_t ROUNDUP_DW(uint64_t sz) {
    return (((sz + 7) / 8) * 8);
}

void initialize(uint64_t rootstack_size, uint64_t heap_size) {
    rootstack_size = ROUNDUP_DW(rootstack_size);
    heap_size = ROUNDUP_DW(heap_size);

    rootstack_begin = (int64_t**)malloc(rootstack_size);
    memset((void*)rootstack_begin, 0, rootstack_size);

    fromspace_begin = (int64_t*)malloc(heap_size);
    fromspace_end = (int64_t*)(((char*)fromspace_begin) + heap_size);
    memset((void*)fromspace_begin, 0, heap_size);

    tospace_begin = (int64_t*)malloc(heap_size);
    tospace_end = (int64_t*)(((char*)tospace_end) + heap_size);
    memset((void*)tospace_begin, 0, heap_size);
}

///////////////////////////////////////////////////////////////

const uint64_t TUPLE_POINTER_MASK = 0xfffffff0u;
const uint64_t TUPLE_LEN_MASK = 0x0eu;
const uint64_t TUPLE_IS_COPIED_MASK = 0x01u;

static unsigned int tuple_length(uint64_t tp_entry) {
    return ((tp_entry & TUPLE_LEN_MASK) >> 1);
}

static int tuple_is_copied(uint64_t tp_entry) {
    return ((tp_entry & TUPLE_IS_COPIED_MASK) == 0);
}

static void mark_tuple_is_copied(uint64_t* tp_entry) {
    uint64_t entry_copy = *tp_entry;
    *tp_entry = (entry_copy & (~TUPLE_IS_COPIED_MASK));
}

static void swap_ptr(int64_t** a, int64_t** b) {
    int64_t* tmp = *b;
    *b = *a;
    *a = tmp;
}

void collect(int64_t** rootstack_ptr, uint64_t bytes_needed) {
    // Remember that all the elements on |rootstack_ptr| are tuples.

    assert(rootstack_ptr >= rootstack_begin);
    // Find out all the alive tuples from the root stack. It is guaranteed that
    // registers will not hold any of tuples.
    while (rootstack_ptr > rootstack_begin) {
        --rootstack_ptr;
        if (*rootstack_ptr == NULL) {
            continue;
        }
        uint64_t tp_entry = (uint64_t)(*rootstack_ptr);
        assert(!tuple_is_copied(tp_entry));
        unsigned len = tuple_length(tp_entry);
    }
}