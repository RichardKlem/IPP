<?php
$batchSize = 1;
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
$longopts  = array("help", "stats:", "loc", "comments", "jumps");
$options = getopt($shortopts, $longopts);

function get_type_and_value($opcode, $arg){
    $type = "";
    $value = "";
    if (in_array($opcode, array("LABEL", "JUMP", "CALL"))) {
        $type = "label";
        if (preg_match('/^[\-\$&%*!?a-zA-Z_][\-\$&%*!?\w]*$/', $arg, $matches))
            $value = $arg;
        else
            exit(23);

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
        if (preg_match('/[GLT]F@(.*)/', $arg, $matches_0)){
            if (preg_match('/^[\-\$&%*!?a-zA-Z_][\-\$&%*!?\w]*$/', $matches_0[1], $matches)){
                $type = "var";
                $value = $arg;
            }
            else
                exit(23);
        }
        elseif (preg_match("/(string|int|type)@(.*)/", $arg, $matches)) {
            $type = $matches[1];
            $value = $matches[2];
        }
        elseif (preg_match('/bool@(true|false)/', $arg, $matches)){
            $type = "bool";
            $value = strtolower($matches[1]);
        }
        elseif (preg_match("/(nil)@/", $arg)){
            $type = "nil";
            $value = "nil";
        }
        elseif (preg_match("/JUMPIFN?EQ/", $opcode)){
            $type = "label";
            if (preg_match('/^[\-\$&%*!?a-zA-Z_][\-\$&%*!?\w]*$/', $arg, $matches))
                $value = $arg;
            else
                exit(23);
        }
    }
    global $zero_arg_opcodes, $opcodes;
    if((!strcmp($type,"")) && (!in_array($opcode, $zero_arg_opcodes)) && (in_array($opcode, $opcodes)))
        exit(23);
    return array($type, $value);
}

/**
 * @brief Function represent question "Is there too many args?". Returns 0 if answer is false, 1 otherwise.
 * @param $comp array array of args
 * @param $num_of_correct_args int expected num of args
 * @return int 0 if there are correct num of args, 1 else
 */
function too_many_args($comp, $num_of_correct_args){
    # comp always contains opcode and newline character, so we need to add 2 to get needed number
    if (count($comp) == $num_of_correct_args + 1)
        return 0;
    else
        return 1;
}
if(key_exists("help", $options)){
        echo "Toto je napoveda\n";
        exit(0);
}
# _________XMLWrite__________
$xmlWriter = new XMLWriter();
$xmlWriter->openUri('php://output');
$xmlWriter->setIndent(true);
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

    $line = trim(fgets($input)); #trim cuts whitespaces on both sides of input line
    while($line[0] === "" || $line[0] === "#"){
        $line = fgets($input);
    }
    $line = strtolower($line);
    $resultos = preg_match('/^\.ippcode20$/', $line);

    if ($resultos != 1)
        exit(21);

    while (!feof($input)) {
        $line = fgets($input);
        $line = rtrim($line, "\r");  # delete carriage return
        $line = rtrim($line, "\n");  # delete newline
        # comments are thrown away
        $comment_index = strpos($line, "#");
        if ($comment_index !== false) {
            $line = substr($line, 0, $comment_index);
            $line = rtrim($line);
        }
        if ($line !== "")
            break;
    }
    #echo $line;
    while($line)
    {
        #echo $line;
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
            if(in_array($comp[0], $zero_arg_opcodes))
                if(too_many_args($comp, 0))
                    exit(23);
            if(in_array($comp[0], $one_arg_opcodes)){
                $memXmlWriter->startElement('arg1');
                if(too_many_args($comp, 1))
                    exit(23);
                list($type, $value) = get_type_and_value($comp[0], $comp[1]);
                $memXmlWriter->writeAttribute('type', $type);
                $memXmlWriter->text($value);
                $memXmlWriter->endElement();
            }
            elseif(in_array($comp[0], $two_arg_opcodes)){
                if ($comp[0] === "READ"){

                    $memXmlWriter->startElement("arg1");
                    if(too_many_args($comp, 2))
                        exit(23);
                    elseif (preg_match("/[GLT]F@/", $comp[1])) {
                        $type = "var";
                        $value = $comp[1];
                    }
                    else
                        exit(23);
                    $memXmlWriter->writeAttribute('type', $type);
                    $memXmlWriter->text($value);
                    $memXmlWriter->endElement();

                    $memXmlWriter->startElement("arg2");
                    if (preg_match("/(string|int|bool)/", $comp[2], $matches)){
                        $type = "type";
                        $value = $matches[0];
                    }
                    else
                        exit(23);
                    $memXmlWriter->writeAttribute('type', $type);
                    $memXmlWriter->text($value);
                    $memXmlWriter->endElement();
                }
                else{
                    for($j = 0; $j < 2; $j++){
                        $memXmlWriter->startElement($args[$j]);
                        if(too_many_args($comp, 2))
                            exit(23);
                        list($type, $value) = get_type_and_value($comp[0], $comp[$j + 1]);
                        $memXmlWriter->writeAttribute('type', $type);
                        $memXmlWriter->text($value);
                        $memXmlWriter->endElement();
                    }
                }
            }
            elseif(in_array($comp[0], $three_arg_opcodes)){
                for($j = 0; $j < 3; $j++){
                    $memXmlWriter->startElement($args[$j]);
                    if(too_many_args($comp, 3))
                        exit(23);
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
        $line = rtrim($line, "\r");  # delete carriage return
        $line = rtrim($line, "\n");  # delete newline
        # comments are thrown away
        $comment_index = strpos($line, "#");
        if ($comment_index !== false){
            $line = substr($line, 0, $comment_index);
            $line = rtrim($line);
        }
    }
    $memXmlWriter->flush();
    unset($memXmlWriter);
    $xmlWriter->endElement(); # </program>
    $xmlWriter->endDocument();
}

#END of file

#echo $options;

#var_dump($options);