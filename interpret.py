#!/usr/bin/env python3
# Author: Richard Klem
# Contact: xklemr00@fit.vutbr.cz
# Created: 10.2.2020

import argparse
import os
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

    def __init__(self, source_file, input_file):
        if source_file:
            self.source_data = source_file
        if input_file:
            self.input_data = input_file
        #self.local_frame = self.frame_stack[-1]

    def inst2method(self, instruction):
        constants.inst2method_dict[str(instruction.get('opcode')).upper()](self, instruction)

    @staticmethod
    def check_instruction_correctness(instruction: ET.Element):
        """
        Check if instruction has everything what it should have and everything is correct in all
        ways(lexical, syntactic and semantic).
        :param instruction: ElementTree.Element xml element representing one instruction
        :return: true if instruction is correct in every way, false other
        """

    def interpret(self):
        xmlreader = ET.parse("supplementary-tests/int-only/order_test.src")
        program = xmlreader.getroot()
        program[:] = sorted(program, key=lambda child: (child.tag, int(child.get('order'))))
        # xmlstr = ET.tostring(program, encoding="utf-8", method="xml")
        # print(xmlstr.decode("utf-8"))
        if int(next(x for x in program).get('order')) < 1:
            exit(32)

        prev_inst_order = 0
        for instruction in program:
            if str(instruction.get('opcode')).upper() not in constants.opcodes:
                exit(32)
            cur_inst_order = int(instruction.get('order'))
            if prev_inst_order == cur_inst_order:
                exit(32)
            prev_inst_order = cur_inst_order
            if any(attrib not in constants.instruction_attributes for attrib in
                    instruction.attrib.keys()):
                exit(32)
            Interpret.check_instruction_correctness(instruction)
            print(list(instruction)[0].attrib)
            exit(5)
            self.inst2method(instruction)


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
