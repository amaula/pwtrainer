#!/usr/bin/python
# -*- mode: python; coding: utf-8 -*-
"""
Really Simple Password Trainer v1.4 - A simple password training program.

Copyright (C) 2012 Antti Maula

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

See <http://www.gnu.org/licenses/>.
"""

import sys
from time import time
from getpass import getpass
from math import sqrt

# Class contents
c_normal = 'abcdefghijklmnopqrstuvwxyz'
c_capital = c_normal.upper()
c_number = '0123456789'


read_char = None
def init_read_char():
    global read_char
    try:
        import sys, tty, termios
        def read_char_unix():
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch
        read_char = read_char_unix
    except ImportError:
        import msvcrt
        read_char = msvcrt.getch


def read_password():
    """Read password, one character at a time, measuring the interval
    between characters. Timing starts when the first character is
    entered. (i.e. measure time _between_ chars)

    Returns a tuple of the password read, and array of times per character.
    Times include the terminating enter character.
    ( <password_string>, [ <time per character>, <time per character>, ... ] )
    """
    times = []
    pw = ''
    ch = 'a'
    while ord(ch) not in [13, 3]:
        ch = read_char()
        times.append(time())
        if ord(ch) != 13:
            pw = pw + ch

    # Convert times to between-character 
    rtimes = []
    if len(times) >= 2:
        for i,t in enumerate(times[1:]):
            rtimes.append(t - times[i])

    # Return as tuple
    return (pw, rtimes)

def mean(t):
    """ Calculate mean to dividing sum by number of elements.
    """
    return sum(t) / len(t)


def std(t):
    """Calculate standard deviation.
    """
    m = mean(t)
    total = 0
    for v in t:
        total = total + (v-m)**2
    return sqrt(total / len(t))


def calculate_timing_analysis(timing):
    """ Calculate mean, min, max and standard deviation from the array of measures.
    Return as a list of lists.
    """
    result = []
    for index,t in enumerate(timing):
        meanvalue = mean(t)
        minvalue = min(t)
        maxvalue = max(t)
        stdvalue = std(t)
        result.append([meanvalue, minvalue, maxvalue, stdvalue])
    return result


def show_timing_analysis(timing):
    """Just print timing statistics.
    """
    print "Showing statistics per entered password character:"
    ta = calculate_timing_analysis(timing)
    for index, t in enumerate(ta):
        print "Correct #%d: mean %.3fs, min: %.3fs, max: %.3fs, std: %.3fs" % \
              (index+1, t[0], t[1], t[2], t[3])


def is_good_enough_timing(timing, mean_lim, std_lim):
    """ Returns True if the given timing table is good enough. Good
    enough is determined by counting the average of last three
    entries. If the averages of mean and std values are below given
    values, the function returns True.
    """
    if len(timing) < 3:
        return False
    ta = calculate_timing_analysis(timing)
    last_three_mean_mean = mean([ta[-1][0], ta[-2][0], ta[-3][0]])
    last_three_mean_std = mean([ta[-1][3], ta[-2][3], ta[-3][3]])

    if last_three_mean_std < std_lim and last_three_mean_mean < mean_lim:
        return True
    return False

def main():
    print "Really Simple Password Trainer v1.4"
    print "(c) 2012 Antti Maula"
    print ""

    # Init the read_char
    init_read_char()

    # Limits
    required_correct = 20
    required_mean_lim = 0.5
    required_std_lim = 0.3
    limit = 100
    correct = 0
    incorrect = 0
    correct_times = []

    # Class counts
    c_normal_count = 0
    c_capital_count = 0
    c_number_count = 0
    c_special_count = 0


    try:
        # Read reference
        pwh = getpass('Reference password: ')
        for c in pwh:
            if c in c_normal:
                c_normal_count = c_normal_count + 1
            elif c in c_capital:
                c_capital_count = c_capital_count + 1
            elif c in c_number:
                c_number_count = c_number_count + 1
            else:
                c_special_count = c_special_count + 1
        pw_length = len(pwh)
        class_count = ( int(c_number_count>0) + int(c_normal_count>0) + \
                        int(c_capital_count>0) + int(c_special_count>0) )
        class_depth = len(c_number)*int(c_number_count>0) + \
                      len(c_normal)*int(c_normal_count>0) + \
                      len(c_capital)*int(c_capital_count>0) + \
                      33*int(c_special_count>0)
        combinations = class_depth ** pw_length

        print "\nReference password read, properties:"
        print "Length: %d characters" % pw_length
        print "Contains characters from %d classes (%d different characters)" % \
              (class_count, class_depth)
        print "Search space size: %d combinations" % combinations


        # Iterate
        print "\nNow, type the password again correctly for %d times" % \
              required_correct
        while correct < required_correct and correct+incorrect < limit and \
                  not is_good_enough_timing(correct_times, required_mean_lim, required_std_lim):
            pw, timing = read_password()
            if pw == pwh:
                print "Correct."
                correct = correct + 1
                correct_times.append(timing)

            elif len(pw) == 1 and ord(pw[0]) == 3:
                print "Exit requested."
                break

            else:
                print "*** Incorrect!"
                incorrect = incorrect + 1

            print "Status: %d correct, %d incorrect. %d more corrects required" % \
                  (correct, incorrect, required_correct-correct)

        if is_good_enough_timing(correct_times, required_mean_lim, required_std_lim):
            print "\nYour input quality exceeded requirements, hence no more attempts required"
        print "Completed. You got %d correct out of %d attempts\n" % (correct, correct+incorrect)

        
        show_timing_analysis(correct_times)

    except EOFError:
        print "\n\n\nTerminated by EOF.\n\n"
        exit(0)


if __name__ == '__main__':
    main()
