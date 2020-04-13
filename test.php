<?php
$passed_count = 0;
$failed_count = 0;
$shortopts = "";
$longopts  = array("help", "directory:", "recursive", "parse-script:", "int-script:", "parse-only", "int-only", "jexamxml:");
$allopts = array("help" => false, "directory" => getcwd(), "recursive" => false, "parse-script" => "parse.php",
                 "int-script" => "interpret.py", "parse-only" => false, "int-only" => false,
                 "jexamxml" => "/pub/courses/ipp/jexamxml/jexamxml.jar");
$options = getopt($shortopts, $longopts);

function print_help() {
    //TODO
    printf("Napoveda");
}

foreach (array_keys($options) as $option) {
    if (! key_exists($option, $allopts))
        exit(10);
    $allopts[$option] = $options[$option];
    if ($allopts[$option] === false)
        $allopts[$option] = true;
}

if (key_exists("help", $options)){
    if (count($options) != 1) {
        exit(10);
    }
    print_help();
    exit(0);
}

if (($allopts["parse-only"] and $allopts["int-only"]) or ($allopts["parse-only"] and key_exists("int-script", $options)) or
    ($allopts["int-only"] and key_exists("parse-script", $options)))
    exit(10);

$src_filenames = array();
$out_filenames = array();
$in_filenames = array();
$rc_filenames = array();

function recursive_dir_walk($dir){
    global $src_filenames, $out_filenames, $in_filenames, $rc_filenames;
    foreach (scandir($dir) as $file_or_dir) {
        if ($file_or_dir === "." or $file_or_dir === "..")
            continue;
        if (is_dir($dir.DIRECTORY_SEPARATOR.$file_or_dir)){
            recursive_dir_walk($dir.DIRECTORY_SEPARATOR.$file_or_dir);
        }
        else {
            preg_match("/(.+\.src)/", $file_or_dir, $match_src);
            preg_match("/(.+\.out)/", $file_or_dir, $match_out);
            preg_match("/(.+\.in)/", $file_or_dir, $match_in);
            preg_match("/(.+\.rc)/", $file_or_dir, $match_rc);
            if ($match_src)
                array_push($src_filenames, $dir.DIRECTORY_SEPARATOR.$match_src[1]);
            if ($match_out)
                array_push($out_filenames, $dir.DIRECTORY_SEPARATOR.$match_out[1]);
            if ($match_in)
                array_push($in_filenames, $dir.DIRECTORY_SEPARATOR.$match_in[1]);
            if ($match_rc)
                array_push($rc_filenames, $dir.DIRECTORY_SEPARATOR.$match_rc[1]);
        }
    }
}
recursive_dir_walk($allopts["directory"]);
foreach ($src_filenames as $src_file) {
    preg_match("/(.+)\.src/", $src_file, $file_core_name);
    if (!in_array($file_core_name[1].".out", $out_filenames))
        fclose(fopen($file_core_name[1].".out", "w"));
    if (!in_array($file_core_name[1].".in", $in_filenames))
        fclose(fopen($file_core_name[1].".in", "w"));
    if (!in_array($file_core_name[1].".rc", $rc_filenames)) {
        fclose(fopen($file_core_name[1].".rc", "w"));
        echo "0" > $file_core_name[1].".rc";
    }
}
$html_output = "";

function html_print_failed($test_name, $expected_rc, $actual_rc, $script='interpret.py'){
    global $html_output;
    if ($expected_rc != $actual_rc){
        $detail = "Očekáváno: {$expected_rc}, vráceno: {$actual_rc}";
    }
    else
        $detail = "Výstup není shodný.";
    $html_output .= "<tr>
    <th><span style=\"color: red; \">FAILED</span></th>
    <th>{$detail}</th>
    <th>{$script}</th>
    <th>{$test_name}</th>
  </tr>";
}

function html_print_passed($test_name, $script='interpret.py'){
    global $html_output;
    $html_output .= "<tr>
    <th><span style=\"color: green; \">PASSED</span></th>
    <th> </th>
    <th>$script</th>
    <th>{$test_name}</th>
  </tr>";
}

function parse_test($file_name, $interpret=false){
    global $allopts;
    global $passed_count;
    global $failed_count;
    $success = false;
    preg_match("/(.+)\.src/", $file_name, $file_core_name);
    $file_core_name = $file_core_name[1];
    $act_out_file = $file_core_name.".prsout";
    $expected_rc = intval(file_get_contents($file_core_name.".rc"));
    $command = "php7.4 {$allopts['parse-script']} < '{$file_name}' > '{$act_out_file}'";
    exec($command, $output, $retcode);
    //both - parse i interpret
    if($interpret) {
        if ($retcode === 0){
            $success = true;
        }
        else{
            if ($retcode !== $expected_rc){
                $failed_count++;
                html_print_failed($file_core_name, $expected_rc, $retcode, 'parse.php');
            }
            //kdyz je vse ok, tak nepisu ani fail ani pass, protoze pobezi jeste interpret.py
        }
    }
    //parse-only
    else {
        //exit kody se nerovnaji
        if ($retcode !== $expected_rc) {
            $failed_count++;
            html_print_failed($file_core_name, $expected_rc, $retcode, 'parse.php');
        }
        //exit kody se rovnaji
        else {
            if ($retcode !== 0){
                $passed_count++;
                html_print_passed($file_core_name, 'parse.php');
            }
            //exit kod je 0, musi se provest porovnani vystupu
            else {
                $out_file = $file_core_name.".out";
                $options = "/pub/courses/ipp/jexamxml/options";
                $command_jexamxml = "java -jar {$allopts['jexamxml']} {$out_file} {$act_out_file} /O:{$options}";
                exec($command_jexamxml, $jxml_output, $jxml_retcode);
                if ($jxml_retcode !== 0) {
                    $failed_count++;
                    html_print_failed($file_core_name, $expected_rc, $retcode, 'parse.php');
                }
                else {
                    $passed_count++;
                    if (!$interpret)
                        html_print_passed($file_core_name, 'parse.php');
                }
            }
        }
        unlink($act_out_file); //smaze docasny vystup
    } //konec parse-only vetve
    return $success;
}

function interpret_test($file_name, $extension='.src'){
    global $allopts;
    global $failed_count;
    global $passed_count;
    //pokud se pousti interpret, bud je int-only, pak je soubor .src, anebo musel byt both a tak tam musi byt taky
    // soubor .src, i kdyz se pro interpret pouzije jiny jako vstup
    preg_match("/(.+)\.src/", $file_name, $file_core_name);
    $file_core_name = $file_core_name[1];
    $act_out_file = $file_core_name.".intout";
    $in_file = $file_core_name.".in";
    $out_file = $file_core_name.".out";
    $file_name = $file_core_name.$extension; //nastavi se jemno souboru s xml vstupem podle rezimu int-only nebo both
    $expected_rc = intval(file_get_contents($file_core_name.".rc"));
    $command = "python3.8 {$allopts['int-script']} --source={$file_name} --input={$in_file} > {$act_out_file}";
    exec($command, $output, $retcode);
    if ($retcode !== $expected_rc){
        $failed_count++;
        html_print_failed($file_core_name, $expected_rc, $retcode);
    }
    //exit kody se rovnaji
    else {
        //interpret ma skoncit chybou, tak se i stalo, vse je ok => PASSED
        if ($retcode !== 0) {
            $passed_count++;
            html_print_passed($file_core_name);
        }
        //je potreba porovnat vystup
        else {
            $command_diff = "diff '{$act_out_file}' '{$out_file}'";
            exec($command_diff, $diff_output);
            //kdyz diff neco vypise, tak jsou vystupy rozdilne => FAILED
            if (count($diff_output) !== 0){
                $failed_count++;
                html_print_failed($file_core_name, $expected_rc, $retcode);
            }
            //vystupy jsou stejne, vse je ok => PASSED
            else{
                $passed_count++;
                html_print_passed($file_core_name);
            }
        }
    }
    if (file_exists($act_out_file))
        #unlink($act_out_file);
    if (file_exists($file_core_name.$extension) and $extension !== ".src")
        unlink($file_core_name.$extension);
}

$html_name_of_test = "";
if ($allopts['parse-only']) {
    $html_name_of_test = "Výsledky testování skriptu parse.php";
    foreach ($src_filenames as $src_file) {
        parse_test($src_file);
    }
}
elseif ($allopts['int-only']) {
    $html_name_of_test = "Výsledky testování skriptu interpret.py";
    foreach ($src_filenames as $src_file) {
        interpret_test($src_file);
    }
}
else {
    $html_name_of_test = "Výsledky testování skriptů parse.php a interpret.py";
    foreach ($src_filenames as $src_file) {
        $success = parse_test($src_file, true);
        if ($success)
            interpret_test($src_file, '.prsout');
    }
}


$html_heading = "<!DOCTYPE html>
<html lang=\"cs\">

<head>
<title>Výsledky testování
</title>
<style>
table {
  font-family: arial, sans-serif;
  border-collapse: collapse;
  width: 90%;
}

td, th {
  border: 1px solid #dddddd;
  text-align: left;
  padding: 8px;
}

tr:nth-child(even) {
  background-color: #F1F1F1;
}
</style>
</head>";

$end_html = "</table>
</body>
</html>";

$html_body = "
<body>
<h2>Výsledky testování {$html_name_of_test}</h2>
<h3>{$passed_count}<span style=\"color: green; \">PASSED</span>, {$failed_count}<span style=\"color: red; \">FAILED</span></h3>
<table>
  <tr>
    <th>Výsledek</th>
    <th>Detail</th>
    <th>Skript</th>
    <th>Umístění souboru</th>
  </tr>

";
$html_output = $html_heading.$html_body.$html_output.$end_html;
echo $html_output;
