import re
import sys
import interpret as i

def var_prepare(instruction, interpret):
    regex = re.match(r'^([GLT]F)@([\-$&%*!?a-zA-Z_][\-$&%*!?\w]*$)+', list(instruction)[
        0].text)
    if regex.lastindex != 2:
        exit(53)
    var_name = regex.group(2)
    var_frame = interpret.get_frame_of_var(var_name, regex.group(1))
    if var_frame is None:
        exit(54)
    return var_frame, var_name


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
    interpret.call_stack.append(interpret.inst_index + 1)
    interpret.inst_index = interpret.label_dict[list(instruction)[0].text]


def pushs_i(interpret: i.Interpret, instruction):
    interpret.data_stack.append(list(instruction)[0].text)


def pops_i(interpret: i.Interpret, instruction):
    if len(interpret.data_stack) == 0:
        exit(56)

    regex = re.match(r'^([GLT]F)@([\-$&%*!?a-zA-Z_][\-$&%*!?\w]*$)+', list(instruction)[0].text)
    if regex.lastindex != 2:
        exit(32)
    var_frame = regex.group(1)
    variable = regex.group(2)

    frame = interpret.get_frame_of_var(variable, var_frame)
    if frame is not None:
        frame[variable] = interpret.data_stack.pop()


def write_i(interpret: i.Interpret, instruction):
    symb_type, symb_value = interpret.get_type_and_value_of_symb(list(instruction)[0])
    if symb_type == 'nil':
        print('', end='')
    elif symb_type == 'bool':
        print(str(symb_value).lower(), end='')
    elif symb_type == 'string':
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
    var_frame[var_name] = tuple([symb1_type, symb1_value])


def not_i(interpret: i.Interpret, instruction):
    regex = re.match(r'^(?:([GLT]F)@)?([\-$&%*!?a-zA-Z_][\-$&%*!?\w]*$)+', list(instruction)[
        0].text)
    if regex.lastindex != 2:
        exit(32)
    interpret.get_frame_of_var(regex.group(2), regex.group(1))
    if list(instruction)[1].get('type') == 'var':
        symb1_type, symb1_value = interpret.check_arg_type_and_get_value(list(instruction)[
        0])
        symb1_type = interpret.get_type_from_var_value(symb1_value)
    else:
        symb1_value = list(instruction)[1].text
        symb1_type = interpret.get_type_from_var_value(symb1_value)
    if symb1_type != 'bool':
        exit(32)
    if symb1_value == 'true':
        symb1_value = 'false'
    else:
        symb1_value = 'true'

    var_frame = regex.group(1)
    var_name = regex.group(2)
    if var_frame == 'GF':
        interpret.global_frame[var_name] = symb1_value
    elif var_frame == 'LF':
        interpret.local_frame[var_name] = symb1_value
    elif var_frame == 'TF':
        interpret.tmp_frame[var_name] = symb1_value


def int2char_i(interpret: i.Interpret, instruction):
    regex = re.match(r'^(?:([GLT]F)@)?([\-$&%*!?a-zA-Z_][\-$&%*!?\w]*$)+', list(instruction)[
        0].text)
    if regex.lastindex != 2:
        exit(32)
    var_value = regex.group(2)
    interpret.get_frame_of_var(regex.group(2), regex.group(1))
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


def read_i(interpret: i.Interpret, instruction):
    regex_var = re.match(r'^(?:([GLT]F)@)?([\-$&%*!?a-zA-Z_][\-$&%*!?\w]*$)+', list(instruction)[
        0].text)
    if regex_var is None or regex_var.lastindex != 2:
        exit(32)
    var_frame = regex_var.group(1)
    var_name = regex_var.group(2)
    interpret.get_frame_of_var(var_name, var_frame)
    symb1_type, symb1_val = interpret.check_arg_type_and_get_value(list(instruction)[1])
    if symb1_type != 'type' or symb1_val not in ['int', 'bool', 'string']:
        exit(32)
    try:
        if interpret.input_data:
            with open(interpret.input_data, "r") as file:
                read_input = file.readline()
        else:
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


def strlen_i(interpret: i.Interpret, instruction):
    regex_var = re.match(r'^(?:([GLT]F)@)?([\-$&%*!?a-zA-Z_][\-$&%*!?\w]*$)+', list(instruction)[
        0].text)
    if regex_var is None or regex_var.lastindex != 2:
        exit(32)
    var_frame = regex_var.group(1)
    var_name = regex_var.group(2)
    interpret.get_frame_of_var(var_name, var_frame)
    symb1_type, symb1_val = interpret.check_arg_type_and_get_value(list(instruction)[1])


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
    regex_var = re.match(r'^(?:([GLT]F)@)?([\-$&%*!?a-zA-Z_][\-$&%*!?\w]*$)+', list(instruction)[
        0].text)
    if regex_var.lastindex != 2:
        exit(53)
    var_frame = regex_var.group(1)
    var_value = regex_var.group(2)
    interpret.get_frame_of_var(regex_var.group(2), regex_var.group(1))
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


def mul_i(interpret: i.Interpret, instruction):
    regex_var = re.match(r'^(?:([GLT]F)@)?([\-$&%*!?a-zA-Z_][\-$&%*!?\w]*$)+', list(instruction)[
        0].text)
    if regex_var.lastindex != 2:
        exit(53)
    var_frame = regex_var.group(1)
    var_value = regex_var.group(2)
    interpret.get_frame_of_var(regex_var.group(2), regex_var.group(1))
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


def idiv_i(interpret: i.Interpret, instruction):
    regex_var = re.match(r'^(?:([GLT]F)@)?([\-$&%*!?a-zA-Z_][\-$&%*!?\w]*$)+', list(instruction)[
        0].text)
    if regex_var.lastindex != 2:
        exit(53)
    var_frame = regex_var.group(1)
    var_value = regex_var.group(2)
    interpret.get_frame_of_var(regex_var.group(2), regex_var.group(1))
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


def lt_i(interpret: i.Interpret, instruction):
    regex = re.match(r'^(?:([GLT]F)@)?([\-$&%*!?a-zA-Z_][\-$&%*!?\w]*$)+', list(instruction)[
        0].text)
    if regex.lastindex != 2:
        exit(53)
    interpret.get_frame_of_var(regex.group(2), regex.group(1))
    if list(instruction)[1].get('type') == 'var':
        symb1_type, symb1_value = interpret.check_arg_type_and_get_value(list(instruction)[
                                                                             1])
        symb1_type = interpret.get_type_from_var_value(symb1_value)
    else:
        symb1_value = list(instruction)[1].text
        symb1_type = interpret.get_type_from_var_value(symb1_value)

    if list(instruction)[2].get('type') == 'var':
        symb2_type, symb2_value = interpret.check_arg_type_and_get_value(list(instruction)[
                                                                             2])
        symb2_type = interpret.get_type_from_var_value(symb2_value)
    else:
        symb2_value = list(instruction)[2].text
        symb2_type = interpret.get_type_from_var_value(symb2_value)

    if interpret.not_any_in([symb1_type,symb2_type], ['int', 'bool', 'string']):
        exit(32)
    if symb1_type != symb2_type:
        exit(53)
    if symb1_value < symb2_value:
        result = 'true'
    else:
        result = 'false'

    var_frame = regex.group(1)
    var_name = regex.group(2)
    if var_frame == 'GF':
        interpret.global_frame[var_name] = result
    elif var_frame == 'LF':
        interpret.local_frame[var_name] = result
    elif var_frame == 'TF':
        interpret.tmp_frame[var_name] = result


def gt_i(interpret: i.Interpret, instruction):
    regex = re.match(r'^(?:([GLT]F)@)?([\-$&%*!?a-zA-Z_][\-$&%*!?\w]*$)+', list(instruction)[
        0].text)
    if regex.lastindex != 2:
        exit(53)
    interpret.get_frame_of_var(regex.group(2), regex.group(1))
    if list(instruction)[1].get('type') == 'var':
        symb1_type, symb1_value = interpret.check_arg_type_and_get_value(list(instruction)[
                                                                             1])
        symb1_type = interpret.get_type_from_var_value(symb1_value)
    else:
        symb1_value = list(instruction)[1].text
        symb1_type = interpret.get_type_from_var_value(symb1_value)

    if list(instruction)[2].get('type') == 'var':
        symb2_type, symb2_value = interpret.check_arg_type_and_get_value(list(instruction)[
                                                                             2])
        symb2_type = interpret.get_type_from_var_value(symb2_value)
    else:
        symb2_value = list(instruction)[2].text
        symb2_type = interpret.get_type_from_var_value(symb2_value)
    if interpret.not_any_in([symb1_type, symb2_type], ['int', 'bool', 'string']):
        exit(53)
    if symb1_type != symb2_type:
        exit(53)
    if symb1_value > symb2_value:
        result = 'true'
    else:
        result = 'false'

    var_frame = regex.group(1)
    var_name = regex.group(2)
    if var_frame == 'GF':
        interpret.global_frame[var_name] = result
    elif var_frame == 'LF':
        interpret.local_frame[var_name] = result
    elif var_frame == 'TF':
        interpret.tmp_frame[var_name] = result


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
        symb1_value.replace('&lt', '<').replace('&gt', '>').replace('&amp', '&')
        symb2_value.replace('&lt', '<').replace('&gt', '>').replace('&amp', '&')
        for char_int in range(127):
            char_str = chr(char_int)
            if char_int < 10:
                char_int = '00' + str(char_int)
            elif char_int < 100:
                char_int = '0' + str(char_int)
            symb1_value = symb1_value.replace('\\' + str(char_int), char_str)
            symb2_value = symb2_value.replace('\\' + str(char_int), char_str)
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


def str2int_i(interpret: i.Interpret, instruction):
    regex = re.match(r'^(?:([GLT]F)@)?([\-$&%*!?a-zA-Z_][\-$&%*!?\w]*$)+', list(instruction)[
        0].text)
    if regex.lastindex != 2:
        exit(53)
    interpret.get_frame_of_var(regex.group(2), regex.group(1))
    if list(instruction)[1].get('type') == 'var':
        symb1_type, symb1_value = interpret.check_arg_type_and_get_value(list(instruction)[
                                                                             1])
        symb1_type = interpret.get_type_from_var_value(symb1_value)
    else:
        symb1_value = list(instruction)[1].text
        symb1_type = interpret.get_type_from_var_value(symb1_value)
    if symb1_type != 'string':
        exit(53)

    if list(instruction)[2].get('type') == 'var':
        symb2_type, symb2_value = interpret.check_arg_type_and_get_value(list(instruction)[
                                                                             2])
        symb2_type = interpret.get_type_from_var_value(symb2_value)
    else:
        symb2_value = list(instruction)[2].text
        symb2_type = interpret.get_type_from_var_value(symb2_value)
    if symb2_type != 'int':
        exit(53)

    if len(symb1_value) < symb2_value:
        exit(58)

    result = ord(symb1_value[symb2_type])

    var_frame = regex.group(1)
    var_name = regex.group(2)
    if var_frame == 'GF':
        interpret.global_frame[var_name] = result
    elif var_frame == 'LF':
        interpret.local_frame[var_name] = result
    elif var_frame == 'TF':
        interpret.tmp_frame[var_name] = result


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
    regex = re.match(r'^(?:([GLT]F)@)?([\-$&%*!?a-zA-Z_][\-$&%*!?\w]*$)+', list(instruction)[
        0].text)
    if regex is None or regex.lastindex != 2:
        exit(53)
    interpret.get_frame_of_var(regex.group(2), regex.group(1))
    if list(instruction)[1].get('type') == 'var':
        symb1_type, symb1_value = interpret.check_arg_type_and_get_value(list(instruction)[
                                                                             1])
        symb1_type = interpret.get_type_from_var_value(symb1_value)
    else:
        symb1_value = list(instruction)[1].text
        symb1_type = interpret.get_type_from_var_value(symb1_value)
    if symb1_type != 'string':
        exit(53)

    if list(instruction)[2].get('type') == 'var':
        symb2_type, symb2_value = interpret.check_arg_type_and_get_value(list(instruction)[
                                                                             2])
        symb2_type = interpret.get_type_from_var_value(symb2_value)
    else:
        symb2_value = list(instruction)[2].text
        symb2_type = interpret.get_type_from_var_value(symb2_value)
    if symb2_type != 'int':
        exit(53)

    if len(symb1_value) < int(symb2_value):
        exit(58)

    result = symb1_value[symb2_type]

    var_frame = regex.group(1)
    var_name = regex.group(2)
    if var_frame == 'GF':
        interpret.global_frame[var_name] = result
    elif var_frame == 'LF':
        interpret.local_frame[var_name] = result
    elif var_frame == 'TF':
        interpret.tmp_frame[var_name] = result


def setchar_i(interpret: i.Interpret, instruction):
    regex = re.match(r'^(?:([GLT]F)@)?([\-$&%*!?a-zA-Z_][\-$&%*!?\w]*$)+', list(instruction)[
        0].text)
    if regex.lastindex != 2:
        exit(53)
    interpret.get_frame_of_var(regex.group(2), regex.group(1))

    var_frame = regex.group(1)
    var_name = regex.group(2)
    var_value = interpret.get_value_from_var(var_name)
    var_type = interpret.get_type_from_var_value(var_value)

    if var_type != 'string':
        exit(53)
    if list(instruction)[1].get('type') == 'var':
        symb1_type, symb1_value = interpret.check_arg_type_and_get_value(list(instruction)[1])
        symb1_type = interpret.get_type_from_var_value(symb1_value)
    else:
        symb1_value = list(instruction)[1].text
        symb1_type = interpret.get_type_from_var_value(symb1_value)
    if symb1_type != 'int':
        exit(53)

    if list(instruction)[2].get('type') == 'var':
        symb2_type, symb2_value = interpret.check_arg_type_and_get_value(list(instruction)[2])
        symb2_type = interpret.get_type_from_var_value(symb2_value)
    else:
        symb2_value = list(instruction)[2].text[0]
        symb2_type = interpret.get_type_from_var_value(symb2_value)
    if symb2_type != 'string':
        exit(53)

    if len(symb1_value) < symb2_value:
        exit(58)

    result = var_value[:symb1_value] + symb2_value + var_value[symb1_value + 1:]

    if var_frame == 'GF':
        interpret.global_frame[var_name] = result
    elif var_frame == 'LF':
        interpret.local_frame[var_name] = result
    elif var_frame == 'TF':
        interpret.tmp_frame[var_name] = result


def jumpifeq_i(interpret: i.Interpret, instruction):
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


def jumpifneq_i(interpret: i.Interpret, instruction):
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
