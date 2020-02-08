<?php


class parse
{
}
#$options = getopt("--help:");
#var_dump($options);

$shortopts  = "";
$shortopts .= "f:";  // Required value
$shortopts .= "v::"; // Optional value
$shortopts .= "h"; // These options do not accept values

$longopts  = array(
    "help",
);
$options = getopt($shortopts, $longopts);
#var_dump($options);

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

    $i = 0;
    $input = fopen('php://stdin', 'r');
    if(!strcmp(strtolower($line = fgets($input)),'.ippcode20'))
        exit(21);
    while($line)
    {
        $memXmlWriter->startElement('instruction');
        $memXmlWriter->writeAttribute('order', $i);
        $memXmlWriter->writeAttribute('opcode', "TODO");
        #$memXmlWriter->text('book_'.$i);
        $memXmlWriter->endElement();

        if($i%5 == 0)
        {
            $batchXmlString = $memXmlWriter->outputMemory(true);
            $xmlWriter->writeRaw($batchXmlString);
        }
        $i++;
    }
    $memXmlWriter->flush();
    unset($memXmlWriter);
    $xmlWriter->endElement();
    $xmlWriter->endDocument();
}