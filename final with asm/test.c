#include <stdio.h>
#include <dlfcn.h>

void move_parabolic(double *x, double *y, double *vel_x, double *vel_y, double *gravity);

int main() {
    void *handle = dlopen("./libballmotion.so", RTLD_LAZY);
    if (!handle) {
        fprintf(stderr, "%s\n", dlerror());
        return 1;
    }
    dlerror();

    void (*move_parabolic)(double*, double*, double*, double*, double*) = dlsym(handle, "move_parabolic");
    char *error;
    if ((error = dlerror()) != NULL)  {
        fprintf(stderr, "%s\n", error);
        return 1;
    }

    double x = 0.0, y = 0.0, vel_x = 1.0, vel_y = 2.0, gravity = 9.8;
    move_parabolic(&x, &y, &vel_x, &vel_y, &gravity);
    printf("x: %f, y: %f, vel_x: %f, vel_y: %f\n", x, y, vel_x, vel_y);

    dlclose(handle);
    return 0;
}
