	.globl main
main:
    pushq %rbp
    movq %rsp, %rbp
    subq $16, %rsp
    callq read_int
    movq %rax, %r9
    negq %r9
    negq %r9
    negq %r9
    movq %r9, %rdi
    callq print_int
    addq $16, %rsp
    popq %rbp
    retq 
