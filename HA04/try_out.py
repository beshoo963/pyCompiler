from ast import parse,dump
from compiler_register_allocator import Compiler

compiler = Compiler()

progA="""
a = 1
b = 2
c = a + b
print_int(c + 4 + a + b)
"""

progB="""
a = 1
b = 2
c = a + b
print_int(c + 4)
"""

ast = parse(progB)
print(dump(ast, indent=2))

print("===============================")

ast_after_rco = compiler.remove_complex_operands(ast)
print(str(ast_after_rco))

print("===============================")

ast_after_select_instrs = compiler.select_instructions(ast_after_rco)
print(ast_after_select_instrs)

print("===============================")

ast_after_assign_registers = compiler.assign_homes(ast_after_select_instrs)
print(ast_after_assign_registers)

print("===============================")

ast_after_patch_instructions = compiler.patch_instructions(ast_after_assign_registers)
print(ast_after_patch_instructions)