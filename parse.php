<?php

  class Token {

  }

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

 function removeComments($str) {
   if (strstr($str, '#', true) === FALSE) {
     return $str;
   } else {
     $str = strstr($str, '#', true) . "\n";
     return $str;
   }
 }

  function loadInstruct() {
    $instruction = fgets(STDIN); // get line
    global $lineCnt;
    $lineCnt++;
    $instruction = removeComments($instruction);
    if (strcmp("\n",$instruction) == 0) loadInstruct();
    return $instruction;
  }

  function checkValidHeader() {
    $header = loadInstruct();

    if ($header) {
      $header = preg_replace('/\s+/', '', $header); // remove whitespaces
      echo "-" . $header . "-\n";
      return strcmp(".IPPcode18",$header) ? false : true;
    } else {
      return false;
    }
  }

  if (checkValidHeader()) {
    while(loadInstruct()) {
      echo "OK\n";
    }
  } else {
    fwrite(STDERR, "ERROR 21: semantic/lexical error on line: " . $lineCnt . " (invalid header)" . "\n");
    return 21;
  }

  return 0;

 ?>
