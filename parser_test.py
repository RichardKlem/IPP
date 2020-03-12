import sys
import os
import subprocess


class Bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def main():

    path = os.getcwd() + "/ipp-2020-tests/parse-only/"
    input_files = []
    expected_output_files = []
    src_ext = '.src'
    out_ext = '.out'
    act_out_ext = '.actout'

    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for file in f:
            if file.endswith(src_ext):
                input_files.append(os.path.join(r, file))

    for r, d, f in os.walk(path):
        for file in f:
            if file.endswith(out_ext):
                expected_output_files.append(os.path.join(r, file))

    actual_output_file = ""
    output_file = ""
    rc_file = ""
    passed_count = 0
    failed_count = 0
    for file in input_files:
        if file.endswith('.src'):
            actual_output_file = file[:-4] + act_out_ext
            output_file = file[:-4] + out_ext
            rc_file = file[0:-4] + ".rc"
        test_file_name = str(file.split('/')[-1])

        command = "php7.4 parse.php < '{}' > '{}'".format(file, actual_output_file)
        php_return = subprocess.run(command, shell=True, universal_newlines=True)

        with open(rc_file, "r") as rc_file:
            #print(test_file_name, php_return.returncode, int(rc_file.read()))
            rc_file_int = int(rc_file.read())
            #print(rc_file_int, php_return.returncode)
            if rc_file_int == php_return.returncode:
                if php_return.returncode == 0:
                    options = os.path.join(os.getcwd(), "jexamxml", "options")
                    command_jexamxml = "java -jar {}/jexamxml/jexamxml.jar {} {} /O:{}".format(os.getcwd(), output_file, actual_output_file, options)
                    ret_code = (subprocess.run(command_jexamxml, shell=True,
                                               universal_newlines=True)).returncode
                    if ret_code in [0]:
                        passed_count += 1
                        print(
                            Bcolors.OKGREEN + Bcolors.BOLD + 'PASSED ' + Bcolors.ENDC + test_file_name)
                        os.remove(actual_output_file) # remove
                    else:
                        failed_count += 1
                        print(Bcolors.FAIL + Bcolors.BOLD + 'FAILED ' + Bcolors.ENDC + test_file_name)
                else:
                    passed_count += 1
                    print(Bcolors.OKGREEN + Bcolors.BOLD + 'PASSED ' + Bcolors.ENDC + test_file_name)
                    os.remove(actual_output_file) # remove
            elif rc_file_int != php_return.returncode:
                failed_count += 1
                print(Bcolors.FAIL + Bcolors.BOLD + 'FAILED ' + Bcolors.ENDC + test_file_name)
                continue

        """    
        expected_output = []
        actual_output = (open(actual_output_file).read()).splitlines()
        try:
            expected_output = (open(output_file).read()).splitlines()
            expected_output_list = []
            for line in expected_output:
                expected_output_list.append(line.strip())
            expected_output = expected_output_list
        except:
            print("MISSING output_file.out for this source_file:\n{}".format(file))
            exit(1)

        test_file_name = str(file.split('/')[-1])

        if actual_output == expected_output:
            passed_count += 1
            print(Bcolors.OKGREEN + Bcolors.BOLD + 'PASSED ' + Bcolors.ENDC + test_file_name)
        else:
            failed_count += 1
            print(Bcolors.FAIL + Bcolors.BOLD + 'FAILED ' + Bcolors.ENDC + test_file_name)
            for line1, line2 in zip(expected_output, actual_output):
                if line1 != line2:
                    print(Bcolors.BOLD +
                          "Expected:\n" + Bcolors.ENDC +
                          "{}\n".format(line1) + Bcolors.BOLD +
                          "Got:\n" + Bcolors.ENDC +
                          "{}\n".format(line2))
        if len(expected_output) != len(actual_output):
            larger_file, larger_file_name = (expected_output, str(output_file.split('/')[-1])) \
                    if expected_output > actual_output else (actual_output, str(actual_output_file.split('/')[-1]))
            print(Bcolors.BOLD + "Extra lines in " + larger_file_name + Bcolors.ENDC)
            for line in larger_file[-(abs(len(actual_output) - len(expected_output))):]:
                print("+" + line)
        
        """
        try:
            pass
            #os.remove(actual_output_file, )
        except OSError:
            pass
    print(Bcolors.OKGREEN + "\n{} passed\n".format(passed_count) + Bcolors.FAIL + "{} failed".format(failed_count)
          + Bcolors.ENDC)


if __name__ == '__main__':
    sys.exit(main())
