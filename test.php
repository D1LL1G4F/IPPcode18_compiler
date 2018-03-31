<?php

  /*
  * author: Matej Knazik
  * login: xknazi00
  *
  */

  $directory = getcwd();
  $recSearch = false;
  $parser = "parse.php";
  $interpreter = "interpret.py";

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

  function generateOutputFiles($sources) {
    global $parser;
    global $interpreter;
    global $returnCodes;
    global $directory;
    $outputs = array();


    foreach ($sources as $source) {
      $outFile = fopen(getTestName($source) . ".in","w");
      $output = NULL;
      $rc = NULL;
      exec("php " . $parser . " < " . $source, $output, $rc); # TODO MERLIN
      if ($rc == 0) {
        $tmpFileName = tempnam($directory, "tmpXML");
        $XML = fopen($tmpFileName, "w");
        fwrite($XML, implode("\n", $output));
        $output = array();
        exec("python3.6 " . $interpreter . " --source=" . $tmpFileName, $output, $rc);
        fclose($XML);
        unlink($tmpFileName);
        fwrite($outFile, implode("\n", $output));
      }
      fclose($outFile);

      $returnCodes = array_merge($returnCodes, array($source => $rc));
      $outputs  = array_merge($outputs, array($source => getTestName($source) . ".in"));
    }
    return $outputs;
  }

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

  function execTest($test) {
    global $returnCodes;
    global $outputFiles;
    global $referenceFiles;
    global $referenceReturnCodes;
    $output = NULL;
    exec("diff " . $outputFiles[$test] . " " . $referenceFiles[$test], $output);
    return empty($output) && $returnCodes[$test] == $referenceReturnCodes[$test];
  }

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

  $HTML = new domDocument;
  $HTML->loadHTML($templateHTML);
  $table = $HTML->getElementsByTagName('table');
  $body = $HTML->getElementsByTagName('body');

  chdir($directory);

  if ($recSearch) {
    $sources = recursiveGlob(".", "/.*.\.src/");
  } else {
    $sources = glob("*.src"); // TODO
  }

  $returnCodes = array();
  $outputFiles = generateOutputFiles($sources);
  $referenceFiles = getRefFiles($sources);
  $referenceReturnCodes = getReturnCodes($sources);
  $total = 0;
  $success = 0;

  foreach ($sources as $test) {
    $total++;
    $testElem = $HTML->createElement("tr");
    $testResult = execTest($test);
    $color = $testResult ? "green" : "red";
    $success += $testResult ? 1 : 0;
    $attribs = [getTestName($test), $testResult ? "OK" : "FAILED", $returnCodes[$test], $referenceReturnCodes[$test]];
    $table[0]->appendChild(createTableLine($color, $attribs));
  }
  if ($total > 0) {
    $percentage = ($success / $total)*100;
  } else {
    $percentage = 0;
  }

  $stats = $HTML->createElement("h3", "Statistics:");
  $succ = $HTML->createElement("p", "successfull tests: " . (string)$success . "/" . (string)$total);
  $perc = $HTML->createElement("p", "percentage: " . (string)$percentage . "%");

  $body[0]->appendChild($stats);
  $body[0]->appendChild($succ);
  $body[0]->appendChild($perc);

  echo $HTML->saveHTML();
  return 0;
 ?>
