import os
import subprocess as sp
import sys
import shutil as shu

DEFAULT_TESTS_DIR = 'tests'
SCH_COMPILER = 'integrated.py'
RUNTIME_SRC_PATHs = [
    os.path.join('runtime', 'runtime.c'),
]

OKGREEN = '\033[92m'
FAIL = '\033[91m'
ENDC = '\033[0m'


def DropExt(filepath):
    return ChangeExt(filepath, None)


def ChangeExt(filepath, ext):
    path = os.path.splitext(filepath)[0]
    if ext is None:
        return path
    return '%s.%s' % (path, ext)


def GetShellCmd(cmds):
    return ' '.join(cmds)


def ExecCommand(cmd_list):
    cmd = GetShellCmd(cmd_list)
    # print '    exec: {}'.format(cmd)
    out = sp.check_output(cmd, shell=True)
    return out


def RunTestCase(test_path, input_path):
    try:
        # add '#lang racket' header to test scheme code
        tmp_test_path = test_path + '.tmp'
        with open(test_path, 'r') as rf, open(tmp_test_path, 'w') as wf:
            wf.write('#lang racket\n\n')
            for l in rf:
                wf.write(l)

        # expected output
        cmd_list = ['racket', tmp_test_path]
        if input_path is not None:
            cmd_list.extend(['<', input_path])
        expected_out = ExecCommand(cmd_list)
        expected_out = expected_out.strip()

        # compiler output

        # compile to assembly
        out_bin = DropExt(test_path)
        cmd_list = ['python', SCH_COMPILER, test_path]
        ExecCommand(cmd_list)

        # link runtime and produce binary
        asm_path = ChangeExt(test_path, 's')
        cmd_list = ['gcc', '-o', out_bin, asm_path] + RUNTIME_SRC_PATHs
        ExecCommand(cmd_list)

        # call binary

        cmd_list = ['./{}'.format(out_bin)]
        if input_path is not None:
            cmd_list.extend(['<', input_path])
        compiler_out = ExecCommand(cmd_list)
        compiler_out = compiler_out.strip()

        test_name = os.path.basename(test_path)
        if expected_out == compiler_out:
            print 'Test={} {}OK{}'.format(test_name, OKGREEN, ENDC)
            return True
        else:
            print 'Test={} {}Failed{}'.format(test_name, FAIL, ENDC)
            print 'expeted: \n{}'.format(expected_out)
            print 'got: \n{}'.format(compiler_out)
            return False
    finally:
        os.remove(tmp_test_path)


def RunTests():
    test_dir = DEFAULT_TESTS_DIR
    tmp_test_dir = os.path.join(test_dir, 'tmp')

    # create tmp test directory
    if os.path.isdir(tmp_test_dir):
        shu.rmtree(tmp_test_dir)
    os.makedirs(tmp_test_dir)

    for test_prefix in ['r1', 'r2']:
        for name in os.listdir(test_dir):
            test_path = os.path.join(test_dir, name)
            if os.path.isfile(test_path) and name.startswith(test_prefix) and name.endswith('.rkt'):
                shu.copy(test_path, tmp_test_dir)
                tmp_test_path = os.path.join(tmp_test_dir, name)

                input_path = ChangeExt(test_path, 'in')
                tmp_input_path = None
                if os.path.isfile(input_path):
                    shu.copy(input_path, tmp_test_dir)
                    tmp_input_path = ChangeExt(tmp_test_path, 'in')
                else:
                    input_path = None

                result = RunTestCase(tmp_test_path, tmp_input_path)
                if not result:
                    break
                # break
    shu.rmtree(tmp_test_dir)

if __name__ == '__main__':
    RunTests()
