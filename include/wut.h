#ifndef WUT_H
#define WUT_H

void wut_init();
int wut_create(void (*run)(void));
int wut_id();
int wut_yield();
int wut_cancel(int id);
int wut_join(int id);
void wut_exit(int status);

#endif
