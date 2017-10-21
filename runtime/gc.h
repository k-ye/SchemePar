#include <stdint.h>

extern int64_t* free_ptr;
extern int64_t* fromspace_begin;
extern int64_t* fromspace_end;
extern int64_t** rootstack_begin;

void initialize(uint64_t rootstack_size, uint64_t heap_size);

void collect(int64_t** rootstack_ptr, uint64_t bytes_needed);
