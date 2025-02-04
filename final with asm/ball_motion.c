#include <math.h>

// Command to compile the code as a shared library:
// gcc -shared -o libballmotion.so -fPIC -g ball_motion.c -lm

// Function to move a ball in a parabolic path
void move_parabolic(double *x, double *y, double *vel_x, double *vel_y, double *gravity) {
    asm volatile (
        // Load the current x position onto the FPU stack
        "fldl %[x];"
        // Add the horizontal velocity (vel_x) to the x position
        "faddl %[vel_x];"
        // Store the result back into the memory location of x
        "fstpl %[x];"
        // Load the current vertical velocity (vel_y) onto the FPU stack
        "fldl %[vel_y];"
        // Subtract the value of gravity * 0.1 from the vertical velocity (simulates gravity's effect)
        "fsubl %[gravity];"
        // Store the updated vertical velocity back into the memory location of vel_y
        "fstpl %[vel_y];"
        // Load the current y position onto the FPU stack
        "fldl %[y];"
        // Subtract the current vertical velocity from the y position (simulates upward movement)
        "fsubl %[vel_y];"
        // Store the updated y position back into the memory location of y
        "fstpl %[y];"
        : [x] "+m" (*x), [y] "+m" (*y), [vel_x] "+m" (*vel_x), [vel_y] "+m" (*vel_y)  // Output operands: update the values at memory locations of x, y, vel_x, and vel_y
        : [gravity] "m" (*gravity)  // Input operands: pass values of gravity
        : "st", "st(1)", "st(2)", "st(3)", "st(4)", "st(5)", "st(6)", "st(7)"  // Clobbers: indicate that the FPU stack is modified
    );
}

void move_sinusoidal(double *x, double *y, double *vel_x, double *w, double *amp){
    asm volatile (
        // Load the current x position onto the FPU stack
        "fldl %[x];"
        // Add the horizontal velocity (vel_x) to the x position
        "faddl %[vel_x];"
        // Store the result back into the memory location of x
        "fstpl %[x];"

        // Load the current y position onto the FPU stack
        "fldl %[y];"
        // Load the angular frequency (w) onto the FPU stack
        "fldl %[w];"
        // Load the current x position onto the FPU stack
        "fldl %[x];"
        // Multiply x by w (x * w)
        "fmulp %%st(1), %%st(0);"
        // Compute sin(x * w)
        "fsin;"
        // Multiply sin(x * w) by amplitude
        "fldl %[amp];"
        "fmulp %%st(1), %%st(0);"
        // Add the result to the y position
        "faddp %%st(1), %%st(0);"
        // Store the updated y position back into the memory location of y
        "fstpl %[y];"

        : [x] "+m" (*x), [y] "+m" (*y)  // Output operands: update the values at memory locations of x and y
        : [vel_x] "m" (*vel_x), [w] "m" (*w), [amp] "m" (*amp)  // Input operands: pass values of vel_x, w, and amplitude
        : "st", "st(1)", "st(2)", "st(3)", "st(4)", "st(5)", "st(6)", "st(7)"  // Clobbers: indicate that the FPU stack is modified
    );
}

void move_angled(double *x, double *y, double *vel_x, double *angle) {
    asm volatile (
        // Load the current x position onto the FPU stack
        "fldl %[x];"
        // Add the horizontal velocity (vel_x) to the x position
        "faddl %[vel_x];"
        // Store the result back into the memory location of x
        "fstpl %[x];"

        // Load the current y position onto the FPU stack
        "fldl %[y];"
        // Load the horizontal velocity (vel_x) onto the FPU stack
        "fldl %[vel_x];"
        // Load the angle onto the FPU stack
        "fldl %[angle];"
        // Compute the tangent of the angle (pushes tan(angle) and 1.0 onto the stack)
        "fptan;"
        // Pop the 1.0 from the stack (discard it)
        "fstp %%st(0);"
        // Multiply the tangent by the horizontal velocity (vel_x)
        "fmulp %%st(1), %%st(0);"
        // Subtract the result from the y position (y -= vel_x * tan(angle))
        // Use fsubp to subtract st(0) from st(1) and pop the stack
        "fsubrp %%st(0), %%st(1);"
        // Store the updated y position back into the memory location of y
        "fstpl %[y];"

        : [x] "+m" (*x), [y] "+m" (*y)  // Output operands: update the values at memory locations of x and y
        : [vel_x] "m" (*vel_x), [angle] "m" (*angle)  // Input operands: pass values of vel_x and angle
        : "st", "st(1)", "st(2)", "st(3)", "st(4)", "st(5)", "st(6)", "st(7)"  // Clobbers: indicate that the FPU stack is modified
    );
}