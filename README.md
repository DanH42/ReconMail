ReconMail
=========

Detects system messages sent by Broad Ops Recon software and relays them via email

Requirements
------------

- Python 2.7
- A local SMTP server (such as sendmail, exim, or postfix)
- GNU screen (optional)

This script has not been tested on Windows, and may not work on non-*NIX systems.

Usage
-----

It's recommended that you run this script inside a screen session (`screen -S reconmail`) so ti can run in the background once you close the terminal.

To start the script:

    $ python2.7 reconmail.py your_address@email.com

When the script detects a network message, it will parse the message, acknowledge it, and then email its contents to the address provided.

Warning
-------

This script is, and probably always will be, in beta. While reasonable precautions have been taken, there's always a *slight* possibility that it could cause you to miss an important message. Use at your own risk.
