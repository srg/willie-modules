"""
a script that will remove all the unwanted installed willie modules
 from site.sitepackages()
"""
import os, site, sys
from errno import EACCES

whitelist = ["__init__", "admin", "reload"]

def rm_rf(site_packages_dir):
    path = "%s/willie/modules/" % site_packages_dir
    deleted = 0
    if os.path.isdir(path):
        try:
            for f in os.listdir(path):
                delete = True
                for wh in whitelist:
                    if f == wh + ".py" or f == wh + ".pyc":
                        delete = False
                        break
                if delete:
                    print "Deleting", path + f
                    os.remove(path + f)
                    deleted += 1
                else:
                    print "Skipping", path + f
        except OSError as (errno, sterror):
            if errno is EACCES:
                print "Permission denied! Run as root!"
                sys.exit(1)
    return deleted


if __name__ == "__main__":
    site_dirs = site.getsitepackages()
    for site_dir in site_dirs:
        deleted = rm_rf(site_dir)
        print "Deleted %d modules from %s" % (deleted, site_dir)
