def progress_bar(iteration, total, length=50, fill='='):
    """
    Call in a loop to create terminal progress bar.
    Taken from: https://stackoverflow.com/a/34325723
    Args:
        iteration (int): current iteration
        total (int): total iterations
        length (int): character length of progress bar
        fill (str): progress bar fill character
    Returns:
        str: Progress bar
    """
    if total > 0:
        percent = int(100 * (iteration / float(total)))
        filled_length = int(length * iteration // total)
        bar = fill * filled_length + '-' * (length - filled_length)
        print('\rProgress |%s| %s%% Complete' % (bar, percent), end='\r')
        # Print New Line on Complete
        if iteration == total:
            print()
