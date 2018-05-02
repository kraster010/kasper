# coding=utf-8
import os
from subprocess import check_output, CalledProcessError


def stop(reset=False, migrate=False):
    """
    tool per chiudere evennia completamente
    """
    # cambiare con il proprio virtual env
    virtual_env = "kasper"

    if len(check_output(["workon", virtual_env], shell=True).strip()) > 0:
        print "Non hai nessun virtual env con nome: %s\n"
        return

    try:
        s = check_output(["workon", virtual_env, "&", "echo", "%cd%"], shell=True).strip()
        if s != os.path.abspath("."):
            print "workon non è configurato nella cartella giusta (cioè da dentro il virtualenv se digito cdproject " \
                  "devo finire nella home del progetto) ma è necessario per eseguire questo script."
            return
    except CalledProcessError:
        pass

    try:
        check_output(["Taskkill", "/IM", "twistd.exe", "/F"], shell=True)
    except CalledProcessError:
        pass

    try:
        portal_file = os.path.join("server", "portal.pid")
        with open(portal_file, "r") as f:
            pid = f.readline().strip()
            f.close()
            try:
                check_output(["Taskkill", "/PID", pid, "/F"], shell=True)
                print "deleted file at pid: {}".format(pid)
            except CalledProcessError:
                pass
            os.remove(portal_file)
    except IOError:
        pass

    try:
        server_file = os.path.join("server", "server.pid")
        with open(server_file, "r") as f:
            pid = f.readline().strip()
            f.close()
            try:
                check_output(["Taskkill", "/PID", pid, "/F"], shell=True)
                print "deleted file at pid: {}".format(pid)
            except CalledProcessError:
                pass
            os.remove(server_file)
    except IOError:
        pass

    if reset:
        try:
            database_file = os.path.join("server", "evennia.db3")
            os.remove(database_file)
        except:
            pass

    if migrate:

        try:
            s = check_output(["workon", virtual_env, "&", "evennia", "migrate"], shell=True)
            print s
        except CalledProcessError:
            pass

        try:
            s = check_output(
                ["workon", virtual_env, "&", "django-admin", "createsuperuser", "--username", "a", "--email", "a@a.it",
                 "--noinput", "--settings=server.conf.settings"], shell=True)
            print s
        except CalledProcessError:
            pass

    print "fine."


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='tool per chiudere evennia completamente.')
    parser.add_argument('--reset', dest='reset', action='store_true', default=False, help="resetta tutto anche il db")
    parser.add_argument('--migrate', dest='migrate', action='store_true', default=False,
                        help="migra il db al t ermine di tutto")

    args = parser.parse_args()

    stop(reset=args.reset, migrate=args.migrate)
