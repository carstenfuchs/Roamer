import glob, os, subprocess, sys


RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(30, 38)


def Warn(x):
    return (COLOR_SEQ % (RED)) + x + RESET_SEQ

def Info(x, col=GREEN):
    return (COLOR_SEQ % (col)) + x + RESET_SEQ


def run(cmd, cwd=None, specialCase=None):
    print(Info("\n{}$".format(cwd or ""), BLUE), Info(" ".join(cmd), BLUE))
    try:
        if specialCase == "showmigrations":
            for l in subprocess.check_output(cmd, universal_newlines=True).splitlines():
                if not "[X]" in l:
                    print(l)
        else:
            subprocess.call(cmd, cwd=cwd)
    except OSError as e:
        print(Warn(e.strerror))
    except KeyboardInterrupt:
        print("(got Ctrl+C)")


if __name__ == "__main__":
    print(Info("\n$ # manually update the source code from the Git repository", BLUE))

    # Laufen wir innerhalb einer virtualenv? (Sollte `pip` nicht ausführen, wenn das nicht der Fall ist.)
    # Siehe http://stackoverflow.com/questions/1871549/python-determine-if-running-inside-virtualenv
    # Innerhalb einer virtualenv sollte sys.prefix etwas wie "/home/carsten/.virtualenvs/Zeiterfassung"
    # sein (wir verwenden es unten nochmal), sys.real_prefix etwas wie "/usr".
    if not hasattr(sys, 'real_prefix'):
        print(Warn("\nEs scheint keine virtualenv aktiv zu sein.\n"))
        sys.exit()

  # run(["svn", "update"])
    run(["pip", "install", "-q", "-r", "requirements.txt"])

  # run(["python", "make.py", "--pdf"], cwd="Handbuch")
    run(["python", "manage.py", "collectstatic", "--noinput"])
    run(["python", "manage.py", "check", "--deploy"])
  # run(["python", "manage.py", "checkDatabase"])
  # run(["python", "manage.py", "clearsessions"])
    run(["python", "manage.py", "showmigrations"], specialCase="showmigrations")

    #  $ ./tools/loadFilialoeffnungszeiten.py                       <-- ist nur EIN Mal durchzuführen, nicht auf jedem Lori-Server!
    #  $ ./tools/updatePekoBenchmarkCache.py                        <-- ist nur EIN Mal durchzuführen, nicht auf jedem Lori-Server!
    #  $ ./tools/updateSalden.py       # eher selten, idR nur bei konkretem Anlass oder probehalber     <-- ist nur EIN Mal durchzuführen, nicht auf jedem Lori-Server!

    # run(["touch", "--no-create", "Zeiterfassung/wsgi.py"])

    # Führe die Tests aus:
    # python -Wall -Werror manage.py test --keepdb --failfast

    print("All done.\n")
