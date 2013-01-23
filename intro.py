import sys
import subprocess
import csv
import urllib
from optparse import OptionParser

import settings

def load_people(filename="people.csv"):
    r = csv.reader(open(filename))
    people = {}
    for person in r:
        people[person[0]] = [person[1], person[2]]
        if not person[1]:
            people[person[0]][0] = person[0].title()
    return people

def save_person(nick, desc, name=None, filename="people.csv"):
    with open(filename, 'ab') as csvfile:
        w = csv.writer(csvfile)
        w.writerow([nick, name, desc])

def write_introduction(people, message):
    i = " & ".join([v[0] for n,v in people.items()]) + ", please meet.\n\n"
    i += "\n\n".join([v[1] for n,v in people.items()])
    if message:
        i += "\n\n" + message
    else:
        i += "\n\n" + settings.closing
    i += "\n\n" + settings.valediction + ",\n\n" + settings.name
    return i

def prompt_for_mail_client():
    """Ask if user wants to launch default mail client"""
    answ = raw_input("\nOpen default client with above message? (y/n) ").lower()
    if not answ or answ not in ["y","n"]:
        print "Please answer 'y' or 'n'."
        return prompt_for_mail_client()
    elif answ == "y":
        return True
    else:
        return False

def open_client(introducing, msg):
    """Open default mail client with filled subject & body"""
    subject = urllib.quote("Introduction from %s" % settings.name)
    body = urllib.quote(msg)
    s = "mailto:?subject=%s&body=%s" % (subject, body)
    if "linux" in sys.platform:
        proc_args = ["xdg-open", s]
    elif "darwin" in sys.platform:
        proc_args = ["open", s]
    # TODO: os.startfile works in Windows?
    p = subprocess.Popen(proc_args)

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-a", "--add", dest="add", action="store_true")
    parser.add_option("-m", "--message", dest="message", default=False, action="store")
    (options, args) = parser.parse_args()

    if options.add: # we're adding a new person
        if len(args) == 2:
            save_person(args[0], args[1])
        else:
            save_person(args[0], args[2], args[1])

    else: # write the intro
        people = load_people()

        introducing = {} # get the people data from the set
        for person in args:
            try:
                introducing[person] = people[person]
            except KeyError, e:
                print "Missing person %s in your data!" % e
                sys.exit()

        msg = write_introduction(introducing, options.message)
        print msg

        platform_ok = "linux" in sys.platform or "darwin" in sys.platform
        if platform_ok and prompt_for_mail_client():
            open_client(introducing, msg)

        p = subprocess.Popen(["pbcopy"],stdin=subprocess.PIPE)
        p.stdin.write(msg)
