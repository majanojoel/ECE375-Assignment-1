#include "test.h"

#include "wut.h"

int x = 0; 

void null_run(){
    return;
}

void t1_run() {
    shared_memory[4] = wut_cancel(0); // 0 is sent to cancelled, 2 no longer has anything joined
    shared_memory[5] = wut_join(0); // get status of cancelled 0 == 128
    shared_memory[6] = wut_join(2); // join succeeds and returns 0
    ++x; 
    shared_memory[8] = x; // should equal 2
}

void t2_run() {
    ++x;
    shared_memory[7] = x; // should equal 1
    int id4 = wut_create(null_run); // queue = {2, 0}
    shared_memory[9] = id4; //should equal 0 (reuses id 0)
}

void test(void) {
    wut_init();
    shared_memory[0] = wut_id(); // should equal 0
    shared_memory[1] = wut_create(t1_run); // should equal 1
    shared_memory[2] = wut_create(t2_run); // should equal 2, queue = {0, 1, 2}
    int id2 = shared_memory[2];
    shared_memory[3] = wut_join(id2); // queue = {2}
}

void check(void) {
    expect(
        shared_memory[0], 0, "wut_id of the main thread is wrong"
    );
    expect(
        shared_memory[1], 1, "wut_id of the second thread is wrong"
    );
    expect(
        shared_memory[2], 2, "wut_id of the third thread is wrong"
    );
    expect(
        shared_memory[3], TEST_MAGIC, "wut_join should never return because id 0 is cancelled"
    );
    expect(
        shared_memory[4], 0, "second wut_join should return 0"
    );
    expect(
        shared_memory[5], 128, "third wut_join should return the status of cancelled thread"
    );
    expect(
        shared_memory[6], 0, "fourth wut_join should should return 0"
    );
    expect(
        shared_memory[7], 1, "x should increment by 1"
    );
    expect(
        shared_memory[8], 2, "x should increment again"
    );
    expect(
        shared_memory[9], 0, "new thread should reuse id 0"
    );
}
