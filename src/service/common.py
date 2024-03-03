#def status_bar(text: str, status: bool, length=100, indent='    ', print_end="\r"):
#
#    print(f'\r{text} |{bar}| {percent}% {suffix}', end=print_end)
#    if iteration == total:
#        print()


def progress_bar(iteration, total, prefix='', suffix='', decimals=0, length=100, fill='█', indent='    ', print_end="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        print_end   - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{indent}{prefix} |{bar}| {percent}% {suffix}', end=print_end)
    if iteration == total:
        print()
