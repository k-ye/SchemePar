#include "gc.h"

#include <assert.h>
#include <stdio.h>

void test_init_shutdown() {
  printf("Running test_init_shutdown...\n");
  initialize(120, 1023);
  printf("test_init_shutdown passed.\n\n");
}

void test_basic_gc() {
  printf("Running test_basic_gc...\n");
  initialize(64, 1024);

  // Allocate a 2-tuple on the FromSpace heap.
  const unsigned len = 2;
  int64_t* tuple1 = free_ptr;
  free_ptr += len + 1;
  const int64_t tag = ((len << 1) | 1);
  *tuple1 = tag;
  const int64_t e0 = 0xff5723, e1 = 0x04829ec;
  *(tuple1 + 1) = e0;
  *(tuple1 + 2) = e1;

  // Push this tuple pointer onto the root stack.
  int64_t** rootstack_ptr = rootstack_begin;
  *rootstack_ptr = tuple1;
  ++rootstack_ptr;

  collect(rootstack_ptr, /*unused*/ 1024);

  // Check
  tuple1 = fromspace_begin;
  // Is stack updated?
  assert(*(rootstack_ptr - 1) == tuple1);
  // Are the content of the tuple still valid?
  assert(*tuple1 == tag);
  assert(*(tuple1 + 1) == e0);
  assert(*(tuple1 + 2) == e1);
  // Did |free_ptr| get updated correctly?
  assert(tuple1 + 3 == free_ptr);

  printf("test_basic_gc passed.\n\n");
}

void test_many_tuples() {
  printf("Running test_many_tuples...\n");
  initialize(64, 1024);

  // Allocate several tuples on the FromSpace heap.
  // The 0-th element of |tuple1| is a pointer to |tuple3|.
  // The 1-th element of |tuple2| is a pointer to |tuple3|, too.
  // |tuple4| is not referenced by any alive tuples, it should be gone after GC.
  const unsigned len1 = 3, len2 = 2, len3 = 1, len4 = 3;
  int64_t* tuple1 = free_ptr;
  free_ptr += len1 + 1;

  int64_t* tuple2 = free_ptr;
  free_ptr += len2 + 1;

  int64_t* tuple3 = free_ptr;
  free_ptr += len3 + 1;

  int64_t* tuple4 = free_ptr;
  free_ptr += len4 + 1;

  const int64_t tag1 = ((1 << 7) | (len1 << 1) | 1);
  *tuple1 = tag1;
  const int64_t e1_1 = 0xfee982f5723, e1_2 = 0x04829ec002;
  *(tuple1 + 1) = (int64_t)tuple3;
  *(tuple1 + 2) = e1_1;
  *(tuple1 + 3) = e1_2;

  const int64_t tag2 = ((2 << 7) | (len2 << 1) | 1);
  *tuple2 = tag2;
  const int64_t e2_0 = 0x3538a0b9d;
  *(tuple2 + 1) = e2_0;
  *(tuple2 + 2) = (int64_t)tuple3;

  const int64_t tag3 = ((len3 << 1) | 1);
  *tuple3 = tag3;
  const int64_t e3_0 = 0x53fb00a267;
  *(tuple3 + 1) = e3_0;

  // nobody references |tuple4|
  const int64_t tag4 = ((7 << 7) | (len4 << 1) | 1);
  *tuple4 = tag4;  
  *(tuple4 + 1) = (int64_t)tuple1;
  *(tuple4 + 2) = (int64_t)tuple2;
  *(tuple4 + 3) = (int64_t)tuple3;

  // Push this tuple pointer onto the root stack.
  int64_t** rootstack_ptr = rootstack_begin;
  *rootstack_ptr = tuple1;
  ++rootstack_ptr;
  *rootstack_ptr = tuple2;
  ++rootstack_ptr;

  // GC
  collect(rootstack_ptr, /*unused*/ 1024);

  // Check

  // bad, this relies on implementation detail.
  tuple2 = fromspace_begin;
  tuple1 = tuple2 + len2 + 1;
  tuple3 = tuple1 + len1 + 1;
  // Did |free_ptr| get updated correctly?
  // Also, only |tuple1|, |tuple2| and |tuple3| should be preserved.
  assert((free_ptr - fromspace_begin) == len1 + 1 + len2 + 1 + len3 + 1);
  // Is stack updated?
  assert(*(rootstack_ptr - 1) == tuple2);
  assert(*(rootstack_ptr - 2) == tuple1);
  // Are the content of the tuples still valid?
  assert(*tuple1 == tag1);
  assert(*(tuple1 + 1) == (int64_t)tuple3);
  assert(*(tuple1 + 2) == e1_1);
  assert(*(tuple1 + 3) == e1_2);

  assert(*tuple2 == tag2);
  assert(*(tuple2 + 1) == e2_0);
  assert(*(tuple2 + 2) == (int64_t)tuple3);

  assert(*tuple3 == tag3);
  assert(*(tuple3 + 1) == e3_0);

  printf("test_many_tuples passed.\n\n");
}

int main() {
  test_init_shutdown();
  test_basic_gc();
  test_many_tuples();
  return 0;
}