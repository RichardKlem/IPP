from instruction_methods import *

opcodes = ['CREATEFRAME', 'PUSHFRAME', 'POPFRAME', 'RETURN', 'BREAK', 'DEFVAR', 'CALL', 'PUSHS',
           'POPS', 'WRITE', 'LABEL', 'JUMP', 'EXIT', 'DPRINT', 'MOVE', 'NOT', 'INT2CHAR',
           'READ', 'STRLEN', 'TYPE', 'ADD', 'SUB', 'MUL', 'IDIV', 'LT', 'GT', 'EQ', 'AND', 'OR',
           'STRI2INT', 'CONCAT', 'GETCHAR', 'SETCHAR', 'JUMPIFEQ', 'JUMPIFNEQ']
zero_arg_opcodes = ['CREATEFRAME', 'PUSHFRAME', 'POPFRAME', 'RETURN', 'BREAK', 'CLEARS']
one_arg_opcodes = ['DEFVAR', 'CALL', 'PUSHS', 'POPS', 'WRITE', 'LABEL', 'JUMP', 'EXIT',
                   'DPRINT', 'ADDS', 'SUBS', 'MULS', 'IDIVS', 'LTS', 'GTS', 'EQS', 'ANDS',
                   'ORS', 'NOTS', 'INT2CHARS', 'STRI2INTS', 'JUMPIFEQS', 'JUMPIFNEQS']
two_arg_opcodes = ['MOVE', 'NOT', 'INT2CHAR', 'READ', 'STRLEN', 'TYPE']
three_arg_opcodes = ['ADD', 'SUB', 'MUL', 'IDIV', 'LT', 'GT', 'EQ', 'AND', 'OR', 'STRI2INT',
                     'CONCAT', 'GETCHAR', 'SETCHAR', 'JUMPIFEQ', 'JUMPIFNEQ']

program_attributes = ['language', 'name', 'description']
instruction_attributes = ['order', 'opcode']
argument_attributes = ['type']
symbol_types = ['var', 'int', 'bool', 'string', 'nil', 'label', 'type']

inst2method_dict = {'CREATEFRAME': createframe_i, 'PUSHFRAME': pushframe_i, 'POPFRAME': popframe_i,
                    'RETURN': return_i, 'BREAK': break_i, 'DEFVAR': defvar_i, 'CALL': call_i,
                    'PUSHS': pushs_i, 'POPS': pops_i, 'WRITE': write_i, 'LABEL': label_i,
                    'JUMP': jump_i, 'EXIT': exit_i, 'DPRINT': dprint_i, 'MOVE': move_i,
                    'NOT': not_i, 'INT2CHAR': int2char_i, 'READ': read_i, 'STRLEN': strlen_i,
                    'TYPE': type_i, 'ADD': add_i, 'SUB': sub_i, 'MUL': mul_i,
                    'IDIV': idiv_i, 'LT': lt_i, 'GT': gt_i, 'EQ': eq_i,
                    'AND': and_i, 'OR': or_i, 'STRI2INT': stri2int_i, 'CONCAT': concat_i,
                    'GETCHAR': getchar_i, 'SETCHAR': setchar_i, 'JUMPIFEQ': jumpifeq_i,
                    'JUMPIFNEQ': jumpifneq_i, 'CLEARS': clears_i, 'ADDS': adds_i, 'SUBS': subs_i,
                    'MULS': muls_i, 'IDIVS': idivs_i, 'LTS': lts_i, 'GTS': gts_i, 'EQS': eqs_i,
                    'ANDS': ands_i, 'ORS': ors_i, 'NOTS': nots_i, 'INT2CHARS': int2chars_i,
                    'STRI2INTS': stri2ints_i, 'JUMPIFEQS': jumpifeqs_i, 'JUMPIFNEQS': jumpifneqs_i}
