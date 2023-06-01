#!/bin/bash

#-----------
#For testing, it's a pain to always enter the password; in development, I'm pulling
#directly from a shell variable instead so I only have to set it once:
# if [ -z "${SPACETRADER_PASSWORD}" ]
# then
#     echo -n Enter Spacetrader Password:
#     read password
#     export SPACETRADER_PASSWORD="${password}"
#     echo "${SPACETRADER_PASSWORD}"
# else
#     echo "Proceeding with password in shell variables"
# fi

#-----------
#echo "Done!"
python3 -m unittest discover ./tests
