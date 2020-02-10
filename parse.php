<?php

$zero_arg_opcodes = array("CREATEFRAME", "PUSHFRAME", "POPFRAME", "RETURN", "BREAK");
$one_arg_opcodes = array("DEFVAR", "CALL", "PUSHS", "POPS", "WRITE", "LABEL", "JUMP", "EXIT", "DPRINT");
$two_arg_opcodes = array("MOVE", "NOT", "INT2CHAR", "READ", "STRLEN", "TYPE");
$three_arg_opcodes = array("ADD", "SUB", "MUL", "IDIV", "LT", "GT", "EQ", "AND", "OR",
                           "STRI2INT", "CONCAT", "GETCHAR", "SETCHAR", "JUMPIFEQ", "JUMPIFNEQ");
$opcodes = array("CREATEFRAME", "PUSHFRAME", "POPFRAME", "RETURN", "BREAK", "DEFVAR", "CALL", "PUSHS", "POPS", "WRITE",
    "LABEL", "JUMP", "EXIT", "DPRINT", "MOVE", "NOT", "INT2CHAR", "READ", "STRLEN", "TYPE", "ADD", "SUB", "MUL", "IDIV",
    "LT", "GT", "EQ", "AND", "OR", "STRI2INT", "CONCAT", "GETCHAR", "SETCHAR", "JUMPIFEQ", "JUMPIFNEQ");

$shortopts  = "";
$shortopts .= "h";
$longopts  = array("help",);
$options = getopt($shortopts, $longopts);

function get_type_and_value($opcode, $arg){
    $type = "";
    $value = "";
    if (in_array($opcode, array("LABEL", "JUMP", "CALL"))) {
        $type = "label";
        $value = $arg;
    }
    elseif (!strcmp($opcode, "EXIT")){

        if(((preg_match("/(int)@(.*)/", $arg, $matches)) != 1) || ($matches[2] < 0 || $matches[2] > 49))
            exit(57);
        else {
            $type = $matches[1];
            $value = $matches[2];
        }
    }
    else {
        if (preg_match("/[GL]F@/", $arg)) {
            $type = "var";
            $value = $arg;
        }
        elseif (preg_match("/(string|int|bool|type)@(.*)/", $arg, $matches)) {
            $type = $matches[1];
            $value = $matches[2];
            if (!strcmp($type, 'bool'))
                $value = strtolower($value);
        }
        elseif (!strcmp($arg, "nil")){
            $type = "nil";
            $value = "nil";
        }
        elseif (preg_match("/JUMPIFN?EQ/", $opcode)){
            $type = "label";
            $value = $arg;
        }
    }
    return array($type, $value);
}
if(key_exists("help", $options)){
        echo "Toto je napoveda\n";
        exit(0);
}

# _________XMLWrite__________
$xmlWriter = new XMLWriter();
$xmlWriter->openUri('php://output');
$xmlWriter->setIndent(false);
if($xmlWriter)
{
    $xmlWriter->startDocument('1.0','UTF-8');
    $xmlWriter->startElement('program');
    $xmlWriter->writeAttribute('language', 'IPPcode20');

    $memXmlWriter = new XMLWriter();

    $memXmlWriter->openMemory();
    $memXmlWriter->setIndent(true);

    $i = 1;
    $input = fopen('php://stdin', 'r');

    if(!strcmp(strtolower($line = fgets($input)),'.ippcode20'))
        exit(21);

    $line = fgets($input);
    while($line)
    {
        $comp = preg_split('/\s+/', $line);
        $comp[0] = strtoupper($comp[0]);
        if((strcmp($comp[0], "#")) && (strcmp($comp[0], ""))){
            if(!in_array($comp[0], $opcodes))
                exit(22);
            $memXmlWriter->startElement('instruction');
            $memXmlWriter->writeAttribute('order', $i);
            $memXmlWriter->writeAttribute('opcode', $comp[0]);
            $args = array("arg1", "arg2", "arg3");
            $type = "";
            $value = "";
            if(in_array($comp[0], $one_arg_opcodes)){
                $memXmlWriter->startElement('arg1');
                list($type, $value) = get_type_and_value($comp[0], $comp[1]);
                $memXmlWriter->writeAttribute('type', $type);
                $memXmlWriter->text($value);
                $memXmlWriter->endElement();
            }
            elseif(in_array($comp[0], $two_arg_opcodes)){
                for($j = 0; $j < 2; $j++){
                    $memXmlWriter->startElement($args[$j]);
                    list($type, $value) = get_type_and_value($comp[0], $comp[$j + 1]);
                    $memXmlWriter->writeAttribute('type', $type);
                    $memXmlWriter->text($value);
                    $memXmlWriter->endElement();
                }
            }
            elseif(in_array($comp[0], $three_arg_opcodes)){
                for($j = 0; $j < 3; $j++){
                    $memXmlWriter->startElement($args[$j]);
                    list($type, $value) = get_type_and_value($comp[0], $comp[$j + 1]);
                    $memXmlWriter->writeAttribute('type', $type);
                    $memXmlWriter->text($value);
                    $memXmlWriter->endElement();
                }
            }
            //if opcode is in zero_arg_opcodes nothing has to be done
            $i++;

            #var_dump($comp);
            $memXmlWriter->endElement(); #</instruction>

            $batchXmlString = $memXmlWriter->outputMemory(true);
            $xmlWriter->writeRaw($batchXmlString);
        }
        $line = fgets($input);
    }
    $memXmlWriter->flush();
    unset($memXmlWriter);
    $xmlWriter->endElement(); # </program>
    $xmlWriter->endDocument();
}
#END of file