.. -*- fill-column: 79; mode: rst; eval: (flyspell-mode) -*-

==========================
Butch - the Batch emulator
==========================

.. |butch| replace:: Butch Coolidge
.. _butch: https://pulpfiction.fandom.com/wiki/Butch_Coolidge

Named after the famous Pulp Fiction boxer |butch|_ from Tennessee.

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
- [ ] `CLS <https://ss64.com/nt/cls.html>`__
- [ ] `COLOR <https://ss64.com/nt/color.html>`__
- [ ] `COPY <https://ss64.com/nt/copy.html>`__
- [ ] `DATE <https://ss64.com/nt/date.html>`__
- [X] `DEL <https://ss64.com/nt/del.html>`__

  *pending:*

  - [ ] ``/F`` force deleting of read-only files
  - [ ] ``/S`` delete specified files from all subdirectories
  - [ ] ``/A`` selects files to delete based on attributes

- [ ] `DIR <https://ss64.com/nt/dir.html>`__
- [X] `ECHO <https://ss64.com/nt/echo.html>`__
- [ ] `ENDLOCAL <https://ss64.com/nt/endlocal.html>`__
- [X] `ERASE <https://ss64.com/nt/erase.html>`__
- [X] `EXIT <https://ss64.com/nt/exit.html>`__
- [ ] `FOR <https://ss64.com/nt/for.html>`__
- [ ] `FOR <https://ss64.com/nt/for.html>`__
- [ ] `FOR <https://ss64.com/nt/for.html>`__
- [ ] `FTYPE <https://ss64.com/nt/ftype.html>`__
- [ ] `GOTO <https://ss64.com/nt/goto.html>`__
- [ ] `IF <https://ss64.com/nt/if.html>`__
- [ ] `MD <https://ss64.com/nt/md.html>`__
- [ ] `MKLINK <https://ss64.com/nt/mklink.html>`__
- [ ] `MOVE <https://ss64.com/nt/move.html>`__
- [ ] `PATH <https://ss64.com/nt/path.html>`__
- [X] `PAUSE <https://ss64.com/nt/pause.html>`__
- [ ] `POPD <https://ss64.com/nt/popd.html>`__
- [X] `PROMPT <https://ss64.com/nt/prompt.html>`__
- [ ] `PUSHD <https://ss64.com/nt/pushd.html>`__
- [ ] `RD <https://ss64.com/nt/rd.html>`__
- [ ] `REM <https://ss64.com/nt/rem.html>`__
- [ ] `REN <https://ss64.com/nt/ren.html>`__
- [ ] `RMDIR <https://ss64.com/nt/rmdir.html>`__
- [ ] `SET <https://ss64.com/nt/set.html>`__

  *pending:* pretty much everything except the basic value add + clear

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
- [ ] Redirection to commands (``|`` - pipes)
- [ ] Redirection to files (``<``, ``<<``, ``>>``, ``>``)
- [ ] Redirection to special (``nul``)
- [ ] Command concatenation (``&``)
- [ ] Command concatenation (``&&``)
- [ ] Command concatenation (``||``)
- [ ] Recognize Windows path separator in path input (``\``)

TODO
****

- [ ] `Ensure <https://github.com/kislyuk/ensure>`__ for dynamic type checking
- [ ] `Mypy <https://github.com/python/mypy>`__ for static type checking
- [ ] Documentation
- [ ] PyPI package
- [ ] Library interface for programmatic emulation
