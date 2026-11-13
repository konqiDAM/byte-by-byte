# 01 — What "matching" means

For someone who has never looked at decompilation. No prior assembly knowledge assumed, but
you should know what a compiler is.

## The problem

A game ships as a binary: `Fallout3.exe`, 15 million bytes of machine code. The C++ it was
compiled from is gone. What people usually do is run a **decompiler** over it, which produces
C-like output that describes what the machine code does. That output is a reconstruction, not a
recovery:

- variable and function names are gone, so you get `FUN_0041a300` and `local_14`;
- types are inferred from how memory is used, and the inference is often wrong;
- the code it prints *means* the same thing, but it does not compile back to the same bytes.

So decompiler output is useful to read and useless as a build.

## The stricter goal

Matching decompilation sets a much harder target: write C++ that, compiled with **the same
compiler and the same flags as the original**, produces **byte-identical machine code** to the
function in the binary. Not "equivalent". Identical.

That sounds impossible until you notice that compilers are deterministic. Same source, same
compiler, same flags, same output — every time. So if you can find *a* source that produces
those exact bytes, you have found a source indistinguishable from the original from the
compiler's point of view. In practice that is the original source, reconstructed.

This is how the console-game decompilation projects work, and it is why they can rebuild a game
from source and get a binary that matches the retail one.

## Why one function at a time

The unit of work is a single function, because that is the smallest thing you can compile and
compare on its own. A typical loop:

1. pick a function from the binary (say 243 bytes at `0x00904da0`);
2. write a C++ version whose signature, types and body you believe are right;
3. compile it with the project's exact compiler and flags;
4. compare your function's machine code to the original's, instruction by instruction;
5. when they differ, change something and go back to 3.

The comparison tool reports two numbers that drive everything:

- **extent** — how many bytes your function compiled to. If it is not the original's size, the
  difference is structural (an extra local, a different type, a missing branch) and no amount
  of rearranging will fix it.
- **residue** (`ndiff`) — how many instructions still differ once the sizes match. Residue 0 is
  a match.

## What actually differs, and why it is hard

When the size is right and one instruction still differs, the cause is usually one of:

- **register allocation** — the compiler chose `eax` where the original chose `ecx`;
- **instruction order** — two independent operations scheduled the other way round;
- **stack layout** — the same locals placed at different offsets;
- **a type** — `int` where the original had `unsigned`, or a struct field at a different offset;
- **the compiler lowering a construct differently** — for example `x - 376` written one way
  becomes `sub eax, 0x178` while the original has `add eax, 0xfffffe88`.

That last category is the interesting one, and it is where matching decompilation stops being
about style and starts being about reverse-engineering the compiler: two instructions that do
the same arithmetic are not the same bytes, and you have to find the source shape that makes
the compiler emit the original's choice.

## Why anyone does this

- You get a readable, buildable game: bug fixes, ports, modding at source level.
- It is a precise, checkable form of software archaeology: the binary is the oracle, and every
  claim is verified by a compiler, not by an opinion.
- You learn how compilers really behave, from the outside, with no source available.

The cost is time: this is hours per function, and the difficulty is wildly uneven. Which is why
the rest of this repository is mostly about **choosing the next function well** — measuring
yield, harvesting existing attempts, and finding the original source when a twin of it exists
in another game built from the same engine.
