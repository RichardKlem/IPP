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
    path2 = os.getcwd() + r"/ipp-2020-tests/interpret-only/valid"
    src_files = []
    expected_output_files = []
    in_files = []
    rc_files = []

    src_ext = '.src'
    out_ext = '.out'
    in_ext = '.in'
    rc_ext = '.rc'
    act_out_ext = '.actout'

    # r=root, d=directories, f = files
    for r, d, f in os.walk(path2):
        for file in f:
            if file.endswith(src_ext):
                src_files.append(os.path.join(r, file))
            elif file.endswith(out_ext):
                expected_output_files.append(os.path.join(r, file))
            elif file.endswith(in_ext):
                in_files.append(os.path.join(r, file))
            elif file.endswith(rc_ext):
                rc_files.append(os.path.join(r, file))

    passed_count = 0
    failed_count = 0
    for file in src_files:
        actual_output_file = file[:-4] + act_out_ext
        output_file = file[:-4] + out_ext
        rc_file = file[0:-4] + rc_ext
        in_file = file[0:-4] + in_ext
        test_file_name = str(file.split('/')[-1])

        command = "python3.8 interpret.py --source={} --input={} > '{}'".format(file, in_file,
                                                                                actual_output_file)
        rc = subprocess.run(command, shell=True, universal_newlines=True)

        with open(rc_file, "r") as rc_file:
            rc_file_int = int(rc_file.read())
        if rc.returncode != 0 and rc.returncode == rc_file_int:
            passed_count += 1
            print(Bcolors.OKGREEN + Bcolors.BOLD + 'PASSED ' + Bcolors.ENDC + test_file_name)
            os.remove(actual_output_file)  # remove
            continue
        elif rc_file_int != rc.returncode:
            failed_count += 1
            print(Bcolors.FAIL + Bcolors.BOLD + 'FAILED ' + Bcolors.ENDC + test_file_name)
            continue
        else:
            with open(output_file, 'r') as output_file, open(actual_output_file, 'r') as actual_output_fil:
                output_file_data = output_file.read()
                actual_output_data = actual_output_fil.read()
            if output_file_data != actual_output_data:
                failed_count += 1
                print(Bcolors.FAIL + Bcolors.BOLD + 'FAILED ' + Bcolors.ENDC + test_file_name)
                continue

        passed_count += 1
        print(Bcolors.OKGREEN + Bcolors.BOLD + 'PASSED ' + Bcolors.ENDC + test_file_name)
        os.remove(actual_output_file)  # remove

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
            # os.remove(actual_output_file, )
        except OSError:
            pass
    print(
            Bcolors.OKGREEN + "\n{} passed\n".format(
                passed_count) + Bcolors.FAIL + "{} failed".format(
                    failed_count)
            + Bcolors.ENDC)


if __name__ == '__main__':
    sys.exit(main())
