Demo of program flow. The numbers and underscores are for visual effect, and the braces are what make the instruction pointer jump around.

![Demo of program flow](https://raw.githubusercontent.com/aaronduino/interlocking-braces/master/demo.gif?raw=True)

## How to run the interpreter
The only argument is the file that you want to run.

For example, this is how you would run the file `bounce.ib`:

```
python3 __main__.py bounce.ib
```

## Language Specs

Control Flow:  
`(` `)` `[` `]` `{` `}` jump to matching brace  

`?` pop top of stack; skip next char if >0  
`;` skip next char (unconditionally)  

`&` terminate the program  

Stack Operations:  
_Note: Trying to get the top element from an empty stack returns 0_  

`~ ` switch active stack  

`^` push from register  
`v` pop to register (but don't change the register)  

`\` swap top two elements  
`:` duplicate top element  

`$` pop the top of the stack and discard  

`#` get integer from user  
`@` get character from user  

I/O:  
`.` pop the top of the stack and print as integer  
`,` pop the top of the stack and print as ASCII character  

Literals:  
`123` specify numbers like normal  
`_` delimit numbers (if needed)  
`"abc"` string literal  
`i"abc"` string literal put in stack in reverse (so that it will be popped in order)  

Arithmetic:  
`+`
`-`
`*`
`/`
`%`
`=`
`>`
`<`
`!`
`|`

Misc:  
`w` wait for 1 ms  

Examples:

```
(hello world)
i"Hello, world!";(,:?)
```

```
(counter)
;(1+:.)
```

```
(fibonacci)
0v;(^1+:v+:.)
```

```
(factorial)
1~#v;[1+:^\v~^*~v:^=?]~.
```

```
(factorial -- explained)
1~      (add 1 to left stack)
#v      (store input in register)
;[      (enter loop)
  1+    (add 1 to counter)
  :     (make a copy)
  ^\v   (swap inputted value with counter)
  ~     (move to left stack)
  ^     (push the counter (on the register) onto the stack)
  *     (multiply)
  ~     (move back to right stack)
  v     (put inputted value back in register)
:^=?]   (if counter > inputted value, exit)
~.      (print value on left stack)
```
