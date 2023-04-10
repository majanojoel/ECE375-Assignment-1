#include "test.h"

#include "wut.h"

void test(void) {
    wut_init();
    shared_memory[0] = wut_id();
}

void check(void) {
    expect(
        shared_memory[0], 0, "wut_id of the main thread is wrong"
    );
}
