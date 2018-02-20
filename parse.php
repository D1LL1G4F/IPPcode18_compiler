<?php

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
    "not" => array(3,"var","symb","symb"),
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
  $xmlOutput = new DomDocument("1.0", "UTF-8");

 function removeComments($str) {
   if (strstr($str, '#', true) === FALSE) {
     return $str;
   } else {
     $str = strstr($str, '#', true) . "\n";
     return $str;
   }
 }

  function loadInstruct() {
    do {
      $instruction = fgets(STDIN); // get line
      global $lineCnt;
      $lineCnt++;
      $instruction = removeComments($instruction);
    } while(strcmp("\n",$instruction) == 0); // repeat if there is empty instruct
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

  //TODO istype,validvaluecheck
  function isInt($str) {
    if (substr_count($str,"@") == 1) {
        $part = explode('@',$str,-1);
        if ($part[0] != "int") {
          return false;
        }

    } else {
      return false;
    }
    return true;
  }

  function parseInstruct($part) {
    global $instructOp;
    $opcode = strtolower($part[0]); // opcode in small caps
    if (!array_key_exists($opcode,$instructOp)) { // check valid OP code
      return false;
    }
    if ($instructOp[$opcode][0] != (count($part)-1)) { // check if there is valid number of arguments
      return false;
    }



    return true;
  }



  if (checkValidHeader()) {
    $program = $xmlOutput->createElement("program");
    $xmlOutput->appendChild($program);
    while($instruct = loadInstruct()) {

      $instructOrder++;
      $instructPart = preg_split('/\s+/', $instruct, -1, PREG_SPLIT_NO_EMPTY); // split instruct by whitespaces to array

      $instructElem = $xmlOutput->createElement("instruction");
      $instructElem->setAttribute("order",$instructOrder);
      $instructElem->setAttribute("opcode",strtoupper($instructPart[0]));
      $program->appendChild($instructElem);

      if (!parseInstruct($instructPart)) {
        fwrite(STDERR, "ERROR 21: semantic/lexical error on line: " . $lineCnt . "\n");
        return 21;
      }
    }
  } else {
    fwrite(STDERR, "ERROR 21: semantic/lexical error on line: " . $lineCnt . " (invalid header)" . "\n");
    return 21;
  }
  $xmlOutput->formatOutput = true;
  print $xmlOutput->saveXML();
  return 0;

 ?>
