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

static uint64_t ROUNDUP_DW(uint64_t sz) { return (((sz + 7) / 8) * 8); }

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

const int64_t TUPLE_POINTER_MASK = 0xffffff80;
const int64_t TUPLE_LEN_MASK = 0x7e;
const int64_t TUPLE_IS_COPIED_MASK = 0x01;
const int64_t TUPLE_FWD_ADDR_MASK = 0xfffffff8;

// A Tuple is a chunk of continuous memory where each element is 8-byte long.
// To make tuple GC-able, an additional 8-byte tag is prepended to this memory.
// Therefore, a tuple of size N consumes (N + 1) * 8 bytes. The length of a 
// tuple is limited to 50.
//
// The tag is divided into three segments:
// |          63 .. 7          |      6 .. 1      |     0      |
//  \_____ pointer masks _____/ \____ length ____/ \_ copied _/
//
// 
// Bit 63 .. 7: Bit (7 + k) corresponds to the k-th element in the tuple, where
//      0 <= k < 50 (the max tuple length is 50). Each bit indicates whether
//      the element is a tuple pointer (1) or a basic int/bool (0). During GC,
//      we can ignore the int/bools after copying the tuple, but need to
//      recursively handle the tuple pointers.
// Bit 6 .. 1: Stores the length of the tuple.
// Bit 0: Indicates whether this tuple is already copied to ToSpace. If it has
//      not yet, this bit is 1, otherwise it is 0. In the latter case, the
//      entire tag in the *FromSpace* is actually a pointer that points to the
//      copied tuple in ToSpace. (The tag of this copied tuple in ToSpace is
//      still a tag.)

static int64_t get_tuple_pointer_mask(int64_t tag) {
  return ((tag & TUPLE_POINTER_MASK) >> 7);
}

static unsigned int get_tuple_length(int64_t tag) {
  return ((tag & TUPLE_LEN_MASK) >> 1);
}

static int tuple_is_copied(int64_t tag) {
  return ((tag & TUPLE_IS_COPIED_MASK) == 0);
}

static void mark_tuple_as_copied(int64_t* old_addr, int64_t* new_addr) {
  int64_t new_addri = (int64_t)(new_addr);
  assert((new_addri & (~TUPLE_FWD_ADDR_MASK)) == 0);
  *old_addr = new_addri;
}

static int64_t* get_tuple_forward_addr(int64_t tag) {
  assert(tuple_is_copied(tag));
  return (int64_t*)(tag & TUPLE_FWD_ADDR_MASK);
}

static void swap_ptr(int64_t** a, int64_t** b) {
  int64_t* tmp = *b;
  *b = *a;
  *a = tmp;
}

// Returns:
//  0: The tuple is copied to ToSpace successfully.
//  1: The tuple is already in ToSpace.
//  -1: An error, |*old_addr_ptr| points to NULL.
static int maybe_copy_tuple_to_tospace(int64_t** old_addr_ptr,
                                       int64_t** next_free_ptr,
                                       int allow_null) {
  // When GC starts from the rootstack, |allow_null| = 1. Otherwise it should
  // always be 0.
  assert(old_addr_ptr != NULL);
  int64_t* old_addr = (*old_addr_ptr);
  if (old_addr == NULL) {
    if (allow_null) {
      return -1;
    }
    abort();
  }

  int64_t tag = *old_addr;
  int64_t* new_addr = NULL;
  int ret_code = 0;
  if (tuple_is_copied(tag)) {
    // If tuple pointed by |old_addr| is already copied to the new address,
    // |tag| is actually the forward pointer.
    new_addr = get_tuple_forward_addr(tag);
    ret_code = 1;
  } else {
    // Allocate memory in ToSpace
    new_addr = *next_free_ptr;

    unsigned len = get_tuple_length(tag);
    unsigned dwords_needed = len + 1;  // #elements + tag
    unsigned bytes_needed = (dwords_needed << 3);
    // Copy all the data from FromSpace to ToSpace
    memmove((void*)new_addr, (const void*)old_addr, bytes_needed);

    // Update the free pointer
    *next_free_ptr += dwords_needed;
    assert(((uint64_t)(*next_free_ptr) - (uint64_t)(new_addr)) == bytes_needed);

    // Update the tag of the tuple in the *FromSpace*, so that it stores a
    // forward pointer. This must happen *after* the original content is copied
    // to ToSpace, because the tag in the new tuple needs to be preserved.
    mark_tuple_as_copied(old_addr, new_addr);
    ret_code = 0;
  }

  *old_addr_ptr = new_addr;
  return 0;
}

void collect(int64_t** rootstack_ptr, uint64_t bytes_needed) {
  // Remember that all the elements on |rootstack_ptr| are tuples.
  assert(rootstack_ptr >= rootstack_begin);

  int64_t* queue_head = tospace_begin;
  int64_t* queue_tail = tospace_begin;
  // Find out all the alive tuples from the root stack. It is guaranteed that
  // registers will not hold any of tuples.
  while (rootstack_ptr > rootstack_begin) {
    --rootstack_ptr;
    if (*rootstack_ptr == NULL) {
      continue;
    }
    maybe_copy_tuple_to_tospace(rootstack_ptr, &queue_tail, /*allow_null=*/1);
  }
  // BFS
  while (queue_head != queue_tail) {
    int64_t tag = *queue_head;
    unsigned len = get_tuple_length(tag);
    int64_t pointer_mask = get_tuple_pointer_mask(tag);
    for (unsigned i = 0; i < len; ++i) {
      if ((pointer_mask >> i) & 1) {
        // this is also a tuple
        int64_t** tuple_ptr = (int64_t**)(queue_head + i + 1);
        maybe_copy_tuple_to_tospace(tuple_ptr, &queue_tail, /*allow_null=*/0);
      }
    }
    queue_head += (len + 1);
  }

  free_ptr = queue_tail;
  swap_ptr(&fromspace_begin, &tospace_begin);
  swap_ptr(&fromspace_end, &tospace_end);
}