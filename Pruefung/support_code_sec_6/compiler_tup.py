from ast import *
from x86_ast import *
import x86_ast
from graph import *
from utils import *
from dataflow_analysis import analyze_dataflow
import copy
from type_check_Ltup import TypeCheckLtup
import type_check_Ctup

Binding = tuple[Name, expr]
Temporaries = list[Binding]
get_fresh_tmp = lambda: generate_name('tmp')

label = lambda v: v.id if isinstance(v, Reg) else str(v)

registers_for_coloring = [
    Reg('rcx'),
    Reg('rdx'),
    Reg('rsi'),
    Reg('r8'),
    Reg('r9'),
    Reg('r10')
]


def get_loc_from_arg(a: arg) -> set[location]:
    match a:
        case Reg(_):
            return set([a])
        case Variable(_):
            return set([a])
        case ByteReg(_):
            return set([a])
        case _:
            return set([])

def create_block(stmts: list[stmt], basic_blocks) -> list[stmt]:
    match stmts:
        case [Goto(label)]:
            return stmts
        case _:
            label = label_name(generate_name('block'))
            basic_blocks[label] = stmts
            return [Goto(label)]

def cc(op: cmpop) -> str:
    match op:
        case Eq() | Is():
            return 'e'
        case NotEq():
            return 'ne'
        case Lt():
            return 'l'
        case LtE():
            return 'le'
        case Gt():
            return 'g'
        case GtE():
            return 'ge'
        case _:
            raise Exception('unhandled case in cc:' + repr(op))

class Compiler:

    def tmps_to_stmts(self, tmps: Temporaries) -> list[stmt]:
        result = []
        for tmp in tmps:
            result.append(Assign(tmp[0], tmp[1]))
        return result

    ###########################################################################
    # Shrink
    ###########################################################################

    def shrink_exp(self, e: expr) -> expr:
        match e:
            case Constant(_) | Name(_) | GlobalValue(_) | Call(Name('input_int'), []):
                return e
            case BoolOp(And(), [e1, e2]):
                return IfExp(self.shrink_exp(e1), self.shrink_exp(e2), Constant(False))
            case BoolOp(Or(), [e1, e2]):
                return IfExp(self.shrink_exp(e1), Constant(True), self.shrink_exp(e2))
            case IfExp(test, thn, els):
                return IfExp(self.shrink_exp(test), self.shrink_exp(thn), self.shrink_exp(els))
            case Compare(e1, [cmp], [e2]):
                return Compare(self.shrink_exp(e1), [cmp], [self.shrink_exp(e2)])
            case BinOp(e1, op, e2):
                return BinOp(self.shrink_exp(e1), op, self.shrink_exp(e2))
            case UnaryOp(op, e):
                return UnaryOp(op, self.shrink_exp(e))
            case Call(Name('len'), [e]):
                return Call(Name('len'), [self.shrink_exp(e)])
            case Subscript(exp, Constant(index), Load()):
                return Subscript(self.shrink_exp(exp), Constant(index), Load())
            case Tuple(elts, Load()):
                return Tuple([self.shrink_exp(e) for e in elts], Load())
            case Expr(exp):
                return Expr(self.shrink_exp(exp))
            case _:
                raise Exception('unhandled case in shrink_exp:' + repr(e))

    def shrink_stmt(self, stm: stmt) -> stmt:
        match stm:
            case If(test, thn, els):
                test_shrink = self.shrink_exp(test)
                thn_shrink = [self.shrink_stmt(s) for s in thn]
                els_shrink = [self.shrink_stmt(s) for s in els]
                return If(test_shrink, thn_shrink, els_shrink)
            case While(test, body, []):
                test_shrink = self.shrink_exp(test)
                body_shrink = [self.shrink_stmt(s) for s in body]
                return While(test_shrink, body_shrink, [])
            case Expr(Call(Name('print'), [e])):
                return Expr(Call(Name('print'), [self.shrink_exp(e)]))
            case Expr(e):
                return Expr(self.shrink_exp(e))
            case Assign(lhs, rhs):
                return Assign(lhs, self.shrink_exp(rhs))
            case Collect(_):
                return stm
            case _:
                raise Exception('unhandled case in shrink_stmt:' + repr(stm))


    def shrink(self, p: Module) -> Module:
        new_body = []
        for stm in p.body:
            new_body.append(self.shrink_stmt(stm))
        return Module(new_body)

    ###########################################################################
    # Expose Allocation
    ###########################################################################

    def expose_allocation_exp(self, e: expr) -> expr:
        match e:
            case UnaryOp(op, exp):
                return UnaryOp(op, self.expose_allocation_exp(exp))
            case BinOp(e1, op, e2):
                return BinOp(self.expose_allocation_exp(e1), op, self.expose_allocation_exp(e2))
            case BoolOp(op, [e1, e2]):
                return BoolOp(op, [self.expose_allocation_exp(e1), self.expose_allocation_exp(e2)])
            case Compare(e1, [cmp], [e2]):
                return Compare(self.expose_allocation_exp(e1), [cmp], [self.expose_allocation_exp(e2)])
            case IfExp(test, thn, els):
                return IfExp(self.expose_allocation_exp(test), self.expose_allocation_exp(thn), self.expose_allocation_exp(els))
            case Tuple(elts, Load()):
                exprs = [self.expose_allocation_exp(e) for e in elts]

                assignments: list[stmt] = []
                for exp in exprs:
                    tmp = Name(generate_name('init'))
                    assignments.append(Assign([tmp], exp))

                left_side_check = BinOp(GlobalValue('free_ptr'), Add(), Constant(len(exprs) * 8 + 8))
                right_side_check = GlobalValue('fromspace_end')
                check = Expr(Compare(left_side_check, [Lt()], [right_side_check]))
                thn = [Expr(Constant(0))]
                els = [Collect(len(exprs) * 8 + 8)]
                allocate = self.shrink_stmt(If(check, thn, els))

                tuple_name = Name(generate_name('alloc'))
                tup = Assign([tuple_name], Allocate(Constant(len(exprs)), e.has_type))

                tup_assigns: list[stmt] = []
                index = 0
                for assign in assignments:
                    tup_assigns.append(Assign([Subscript(tuple_name, Constant(index), Load())], assign.targets[0]))
                    index += 1
                result = Begin(assignments + [allocate, tup] + tup_assigns, tuple_name)
                return result
            case _:
                return e
    def expose_allocation_stmt(self, stm: stmt) -> stmt:
        match stm:
            case Expr(Call(Name('print'), [e])):
                return Expr(Call(Name('print'), [self.expose_allocation_exp(e)]))
            case Expr(e):
                return Expr(self.expose_allocation_exp(e))
            case Assign([Name(var)], rhs):
                return Assign([Name(var)], self.expose_allocation_exp(rhs))
            case Assign([Subscript(exp, Constant(index), Store())], rhs):
                return Assign([Subscript(self.expose_allocation_exp(exp), Constant(index), Store())], self.expose_allocation_exp(rhs))
            case If(test, thn, els):
                return If(self.expose_allocation_exp(test),
                          [self.expose_allocation_stmt(s) for s in thn],
                          [self.expose_allocation_stmt(s) for s in els]
                )
            case While(test, body, []):
                return While(self.expose_allocation_exp(test),
                            [self.expose_allocation_stmt(s) for s in body],
                            []
                )

    def expose_allocation(self, p: Module) -> Module:
        TypeCheckLtup().type_check(p)
        new_body = []
        for stm in p.body:
            new_body.append(self.expose_allocation_stmt(stm))
        return Module(new_body)

    ############################################################################
    # Remove Complex Operands
    ############################################################################

    def rco_exp(self, e: expr, need_atomic: bool) -> tuple[expr, Temporaries]:
        match e:
            case Constant(_) | Name(_):
                return e, []
            case Call(Name('input_int'), []):
                if need_atomic:
                    tmp = Name(get_fresh_tmp())
                    return tmp, [(tmp, e)]
                return e, []
            case UnaryOp(op, exp):
                (new_exp, temps) = self.rco_exp(exp, True)
                if need_atomic:
                    tmp = Name(get_fresh_tmp())
                    return tmp, temps + [(tmp, UnaryOp(op, new_exp))]
                return UnaryOp(op, new_exp), temps
            case BinOp(e1, op, e2):
                (new_e1, temps1) = self.rco_exp(e1, True)
                (new_e2, temps2) = self.rco_exp(e2, True)
                if need_atomic:
                    tmp = Name(get_fresh_tmp())
                    return tmp, temps1 + temps2 + [(tmp, BinOp(new_e1, op, new_e2))]
                return BinOp(new_e1, op, new_e2), temps1 + temps2
            case Compare(e1, [cmp], [e2]):
                (new_e1, temps1) = self.rco_exp(e1, True)
                (new_e2, temps2) = self.rco_exp(e2, True)
                if need_atomic:
                    tmp = Name(get_fresh_tmp())
                    return tmp, temps1 + temps2 + [(tmp, Compare(new_e1, [cmp], [new_e2]))]
                return Compare(new_e1, [cmp], [new_e2]), temps1 + temps2
            case IfExp(test, thn, els):
                (new_test, temps1) = self.rco_exp(test, False)
                (new_thn, temps2) = self.rco_exp(thn, False)
                (new_els, temps3) = self.rco_exp(els, False)

                if need_atomic:
                    tmp = Name(get_fresh_tmp())
                    return tmp, [(tmp, IfExp(make_begin(temps1, new_test),
                                make_begin(temps2, new_thn),
                                make_begin(temps3, new_els)))]
                return IfExp(make_begin(temps1, new_test),
                            make_begin(temps2, new_thn),
                            make_begin(temps3, new_els)), []
            case Begin(stmts, e):
                new_stmts = []
                for stm in stmts:
                    for new_stmt in self.rco_stmt(stm):
                        new_stmts.append(new_stmt)
                return Begin(new_stmts, e), []
            case Subscript(e1, e2, Load()):
                (new_e1, temps) = self.rco_exp(e1, True)
                (new_e2, temps2) = self.rco_exp(e2, True)
                if need_atomic:
                    tmp = Name(get_fresh_tmp())
                    return tmp, temps + temps2 + [(tmp, Subscript(new_e1, new_e2, Load()))]
                return Subscript(new_e1, new_e2, Load()), temps + temps2
            case Call(Name('len'), [e]):
                (new_e, temps) = self.rco_exp(e, True)
                if need_atomic:
                    tmp = Name(get_fresh_tmp())
                    return tmp, temps + [(tmp, Call(Name('len'), [new_e]))]
                return Call(Name('len'), [new_e]), temps
            case Allocate(n, t):
                (new_n, temps) = self.rco_exp(n, True)
                if need_atomic:
                    tmp = Name(get_fresh_tmp())
                    return tmp, temps + [(tmp, e)]
                return e, temps
            case GlobalValue(name):
                if need_atomic:
                    tmp = Name(get_fresh_tmp())
                    return tmp, [(tmp, e)]
                return e, []
            case Expr(e):
                return self.rco_exp(e, need_atomic)
            case _:
                raise Exception('unhandled case in rco_exp ' + repr(e))

    def rco_stmt(self, stm: stmt) -> list[stmt]:
        match stm:
            case Expr(Call(Name('print'), [e])):
                (new_e, temps) = self.rco_exp(e, True)
                return make_assigns(temps) + [Expr(Call(Name('print'), [new_e]))]
            case Expr(e):
                (new_e, temps) = self.rco_exp(e, False)
                return make_assigns(temps) + [Expr(new_e)]
            case Assign(lhs, rhs):
                (new_rhs, temps) = self.rco_exp(rhs, False)
                return make_assigns(temps) + [Assign(lhs, new_rhs)]
            case If(test, thn, els):
                (new_test, temps) = self.rco_exp(test, False)
                new_th = []
                for stm in thn:
                    new_th += self.rco_stmt(stm)
                new_els = []
                for stm in els:
                    new_els += self.rco_stmt(stm)
                return make_assigns(temps) + [If(new_test, new_th, new_els)]
            case While(test, body, []):
                (new_test, temps) = self.rco_exp(test, False)
                new_body = [self.rco_stmt(s) for s in body]
                return make_assigns(temps) + [While(new_test, new_body, [])]
            case Collect(_):
                return [stm]
            case Assign([Subscript(e1, e2, Store())], e3):
                (new_e1, temps1) = self.rco_exp(e1, True)
                (new_e2, temps2) = self.rco_exp(e2, True)
                (new_e3, temps3) = self.rco_exp(e3, True)
                return make_assigns(temps1 + temps2 + temps3) + [Assign([Subscript(new_e1, new_e2, Store())], new_e3)]
            case _:
                raise Exception(f'Unexpected statement: {stm}')


    def remove_complex_operands(self, p: Module) -> Module:
        new_body = []
        for stm in p.body:
            new_body.extend(self.rco_stmt(stm))
        return Module(new_body)

    ############################################################################
    # Explicate Control
    ############################################################################

    def explicate_effect(self, e, cont, basic_blocks) -> list[stmt]:
        match e:
            case IfExp(test, body, orelse):
                goto_cont = create_block(cont, basic_blocks)
                body_instr = self.explicate_effect(body, goto_cont, basic_blocks)
                orelse_instr = self.explicate_effect(orelse, goto_cont, basic_blocks)

                return self.explicate_pred(test, body_instr, orelse_instr, basic_blocks)
            case Call(func, args):
                return [Expr(e)] + cont
            case Begin(body, result):
                new_body = self.explicate_effect(result, cont, basic_blocks) + [cont]
                for s in reversed(body):
                    new_body = self.explicate_stmt(s, new_body, basic_blocks)
                return new_body
            case _:
                return cont

    def explicate_assign(self, rhs, lhs, cont, basic_blocks) -> list[stmt]:
        match rhs:
            case IfExp(test, body, orelse):
                goto_cont = create_block(cont, basic_blocks)

                body_instr = self.explicate_assign(body, lhs, goto_cont, basic_blocks)
                orelse_instr = self.explicate_assign(
                    orelse, lhs, goto_cont, basic_blocks
                )

                return self.explicate_pred(test, body_instr, orelse_instr, basic_blocks)
            case Begin(body, result):
                new_body = self.explicate_assign(result, lhs, cont, basic_blocks)
                for s in reversed(body):
                    new_body = self.explicate_stmt(s, new_body, basic_blocks)
                return new_body
            case _:
                return [Assign([lhs], rhs)] + cont

    def explicate_pred(self, cnd, thn, els, basic_blocks) -> list[stmt]:
        match cnd:
            case Compare(left, [op], [right]):
                goto_thn = create_block(thn, basic_blocks)
                goto_els = create_block(els, basic_blocks)

                return [If(cnd, goto_thn, goto_els)]
            case Constant(True):
                return thn
            case Constant(False):
                return els
            case UnaryOp(Not(), operand):
                return self.explicate_pred(operand, els, thn, basic_blocks)
            case IfExp(test, body, orelse):
                goto_thn = create_block(thn, basic_blocks)
                goto_els = create_block(els, basic_blocks)

                new_body_if_cond = self.explicate_pred(
                    body, goto_thn, goto_els, basic_blocks
                )

                new_orelse_if_cond = self.explicate_pred(
                    orelse, goto_thn, goto_els, basic_blocks
                )

                return self.explicate_pred(
                    test, new_body_if_cond, new_orelse_if_cond, basic_blocks
                )
            case Begin(body, result):
                new_body = self.explicate_pred(result, thn, els, basic_blocks)
                for s in reversed(body):
                    new_body = self.explicate_stmt(s, new_body, basic_blocks)

                return new_body
            case _:
                return [
                    If(
                        Compare(cnd, [Eq()], [Constant(False)]),
                        create_block(els, basic_blocks),
                        create_block(thn, basic_blocks),
                    )
                ]

    def explicate_stmt(self, s: stmt, cont, basic_blocks) -> list[stmt]:
        match s:
            case Assign([lhs], rhs):
                return self.explicate_assign(rhs, lhs, cont, basic_blocks)
            case Expr(value):
                return self.explicate_effect(value, cont, basic_blocks)
            case If(test, body, orelse):
                goto_cont = create_block(cont, basic_blocks)

                explicate_body = []
                explicate_body += goto_cont
                for s in reversed(body):
                    explicate_body = self.explicate_stmt(
                        s, explicate_body, basic_blocks
                    )

                explicate_orelse = []
                explicate_orelse += goto_cont
                for s in reversed(orelse):
                    explicate_orelse = self.explicate_stmt(
                        s, explicate_orelse, basic_blocks
                    )

                return self.explicate_pred(
                    test, explicate_body, explicate_orelse, basic_blocks
                )
            case While(test, body, []):
                goto_cont = create_block(cont, basic_blocks)

                label = label_name(generate_name('loop'))
                goto_loop = [Goto(label)]

                explicate_body = goto_loop
                for s in reversed(body):
                    explicate_body = self.explicate_stmt(
                        s, explicate_body, basic_blocks
                    )

                basic_blocks[label] = self.explicate_pred(
                    test, explicate_body, goto_cont, basic_blocks
                )

                return goto_loop
            case Collect(_):
                return [s] + cont
            case _:
                raise Exception('unhandled case in explicate_stmt: ' + repr(s))

    def explicate_control(self, p: Module):
        match p:
            case Module(body):
                new_body = [Return(Constant(0))]
                basic_blocks = {}
                for s in reversed(body):
                    new_body = self.explicate_stmt(s, new_body, basic_blocks)
                basic_blocks[label_name('start')] = new_body
                return CProgram(basic_blocks)

    ############################################################################
    # Select Instructions
    ############################################################################

    def select_arg(self, e: arg) -> arg:
        match e:
            case Constant(True):
                return Immediate(1)
            case Constant(False):
                return Immediate(0)
            case Constant(n):
                return Immediate(n)
            case Name(v):
                return Variable(v)
            case GlobalValue(v):
                return x86_ast.Global(v)
            case [a]:
                return self.select_arg(a)
    def select_assign(self, s: stmt) -> list[instr]:
        match s:
            case Assign([Name(var)], BinOp(atm1, Add(), atm2)):
                arg1 = self.select_arg(atm1)
                arg2 = self.select_arg(atm2)
                lhs = Variable(var)
                if arg1 == lhs:
                    return [Instr('addq', [arg2, lhs])]
                elif arg2 == lhs:
                    return [Instr('addq', [arg1, lhs])]
                else:
                    return [Instr('movq', [arg1, lhs]),
                            Instr('addq', [arg2, lhs])]
            case Assign([Name(var)], BinOp(atm1, Sub(), atm2)):
                arg1 = self.select_arg(atm1)
                arg2 = self.select_arg(atm2)
                lhs = Variable(var)
                if arg1 == lhs:
                    return [Instr('subq', [arg2, lhs])]
                elif arg2 == lhs:
                    return [Instr('negq', [lhs]),
                            Instr('addq', [arg1, lhs])]
                else:
                    return [Instr('movq', [arg1, lhs]),
                            Instr('subq', [arg2, lhs])]
            case Assign([Name(var)], UnaryOp(USub(), atm)):
                arg = self.select_arg(atm)
                return [Instr('movq', [arg, Variable(var)]),
                        Instr('negq', [Variable(var)])]
            case Assign([Name(var)], Call(Name('input_int'), [])):
                return [Callq(label_name('read_int'), 0),
                        Instr('movq', [Reg('rax'), Variable(var)])]
            case Assign([Name(var)], Compare(left, [op], [right])):
                return [
                    Instr('cmpq', [self.select_arg(right), self.select_arg(left)]),
                    Instr('set' + cc(op), [ByteReg('al')]),
                    Instr('movzbq', [ByteReg('al'), Variable(var)]),
                ]
            case Assign([Name(var)], UnaryOp(Not(), atm)):
                arg = self.select_arg(atm)
                lhs = Variable(var)
                if lhs == arg:
                    return [Instr('xorq', [Immediate(1), Variable(var)])]
                else:
                    return [
                        Instr('movq', [self.select_arg(arg), Variable(var)]),
                        Instr('xorq', [Immediate(1), Variable(var)]),
                    ]
            case Assign([Name(var)], Call(Name('len'), [atm])):
                arg = self.select_arg(atm)
                return [
                    Instr('movq', [arg, Reg('r11')]),
                    Instr('movq', [Deref('r11', 0), Reg('r11')]),
                    Instr('andq', [Immediate(126), Reg('r11')]),
                    Instr('sarq', [Immediate(1), Reg('r11')]),
                    Instr('movq', [Reg('r11'), Variable(var)])
                ]
            case Assign([Name(var)], Allocate(Constant(n), t)):
                tag = self.calculate_tag(n, t)
                return [
                    Instr('movq', [x86_ast.Global('free_ptr'), Reg('r11')]),
                    Instr('addq', [Immediate(8 * (n + 1)), x86_ast.Global('free_ptr')]),
                    Instr('movq', [Immediate(tag), Deref('r11', 0)]),
                    Instr('movq', [Reg('r11'), Variable(var)])
                ]
            case Assign([Subscript(atm1, Constant(n), ls)], Call(Name('len'), [atm2])):
                return [Instr('movq', [self.select_arg(atm2), Reg('r11')]),
                        Instr('movq', [Deref('r11', 0), Reg('r11')]),
                        Instr('andq', [Immediate(126), Reg('r11')]),
                        Instr('sarq', [Immediate(1), Reg('r11')]),
                        Instr('movq', [self.select_arg(atm1), Reg('r12')]),
                        Instr('movq', [Reg('r11'), Deref('r12', 8 * (n + 1))])
                        ]
            case Assign([Subscript(atm1, Constant(n), ls)], Allocate(n2, t)):
                tag = self.calculate_tag(n, t)
                return [
                    Instr('movq', [x86_ast.Global('free_ptr'), Reg('r11')]),
                    Instr('addq', [Immediate(8 * (n + 1)), x86_ast.Global('free_ptr')]),
                    Instr('movq', [Immediate(tag), Deref('r11', 0)]),
                    Instr('movq', [self.select_arg(atm1), Reg('r12')]),
                    Instr('movq', [Reg('r11'), Deref('r12', 8 * (n + 1))])
                ]
            case Assign([Subscript(atm1, Constant(n1), ls)], Subscript(atm2, Constant(n2), ls2)):
                arg1 = self.select_arg(atm1)
                arg2 = self.select_arg(atm2)
                return [Instr('movq', [arg2, Reg('r11')]),
                        Instr('movq', [Deref('r11', 8 * (n2 + 1)), Reg('r12')]),
                        Instr('movq', [arg1, Reg('r11')]),
                        Instr('movq', [Reg('r12'), Deref('r11', 8 * (n1 + 1))])]
            case Assign(atm1, Subscript(atm2, Constant(n), ls)):
                arg1 = self.select_arg(atm1)
                arg2 = self.select_arg(atm2)
                return [Instr('movq', [arg2, Reg('r11')]),
                        Instr('movq', [Deref('r11', 8 * (n + 1)), arg1])]
            case Assign([Subscript(atm1, Constant(n), ls)], atm2):
                arg1 = self.select_arg(atm1)
                arg2 = self.select_arg(atm2)
                return [Instr('movq', [arg1, Reg('r11')]),
                        Instr('movq', [arg2, Deref('r11', 8 * (n + 1))])]
            case Assign([Name(var)], atm):
                arg = self.select_arg(atm)
                return [Instr('movq', [arg, Variable(var)])]

    def calculate_tag(self, n, t):
        unused = 0b000000
        mask = 0
        length = n
        fwd = 0b0
        index = 0
        for type in t.types:
            match type:
                case TupleType(_):
                    mask |= (1 << index)
            index += 1
        tag = unused
        tag <<= 51
        tag |= mask
        tag <<= 6
        tag |= length
        tag <<= 1
        tag |= fwd
        return tag

    def select_stmt(self, s: stmt) -> list[instr]:
        match s:
            case Assign(_, _):
                return self.select_assign(s)
            case Expr(Call(Name('print'), [atm])):
                arg = self.select_arg(atm)
                return [
                    Instr('movq', [arg, Reg('rdi')]),
                    Callq(label_name('print_int'), 1),
                ]
                # input_int()
            case Expr(Call(Name('input_int'), [])):
                return [Callq(label_name('read_int'), 0)]
            case If(Compare(left, [op], [right]), [Goto(thn)], [Goto(els)]):
                return [
                    Instr('cmpq', [self.select_arg(right), self.select_arg(left)]),
                    JumpIf(cc(op), thn),
                    Jump(els),
                ]
            case Goto(label):
                return [Jump(label)]
            case Return(arg):
                return [
                    Instr('movq', [self.select_arg(arg), Reg('rax')]),
                    Jump('conclusion'),
                ]
            case Expr(Call(Name('len'), [atm])):
                return [
                    Instr('len', []),
                ]
            case Collect(n):
                return [
                    Instr('movq', [Reg('r15'), Reg('rdi')]),
                    Instr('movq', [Immediate(n), Reg('rsi')]),
                    Callq('collect', 1),
                ]

    def select_instructions(self, p: CProgram) -> X86Program:
        new_body = {}
        for block_id, stmts in p.body.items():
            instrs = []
            for s in stmts:
                s = self.select_stmt(s)
                instrs += s
            new_body[block_id] = instrs
        return X86Program(new_body)

    ###########################################################################
    # Uncover Live
    ###########################################################################


    ############################################################################
    # Build Interference
    ############################################################################


    ############################################################################
    # Allocate Registers
    ############################################################################

  
    ############################################################################
    # Assign Homes
    ############################################################################


    ###########################################################################
    # Patch Instructions
    ###########################################################################


    ###########################################################################
    # Prelude & Conclusion
    ###########################################################################


    ##################################################
    # Compiler
    ##################################################

    def compile(self, s: str, logging=False) -> X86Program:
        compiler_passes = {
            'shrink': self.shrink,
            'expose allocation': self.expose_allocation,
            'remove complex operands': self.remove_complex_operands,
            'explicate control': self.explicate_control,
            'select instructions': self.select_instructions,
            'assign homes': self.assign_homes,
            'patch instructions': self.patch_instructions,
            'prelude & conclusion': self.prelude_and_conclusion,
        }

        current_program = parse(s)

        if logging == True:
            print()
            print('==================================================')
            print(' Input program')
            print('==================================================')
            print()
            print(s)

        for pass_name, pass_fn in compiler_passes.items():
            current_program = pass_fn(current_program)

            if logging == True:
                print()
                print('==================================================')
                print(f' Output of pass: {pass_name}')
                print('==================================================')
                print()
                print(current_program)

        return current_program


##################################################
# Execute
##################################################

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python compiler.py <source filename>')
    else:
        file_name = sys.argv[1]
        with open(file_name) as f:
            print(f'Compiling program {file_name}...')

            try:
                program = f.read()
                compiler = Compiler()
                x86_program = compiler.compile(program, logging=True)

                with open(file_name + '.s', 'w') as output_file:
                    output_file.write(str(x86_program))

            except:
                print(
                    'Error during compilation! **************************************************'
                )
                import traceback

                traceback.print_exception(*sys.exc_info())
