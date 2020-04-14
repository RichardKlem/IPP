import re
import sys
import interpret as i

def var_prepare(instruction, interpret):
    regex = re.match(r'^([GLT]F)@([\-$&%*!?a-zA-Z_][\-$&%*!?\w]*$)+', list(instruction)[0].text)
    if regex.lastindex != 2:
        exit(53)
    var_name = regex.group(2)
    var_frame = interpret.get_frame_of_var(var_name, regex.group(1))
    if var_frame is None:
        exit(54)
    return var_frame, var_name


def replace_escape_sequences(symb1_value):
    symb1_value.replace('&lt', '<').replace('&gt', '>').replace('&amp', '&')
    for char_int in range(127):
        char_str = chr(char_int)
        if char_int < 10:
            char_int = '00' + str(char_int)
        elif char_int < 100:
            char_int = '0' + str(char_int)
        symb1_value = symb1_value.replace('\\' + str(char_int), char_str)
    return symb1_value


def createframe_i(interpret: i.Interpret, instruction):
    interpret.tmp_frame = {}


def pushframe_i(interpret: i.Interpret, instruction):
    if interpret.tmp_frame is None:
        exit(55)
    interpret.frame_stack.append(interpret.tmp_frame)
    interpret.local_frame = interpret.frame_stack[-1]
    interpret.tmp_frame = None


def popframe_i(interpret: i.Interpret, instruction):
    if len(interpret.frame_stack) == 0:
        exit(55)
    interpret.tmp_frame = interpret.frame_stack.pop()
    if len(interpret.frame_stack) != 0:
        interpret.local_frame = interpret.frame_stack[-1]
    else:
        interpret.local_frame = None


def return_i(interpret: i.Interpret, instruction):
    if len(interpret.call_stack) == 0:
        exit(56)
    interpret.inst_index = interpret.call_stack.pop()


def break_i(interpret: i.Interpret, instruction):
    output = """Aktualni instrukce = {}\n
                Operacni cislo instrukce = {}\n\n
                Globalni ramec = {}\n
                Lokalni ramec = {}\n
                Docasny ramec = {}\n\n
                Slovnik navesti = {}\n\n
                Datovy zasobnik = {}\n
                Zasobnik volani = {}\n
             """.format(instruction.get('opcode'), instruction.get('order'),
                        interpret.global_frame, interpret.local_frame, interpret.tmp_frame,
                        interpret.label_dict, interpret.data_stack, interpret.call_stack)
    print(output, file=sys.stderr)


def defvar_i(interpret: i.Interpret, instruction):
    regex = re.match(r'^([GLT]F)@([\-$&%*!?a-zA-Z_][\-$&%*!?\w]*$)+', list(instruction)[0].text)
    if regex is None or regex.lastindex != 2:
        exit(32)
    frame = regex.group(1)
    variable = regex.group(2)
    if frame == 'GF':
        if interpret.get_frame_of_var(variable, 'GF') is not None:
            exit(52)
        interpret.global_frame[variable] = tuple([None, None])
    elif frame == 'LF':
        if interpret.get_frame_of_var(variable, 'LF') is not None:
            exit(52)
        interpret.local_frame[variable] = tuple([None, None])
    elif frame == 'TF':
        if interpret.get_frame_of_var(variable, 'TF') is not None:
            exit(52)
        interpret.tmp_frame[variable] = tuple([None, None])


def call_i(interpret: i.Interpret, instruction):
    if list(instruction)[0].text not in interpret.label_dict.keys():
        exit(52)
    interpret.call_stack.append(interpret.inst_index)
    interpret.inst_index = interpret.label_dict[list(instruction)[0].text]


def pushs_i(interpret: i.Interpret, instruction):
    symb_type, symb_value = interpret.get_type_and_value_of_symb(list(instruction)[0])
    if symb_value is None:
        exit(56)
    interpret.data_stack.append(tuple([symb_type, symb_value]))


def pops_i(interpret: i.Interpret, instruction):
    if len(interpret.data_stack) == 0:
        exit(56)
    var_frame, var_name = var_prepare(instruction, interpret)
    var_frame[var_name] = interpret.data_stack.pop()

def write_i(interpret: i.Interpret, instruction):
    symb_type, symb_value = interpret.get_type_and_value_of_symb(list(instruction)[0])
    if symb_value is None:
        exit(56)
    if symb_type == 'nil':
        print('', end='')
    elif symb_type == 'bool':
        print(str(symb_value).lower(), end='')
    elif symb_type == 'string':
        symb_value = replace_escape_sequences(symb_value)
        print(symb_value, end='')
    else:
        print(symb_value, end='')


def label_i(interpret: i.Interpret, instruction):
    pass


def jump_i(interpret: i.Interpret, instruction):
    if list(instruction)[0].text not in interpret.label_dict.keys():
        exit(52)
    interpret.inst_index = interpret.label_dict[list(instruction)[0].text]


def exit_i(interpret: i.Interpret, instruction):
    symb1_type, symb1_value = interpret.get_type_and_value_of_symb(list(instruction)[0])
    if symb1_value is None:
        exit(56)
    if symb1_type != 'int':
        exit(53)
    if 0 <= symb1_value <= 49:
        exit(symb1_value)
    else:
        exit(57)


def dprint_i(interpret: i.Interpret, instruction):
    regex = re.match(r'([GLT]F)@([\-$&%*!?a-zA-Z_][\-$&%*!?\w]*$)+', list(instruction)[
        0].text)
    if regex is None or regex.lastindex != 2:
        _, symb1_val = interpret.check_arg_type_and_get_value(list(instruction)[0])
    else:
        symb1_val = interpret.get_value_from_var(regex.group(2), regex.group(1))
    print(symb1_val, file=sys.stderr)


def move_i(interpret: i.Interpret, instruction):
    var_frame, var_name = var_prepare(instruction, interpret)
    symb1_type, symb1_value = interpret.get_type_and_value_of_symb(list(instruction)[1])
    if symb1_value is None:
        exit(56)
    var_frame[var_name] = tuple([symb1_type, symb1_value])


def not_i(interpret: i.Interpret, instruction):
    var_frame, var_name = var_prepare(instruction, interpret)

    symb1_type, symb1_value = interpret.get_type_and_value_of_symb(list(instruction)[1])
    if symb1_value is None:
        exit(56)
    if symb1_type != 'bool':
        exit(53)

    var_frame[var_name] = tuple([symb1_type, not symb1_value])


def int2char_i(interpret: i.Interpret, instruction):
    var_frame, var_name = var_prepare(instruction, interpret)
    symb1_type, symb1_value = interpret.get_type_and_value_of_symb(list(instruction)[1])
    if symb1_value is None:
        exit(56)
    if symb1_type != 'int':
        exit(53)
    try:
        symb1_value = chr(symb1_value)
    except:
        exit(58)
    var_frame[var_name] = tuple(['string', symb1_value])


def read_i(interpret: i.Interpret, instruction):
    print(interpret.input_data)
    var_frame, var_name = var_prepare(instruction, interpret)
    symb1_type, symb1_value = interpret.get_type_and_value_of_symb(list(instruction)[1])
    if symb1_value is None:
        exit(56)
    if symb1_type != 'type' or symb1_value not in ['int', 'bool', 'string']:
        exit(53)
    try:
        if interpret.input_data:
            read_input = interpret.input_data.pop(0)
            read_input.rstrip('\n\r')
        else:
            read_input = input()

        if symb1_value == 'int':
            try:
                read_input = int(read_input)
            except:
                read_input = 'nil'
                symb1_value = 'nil'
        elif symb1_value == 'string':
            try:
                read_input = str(read_input)
            except:
                read_input = 'nil'
                symb1_value = 'nil'
        elif symb1_value == 'bool':
            if read_input != 'true':
                read_input = 'false'
    except:
        symb1_value = 'nil'
        read_input = 'nil'

    var_frame[var_name] = tuple([symb1_value, read_input])


def strlen_i(interpret: i.Interpret, instruction):
    var_frame, var_name = var_prepare(instruction, interpret)
    symb1_type, symb1_val = interpret.get_type_and_value_of_symb(list(instruction)[1])
    if symb1_val is None:
        exit(56)
    if symb1_type != 'string':
        exit(53)
    var_frame[var_name] = tuple(['int', len(symb1_val)])


def type_i(interpret: i.Interpret, instruction):
    var_frame, var_name = var_prepare(instruction, interpret)

    symb1_type, symb1_val = interpret.get_type_and_value_of_symb(list(instruction)[1])
    if symb1_type in ['int', 'nil', 'bool']:
        symb1_val = symb1_type
    elif symb1_val is None:
        symb1_val = ''
    else:
        symb1_val = 'string'

    var_frame[var_name] = tuple(['string', symb1_val])


def add_i(interpret: i.Interpret, instruction):
    var_frame, var_name = var_prepare(instruction, interpret)

    symb1_type, symb1_val = interpret.get_type_and_value_of_symb(list(instruction)[1])
    symb2_type, symb2_val = interpret.get_type_and_value_of_symb(list(instruction)[2])
    if symb1_val is None or symb2_val is None:
        exit(56)
    if symb1_type != 'int' or symb2_type != 'int':
        exit(53)
    result = symb1_val + symb2_val

    var_frame[var_name] = tuple([symb1_type, result])


def sub_i(interpret: i.Interpret, instruction):
    var_frame, var_name = var_prepare(instruction, interpret)

    symb1_type, symb1_val = interpret.get_type_and_value_of_symb(list(instruction)[1])
    symb2_type, symb2_val = interpret.get_type_and_value_of_symb(list(instruction)[2])
    if symb1_val is None or symb2_val is None:
        exit(56)
    if symb1_type != 'int' or symb2_type != 'int':
        exit(53)
    result = symb1_val - symb2_val

    var_frame[var_name] = tuple([symb1_type, result])


def mul_i(interpret: i.Interpret, instruction):
    var_frame, var_name = var_prepare(instruction, interpret)

    symb1_type, symb1_val = interpret.get_type_and_value_of_symb(list(instruction)[1])
    symb2_type, symb2_val = interpret.get_type_and_value_of_symb(list(instruction)[2])
    if symb1_val is None or symb2_val is None:
        exit(56)
    if symb1_type != 'int' or symb2_type != 'int':
        exit(53)
    result = symb1_val * symb2_val

    var_frame[var_name] = tuple([symb1_type, result])


def idiv_i(interpret: i.Interpret, instruction):
    var_frame, var_name = var_prepare(instruction, interpret)

    symb1_type, symb1_val = interpret.get_type_and_value_of_symb(list(instruction)[1])
    symb2_type, symb2_val = interpret.get_type_and_value_of_symb(list(instruction)[2])
    if symb1_val is None or symb2_val is None:
        exit(56)
    if symb1_type != 'int' or symb2_type != 'int':
        exit(53)
    if symb2_val == 0:
        exit(57)
    result = symb1_val // symb2_val

    var_frame[var_name] = tuple([symb1_type, result])


def lt_i(interpret: i.Interpret, instruction):
    var_frame, var_name = var_prepare(instruction, interpret)

    symb1_type, symb1_value = interpret.get_type_and_value_of_symb(list(instruction)[1])
    symb2_type, symb2_value = interpret.get_type_and_value_of_symb(list(instruction)[2])
    if symb1_value is None or symb2_value is None:
        exit(56)

    elif symb1_type != symb2_type:
        exit(53)
    elif symb1_type == 'bool':
        var_frame[var_name] = tuple(['bool', str(symb1_value) < str(symb2_value)])
    elif symb1_type == 'string':
        symb1_value = replace_escape_sequences(symb1_value)
        symb2_value = replace_escape_sequences(symb2_value)
        var_frame[var_name] = tuple(['bool', symb1_value < symb2_value])
    elif symb1_type == 'int':
        var_frame[var_name] = tuple(['bool', symb1_value < symb2_value])
    else:
        exit(53)


def gt_i(interpret: i.Interpret, instruction):
    var_frame, var_name = var_prepare(instruction, interpret)

    symb1_type, symb1_value = interpret.get_type_and_value_of_symb(list(instruction)[1])
    symb2_type, symb2_value = interpret.get_type_and_value_of_symb(list(instruction)[2])
    if symb1_value is None or symb2_value is None:
        exit(56)

    elif symb1_type != symb2_type:
        exit(53)
    elif symb1_type == 'bool':
        var_frame[var_name] = tuple(['bool', str(symb1_value) > str(symb2_value)])
    elif symb1_type == 'string':
        symb1_value = replace_escape_sequences(symb1_value)
        symb2_value = replace_escape_sequences(symb2_value)
        var_frame[var_name] = tuple(['bool', symb1_value > symb2_value])
    elif symb1_type == 'int':
        var_frame[var_name] = tuple(['bool', symb1_value > symb2_value])
    else:
        exit(53)


def eq_i(interpret: i.Interpret, instruction):
    var_frame, var_name = var_prepare(instruction, interpret)

    symb1_type, symb1_value = interpret.get_type_and_value_of_symb(list(instruction)[1])
    symb2_type, symb2_value = interpret.get_type_and_value_of_symb(list(instruction)[2])
    if symb1_value is None or symb2_value is None:
        exit(56)

    if symb1_type == 'nil' or symb2_type == 'nil':
        if symb1_type == symb2_type:
            var_frame[var_name] = tuple(['bool', True])
        else:
            var_frame[var_name] = tuple(['bool', False])
    elif symb1_type != symb2_type:
        exit(53)
    elif symb1_type == 'bool':
        var_frame[var_name] = tuple(['bool', str(symb1_value) == str(symb2_value)])
    elif symb1_type == 'string':
        symb1_value = replace_escape_sequences(symb1_value)
        symb2_value = replace_escape_sequences(symb2_value)
        var_frame[var_name] = tuple(['bool', symb1_value == symb2_value])
    elif symb1_type == 'int':
        var_frame[var_name] = tuple(['bool', symb1_value == symb2_value])
    else:
        exit(53)


def and_i(interpret: i.Interpret, instruction):
    var_frame, var_name = var_prepare(instruction, interpret)

    symb1_type, symb1_value = interpret.get_type_and_value_of_symb(list(instruction)[1])
    symb2_type, symb2_value = interpret.get_type_and_value_of_symb(list(instruction)[2])
    if symb1_value is None or symb2_value is None:
        exit(56)
    if symb1_type != 'bool' or symb2_type != 'bool':
        exit(53)

    var_frame[var_name] = tuple([symb1_type, symb1_value and symb2_value])


def or_i(interpret: i.Interpret, instruction):
    var_frame, var_name = var_prepare(instruction, interpret)

    symb1_type, symb1_value = interpret.get_type_and_value_of_symb(list(instruction)[1])
    symb2_type, symb2_value = interpret.get_type_and_value_of_symb(list(instruction)[2])
    if symb1_value is None or symb2_value is None:
        exit(56)
    if symb1_type != 'bool' or symb2_type != 'bool':
        exit(53)

    var_frame[var_name] = tuple(['bool', symb1_value or symb2_value])


def stri2int_i(interpret: i.Interpret, instruction):
    var_frame, var_name = var_prepare(instruction, interpret)
    symb1_type, symb1_value = interpret.get_type_and_value_of_symb(list(instruction)[1])
    symb2_type, symb2_value = interpret.get_type_and_value_of_symb(list(instruction)[2])

    if symb1_value is None or symb2_value is None:
        exit(56)
    if symb1_type != 'string' or symb2_type != 'int':
        exit(53)
    if 0 > symb2_value or symb2_value > len(symb1_value) - 1:
        exit(58)
    try:
        var_frame[var_name] = tuple(['int', ord(symb1_value[symb2_value])])
    except:
        exit(58)  # mozna jiny kod, neni specifikovano jak se ma ukoncit


def concat_i(interpret: i.Interpret, instruction):
    var_frame, var_name = var_prepare(instruction, interpret)

    symb1_type, symb1_value = interpret.get_type_and_value_of_symb(list(instruction)[1])
    symb2_type, symb2_value = interpret.get_type_and_value_of_symb(list(instruction)[2])
    if symb1_value is None or symb2_value is None:
        exit(56)
    if symb1_type != 'string' or symb2_type != 'string':
        exit(53)

    var_frame[var_name] = tuple([symb1_type, symb1_value + symb2_value])


def getchar_i(interpret: i.Interpret, instruction):
    var_frame, var_name = var_prepare(instruction, interpret)

    symb1_type, symb1_value = interpret.get_type_and_value_of_symb(list(instruction)[1])
    symb2_type, symb2_value = interpret.get_type_and_value_of_symb(list(instruction)[2])
    if symb1_value is None or symb2_value is None:
        exit(56)
    if symb1_type != 'string' or symb2_type != 'int':
        exit(53)
    if 0 > symb2_value or symb2_value > len(symb1_value) - 1:
        exit(58)
    var_frame[var_name] = tuple([symb1_type, symb1_value[symb2_value]])


def setchar_i(interpret: i.Interpret, instruction):
    var_frame, var_name = var_prepare(instruction, interpret)
    var_type, var_value = interpret.get_type_and_value_of_var(list(instruction)[0])
    symb1_type, symb1_value = interpret.get_type_and_value_of_symb(list(instruction)[1])
    symb2_type, symb2_value = interpret.get_type_and_value_of_symb(list(instruction)[2])
    if symb1_value is None or symb2_value is None or var_value is None:
        exit(56)
    if symb1_type != 'int' or symb2_type != 'string' or var_type != 'string':
        exit(53)
    if 0 > symb1_value or symb1_value > len(var_value) - 1 or len(symb2_value) == 0:
        exit(58)
    symb2_value = replace_escape_sequences(symb2_value)
    result = var_value[:symb1_value] + symb2_value[0] + var_value[symb1_value + 1:]
    var_frame[var_name] = tuple([symb2_type, result])


def jumpifeq_i(interpret: i.Interpret, instruction):
    label_name = list(instruction)[0].text
    if label_name not in interpret.label_dict.keys():
        exit(52)

    symb1_type, symb1_value = interpret.get_type_and_value_of_symb(list(instruction)[1])
    symb2_type, symb2_value = interpret.get_type_and_value_of_symb(list(instruction)[2])
    if symb1_value is None or symb2_value is None:
        exit(56)

    if symb1_type == 'nil' or symb2_type == 'nil':
        if symb1_type == symb2_type:
            interpret.inst_index = interpret.label_dict[label_name]
    elif symb1_type != symb2_type:
        exit(53)
    elif symb1_type == 'bool':
        if str(symb1_value) == str(symb2_value):
            interpret.inst_index = interpret.label_dict[label_name]
    elif symb1_type == 'string':
        symb1_value = replace_escape_sequences(symb1_value)
        symb2_value = replace_escape_sequences(symb2_value)
        if symb1_value == symb2_value:
            interpret.inst_index = interpret.label_dict[label_name]
    elif symb1_type == 'int':
        if symb1_value == symb2_value:
            interpret.inst_index = interpret.label_dict[label_name]
    else:
        exit(53)


def jumpifneq_i(interpret: i.Interpret, instruction):
    label_name = list(instruction)[0].text
    if label_name not in interpret.label_dict.keys():
        exit(52)

    symb1_type, symb1_value = interpret.get_type_and_value_of_symb(list(instruction)[1])
    symb2_type, symb2_value = interpret.get_type_and_value_of_symb(list(instruction)[2])
    if symb1_value is None or symb2_value is None:
        exit(56)

    if symb1_type == 'nil' or symb2_type == 'nil':
        if symb1_type != symb2_type:
            interpret.inst_index = interpret.label_dict[label_name]
    elif symb1_type != symb2_type:
        exit(53)
    elif symb1_type == 'bool':
        if str(symb1_value) != str(symb2_value):
            interpret.inst_index = interpret.label_dict[label_name]
    elif symb1_type == 'string':
        symb1_value = replace_escape_sequences(symb1_value)
        symb2_value = replace_escape_sequences(symb2_value)
        if symb1_value != symb2_value:
            interpret.inst_index = interpret.label_dict[label_name]
    elif symb1_type == 'int':
        if symb1_value != symb2_value:
            interpret.inst_index = interpret.label_dict[label_name]
    else:
        exit(53)
