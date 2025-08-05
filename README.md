# MMD - Multi Mode Dashboard


***This project is in a very early stage***


This project is designed to be the basis of a dashboard that unifies data from multiple sources.

The architecture is designed to be flexible; websockets in and out with a translation layer in between.

Data rendering will all be client side.
Dedicated 'sender' applications for each mode translating the events and data for their particular mode.

Only one sender application exists currently:

* mmdblfsender  AMI BLF Sender for Asterisk/FreePBX (https://github.com/Digital-Voice-Radio/mmd-blfsender)

The protocol between sender and server is far from finalised and in fact very specific to the current blf sender.  A next development priority is to define this protocol and build a second sender.



