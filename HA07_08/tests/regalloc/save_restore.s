	.globl main
main:
    pushq %rbp
    movq %rsp, %rbp
    subq $160, %rsp
    movq %r8, -88(%rbp)
    movq %rdx, -96(%rbp)
    movq %rcx, -104(%rbp)
    movq %r10, -112(%rbp)
    movq %rsi, -120(%rbp)
    movq %r11, -128(%rbp)
    movq %r9, -136(%rbp)
    callq read_int
    movq -88(%rbp), %r8
    movq -96(%rbp), %rdx
    movq -104(%rbp), %rcx
    movq -112(%rbp), %r10
    movq -120(%rbp), %rsi
    movq -128(%rbp), %r11
    movq -136(%rbp), %r9
    movq %rax, %rsi
    movq %r8, -88(%rbp)
    movq %rdx, -96(%rbp)
    movq %rcx, -104(%rbp)
    movq %r10, -112(%rbp)
    movq %rsi, -120(%rbp)
    movq %r11, -128(%rbp)
    movq %r9, -136(%rbp)
    callq read_int
    movq -88(%rbp), %r8
    movq -96(%rbp), %rdx
    movq -104(%rbp), %rcx
    movq -112(%rbp), %r10
    movq -120(%rbp), %rsi
    movq -128(%rbp), %r11
    movq -136(%rbp), %r9
    movq %rax, %r8
    movq %rsi, %rcx
    addq %r8, %rcx
    movq %rcx, %rdx
    movq %rsi, %rcx
    subq %r8, %rcx
    movq %rdx, %rdi
    movq %r8, -88(%rbp)
    movq %rdx, -96(%rbp)
    movq %rcx, -104(%rbp)
    movq %r10, -112(%rbp)
    movq %rsi, -120(%rbp)
    movq %r11, -128(%rbp)
    movq %r9, -136(%rbp)
    callq print_int
    movq -88(%rbp), %r8
    movq -96(%rbp), %rdx
    movq -104(%rbp), %rcx
    movq -112(%rbp), %r10
    movq -120(%rbp), %rsi
    movq -128(%rbp), %r11
    movq -136(%rbp), %r9
    movq %rcx, %rdi
    movq %r8, -88(%rbp)
    movq %rdx, -96(%rbp)
    movq %rcx, -104(%rbp)
    movq %r10, -112(%rbp)
    movq %rsi, -120(%rbp)
    movq %r11, -128(%rbp)
    movq %r9, -136(%rbp)
    callq print_int
    movq -88(%rbp), %r8
    movq -96(%rbp), %rdx
    movq -104(%rbp), %rcx
    movq -112(%rbp), %r10
    movq -120(%rbp), %rsi
    movq -128(%rbp), %r11
    movq -136(%rbp), %r9
    movq %rsi, %rdi
    movq %r8, -88(%rbp)
    movq %rdx, -96(%rbp)
    movq %rcx, -104(%rbp)
    movq %r10, -112(%rbp)
    movq %rsi, -120(%rbp)
    movq %r11, -128(%rbp)
    movq %r9, -136(%rbp)
    callq print_int
    movq -88(%rbp), %r8
    movq -96(%rbp), %rdx
    movq -104(%rbp), %rcx
    movq -112(%rbp), %r10
    movq -120(%rbp), %rsi
    movq -128(%rbp), %r11
    movq -136(%rbp), %r9
    movq %r8, %rdi
    movq %r8, -88(%rbp)
    movq %rdx, -96(%rbp)
    movq %rcx, -104(%rbp)
    movq %r10, -112(%rbp)
    movq %rsi, -120(%rbp)
    movq %r11, -128(%rbp)
    movq %r9, -136(%rbp)
    callq print_int
    movq -88(%rbp), %r8
    movq -96(%rbp), %rdx
    movq -104(%rbp), %rcx
    movq -112(%rbp), %r10
    movq -120(%rbp), %rsi
    movq -128(%rbp), %r11
    movq -136(%rbp), %r9
    movq %rdx, %rdi
    movq %r8, -88(%rbp)
    movq %rdx, -96(%rbp)
    movq %rcx, -104(%rbp)
    movq %r10, -112(%rbp)
    movq %rsi, -120(%rbp)
    movq %r11, -128(%rbp)
    movq %r9, -136(%rbp)
    callq print_int
    movq -88(%rbp), %r8
    movq -96(%rbp), %rdx
    movq -104(%rbp), %rcx
    movq -112(%rbp), %r10
    movq -120(%rbp), %rsi
    movq -128(%rbp), %r11
    movq -136(%rbp), %r9
    movq %rcx, %rdi
    movq %r8, -88(%rbp)
    movq %rdx, -96(%rbp)
    movq %rcx, -104(%rbp)
    movq %r10, -112(%rbp)
    movq %rsi, -120(%rbp)
    movq %r11, -128(%rbp)
    movq %r9, -136(%rbp)
    callq print_int
    movq -88(%rbp), %r8
    movq -96(%rbp), %rdx
    movq -104(%rbp), %rcx
    movq -112(%rbp), %r10
    movq -120(%rbp), %rsi
    movq -128(%rbp), %r11
    movq -136(%rbp), %r9
    movq %rsi, %rdi
    movq %r8, -88(%rbp)
    movq %rdx, -96(%rbp)
    movq %rcx, -104(%rbp)
    movq %r10, -112(%rbp)
    movq %rsi, -120(%rbp)
    movq %r11, -128(%rbp)
    movq %r9, -136(%rbp)
    callq print_int
    movq -88(%rbp), %r8
    movq -96(%rbp), %rdx
    movq -104(%rbp), %rcx
    movq -112(%rbp), %r10
    movq -120(%rbp), %rsi
    movq -128(%rbp), %r11
    movq -136(%rbp), %r9
    movq %r8, %rdi
    movq %r8, -88(%rbp)
    movq %rdx, -96(%rbp)
    movq %rcx, -104(%rbp)
    movq %r10, -112(%rbp)
    movq %rsi, -120(%rbp)
    movq %r11, -128(%rbp)
    movq %r9, -136(%rbp)
    callq print_int
    movq -88(%rbp), %r8
    movq -96(%rbp), %rdx
    movq -104(%rbp), %rcx
    movq -112(%rbp), %r10
    movq -120(%rbp), %rsi
    movq -128(%rbp), %r11
    movq -136(%rbp), %r9
    addq $160, %rsp
    popq %rbp
    retq 

