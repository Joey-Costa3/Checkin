#!/bin/bash

find . -exec chown attend:attend {} \;
find . -type d -exec chmod 770 {} \;
find . -type f -exec chmod 660 {} \;
find scripts/ -type f -exec chmod 770 {} \;
