	.align 16
block_267:
    movq free_ptr(%rip), %r11
    addq $16, free_ptr(%rip)
    movq $130, 0(%r11)
    movq %r11, %rsi
    movq %rsi, %r11
    movq %rdx, 8(%r11)
    movq %rsi, %rcx
    movq %rcx, %r11
    movq 8(%r11), %rcx
    movq %rcx, %r11
    movq 16(%r11), %rcx
    movq %rcx, %rdi
    movq %r9, -4320(%rbp)
    movq %rdx, -4328(%rbp)
    movq %rcx, -4336(%rbp)
    movq %r10, -4344(%rbp)
    movq %r8, -4352(%rbp)
    movq %rsi, -4360(%rbp)
    callq print_int
    movq -4320(%rbp), %r9
    movq -4328(%rbp), %rdx
    movq -4336(%rbp), %rcx
    movq -4344(%rbp), %r10
    movq -4352(%rbp), %r8
    movq -4360(%rbp), %rsi
    movq $0, %rax
    jmp conclusion

	.align 16
block_268:
    movq %r15, %rdi
    movq $16, %rsi
    movq %rdx, 0(%r15)
    movq %rdx, -8(%r15)
    movq %r8, -16(%r15)
    movq %rsi, -24(%r15)
    movq %rcx, -32(%r15)
    movq %rcx, -40(%r15)
    movq %rcx, -48(%r15)
    movq %rsi, -56(%r15)
    movq %r9, -4320(%rbp)
    movq %rdx, -4328(%rbp)
    movq %rcx, -4336(%rbp)
    movq %r10, -4344(%rbp)
    movq %r8, -4352(%rbp)
    movq %rsi, -4360(%rbp)
    callq collect
    movq -4320(%rbp), %r9
    movq -4328(%rbp), %rdx
    movq -4336(%rbp), %rcx
    movq -4344(%rbp), %r10
    movq -4352(%rbp), %r8
    movq -4360(%rbp), %rsi
    jmp block_267

	.align 16
block_269:
    movq free_ptr(%rip), %r11
    addq $24, free_ptr(%rip)
    movq $132, 0(%r11)
    movq %r11, %r8
    movq %r8, %r11
    movq %rdx, 8(%r11)
    movq %r8, %r11
    movq %rsi, 16(%r11)
    movq %r8, %rcx
    movq %rcx, %rdx
    movq free_ptr(%rip), %rcx
    addq $16, %rcx
    cmpq fromspace_end(%rip), %rcx
    jl block_267
    jmp block_268

	.align 16
block_270:
    movq %r15, %rdi
    movq $24, %rsi
    movq %rdx, 0(%r15)
    movq %rdx, -8(%r15)
    movq %r8, -16(%r15)
    movq %rsi, -24(%r15)
    movq %rcx, -32(%r15)
    movq %rcx, -40(%r15)
    movq %rcx, -48(%r15)
    movq %rsi, -56(%r15)
    movq %r9, -4320(%rbp)
    movq %rdx, -4328(%rbp)
    movq %rcx, -4336(%rbp)
    movq %r10, -4344(%rbp)
    movq %r8, -4352(%rbp)
    movq %rsi, -4360(%rbp)
    callq collect
    movq -4320(%rbp), %r9
    movq -4328(%rbp), %rdx
    movq -4336(%rbp), %rcx
    movq -4344(%rbp), %r10
    movq -4352(%rbp), %r8
    movq -4360(%rbp), %rsi
    jmp block_269

	.align 16
block_271:
    movq free_ptr(%rip), %r11
    addq $16, free_ptr(%rip)
    movq $2, 0(%r11)
    movq %r11, %rsi
    movq %rsi, %r11
    movq %rdx, 8(%r11)
    movq %rsi, %rdx
    movq $42, %rsi
    movq free_ptr(%rip), %rcx
    addq $24, %rcx
    cmpq fromspace_end(%rip), %rcx
    jl block_269
    jmp block_270

	.align 16
block_272:
    movq %r15, %rdi
    movq $16, %rsi
    movq %rdx, 0(%r15)
    movq %rdx, -8(%r15)
    movq %r8, -16(%r15)
    movq %rsi, -24(%r15)
    movq %rcx, -32(%r15)
    movq %rcx, -40(%r15)
    movq %rcx, -48(%r15)
    movq %rsi, -56(%r15)
    movq %r9, -4320(%rbp)
    movq %rdx, -4328(%rbp)
    movq %rcx, -4336(%rbp)
    movq %r10, -4344(%rbp)
    movq %r8, -4352(%rbp)
    movq %rsi, -4360(%rbp)
    callq collect
    movq -4320(%rbp), %r9
    movq -4328(%rbp), %rdx
    movq -4336(%rbp), %rcx
    movq -4344(%rbp), %r10
    movq -4352(%rbp), %r8
    movq -4360(%rbp), %rsi
    jmp block_271

	.align 16
start:
    movq $7, %rdx
    movq free_ptr(%rip), %rcx
    addq $16, %rcx
    cmpq fromspace_end(%rip), %rcx
    jl block_271
    jmp block_272

	.align 16
conclusion:
    addq $4400, %rsp
    subq $64, %r15
    popq %rbp
    retq 

	.globl main
	.align 16
main:
    pushq %rbp
    movq %rsp, %rbp
    subq $4400, %rsp
    movq $16384, %rdi
    movq $16384, %rsi
    callq initialize
    movq rootstack_begin(%rip), %r15
    movq $0, 0(%r15)
    movq $0, 8(%r15)
    movq $0, 16(%r15)
    movq $0, 24(%r15)
    movq $0, 32(%r15)
    movq $0, 40(%r15)
    movq $0, 48(%r15)
    movq $0, 56(%r15)
    addq $64, %r15
    jmp start


