	.align 16
block_220:
    movq %rcx, %rdi
    movq %r10, -3776(%rbp)
    movq %rsi, -3784(%rbp)
    movq %r8, -3792(%rbp)
    movq %rcx, -3800(%rbp)
    movq %rdx, -3808(%rbp)
    movq %r9, -3816(%rbp)
    callq print_int
    movq -3776(%rbp), %r10
    movq -3784(%rbp), %rsi
    movq -3792(%rbp), %r8
    movq -3800(%rbp), %rcx
    movq -3808(%rbp), %rdx
    movq -3816(%rbp), %r9
    movq $0, %rax
    jmp conclusion

	.align 16
block_222:
    subq $1, %rcx
    jmp loop_221

	.align 16
loop_221:
    cmpq $0, %rcx
    jg block_222
    jmp block_220

	.align 16
start:
    movq $10, %rcx
    jmp loop_221

	.align 16
conclusion:
    addq $3856, %rsp
    popq %rbp
    retq 

	.globl main
	.align 16
main:
    pushq %rbp
    movq %rsp, %rbp
    subq $3856, %rsp
    movq $16384, %rdi
    movq $16384, %rsi
    callq initialize
    movq rootstack_begin(%rip), %r15
    jmp start


