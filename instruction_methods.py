import re
import sys


def createframe_i(interpret, instruction):
    interpret.tmp_frame = {}


def pushframe_i(interpret, instruction):
    if interpret.tmp_frame is None:
        exit(55)
    interpret.frame_stack.append(interpret.tmp_frame)
    interpret.local_frame = interpret.frame_stack[-1]
    interpret.tmp_frame = None


def popframe_i(interpret, instruction):
    if len(interpret.frame_stack) == 0:
        exit(55)
    interpret.tmp_frame = interpret.frame_stack.pop()
    if len(interpret.frame_stack) != 0:
        interpret.local_frame = interpret.frame_stack[-1]
    else:
        interpret.local_frame = None


def return_i(interpret, instruction):
    if len(interpret.call_stack) == 0:
        exit(56)
    interpret.inst_index = interpret.call_stack.pop()


def break_i(interpret, instruction):
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


def defvar_i(interpret, instruction):
    regex = re.match(r'^([GLT]F)@([\-$&%*!?a-zA-Z_][\-$&%*!?\w]*$)+', list(instruction)[0].text)
    if regex.lastindex != 2:
        exit(32)
    frame = regex.group(1)
    variable = regex.group(2)
    if frame == 'GF':
        if interpret.check_var_in_frame(list(instruction)[0].text, 'GF'):
            exit(52)
        interpret.global_frame[variable] = None
    elif frame == 'LF':
        if interpret.check_var_in_frame(list(instruction)[0].text, 'LF'):
            exit(52)
        interpret.local_frame[variable] = None
    elif frame == 'TF':
        if interpret.check_var_in_frame(list(instruction)[0].text, 'TF'):
            exit(52)
        interpret.tmp_frame[variable] = None


def call_i(interpret, instruction):
    if list(instruction)[0].text not in interpret.label_dict.keys():
        exit(52)
    interpret.call_stack.append(interpret.inst_index + 1)
    interpret.inst_index = interpret.label_dict[list(instruction)[0].text]


def pushs_i(interpret, instruction):
    interpret.data_stack.append(list(instruction)[0].text)


def pops_i(interpret, instruction):
    if len(interpret.data_stack) == 0:
        exit(56)

    regex = re.match(r'^([GLT]F)@([\-$&%*!?a-zA-Z_][\-$&%*!?\w]*$)+', list(instruction)[0].text)
    if regex.lastindex != 2:
        exit(32)
    var_frame = regex.group(1)
    variable = regex.group(2)

    frame = interpret.check_var_in_frame(variable, var_frame)
    if frame is not None:
        frame[variable] = interpret.data_stack.pop()


def write_i(interpret, instruction):
    if list(instruction)[0].attrib.keys() == 'bool':
        print(list(instruction)[0].text.lower(), end='')
    elif list(instruction)[0].text == 'nil@nil':
        print('', end='')
    else:
        regex = re.match(r'^([GLT]F)@([\-$&%*!?a-zA-Z_][\-$&%*!?\w]*$)+', list(instruction)[
            0].text)
        if regex is not None and regex.lastindex == 2:
            print(interpret.get_value_from_var(regex.group(2), regex.group(1)), end='')
        elif regex is None:
            symb_value = list(instruction)[0].text
            symb_value.replace('&lt', '<')
            symb_value.replace('&gt', '>')
            symb_value.replace('&amp', '&')
            for char_int in range(127):
                char_str = chr(char_int)
                if char_int < 10:
                    char_int = '00' + str(char_int)
                elif char_int < 100:
                    char_int = '0' + str(char_int)
                symb_value = symb_value.replace('\\' + str(char_int), char_str)
            print(symb_value, end='')
        else:
            exit(32)


def label_i(interpret, instruction):
    pass


def jump_i(interpret, instruction):
    if list(instruction)[0].text not in interpret.label_dict.keys():
        exit(52)
    interpret.inst_index = interpret.label_dict[list(instruction)[0].text]


def exit_i(interpret, instruction):
    retcode = -1
    try:
        retcode = int(list(instruction)[0].text)
    except:
        pass
    if 0 <= retcode <= 49:
        exit(retcode)
    else:
        exit(57)


def dprint_i(interpret, instruction):
    regex = re.match(r'([GLT]F)@([\-$&%*!?a-zA-Z_][\-$&%*!?\w]*$)+', list(instruction)[
        0].text)
    if regex is None or regex.lastindex != 2:
        _, symb1_val = interpret.check_arg_type_and_get_value(list(instruction)[0])
    else:
        symb1_val = interpret.get_value_from_var(regex.group(2), regex.group(1))
    print(symb1_val, file=sys.stderr)


def move_i(interpret, instruction):
    dest = None
    regex_dest = re.match(r'([GLT]F)@([\-$&%*!?a-zA-Z_][\-$&%*!?\w]*$)+', list(instruction)[
        0].text)
    src_type, src_value = interpret.check_arg_type_and_get_value(list(instruction)[1])
    interpret.check_var_in_frame(regex_dest.group(2), regex_dest.group(1))

    if regex_dest and regex_dest.lastindex == 2:
        dest = regex_dest.group(2)
    else:
        exit(53)  # špatné typy operandů
    src = src_value

    var_frame = regex_dest.group(1)
    if var_frame == 'GF':
        interpret.global_frame[dest] = src
    elif var_frame == 'LF':
        interpret.local_frame[dest] = src
    elif var_frame == 'TF':
        interpret.tmp_frame[dest] = src


def not_i(interpret, instruction):
    ...


def int2char_i(interpret, instruction):
    regex = re.match(r'^(?:([GLT]F)@)?([\-$&%*!?a-zA-Z_][\-$&%*!?\w]*$)+', list(instruction)[
        0].text)
    if regex.lastindex != 2:
        exit(32)
    var_value = regex.group(2)
    interpret.check_var_in_frame(regex.group(2), regex.group(1))
    symb1_type, symb1_val = '', ''
    regex2 = re.match(r'^(?:([GLT]F)@)?([\-$&%*!?a-zA-Z_][\-$&%*!?\w]*$)+', list(instruction)[
        1].text)
    if list(instruction)[1].get('type') == 'var':
        if regex.lastindex != 2:
            exit(32)
        symb1_type, symb1_val = interpret.check_arg_type_and_get_value(list(instruction)[1])
        try:
            symb1_val = chr(int(symb1_val))
            symb1_type = interpret.get_type_from_var_value(symb1_val)
        except:
            exit(32)  # 53?

    if symb1_type != 'string':
        exit(53)
    var_frame = list(instruction)[0].text[0:2]
    if var_frame == 'GF':
        interpret.global_frame[var_value] = symb1_val
    elif var_frame == 'LF':
        interpret.local_frame[var_value] = symb1_val
    elif var_frame == 'TF':
        interpret.tmp_frame[var_value] = symb1_val


def read_i(interpret, instruction):
    regex_var = re.match(r'^(?:([GLT]F)@)?([\-$&%*!?a-zA-Z_][\-$&%*!?\w]*$)+', list(instruction)[
        0].text)
    if regex_var is None or regex_var.lastindex != 2:
        exit(32)
    var_frame = regex_var.group(1)
    var_name = regex_var.group(2)
    interpret.check_var_in_frame(var_name, var_frame)
    symb1_type, symb1_val = interpret.check_arg_type_and_get_value(list(instruction)[1])
    if symb1_type != 'type' or symb1_val not in ['int', 'bool', 'string']:
        exit(32)
    try:
        read_input = input()
    except:
        read_input = 'nil'

    if symb1_type == 'int':
        try:
            read_input = int(read_input)
        except:
            exit(32)
    elif symb1_type == 'string':
        try:
            read_input = str(read_input)
        except:
            exit(32)
    elif symb1_type == 'bool':
        if read_input != 'true':
            read_input = 'false'

    if var_frame == 'GF':
        interpret.global_frame[var_name] = read_input
    elif var_frame == 'LF':
        interpret.local_frame[var_name] = read_input
    elif var_frame == 'TF':
        interpret.tmp_frame[var_name] = read_input


def strlen_i(interpret, instruction):
    regex_var = re.match(r'^(?:([GLT]F)@)?([\-$&%*!?a-zA-Z_][\-$&%*!?\w]*$)+', list(instruction)[
        0].text)
    if regex_var is None or regex_var.lastindex != 2:
        exit(32)
    var_frame = regex_var.group(1)
    var_name = regex_var.group(2)
    interpret.check_var_in_frame(var_name, var_frame)
    symb1_type, symb1_val = interpret.check_arg_type_and_get_value(list(instruction)[1])


def type_i(interpret, instruction):
    regex_var = re.match(r'^(?:([GLT]F)@)?([\-$&%*!?a-zA-Z_][\-$&%*!?\w]*$)+', list(instruction)[
        0].text)
    if regex_var.lastindex != 2:
        exit(32)
    var_frame = regex_var.group(1)
    var_name = regex_var.group(2)
    interpret.check_var_in_frame(regex_var.group(2), regex_var.group(1))
    symb1_type, symb1_val = interpret.check_arg_type_and_get_value(list(instruction)[1])
    symb1_type = interpret.get_type_from_var_value(symb1_val)
    if symb1_val is None:
        symb1_type = ''
    if var_frame == 'GF':
        interpret.global_frame[var_name] = symb1_type
    elif var_frame == 'LF':
        interpret.local_frame[var_name] = symb1_type
    elif var_frame == 'TF':
        interpret.tmp_frame[var_name] = symb1_type


def add_i(interpret, instruction):
    regex_var = re.match(r'^(?:([GLT]F)@)?([\-$&%*!?a-zA-Z_][\-$&%*!?\w]*$)+', list(instruction)[
        0].text)
    if regex_var.lastindex != 2:
        exit(32)
    var_frame = regex_var.group(1)
    var_value = regex_var.group(2)
    interpret.check_var_in_frame(regex_var.group(2), regex_var.group(1))
    symb1_type, symb1_val = interpret.check_arg_type_and_get_value(list(instruction)[1])
    symb2_type, symb2_val = interpret.check_arg_type_and_get_value(list(instruction)[2])

    if '' or None in [symb1_val, symb2_val]:
        exit(32)

    symb1_type = interpret.get_type_from_var_value(symb1_val)
    symb2_type = interpret.get_type_from_var_value(symb2_val)
    if symb1_type != 'int' or symb2_type != 'int':
        exit(53)
    result = symb1_val + symb2_val

    var_frame = var_frame[0:2]
    if var_frame == 'GF':
        interpret.global_frame[var_value] = result
    elif var_frame == 'LF':
        interpret.local_frame[var_value] = result
    elif var_frame == 'TF':
        interpret.tmp_frame[var_value] = result


def sub_i(interpret, instruction):
    regex_var = re.match(r'^(?:([GLT]F)@)?([\-$&%*!?a-zA-Z_][\-$&%*!?\w]*$)+', list(instruction)[
        0].text)
    if regex_var.lastindex != 2:
        exit(32)
    var_frame = regex_var.group(1)
    var_value = regex_var.group(2)
    interpret.check_var_in_frame(regex_var.group(2), regex_var.group(1))
    symb1_type, symb1_val = interpret.check_arg_type_and_get_value(list(instruction)[1])
    symb2_type, symb2_val = interpret.check_arg_type_and_get_value(list(instruction)[2])

    if '' or None in [symb1_val, symb2_val]:
        exit(32)
    symb1_type = interpret.get_type_from_var_value(symb1_val)
    symb2_type = interpret.get_type_from_var_value(symb2_val)
    if symb1_type != 'int' or symb2_type != 'int':
        exit(53)
    result = symb1_val - symb2_val

    var_frame = var_frame[0:2]
    if var_frame == 'GF':
        interpret.global_frame[var_value] = result
    elif var_frame == 'LF':
        interpret.local_frame[var_value] = result
    elif var_frame == 'TF':
        interpret.tmp_frame[var_value] = result


def mul_i(interpret, instruction):
    regex_var = re.match(r'^(?:([GLT]F)@)?([\-$&%*!?a-zA-Z_][\-$&%*!?\w]*$)+', list(instruction)[
        0].text)
    if regex_var.lastindex != 2:
        exit(32)
    var_frame = regex_var.group(1)
    var_value = regex_var.group(2)
    interpret.check_var_in_frame(regex_var.group(2), regex_var.group(1))
    symb1_type, symb1_val = interpret.check_arg_type_and_get_value(list(instruction)[1])
    symb2_type, symb2_val = interpret.check_arg_type_and_get_value(list(instruction)[2])

    if '' or None in [symb1_val, symb2_val]:
        exit(32)
    symb1_type = interpret.get_type_from_var_value(symb1_val)
    symb2_type = interpret.get_type_from_var_value(symb2_val)
    if symb1_type != 'int' or symb2_type != 'int':
        exit(53)
    result = symb1_val * symb2_val

    var_frame = var_frame[0:2]
    if var_frame == 'GF':
        interpret.global_frame[var_value] = result
    elif var_frame == 'LF':
        interpret.local_frame[var_value] = result
    elif var_frame == 'TF':
        interpret.tmp_frame[var_value] = result


def idiv_i(interpret, instruction):
    regex_var = re.match(r'^(?:([GLT]F)@)?([\-$&%*!?a-zA-Z_][\-$&%*!?\w]*$)+', list(instruction)[
        0].text)
    if regex_var.lastindex != 2:
        exit(32)
    var_frame = regex_var.group(1)
    var_value = regex_var.group(2)
    interpret.check_var_in_frame(regex_var.group(2), regex_var.group(1))
    symb1_type, symb1_val = interpret.check_arg_type_and_get_value(list(instruction)[1])
    symb2_type, symb2_val = interpret.check_arg_type_and_get_value(list(instruction)[2])

    if '' or None in [symb1_val, symb2_val]:
        exit(32)
    symb1_type = interpret.get_type_from_var_value(symb1_val)
    symb2_type = interpret.get_type_from_var_value(symb2_val)
    if symb1_type != 'int' or symb2_type != 'int':
        exit(53)
    if symb2_val == 0:
        exit(57)
    result = symb1_val // symb2_val

    var_frame = var_frame[0:2]
    if var_frame == 'GF':
        interpret.global_frame[var_value] = result
    elif var_frame == 'LF':
        interpret.local_frame[var_value] = result
    elif var_frame == 'TF':
        interpret.tmp_frame[var_value] = result


def lt_i(interpret, instruction):
    ...


def gt_i(interpret, instruction):
    ...


def eq_i(interpret, instruction):
    ...


def and_i(interpret, instruction):
    ...


def or_i(interpret, instruction):
    ...


def str2int_i(interpret, instruction):
    ...


def concat_i(interpret, instruction):
    ...


def getchar_i(interpret, instruction):
    ...


def setchar_i(interpret, instruction):
    ...


def jumpifeq_i(interpret, instruction):
    _, label = interpret.check_arg_type_and_get_value(list(instruction)[0])
    symb1_type, symb1_val = interpret.check_arg_type_and_get_value(list(instruction)[1])
    symb2_type, symb2_val = interpret.check_arg_type_and_get_value(list(instruction)[2])

    if '' in [label, symb1_val, symb2_val]:
        exit(32)
    if symb1_type == 'var':
        symb1_type = interpret.get_type_from_var_value(symb1_val)
    if symb2_type == 'var':
        symb2_type = interpret.get_type_from_var_value(symb2_type)
    if symb1_type != symb2_type:
        exit(53)
    if symb1_val == symb2_val:
        if label not in interpret.label_dict.keys():
            exit(52)
        interpret.inst_index = interpret.label_dict[label]


def jumpifneq_i(interpret, instruction):
    _, label = interpret.check_arg_type_and_get_value(list(instruction)[0])
    symb1_type, symb1_val = interpret.check_arg_type_and_get_value(list(instruction)[1])
    symb2_type, symb2_val = interpret.check_arg_type_and_get_value(list(instruction)[2])

    if '' in [label, symb1_val, symb2_val]:
        exit(32)
    if symb1_type != symb2_type:
        exit(53)
    if symb1_val != symb2_val:
        if label not in interpret.label_dict.keys():
            exit(52)
        interpret.inst_index = interpret.label_dict[label]
