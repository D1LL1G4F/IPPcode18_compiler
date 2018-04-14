<?php

  /*
  * author: Matej Knazik
  * login: xknazi00
  *
  */

  $python = "python3.6 "; // how to run python scripts
  $php = "php5.6 "; // how to run php scripts


  $directory = getcwd();
  $recSearch = false;
  $parser = "parse.php";
  $interpreter = "interpret.py";

  /* just glob but functioning recursively
  */
  function recursiveGlob($folder, $pattern) {
    $dir = new RecursiveDirectoryIterator($folder);
    $ite = new RecursiveIteratorIterator($dir);
    $files = new RegexIterator($ite, $pattern, RegexIterator::GET_MATCH);
    $fileList = array();
    foreach($files as $file) {
        $fileList = array_merge($fileList, $file);
    }
    return $fileList;
  }

  function getTestName($sourceCodeName){
    return substr($sourceCodeName, 0, -4);
  }

  /* execute interpretation and return output files and load return codes
  * to global $returnCodes variable
  */
  function generateOutputFiles($sources) {
    global $parser;
    global $interpreter;
    global $returnCodes;
    global $directory;
    global $inputFiles;

    global $php;
    global $python;
    $outputs = array();

    foreach ($sources as $source) {
      $output = NULL;
      $rc = NULL;
      $outputFileName = getTestName($source) . "My.out";
      exec($php . $parser . " < " . $source, $output, $rc); // TODO merlin
      if ($rc == 0) {
        $tmpFileName = tempnam($directory, "tmpXML");
        $XML = fopen($tmpFileName, "w");
        fwrite($XML, implode("\n", $output));
        exec($python . $interpreter . " --source=" . $tmpFileName . " < " . $inputFiles[$source] . " > " . $outputFileName ." 2> " . getTestName($source) . ".err" , $output, $rc);
        fclose($XML);
        unlink($tmpFileName);
      }

      $returnCodes = array_merge($returnCodes, array($source => $rc));
      $outputs  = array_merge($outputs, array($source => $outputFileName));
    }
    return $outputs;
  }

  /* get reference output files if doesn't exist create empty one
  */
  function getRefFiles($sources) {
    $refFiles = array();
    foreach ($sources as $source) {
      if (!file_exists(getTestName($source) . ".out")) {
        $newfile = fopen(getTestName($source) . ".out","w");
        fclose($newfile);
      }
      $refFiles  = array_merge($refFiles, array($source => getTestName($source) . ".out"));
    }
    return $refFiles;
  }

  /* get input files if doesn't exist create empty one
  */
  function getInFiles($sources) {
    $inFiles = array();
    foreach ($sources as $source) {
      if (!file_exists(getTestName($source) . ".in")) {
        $newfile = fopen(getTestName($source) . ".in","w");
        fclose($newfile);
      }
      $inFiles  = array_merge($inFiles, array($source => getTestName($source) . ".in"));
    }
    return $inFiles;
  }

  /* get return code files if doesn't exist create one with value 0
  */
  function getReturnCodes($sources) {
    $rcFile = array();
    foreach ($sources as $source) {
      if (!file_exists(getTestName($source) . ".rc")) {
        $newfile = fopen(getTestName($source) . ".rc","w");
        fwrite($newfile, "0");
        fclose($newfile);
      }
      $file = fopen(getTestName($source) . ".rc", "r");
      $content = fread($file, filesize(getTestName($source) . ".rc"));
      $rcFile  = array_merge($rcFile, array($source => $content));
      fclose($file);
    }
    return $rcFile;
  }

  /* execute diff of test and return bool indicating success or fail
  */
  function execTest($test) {
    global $returnCodes;
    global $outputFiles;
    global $referenceFiles;
    global $referenceReturnCodes;
    $output = NULL;
    if ($returnCodes[$test] == $referenceReturnCodes[$test] && $returnCodes[$test] != 0)
      return True;
    exec("diff " . $outputFiles[$test] . " " . $referenceFiles[$test], $output);
    return (empty($output)) && ($returnCodes[$test] == $referenceReturnCodes[$test]);
  }

  /* add new line to table
  * arg1: color of lines
  * arg2: vaulues in line in format [testname , status , rc , expected rc]
  */
  function createTableLine($color, $attribs) {
    global $HTML;
    $testElem = $HTML->createElement("tr");
    foreach ($attribs as $attrib) {
      $itemName = $HTML->createElement("td");
      $fontName = $HTML->createElement("font", $attrib);
      $fontColor = $HTML->createAttribute("color");
      $fontColor->value = $color;
      $fontName->appendChild($fontColor);
      $itemName->appendChild($fontName);
      $testElem->appendChild($itemName);
    }
    return $testElem;
  }


  /// LOAD ARGUMENTS ///

  $options = getopt("", array("help","directory:","recursive","parse-script:","int-script:"));
  /// CHECK IF HELP NEEDET ///
  if (array_key_exists("help",$options)) {
    if (count($options) != 1) {
      fwrite(STDERR, " ERROR 10: invalid combination of arguments, for more info see: --help\n");
      exit(10);
    }
    fwrite(STDOUT, "

    author: Matej Knazik\n
    description: IPPcode18 to formatted XML parser\n\n
    arguments:\n
    --help               : shows brief manual to test.php file (cannot be\n
                           combined with other arguments)\n
    --directory=PATH     : tests will be searched in PATH directory (if not\n
                           specified uses actual directory as default)\n
    --recursive          : tests will be searched in all subfolders of\n
                           selected directory\n
    --parse-script=FILE  : file with php 5.6 script parsing IPPcode18 to XML\n
                           representation\n
    --int-script=FILE    : file with python 3.6 interpret for XML representation\n
                           of IPPcode18\n
    ");
    exit(0);
  }
  ////////////////////////////

  /// GETOPTS PARSER ///
  foreach ($options as $opt => $optVal) {

    switch ($opt) {
      case "help":
        break;
      case "directory":
        $directory = $optVal;
        break;
      case "recursive":
        $recSearch = True;
        break;
      case "parse-script":
        $parser = $optVal;
        break;
      case "int-script":
        $interpreter = $optVal;
        break;
      default:
        fwrite(STDERR, " ERROR 10: invalid combination of arguments, for more info see: --help\n");
        exit(10);
        break;
    }
  }

  $recOptionStr = $recSearch ? "yes" : "no";
  /// END OF GETOPTS PARSER ////

  /* HTML template for output */
  $templateHTML =
  "<!DOCTYPE html>
  <html>
  <head>
  <style>
  table {
      border-collapse: collapse;
      width: 100%;
  }

  th, td {
      text-align: left;
      padding: 8px;
  }

  tr:nth-child(even){background-color: #f2f2f2}
  </style>
  </head>
  <body>

  <h1>Interpreter test</h1>
  <p><font size=\"4\"><strong>test files directory: </strong></font><i>" . $directory . "</i></p>
  <p><font size=\"4\"><strong>recursive directory search: </strong></font><i>" . $recOptionStr ."</i></p>
  <p><font size=\"4\"><strong>parser: </strong></font><i>" . $parser ."</i></p>
  <p><font size=\"4\"><strong>interpreter: </strong></font><i>" . $interpreter . "</i></p>

  <div style=\"overflow-x:auto;\">
    <table>
      <tr>
        <th>Test name</th>
        <th>Status</th>
        <th>Return code</th>
        <th>Expected return code</th>
      </tr>
    </table>
  </div>

  </body>
  </html>";

  /// MAIN program ///
  $HTML = new domDocument;
  $HTML->loadHTML($templateHTML); // load tempalte html
  $table = $HTML->getElementsByTagName('table'); // get table elem
  $body = $HTML->getElementsByTagName('body'); // get body elem

  chdir($directory); // set actual dir

  if ($recSearch) {
    $sources = recursiveGlob(".", "/.*.\.src/"); // load all src files recursively in all dirs
  } else {
    $sources = glob("*.src"); // load all src files from actual directory
  }

  $returnCodes = array(); // array for return codes
  $inputFiles = getInFiles($sources); // get all input files based on sources (if doesn't exist create empty one)
  $outputFiles = generateOutputFiles($sources); // interprete all tests and generate outputs and return codes
  $referenceFiles = getRefFiles($sources); // get all reference outputs (if doesn't exist create empty one)
  $referenceReturnCodes = getReturnCodes($sources); // get all reference return codes (if doesn't exists create one with value 0)
  $total = 0; // variable for total number of tests
  $success = 0; // variable for total number of successfull tests

  foreach ($sources as $test) { // generate table for results
    $total++;
    $testElem = $HTML->createElement("tr");
    $testResult = execTest($test); // execute diff of reference results and actual results
    $color = $testResult ? "green" : "red";
    $success += $testResult ? 1 : 0;
    $attribs = [getTestName($test), $testResult ? "OK" : "FAILED", $returnCodes[$test], $referenceReturnCodes[$test]];
    $table[0]->appendChild(createTableLine($color, $attribs)); // add test to table
  }
  if ($total > 0) { // provide success precentage
    $percentage = ($success / $total)*100;
  } else { // zero division avoidance
    $percentage = 0;
  }

  $stats = $HTML->createElement("h3", "Statistics:");
  $succ = $HTML->createElement("p", "successfull tests: " . (string)$success . "/" . (string)$total);
  $perc = $HTML->createElement("p", "percentage: " . (string)$percentage . "%");


  // append everything to body
  $body[0]->appendChild($stats);
  $body[0]->appendChild($succ);
  $body[0]->appendChild($perc);

  echo $HTML->saveHTML(); // output in HTML format
  return 0;
  ///////////////
 ?>
