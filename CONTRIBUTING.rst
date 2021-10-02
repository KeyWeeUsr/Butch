.. -*- fill-column: 79; mode: rst; eval: (flyspell-mode) -*-

=======================================================
Butch - The free Batch interpreter's contributing guide
=======================================================

*************
Prerequisites
*************


.. |gpghow| replace:: (how)
.. _gpghow: https://docs.github.com/en/github/authenticating-to-github/managing-commit-signature-verification/generating-a-new-gpg-key

#. GPG key associated with your GitHub account |gpghow|_
#. CLA signed

How to sign CLA
===============

#. Fork the repository
#. Clone the fork locally - ``git clone https://github.com/<you>/Butch``
#. Visit the `CLA.rst` document in the repository
#. Read the document
#. Add a row with your data
#. Commit the changes and sign the commit
   (``git commit -m "message" --gpg-sign``)
#. Push the changes to your fork
#. Open a pull request in Butch repository

********************************
Create a development environment
********************************

.. |venv| replace:: ``virtualenv``
.. _venv: https://virtualenv.pypa.io/en/latest/

For Butch it's okay just to use a |venv|_ package, however if you prefer, feel
free to utilize Docker to separate the environment completely from the system
and just mount the files/folders from the cloned repository.

Linux and MacOS
===============

#. ``cd <cloned-repo>``
#. ``python -m virtualenv ~/env_butch``
#. ``source ~/env_butch/bin/activate``
#. ``pip install --editable .[dev]``
#. ``python test.py``

Windows
=======

#. ``cd <cloned-repo>``
#. ``python -m virtualenv %USERPROFILE%\env_butch``
#. ``%USERPROFILE%\env_butch\bin\activate``
#. ``pip install --editable .[dev]``
#. ``python test.py``

*****************************************
Modify some files and open a pull request
*****************************************

#. Modify a file
#. Add a file with changes - ``git add <file>``
#. Check the style by running - ``python style.py``
#. Commit the changes using - ``git commit -m "message" --gpg-sign``
#. Verify the commit(s) are changed with - ``git log --show-signature``
#. Push the changes to your fork - ``git push``
#. Navigate to https://github.com/KeyWeeUsr/Butch/pulls
#. Create a new pull request (don't forget to describe your changes)
#. Wait for review (adjust after review if necessary)
#. Wait for the merge
