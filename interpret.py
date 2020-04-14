#!/usr/bin/env python3
# Author: Richard Klem
# Contact: xklemr00@fit.vutbr.cz
# Created: 10.2.2020

import argparse
import os
import re
import sys
import xml.etree.ElementTree as ET
# from xml.etree.ElementTree import Element, ElementTree

import constants

arg_parser = argparse.ArgumentParser(description='Interpret', add_help=False)
arg_parser.add_argument('--help', action='store_true')
arg_parser.add_argument('--source', action='store',
                        help='vstupní soubor s XML reprezentací zdrojového kódu')
arg_parser.add_argument('--input', action='store',
                        help='soubor se vstupy pro samotnou interpretaci')


class Interpret:
    source_data = None  # XML reprezentace
    input_data = None  # vstup pro instrukci READ
    global_frame = {}
    local_frame = None
    tmp_frame = None
    frame_stack = []
    data_stack = []
    inst_index = 0
    label_dict = {}
    call_stack = []

    def __init__(self, source_file, input_file):
        if source_file:
            self.source_data = source_file
        else:
            self.source_data = sys.stdin
        if input_file:
            with open(input_file, "r") as file:
                self.input_data = file.readlines()
        #else:
         #   self.input_data = sys.stdin
        # self.local_frame = self.frame_stack[-1]

    @staticmethod
    def stop_interpreting(exit_code):
        exit(exit_code)

    @staticmethod
    def not_any_in(is_this, in_that):
        return any(i not in in_that for i in is_this)

    def inst2method(self, instruction: ET.Element):
        constants.inst2method_dict[str(instruction.get('opcode')).upper()](self, instruction)

    @staticmethod
    def check_type_value_compatibility(symb_type: str, symb_value: str):
        if symb_type == 'int':
            try:
                symb_value = int(symb_value)
            except:
                exit(32)
        elif symb_type == 'bool':
            if symb_value == 'true':
                symb_value = True
            elif symb_value == 'false':
                symb_value = False
            else:
                exit(32)
        elif symb_type == 'string':
            if symb_value is None:
                symb_value = ''
            else:
                symb_value = symb_value.replace("&lt", "<").replace("&gt", ">").replace("&amp",
                                                                                        "&")
        elif symb_type == 'nil':
            symb_value = 'nil'
        elif symb_type == 'label':
            if symb_value is None:
                exit(32)
            symb_value = symb_value.replace("&lt", "<").replace("&gt", ">").replace("&amp", "&")
            if not re.match(r'^[\-$&%*!?a-zA-Z_][\-$&%*!?\w]*$', symb_value):
                exit(32)
        elif symb_type == 'type':
            if symb_value not in ['int', 'bool', 'string', 'nil', 'label', 'type', 'var']:
                exit(32)
        else:
            exit(32)  # neznamy typ argumentu
        return symb_type, symb_value

    def get_frame_of_var(self, var: str, frame='any'):
        """
        Podiva se, jestli je promenna v zadanem ramci, pripadne v jakemkoli ramci.
        Kdyz ano, vrati tento ramec. Kdyz ne, vrati None.
        Pokus o pristup k neexistujicimu ramci vede na exit code 55.
        :param var: nazev promenne
        :param frame: nazev ramce, defaultne jakykoli ramec
        :return: ramec v kterem se promenna nachazi, jinak None
        """
        if frame == 'any':
            if self.local_frame is not None and var in self.local_frame.keys():
                return self.local_frame
            elif var in self.global_frame.keys():
                return self.global_frame
            if self.tmp_frame is not None and var in self.tmp_frame.keys():
                return self.tmp_frame
            else:
                return None
        elif frame == 'GF':
            if var in self.global_frame.keys():
                return self.global_frame
            else:
                return None
        elif frame == 'LF':
            if self.local_frame is None:
                exit(55)
            if var in self.local_frame.keys():
                return self.local_frame
            else:
                return None
        elif frame == 'TF':
            if self.tmp_frame is None:
                exit(55)
            if var in self.tmp_frame.keys():
                return self.tmp_frame
            else:
                return None

    def get_type_and_value_of_var(self, argument: ET.Element):
        """
        Metoda ziska typ a hodnotu promenne ulozene na ramci.
        Neexistujici ramec = exit(55)
        Neexistujici promenna na eistujicim ramci = exit(54)
        :param argument: objekt typu ET.Element, ktery predstavuje argument instrukce
        :return: dvojice typ, hodnota promenne
        """
        if self.not_any_in([argument.get('type')], constants.symbol_types):
            exit(32)  #neznamy typ argumentu
        if argument.get('type') != 'var':
            exit(53)  # spatny typ, musi byt var
        regex = re.match(r'^(?:([GLT]F)@)([\-$&%*!?a-zA-Z_][\-$&%*!?\w]*$)+', argument.text)
        if regex is None:
            exit(53)  # mozna 32? TODO
        # najdu ramec v kterem promenna lezi
        frame = self.get_frame_of_var(regex.group(2), regex.group(1))
        if frame is None:  # None znamena, ze promenna nebyla nalezena
            exit(54)  # neexistujici promenna v existujicim ramci
        var_type, var_value = frame[regex.group(2)]
        return var_type, var_value

    def set_type_and_value_of_var(self, dest_var: ET.Element, var_type: str, var_value: str):
        if self.not_any_in([dest_var.get('type')], constants.symbol_types):
            exit(32)  #neznamy typ argumentu
        if dest_var.get('type') != 'var':
            exit(53)  # spatny typ, musi byt var
        regex = re.match(r'^(?:([GLT]F)@)([\-$&%*!?a-zA-Z_][\-$&%*!?\w]*$)+', dest_var.text)
        if regex is None:
            exit(53)  # mozna 32? TODO
        # najdu ramec v kterem promenna lezi
        frame = self.get_frame_of_var(regex.group(2), regex.group(1))
        if frame is None:  # None znamena, ze promenna nebyla nalezena
            exit(54)  # neexistujici promenna v existujicim ramci
        var_type, var_value = self.check_type_value_compatibility(var_type, var_value)
        frame[regex.group(2)] = tuple([var_type, var_value])

    def get_type_and_value_of_symb(self, argument: ET.Element):
        symb_type = argument.get('type')
        symb_value = argument.text
        if symb_type == 'var':
            symb_type, symb_value = self.get_type_and_value_of_var(argument)
        else:
            symb_type, symb_value = self.check_type_value_compatibility(symb_type, symb_value)
        return symb_type, symb_value

    def check_arg_type_and_get_value(self, argument: ET.Element):
        """
        Kontroluje zda je promenna v ramci.
        A ZAROVEN vraci dvojici (typ promenne, jeji hodnota)!!!
        Kdyz je promenna nedefinovana, vraci None, s cimz je potreba pocitat!!!
        :param argument: xml element popisujici argument instrukce
        :return: dvojice (typ promenne, hodnota promenne)
        """
        if self.not_any_in([argument.get('type')], constants.symbol_types):
            exit(32)
        symb_type = argument.get('type')
        regex = None
        if argument.text is not None and symb_type == 'var':
            regex = re.match(r'^(?:([GLT]F)@)([\-$&%*!?a-zA-Z_][\-$&%*!?\w]*$)+', argument.text)
        symb_value = ''
        # kdyz je regex None, tak byl v tetovem poli argumentu prazdny retezec, coz je povoleno
        # pouze pro string, jinak je to chyba
        if regex is None:
            if symb_type == 'string':
                symb_value = ''
            else:
                exit(32)
        elif symb_type == 'int':
            try:
                symb_value = int(argument.text)
            except:
                exit(53)
        elif symb_type == 'var':
            if regex.lastindex != 2:
                exit(53)
            symb_value = self.get_value_from_var(regex.group(2), regex.group(1))
        elif symb_type == 'bool':
            if regex.group(2) not in ['true', 'false']:
                exit(53)
            symb_value = regex.group(2)
        elif symb_type == 'string':
            symb_value = regex.group(2)
        elif symb_type == 'nil':
            if regex.group(2) != 'nil':
                exit(53)
            symb_value = 'nil'
        elif symb_type == 'label':
            symb_value = regex.group(2)
        elif symb_type == 'type':
            if argument.text not in ['int', 'bool', 'string', 'nil', 'label', 'type', 'var']:
                exit(53)
            symb_value = argument.text
        return tuple([symb_type, symb_value])

    def check_instruction_correctness(self, instruction: ET.Element):
        """
        Check if instruction has everything what it should have and everything is correct in all
        ways(lexical, syntactic and semantic).
        :param instruction: ElementTree.Element xml element representing one instruction
        :return: true if instruction is correct in every way, false other
        """
        inst = instruction.get('opcode').upper()
        length = len(instruction[:])
        if ((inst in constants.zero_arg_opcodes and length != 0) or (
                inst in constants.one_arg_opcodes and length != 1) or (
                inst in constants.two_arg_opcodes and length != 2) or (
                inst in constants.three_arg_opcodes and length != 3)):
            exit(32)
        i = 1
        for attribute in instruction:
            if self.not_any_in(attribute.attrib.keys(), constants.argument_attributes):
                exit(32)
            if attribute.tag != 'arg' + str(i):
                exit(32)
            i = i + 1

    def get_type_from_var_value(self, value: str):
        if value in ['true', 'false']:
            return 'bool'
        elif value == 'nil':
            return 'nil'
        is_int = False
        try:
            int(value)
            is_int = True

        except:
            pass
        if is_int:
            return 'int'
        is_string = False
        try:
            str(value)
            is_string = True
        except:
            pass
        if is_string:
            return 'string'
        exit(32)

    def get_value_from_var(self, var: str, frame='any'):
        frame = self.get_frame_of_var(var, frame)
        if frame:
            return frame.get(var)

    def interpret(self):
        try:
            xmlreader = ET.parse(self.source_data)
        except ET.ParseError:
            exit(31)
        program = xmlreader.getroot()
        if len(program) == 0:
            exit(0)
        if program.tag != 'program' or program.get('language') is None or self.not_any_in(
                program.attrib.keys(), constants.program_attributes):
            exit(32)
        try:
            program[:] = sorted(program, key=lambda child: (int(child.get('order'))))
        except:
            exit(32)
        # xmlstr = ET.tostring(program, encoding="utf-8", method="xml")
        # print(xmlstr.decode("utf-8"))
        if int(next(x for x in program).get('order')) < 1:
            exit(32)

        prev_inst_order = 0
        for instruction in program:
            if instruction.tag != 'instruction':
                exit(32)
            if str(instruction.get('opcode')).upper() not in constants.opcodes:
                exit(32)
            cur_inst_order = int(instruction.get('order'))
            if prev_inst_order == cur_inst_order:
                exit(32)
            prev_inst_order = cur_inst_order
            if any(attrib not in constants.instruction_attributes for attrib in
                   instruction.attrib.keys()):
                exit(32)
            instruction[:] = sorted(instruction, key=lambda child: child.tag)

            self.check_instruction_correctness(instruction)
            if re.match(r'LABEL', instruction.get('opcode').upper()):
                if list(instruction)[0].text in self.label_dict.keys():
                    exit(52)
                if not re.match(r'(^[\-$&%*!?a-zA-Z_][\-$&%*!?\w]*$)+', list(instruction)[0].text):
                    exit(32)
                self.label_dict[list(instruction)[0].text] = self.inst_index
            self.inst_index = self.inst_index + 1

        self.inst_index = 0
        last_inst_index = len(program[:]) - 1
        while True:
            instruction = program[self.inst_index]
            self.inst2method(instruction)
            if (self.inst_index == last_inst_index) and not re.match(r'JUMP.*', instruction.get(
                    'opcode')):
                break
            self.inst_index = self.inst_index + 1
            if self.inst_index > last_inst_index:
                break


def main():
    args = arg_parser.parse_args(list(sys.argv[1:]))
    if args.help:
        if len(sys.argv) == 2:
            print('Help')
        else:
            exit(10)
    elif not args.source and not args.input:
        exit(10)
    elif (args.source or args.input) and (1 < len(sys.argv) < 4):
        interpret = Interpret(args.source, args.input)
        interpret.interpret()
    else:
        exit(10)


if __name__ == '__main__':
    sys.exit(main())
