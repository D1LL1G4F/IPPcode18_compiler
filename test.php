<?php

  /*
  * author: Matej Knazik
  * login: xknazi00
  *
  */

  $directory = getcwd();
  $recSearch = false;
  $parser = "parse.php";
  $interpreter = "interpreter.py";

  function appendDirName($array, $dirname) {
    $newArray = $array;
    foreach ($newArray as $key => $item) {
      $newArray[$key] = $dirname . $item; //concatinate your existing array with new one
    }
    return $newArray;
  }

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

  $parser = $directory . "/" . $parser;
  $interpreter = $directory . "/" . $interpreter;
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
      </tr>
      <tr>
        <td><font color=\"red\">test</font></td>
        <td><font color=\"red\">FAILED</font></td>
      </tr>
    </table>
  </div>

  </body>
  </html>";

  $HTML = new domDocument;
  $HTML->loadHTML($templateHTML);
  $table = $HTML->getElementsByTagName('table');

  chdir($directory);

  if ($recSearch) {
    $sources = recursiveGlob(".", "/.*.php/");
  } else {
    $sources = glob("*.php");
    $sources = appendDirName($sources, $directory);
  }

  var_dump($sources);


  echo $HTML->saveHTML();
  return 0;
 ?>
