<?php


class parse
{
}
#$options = getopt("--help:");
#var_dump($options);

$zero_arg_opcodes = array("CREATEFRAME", "PUSHFRAME", "POPFRAME", "RETURN", "BREAK");
$one_arg_opcodes = array("DEFVAR", "CALL", "PUSHS", "POPS", "WRITE", "LABEL", "JUMP", "EXIT", "DPRINT");
$two_arg_opcodes = array("MOVE", "NOT", "INT2CHAR", "READ", "STRLEN", "TYPE");
$three_arg_opcodes = array("ADD", "SUB", "MUL", "IDIV", "LT", "GT", "EQ", "AND", "OR",
                           "STRI2INT", "CONCAT", "GETCHAR", "SETCHAR", "JUMPIFEQ", "JUMPIFNEQ");
$opcodes = array("CREATEFRAME", "PUSHFRAME", "POPFRAME", "RETURN", "BREAK", "DEFVAR", "CALL", "PUSHS", "POPS", "WRITE",
    "LABEL", "JUMP", "EXIT", "DPRINT", "MOVE", "NOT", "INT2CHAR", "READ", "STRLEN", "TYPE", "ADD", "SUB", "MUL", "IDIV",
    "LT", "GT", "EQ", "AND", "OR", "STRI2INT", "CONCAT", "GETCHAR", "SETCHAR", "JUMPIFEQ", "JUMPIFNEQ");

$shortopts  = "";
$shortopts .= "f:";  // Required value
$shortopts .= "v::"; // Optional value
$shortopts .= "h"; // These options do not accept values

$longopts  = array(
    "help",
);
$options = getopt($shortopts, $longopts);

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
    if(!strcmp(strtolower($line = fgets($input)),'.ippcode20'))
        exit(21);
    $line = fgets($input);
    while($line)
    {
        $comp = preg_split('/\s+/', $line);

        if((strcmp($comp[0], "#")) && (strcmp($comp[0], ""))){
            if(!in_array($comp[0], $opcodes))
                exit(22);
            $memXmlWriter->startElement('instruction');
            $memXmlWriter->writeAttribute('order', $i);
            $memXmlWriter->writeAttribute('opcode', $comp[0]);
            if(in_array($comp[0], $one_arg_opcodes)){
                $memXmlWriter->startElement('arg1');
                $memXmlWriter->writeAttribute('type', "TODO");
                $memXmlWriter->text($comp[1]);
                $memXmlWriter->endElement();
            }
            elseif(in_array($comp[0], $two_arg_opcodes)){
                $memXmlWriter->startElement('arg1');
                $memXmlWriter->writeAttribute('type', "TODO");
                $memXmlWriter->text($comp[1]);
                $memXmlWriter->endElement();
                $memXmlWriter->startElement('arg2');
                $memXmlWriter->writeAttribute('type', "TODO");
                $memXmlWriter->text($comp[2]);
                $memXmlWriter->endElement();
            }
            elseif(in_array($comp[0], $three_arg_opcodes)){
                $memXmlWriter->startElement('arg1');
                $memXmlWriter->writeAttribute('type', "TODO");
                $memXmlWriter->text($comp[1]);
                $memXmlWriter->endElement();
                $memXmlWriter->startElement('arg2');
                $memXmlWriter->writeAttribute('type', "TODO");
                $memXmlWriter->text($comp[2]);
                $memXmlWriter->endElement();
                $memXmlWriter->startElement('arg3');
                $memXmlWriter->writeAttribute('type', "TODO");
                $memXmlWriter->text($comp[3]);
                $memXmlWriter->endElement();
            }
            $i++;

            #var_dump($comp);
            $memXmlWriter->endElement();

            $batchXmlString = $memXmlWriter->outputMemory(true);
            $xmlWriter->writeRaw($batchXmlString);
        }
        $line = fgets($input);
    }
    $memXmlWriter->flush();
    unset($memXmlWriter);
    $xmlWriter->endElement();
    $xmlWriter->endDocument();
}