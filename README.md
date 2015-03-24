# PySHed

PySHed simplifies access to shell commands and command-line applications from within Python scripts. Its use is straightforward:

1. Import the desired command or executable name from the `pyshed` module;
1. Call the import function as a standard Python callable, passing runtime options as an argument list.

For example:

    from pyshed import ls

    for line in ls('-lh'):
        print line

All functions imported in the manner above return a `batch` object when called, which serves as an interface to the underlying shell process (see below for more details). Functions also support the following optional, named arguments:

* `daemon` - if `False`, the underlying process remains active even after the calling script terminates (until it terminates by itself, of course);
* `delay` - if present, execution halts for the given number of seconds after the requested shell call is made;
* `stderr` - specifies the standard error channel for the underlying process. Legal values are `pyshed.PIPE` (which pipes output into the batch object's stderr attribute), `pyshed.STDOUT` (which redirects output to the same handler used for standard output), `pyshed.STDNUL` (which sends all output to the null device, i.e. discards it), an existing file descriptor (a positive integer), an existing file object, or a string containing a file path, which will be open in rewrite mode and used to record outputs;
* `stdout` - specifies the standard output channel for the underlying process. Legal values are `pyshed.PIPE` (which pipes output into the batch object's stderr attribute), `pyshed.STDNUL` (which sends all output to the null device, i.e. discards it), an existing file descriptor (a positive integer), an existing file object, or a string containing a file path, which will be open in rewrite mode and used to record outputs.

Any initialization arguments supported by [`Popen`](https://docs.python.org/2.7/library/subprocess.html#popen-constructor) can also be specified as named arguments on the function call.

The `batch` class inherits from `Popen` and supports all its [features](https://docs.python.org/2.7/library/subprocess.html#popen-objects), while adding the following customizations and extensions:

* By default both standard and error outputs are collected in the `stdout` attribute. This can be changed at instantiation time using the named arguments `stdout` and `stderr`, as indicated above;
* Whereas `Popen` objects try to remain alive for as long as the underlying process is active, batch objects work the other way around by terminating the process (if not yet finished) when they're selected for garbage collection (the original behaviour can be restored by entering the `daemon` named argument with a value of `False`);
* `batch` objects are iterable, returning the next (right-trimmed) line of output at each iteration;
* `batch` objects are also their own context managers, terminating the underlying process (if not yet finished) when the context is exited;
* Finally, `batch` objects implement the `close()` method, which terminates the underlying process if it hasn't yet finished, and does nothing otherwise.

Using the `pyshed` module makes possible to write Python scripts that seamlessly interface with shell applications, for example:

    #! /usr/bin/env python
    #coding=utf-8

    # repo_dirty.py - scans a repo base for git projects containing non-commited changes

    from re import search
    from batcher import git, repo

    def gitdirty(path):
        for line in git('status', cwd=path):
            if search(r'(On branch master)|(nothing to commit)', line) != None:
                print 'Project "%s" is dirty' % path
                return True

        return False

    def repodirty():
        projects = 0
        dirty = 0
        for path in repo('forall', '-c', 'pwd'):
            projects += 1
            dirty += 1 if gitdirty(path) else 0

        print 'Finished checking dirty projects'
        print 'Total projects checked: %d' % projects
        print 'Dirty projects: %d' % dirty

    def main():
        repodirty()

    if __name__ == '__main__':
        main()

See other examples in the [code base](https://github.com/xperroni/PySHed/tree/master/Code).

Build & Install
---------------

PySHed is a pure Python package, so there is not much to do besides copying the `pyshed` package to a path within the Python search path. This can be accomplished by running the included `setup.py` script:

    # python setup.py install

Depending on your system's configuration you may need root permission to run the command above.

Version History
---------------

**2015-03-24**

Initial revision.

TO DO
-----

* Add more script samples;
* Review code documentation.
