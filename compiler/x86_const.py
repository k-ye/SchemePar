'''X86 Instructions
'''
ADD = 'add'
SUB = 'sub'
NEG = 'neg'
MOVE = 'move'
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
REXT = {i: 'r{}'.format(i) for i in xrange(8, 16)} 
RSP = 'rsp'
RBP = 'rbp'
