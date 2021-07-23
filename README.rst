.. -*- fill-column: 79; mode: rst; eval: (flyspell-mode) -*-

==================================
Butch - The free Batch interpreter
==================================

.. |butch| replace:: Butch Coolidge
.. _butch: https://pulpfiction.fandom.com/wiki/Butch_Coolidge

Named after the famous Pulp Fiction boxer |butch|_ from Tennessee.

**********
How to run
**********

Installation
============

.. code::

   pip install butch

Post-Installation
-----------------

.. |sitepkgs| replace:: ``site.getsitepackages()``
.. _sitepkgs: https://docs.python.org/3/library/site.html#site.getsitepackages

Make sure to run the test suite after the installation to verify everything
works as it should. The test suite is included in the package itself, so it
should be located in the first ``site-packages`` folder found via |sitepkgs|_.

.. code::

   python $(python -c "import site;print(site.getsitepackages()[0])")/butch/test.py

Development
-----------

Get the latest version:

.. code::

   pip install https://github.com/KeyWeeUsr/butch/zipball/master

Running
=======

Butch is available as a standalone executable as well as a Python module,
therefore it can be invoked by any of these commands if installed properly::

   butch
   python -m butch

which will launch the REPL (console) directly.

Use ``butch /C "echo Hello, Batch"`` for interpreting a Batch command from a
string or use ``butch /C hello.bat`` to run Batch from a file.

Use ``/K`` switch instead of ``/C`` to jump into the console after a command or
a file finishes.

Use ``butch /h`` to display help for other switches.

********
Features
********

Commands
========

.. |CD| replace:: CD
.. _CD: https://ss64.com/nt/cd.html

- [ ] `ASSOC <https://ss64.com/nt/assoc.html>`__
- [ ] `CALL <https://ss64.com/nt/call.html>`__
- [X] |CD|_

  *pending:*

  - [ ] ``/D`` change current drive + path

- [X] `CHDIR <https://ss64.com/nt/chdir.html>`__
- [X] `CLS <https://ss64.com/nt/cls.html>`__
- [ ] `COLOR <https://ss64.com/nt/color.html>`__
- [ ] `COPY <https://ss64.com/nt/copy.html>`__
- [X] `DATE <https://ss64.com/nt/date.html>`__

  *pending:*

  - [ ] set the system date when called without arguments

- [X] `DEL <https://ss64.com/nt/del.html>`__

  *pending:*

  - [ ] ``/F`` force deleting of read-only files
  - [ ] ``/S`` delete specified files from all subdirectories
  - [ ] ``/A`` selects files to delete based on attributes

- [X] `DIR <https://ss64.com/nt/dir.html>`__

  *pending:*

  - [ ] Volume drive lookup
  - [ ] Volume label on drive
  - [ ] ``/A``
  - [ ] ``/B``
  - [ ] ``/C``
  - [ ] ``/D``
  - [ ] ``/L``
  - [ ] ``/N``
  - [ ] ``/O``
  - [ ] ``/P``
  - [ ] ``/Q``
  - [ ] ``/S``
  - [ ] ``/T``
  - [ ] ``/W``
  - [ ] ``/X``
  - [ ] ``DIRCMD`` env variable preset

- [X] `ECHO <https://ss64.com/nt/echo.html>`__
- [ ] `ENDLOCAL <https://ss64.com/nt/endlocal.html>`__
- [X] `ERASE <https://ss64.com/nt/erase.html>`__
- [X] `EXIT <https://ss64.com/nt/exit.html>`__
- [ ] `FOR <https://ss64.com/nt/for.html>`__
- [ ] `FTYPE <https://ss64.com/nt/ftype.html>`__
- [ ] `GOTO <https://ss64.com/nt/goto.html>`__
- [ ] `IF <https://ss64.com/nt/if.html>`__
- [X] `MD <https://ss64.com/nt/md.html>`__
- [X] `MKDIR <https://ss64.com/nt/md.html>`__
- [ ] `MKLINK <https://ss64.com/nt/mklink.html>`__
- [ ] `MOVE <https://ss64.com/nt/move.html>`__
- [ ] `PATH <https://ss64.com/nt/path.html>`__
- [X] `PAUSE <https://ss64.com/nt/pause.html>`__
- [ ] `POPD <https://ss64.com/nt/popd.html>`__
- [X] `PROMPT <https://ss64.com/nt/prompt.html>`__
- [ ] `PUSHD <https://ss64.com/nt/pushd.html>`__
- [X] `RD <https://ss64.com/nt/rd.html>`__
- [ ] `REM <https://ss64.com/nt/rem.html>`__
- [ ] `REN <https://ss64.com/nt/ren.html>`__
- [X] `RMDIR <https://ss64.com/nt/rmdir.html>`__
- [ ] `SET <https://ss64.com/nt/set.html>`__

  *pending:* pretty much everything except the basic value add + clear

  - [ ] case-insensitive access, but case-sensitive output

- [ ] `SETLOCAL <https://ss64.com/nt/setlocal.html>`__
- [ ] `SHIFT <https://ss64.com/nt/shift.html>`__
- [ ] `START <https://ss64.com/nt/start.html>`__
- [ ] `TIME <https://ss64.com/nt/time.html>`__
- [X] `TITLE <https://ss64.com/nt/title.html>`__
- [ ] `TYPE <https://ss64.com/nt/type.html>`__
- [ ] `VER <https://ss64.com/nt/ver.html>`__
- [ ] `VERIFY <https://ss64.com/nt/verify.html>`__
- [ ] `VOL <https://ss64.com/nt/vol.html>`__
- [ ] `:: <https://ss64.com/nt/rem.html>`__
- [ ] External commands
- [ ] CLI prioritization of external commands

Syntax
======

- [X] Echo off (``@``)
- [X] Quotes (``"``)
- [X] Quotes (``"``) in words
- [ ] Conditions (``IF``, ``ELSE``)
- [ ] Caret escaping (``^``)
- [ ] Code blocks (``(``, ``)``)
- [ ] Code blocks (multi-line block with ``(``, ``)``)
- [X] Redirection to commands (``|`` - pipes)

  *pending:*

  - [ ] some individual commands don't pull ctx.output and related parts
  - [ ] generic command I/O handling as a decorator/class?

- [ ] I/O Redirection

  *pending:*

  - [X] ``>`` create new file
  - [ ] ``>>`` append to existing file or create if missing
  - [ ] ``<`` read file to STDIN

  https://ss64.com/nt/syntax-redirection.html

- [ ] Redirection to special (``nul``)
- [ ] Command concatenation (``&``)
- [ ] Command concatenation (``&&``)
- [ ] Command concatenation (``||``)
- [ ] Recognize Windows path separator in path input (``\``)

Console
=======

.. |ANSI| replace:: ANSI
.. _ANSI: https://en.wikipedia.org/wiki/ANSI_character_set

.. |UCS2| replace:: Unicode UCS-2 LE
.. _UCS2: https://en.wikipedia.org/wiki/Universal_Coded_Character_Set

- [ ] ``/?`` as a proper help page trigger
- [ ] ``/T`` for foreground/background colors
- [ ] ``/A`` for printing only |ANSI|_ (which is most likely just 1252)
- [ ] ``/U`` for printing Unicode (|UCS2|_)
- [ ] ``/D`` registry with autorun commands (.bashrc, kind of) + ignore
- [ ] ``/E:ON|OFF``, ``/X``, ``/Y`` enable/disable command extensions
- [ ] ``/S`` quote stripping from commands
- [ ] ``/V:ON|OFF`` delayed expansion

****
TODO
****

- [ ] `Ensure <https://github.com/kislyuk/ensure>`__ for dynamic type checking
- [ ] `Mypy <https://github.com/python/mypy>`__ for static type checking
- [/] Documentation
- [X] PyPI package
- [ ] Library interface for programmatic emulation
