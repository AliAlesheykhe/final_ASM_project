#include <immintrin.h>
#include <cstdlib>  // for _mm_malloc and _mm_free

extern "C" {
    void compute_sin(double* result);
    void compute_tan(double* result);
    void move_parabolic(double *x, double *y, double *vel_x, double *vel_y, double *gravity);
    void move_sinusoidal(double *x, double *y, double *vel_x, double *w, double *amp);
    void move_angled(double *x, double *y, double *vel_x, double *angle);
}

// Ensure proper alignment for SIMD operations
alignas(32) double x[4], y[4], vel_x[4], vel_y[4], temp[4];

// Scalar functions for sine and tangent
void compute_sin(double* result) {
    asm volatile (
        "fldl (%0)\n\t"
        "fsin\n\t"
        "fstpl (%0)\n\t"
        :
        : "r" (result)
        : "st"
    );
}

void compute_tan(double* result) {
    asm volatile (
        "fldl (%0)\n\t"
        "fptan\n\t"
        "fstp %%st(0)\n\t"
        "fstpl (%0)\n\t"
        :
        : "r" (result)
        : "st"
    );
}

// Function to move a ball in a parabolic path
void move_parabolic(double *x, double *y, double *vel_x, double *vel_y, double *gravity) {
    double gravity_scaled = *gravity * 0.1;
    asm volatile (
        "vbroadcastsd %[gravity_scaled], %%ymm4\n\t"  // Broadcast gravity into all elements of ymm4
        
        "vmovupd (%[x]), %%ymm0\n\t"                  // Load x into ymm0
        "vmovupd (%[vel_x]), %%ymm1\n\t"              // Load vel_x into ymm1
        "vmovupd (%[y]), %%ymm2\n\t"                  // Load y into ymm2
        "vmovupd (%[vel_y]), %%ymm3\n\t"              // Load vel_y into ymm3

        "vaddpd %%ymm1, %%ymm0, %%ymm0\n\t"           // x = x + vel_x
        "vsubpd %%ymm4, %%ymm3, %%ymm3\n\t"           // vel_y = vel_y - gravity
        "vsubpd %%ymm3, %%ymm2, %%ymm2\n\t"           // y = y - vel_y

        "vmovupd %%ymm0, (%[x])\n\t"                  // Store x
        "vmovupd %%ymm2, (%[y])\n\t"                  // Store y
        "vmovupd %%ymm3, (%[vel_y])\n\t"              // Store vel_y
        
        : 
        : [x] "r" (x), [y] "r" (y), [vel_x] "r" (vel_x), [vel_y] "r" (vel_y), [gravity_scaled] "m" (gravity_scaled)
        : "ymm0", "ymm1", "ymm2", "ymm3", "ymm4"
    );
}

// Function to move a ball in a sinusoidal path
void move_sinusoidal(double *x, double *y, double *vel_x, double *w, double *amp) {
    alignas(32) double temp[4];
    
    asm volatile (
        "vmovupd (%[x]), %%ymm0\n\t"                  // Load x into ymm0
        "vmovupd (%[vel_x]), %%ymm1\n\t"              // Load vel_x into ymm1
        "vmovupd (%[y]), %%ymm2\n\t"                  // Load y into ymm2
        "vbroadcastsd %[w], %%ymm3\n\t"               // Broadcast w into all elements of ymm3
        "vbroadcastsd %[amp], %%ymm4\n\t"             // Broadcast amp into all elements of ymm4
        
        "vaddpd %%ymm1, %%ymm0, %%ymm0\n\t"           // x = x + vel_x
        "vmovupd %%ymm0, (%[x])\n\t"                  // Store x

        "vmulpd %%ymm3, %%ymm0, %%ymm0\n\t"           // w * x
        "vmovupd %%ymm0, %[temp]\n\t"                 // Store result temporarily

        : [temp] "=m" (temp)
        : [x] "r" (x), [y] "r" (y), [vel_x] "r" (vel_x), [w] "m" (*w), [amp] "m" (*amp)
        : "ymm0", "ymm1", "ymm2", "ymm3", "ymm4"
    );

    
    compute_sin(&temp[0]);   // Scalar sine computation
    
    
    asm volatile (
        "vmovupd %[temp], %%ymm0\n\t"                 // Load sine results into ymm0
        "vmulpd %%ymm4, %%ymm0, %%ymm0\n\t"           // amp * sin(w * x)
        "vaddpd %%ymm0, %%ymm2, %%ymm2\n\t"           // y = y + amp * sin(w * x)

        "vmovupd %%ymm2, (%[y])\n\t"                  // Store y
        
        : 
        : [x] "r" (x), [y] "r" (y), [temp] "m" (temp)
        : "ymm0", "ymm2", "ymm4"
    );
}

// Function to move a ball at an angle
void move_angled(double *x, double *y, double *vel_x, double *angle) {
    alignas(32) double temp[4];

    asm volatile (
        "vmovupd (%[x]), %%ymm0\n\t"                  // Load x into ymm0
        "vmovupd (%[vel_x]), %%ymm1\n\t"              // Load vel_x into ymm1
        "vmovupd (%[y]), %%ymm2\n\t"                  // Load y into ymm2
        "vbroadcastsd %[angle], %%ymm3\n\t"           // Broadcast angle into all elements of ymm3

        "vaddpd %%ymm1, %%ymm0, %%ymm0\n\t"           // x = x + vel_x
        "vmovupd %%ymm3, %[temp]\n\t"                 // Store angle temporarily

        : [temp] "=m" (temp)
        : [x] "r" (x), [y] "r" (y), [vel_x] "r" (vel_x), [angle] "m" (*angle)
        : "ymm0", "ymm1", "ymm2", "ymm3"
    );

    
    compute_tan(&temp[0]);   // Scalar tangent computation
    
    
    asm volatile (
        "vmovupd %[temp], %%ymm3\n\t"                 // Load tangent results into ymm3
        "vmulpd %%ymm3, %%ymm1, %%ymm1\n\t"           // vel_x * tan(angle)
        "vsubpd %%ymm1, %%ymm2, %%ymm2\n\t"           // y = y - vel_x * tan(angle)

        "vmovupd %%ymm0, (%[x])\n\t"                  // Store x
        "vmovupd %%ymm2, (%[y])\n\t"                  // Store y
        
        : 
        : [x] "r" (x), [y] "r" (y), [temp] "m" (temp)
        : "ymm0", "ymm1", "ymm2", "ymm3"
    );
}

