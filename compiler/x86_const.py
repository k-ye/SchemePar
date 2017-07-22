'''X86 Instructions
'''
ADD = 'add'
SUB = 'sub'
NEG = 'neg'
MOVE = 'mov'
CALL = 'call'
PUSH = 'push'
POP = 'pop'
RET = 'ret'

'''X86 Registers (64-bit)
'''
RAX = 'rax'
RBX = 'rbx'
RCX = 'rcx'
RDX = 'rdx'
RSI = 'rsi'
RDI = 'rdi'
R8 = 'r8'
R9 = 'r9'
R10 = 'r10'
R11 = 'r11'
R12 = 'r12'
R13 = 'r13'
R14 = 'r14'
R15 = 'r15'
RSP = 'rsp'
RBP = 'rbp'

def CallerSaveRegs():
    # rax rdx rcx rsi rdi r8 r9 r10 r11
    for r in [RAX, RDX, RCX, RSI, RDI, R8, R9, R10, R11]:
        yield r

def FreeRegs():
    # All the caller save registers
    # rax is excluded due to how Patch Instruction is implemented
    for r in [RDX, RCX, RSI, RDI, R8, R9, R10, R11]:
        yield r