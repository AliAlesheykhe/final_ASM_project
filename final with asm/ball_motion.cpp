#include <immintrin.h>
#include <cstdlib>  // for _mm_malloc and _mm_free
#include <stdint.h> // for uint32_t

extern "C" {
    void compute_sin(double* result);
    void compute_tan(double* result);
    void move_parabolic(double *x, double *y, double *vel_x, double *vel_y, double *gravity);
    void move_sinusoidal(double *x, double *y, double *vel_x, double *w, double *amp);
    void move_angled(double *x, double *y, double *vel_x, double *angle);
    void draw_ball(uint8_t* win_surface, int ball_x, int ball_y, int radius, uint32_t color);
    int check_collision(int ball_x, int ball_y, int player_x, int player_y, int player_w, int player_h);
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

// Function to draw a ball
// Function to draw a ball
void draw_ball(uint8_t* win_surface, int ball_x, int ball_y, int radius, uint32_t color) {
    int width = 1000;  // Width of the screen (replace with actual width if dynamic)
    int height = 600;  // Height of the screen (replace with actual height if dynamic)

    // Extract RGB components from the color
    uint8_t red = (color >> 16) & 0xFF;
    uint8_t green = (color >> 8) & 0xFF;
    uint8_t blue = color & 0xFF;

    // Loop through the bounding box of the circle
    for (int y = -radius; y <= radius; y++) {
        for (int x = -radius; x <= radius; x++) {
            // Check if the pixel is within the circle
            if (x * x + y * y <= radius * radius) {
                int px = ball_x + x;
                int py = ball_y + y;

                // Check if the pixel is within the screen bounds
                if (px >= 0 && px < width && py >= 0 && py < height) {
                    // Calculate the pixel index in the screen surface
                    uint8_t* pixel_addr = win_surface + (py * width + px) * 4;  // 4 bytes per pixel (RGBA)

                    // Set the pixel color using inline assembly
                    asm volatile (
                        "movb %[red], (%[addr])\n\t"    // Set red component
                        "movb %[green], 1(%[addr])\n\t" // Set green component
                        "movb %[blue], 2(%[addr])\n\t"  // Set blue component
                        "movb $0xFF, 3(%[addr])\n\t"    // Set alpha component (fully opaque)
                        :
                        : [addr] "r" (pixel_addr), [red] "r" (red), [green] "r" (green), [blue] "r" (blue)
                        : "memory"
                    );
                }
            }
        }
    }
}
