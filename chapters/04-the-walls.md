# 04 — The walls: when the difference is the compiler, not the code

The happy case is a source shape you have not found yet. The unhappy case — and the expensive
one — is a difference no source can express, because the compiler made a decision you cannot
ask it to make.

Three of those cost real time. They are written down here so nobody pays twice.

## `add reg, -imm` becomes `sub reg, imm`

On a branch-merge edge the compiler prefers `sub`:

```asm
; the original binary
add eax, 0xfffffe88        ; eax += -376

; every C++ spelling we tried
sub eax, 0x178             ; eax -= 376
```

Same arithmetic, different bytes, same length. About 235 spellings were measured on a function
whose entire residue was this one instruction: different integer types, casts, `unsigned`
wrapping, a constant folded through a variable, both branches arranged differently.

The only shape that kept the `add` was giving the value a memory home (a `volatile` temporary),
which costs a load or a store and therefore breaks the extent elsewhere. **Conclusion: a
one-instruction `add`/`sub` residue at a merge edge is not a spelling problem.** Do not spend the
hour.

## A 12-byte temporary's stack slot

One function was 2 952 bytes in the original and compiled to 2 952 bytes — identical except for
a single `lea`:

```asm
lea ecx, [esp+0x2c]     ; original
lea ecx, [esp+0x24]     ; ours
```

It is the hidden return pointer of an aggregate temporary. The compiler lays the frame out
tightly (scalars at 0x00, temporary at 0x08, the next temporary at 0x14); the original put that
12-byte temporary at **0x10**, a 16-byte-aligned offset, so the two temporaries overlap by 8
bytes. Recovering the compiler's own frame map made the difference obvious and also showed why
it is stuck: the only way to force the alignment is `__declspec(align(16))`, which also emits a
stack-alignment prologue the original does not have.

Twenty-five source shapes were measured here (named, const-ref and pointer temporaries,
declaration orders, return-type sizes, brace scopes, out-parameter forms, dead locals). All
failed for the same reason.

## The sret slot wall

Three separate one-instruction near misses — 1 343, 1 708 and 3 018 bytes, each otherwise
byte-identical — ended on the **same** residue: the reservation of the hidden return pointer in
the frame. Once that was established, the correct move was to close all three permanently
rather than let the next person discover it again.

That is why the project keeps a closed list, and why every near miss is checked against it before
an agent is assigned. A one-instruction residue looks like a free win; twice it was a wall that
had already been proved.

## The general lesson

Separate **finding a shape** from **understanding a decision**:

- if the residue changes when you change the source, you are still looking for the shape;
- if 20+ distinct shapes give the same residue, the compiler has made a choice, and the question
  becomes "which choice, and can it be forced at all" — usually answered by looking at the
  frame map or the scheduler, not at more C++;
- if the answer is no, write it down with the failed spellings. The next person's hour is worth
  more than the completeness of your notes.
