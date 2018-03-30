<?php

  /*
  * author: Matej Knazik
  * login: xknazi00
  *
  */

  /// LOAD ARGUMENTS ///
  $options = getopt("", array("stats:","comments","loc","help"));
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
    --help       : shows brief manual to parse.php file (cannot be combined with other arguments)\n
    --stats=FILE : set output FILE for statistics\n
    --comments   : number of lines with comments will be written in FILE with statiscs (must be combined with --stats arg)\n
    --loc        : number of lines with instruction will be written in FILE with statistics (must be combined with --stats arg)\n

    ");
    exit(0);
  }
  ////////////////////////////

  // table for instruction parsing
  $instructOp = array(
    "move" => array(2,"var","symb"),
    "createframe" => array(0),
    "pushframe" => array(0),
    "popframe" => array(0),
    "defvar" => array(1,"var"),
    "call" => array(1,"label"),
    "return" => array(0),
    "pushs" => array(1,"symb"),
    "pops" => array(1,"var"),
    "add" => array(3,"var","symb","symb"),
    "sub" => array(3,"var","symb","symb"),
    "mul" => array(3,"var","symb","symb"),
    "idiv" => array(3,"var","symb","symb"),
    "add" => array(3,"var","symb","symb"),
    "lt" => array(3,"var","symb","symb"),
    "gt" => array(3,"var","symb","symb"),
    "eq" => array(3,"var","symb","symb"),
    "and" => array(3,"var","symb","symb"),
    "or" => array(3,"var","symb","symb"),
    "not" => array(2,"var","symb"),
    "int2char" => array(2,"var","symb"),
    "stri2int" => array(3,"var","symb","symb"),
    "read" => array(2,"var","type"),
    "write" => array(1,"symb"),
    "concat" => array(3,"var","symb","symb"),
    "strlen" => array(2,"var","symb"),
    "getchar" => array(3,"var","symb","symb"),
    "setchar" => array(3,"var","symb","symb"),
    "type" => array(2,"var","symb"),
    "label" => array(1,"label"),
    "jump" => array(1,"label"),
    "jumpifeq" => array(3,"label","symb","symb"),
    "jumpifneq" => array(3,"label","symb","symb"),
    "dprint" => array(1,"symb"),
    "break" => array(0)
  );

  $lineCnt = 0;
  $instructOrder = 0;
  $commentCnt = 0;
  $xmlOutput = new DomDocument("1.0", "UTF-8");

 function removeComments($str) {
   global $commentCnt;
   if (strstr($str, '#', true) === FALSE) {
     return $str;
   } else {
     $str = strstr($str, '#', true) . "\n";
     $commentCnt++;
     return $str;
   }
 }

  function loadInstruct() {
    do {
      $instruction = fgets(STDIN); // get line
      global $lineCnt;
      $lineCnt++;
      $instruction = removeComments($instruction);
    } while(ctype_space($instruction)); // repeat if there is empty instruct
    return $instruction;
  }

  function checkValidHeader() {
    $header = loadInstruct();

    if ($header) {
      $header = preg_replace('/\s+/', '', $header); // remove whitespaces
      return strcmp(".ippcode18",strtolower($header)) ? false : true;
    } else {
      return false;
    }
  }


  function validValue($str,$type) {
    switch ($type) {
      case "int":
        if (preg_match("/(^(\+?\d+$|-?\d+$))/",$str)) {
          return true;
        } else {
          return false;
        }
        break;
      case "bool":
        if ($str == "true" || $str == "false") {
          return true;
        } else {
          return false;
        }
        break;
      case "string":
        if (preg_match_all("(\/\d{3})",$str) == substr_count($str,"/")) { // checks if escape sequences are in valid format
          if (preg_match('!!u', $str)) { // check correct encoding UTF-8 of string
             // this is utf-8
             return true;
          }
          else {
             // definitely not utf-8
             return false;
          }
          return true;
        } else {
          return false;
        }
        break;
      default:
        fwrite(STDERR, "INTERNAL ERROR: function validValue() called with wrong type param\n");
        return false; // should never occur (at least I hope so)
        break;
    }
  }

  function isType($str) {
    switch ($str) {
      case "int":
        return true;
        break;
      case "bool":
        return true;
        break;
      case "string":
        return true;
        break;
      default:
        return false;
        break;
    }
  }

  function validID($str) {
    $specialChars = array("_","-","$","&","%","*");
    if (empty($str)) {
      return false;
    }

    if (preg_match("/^\D.*/",$str)) { // check if starts with non digit char
      $strWithoutSC = str_replace($specialChars,"",$str);
      return (ctype_alnum($strWithoutSC) || empty($strWithoutSC)); // check if remaining str contain only alphanumeric chars
    } else {
      return false;
    }
  }



  /// $str = instruction argument
  /// $type = var/symb/label/type
  /// $parentElem = xml elem of instruction
  /// $numOfArg = number of argument in instruction based on order
  function validArgument($str,$type,$parentElem,$numOfArg) {
    global $xmlOutput;
    switch ($type) {
      case "symb": // if not a constant should fallthrough and check if not var
        // check if symb
        if (substr_count($str,"@") > 0) {
            $part = explode('@',$str);
            $val = "";
            $valType = "";

            if (count($part) != 2) { // check proper type@value
              if ((count($part) > 2) && ($part[0] == "string")) { //string exception (string@string@lalala is valid)
                $valType = $part[0];
                $val = $part[1];
                for ($i=2; $i < count($part) ; $i++) {
                  $val = $val . "@" . $part[$i];
                }
              } else {
                return false;
              }
            } else {
              $val = $part[1];
              $valType = $part[0];
            }


            if (isType($valType)) {
              if (validValue($val,$valType)) {

                $val = htmlspecialchars($val);

                $argElem = $xmlOutput->createElement("arg" . $numOfArg,$val);
                $argElem->setAttribute("type",$valType);
                $parentElem->appendChild($argElem);
                return true;
              } else {
                return false; // return error if it is meant to be a constant but with wrong value
              }
            }
        }
      case "var":
        //check if var
        if (substr_count($str,"@") == 1) {
            $part = explode('@',$str);
            if (count($part) != 2) { // check proper frame@ID
              return false;
            }

            $frame = $part[0];
            $id = $part[1];

            if ($frame == "GF" || $frame == "LF" || $frame == "TF") {
              if (validID($id)) {

                $var = htmlspecialchars($str);

                $argElem = $xmlOutput->createElement("arg" . $numOfArg,$var);
                $argElem->setAttribute("type","var");
                $parentElem->appendChild($argElem);
                return true;
              } else {
                return false;
              }
            } else {
              return false;
            }
        } else {
          return false;
        }
        break;
      case "label":
        // check if label
        if (validID($str)) {
          $argElem = $xmlOutput->createElement("arg" . $numOfArg,htmlspecialchars($str));
          $argElem->setAttribute("type","label");
          $parentElem->appendChild($argElem);
          return true;
        } else {
          return false;
        }
        break;
      case "type":
        // check if type
        if (isType($str)) {
          $argElem = $xmlOutput->createElement("arg" . $numOfArg,$str);
          $argElem->setAttribute("type","type");
          $parentElem->appendChild($argElem);
          return true;
        } else {
          return false;
        }
        break;
      default:
        return false;
        break;
    }

    return true;
  }

  // returns true on success!!
  function parseInstruct($part,$instructElem) {
    global $instructOp;
    $opcode = strtolower($part[0]); // opcode in small caps
    if (!array_key_exists($opcode,$instructOp)) { // check valid OP code
      return false;
    }
    $numOfInstructArg = $instructOp[$opcode][0];

    if ($numOfInstructArg != (count($part)-1)) { // check if there is valid number of arguments
      return false;
    }

    // analyze each argument
    for ($i=0; $i < $numOfInstructArg; $i++) {
      if(!validArgument($part[$i+1],$instructOp[$opcode][$i+1],$instructElem,$i + 1)) {
        return false;
      }
    }

    return true;
  }


  /*
  *  ///////////     MAIN PROGRAM       /////////////////
  */
  if (checkValidHeader()) {
    $program = $xmlOutput->createElement("program");
    $program->setAttribute("language","IPPcode18");
    $xmlOutput->appendChild($program);
    while($instruct = loadInstruct()) {

      $instructOrder++;
      $instructPart = preg_split('/\s+/', $instruct, -1, PREG_SPLIT_NO_EMPTY); // split instruct by whitespaces to array

      $instructElem = $xmlOutput->createElement("instruction");
      $instructElem->setAttribute("order",$instructOrder);
      $instructElem->setAttribute("opcode",strtoupper($instructPart[0]));
      $program->appendChild($instructElem);

      if (!parseInstruct($instructPart,$instructElem)) {
        fwrite(STDERR, "ERROR 21: semantic/lexical error on line: " . $lineCnt . "\n");
        exit(21);
      }
    }
  } else {
    fwrite(STDERR, "ERROR 21: semantic/lexical error on line: " . $lineCnt . " (invalid header)" . "\n");
    exit(21);
  }
  //////////////////////////////////////////////////////////

  /// GETOPTS PARSER ///
  $file = false;
  if (array_key_exists("stats",$options)) {
    $file = fopen($options["stats"], "w");
    if ($file == false) {
      fwrite(STDERR, "ERROR 10: failed in opening file:" . $file . "\n");
      exit(10);
    }
  }

  foreach ($options as $opt => $optVal) {

    switch ($opt) {
      case "stats":
        break;
      case "comments":
        if(fwrite($file,$commentCnt . "\n") == false) {
          fwrite(STDERR, " ERROR 10: missing \"stats=FILE\" argument\n");
          exit(10);
        }
        break;
      case "loc":
        if(fwrite($file,$instructOrder . "\n") == false) {
          fwrite(STDERR, " ERROR 10: missing \"stats=FILE\" argument\n");
          exit(10);
        }
        break;
      default:
        fwrite(STDERR, " ERROR 10: invalid combination of arguments, for more info see: --help\n");
        exit(10);
        break;
    }
  }

  if ($file != false) {
    fclose($file);
  }
  /// END OF GETOPTS PARSER ////

  $xmlOutput->formatOutput = true;
  print $xmlOutput->saveXML();
  exit(0);

 ?>
