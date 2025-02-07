
// Command to compile the code as a shared library:
// gcc -shared -o libballmotion.so -fPIC -g ball_motion.c -lm

extern "C" {
    void move_sinusoidal(double *x, double *y, double *vel_x, double *w, double *amp);
    void move_angled(double *x, double *y, double *vel_x, double *angle);
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