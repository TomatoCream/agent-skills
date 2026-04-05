---
description: Justfile syntax specification
source: https://github.com/casey/just/blob/master/GRAMMAR.md
source_sha: 7706216fbbe4b1fbcfa5d0c49962540ea3277a83
---

# Grammar

## Tokens

```
BACKTICK            = `[^`]*`
INDENTED_BACKTICK   = ```[^(```)]*```
COMMENT             = #([^!].*)?$
DEDENT              = emitted when indentation decreases
EOF                 = emitted at end of file
INDENT              = emitted when indentation increases
LINE                = emitted before a recipe line
NAME                = [a-zA-Z_][a-zA-Z0-9_-]*
NEWLINE             = \n|\r\n
RAW_STRING          = '[^']*'
INDENTED_RAW_STRING = '''[^(''')]*'''
STRING              = "[^"]*" # processes \n \r \t \" \\ escapes
INDENTED_STRING     = """[^(""")]*"""
LINE_PREFIX         = @-|-@|@|-
TEXT                = recipe text, only matches in recipe body
```

## Grammar Syntax

```
|   alternation
()  grouping
_?  option (0 or 1 times)
_*  repetition (0 or more times)
_+  repetition (1 or more times)
```

## Grammar Rules

```
justfile      : item* EOF

item          : alias
              | assignment
              | eol
              | export
              | function
              | import
              | module
              | recipe
              | set

eol           : NEWLINE | COMMENT NEWLINE

alias         : 'alias' NAME ':=' target eol

target        : NAME ('::' NAME)*

assignment    : NAME ':=' expression eol

export        : 'export' assignment

function      : NAME '(' parameters? ')' ':=' expression

parameters    : NAME ( ',' NAME )* ','?

set           : 'set' setting eol

setting       : 'allow-duplicate-recipes' boolean?
              | 'allow-duplicate-variables' boolean?
              | 'dotenv-filename' ':=' string
              | 'dotenv-load' boolean?
              | 'dotenv-path' ':=' string
              | 'dotenv-required' boolean?
              | 'export' boolean?
              | 'fallback' boolean?
              | 'ignore-comments' boolean?
              | 'positional-arguments' boolean?
              | 'script-interpreter' ':=' string_list
              | 'quiet' boolean?
              | 'shell' ':=' string_list
              | 'tempdir' ':=' string
              | 'unstable' boolean?
              | 'windows-powershell' boolean?
              | 'windows-shell' ':=' string_list
              | 'working-directory' ':=' string

boolean       : ':=' ('true' | 'false')

string_list   : '[' string (',' string)* ','? ']'

import        : 'import' '?'? string? eol

module        : 'mod' '?'? NAME string? eol

expression    : disjunct ('||' expression)*
              | disjunct

disjunct      : conjunct ('&&' disjunct)*
              | conjunct

conjunct      : 'if' condition '{' expression '}' 'else' '{' expression '}'
              | 'assert' '(' condition ',' expression ')'
              | '/' expression
              | value '/' expression
              | value '+' expression
              | value

condition     : expression '==' expression
              | expression '!=' expression
              | expression '=~' expression

value         : NAME '(' sequence? ')'
              | BACKTICK
              | INDENTED_BACKTICK
              | NAME
              | string
              | '(' expression ')'

string        : 'x'? STRING
              | 'x'? INDENTED_STRING
              | 'x'? RAW_STRING
              | 'x'? INDENTED_RAW_STRING

sequence      : expression ',' sequence | expression ','?

recipe        : attributes* '@'? NAME parameter* variadic? ':' dependencies eol body?

attributes    : '[' attribute (',' attribute)* ']' eol

attribute     : NAME | NAME ':' string | NAME '(' string (',' string)* ')'

parameter     : '$'? NAME | '$'? NAME '=' value

variadic      : '*' parameter | '+' parameter

dependencies  : dependency* ('&&' dependency+)?

dependency    : target | '(' target expression* ')'

body          : INDENT line+ DEDENT

line          : LINE LINE_PREFIX? (TEXT | interpolation)+ NEWLINE
              | NEWLINE

interpolation : '{{' expression '}}'
```