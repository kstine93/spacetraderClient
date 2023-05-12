# Plan to setup game

So, I just registered myself and just got a HUGE amount of information in the resulting response. It included the following info:
1. Meta game information
    * Account ID
    * Key for accessing account
    * Callsign
2. Information on agent
    * Headquarters ID
    * Information about chosen faction (traits)
3. Information on newly-offered contract
    * payment
    * time limit
    * destination
    * required resources
4. Ship info
    * Navigation
        * location
        * next destination
    * Crew
        * Numbers
        * Wages
        * etc.
    * Fuel
    * Information on the ship itself
        * Frame
        * Reactor
        * Engine
        * Accessory modules (list)
        * Mounts (list - this is apparently somehow ship exterior modules?)
    * Ship "registration" (basically meta info)
    * Cargo
        * Capacity
        * Current inventory

---

This is a huge list of information - and I would expect that most of this information (everything except the game meta info maybe) would be queryable later.

**Next Steps:**
~~1. Look through documentation and see if I can indeed get this information elsewhere through other queries~~
    * ~~Yes, I can get agent details via the `my/agent` endpoint~~
    * ~~Yes, I can get contract details via `my/contracts` endpoint~~
    * ~~Yes, I can get ship details via `my/ships` endpoint~~
2. ~~If yes, prioritize saving only unique information (I can always query other info later)~~
    * ~~Only unique information is **API KEY** - and I can also save **callsign"** and **account ID** - I don't think these are sensitive details~~
3. ~~For unique key, look into encrypting my key with a password so I can store it on GH and unlock it anytime~~
4. ~~create script for decrypting and storing key locally~~
5. Create endpoints for all commands - use [api spec](https://spacetraders.stoplight.io/docs/spacetraders/11f2735b75b02-space-traders-api) to find these and prioritize.

After that's done, I should move more into other commands.

**Other Ideas:**
- How could I create a basic UI for running these commands?
    - I could wrap my Python code in shell scripts (i.e., shell scripts run series of python commands)
    - I could create a ASCII UI - but that might be a bit tedious
    - I could create an HTML interface - might be better



## Completely irrelevant ideas:

**Nested module import:**
I am having trouble when I import modules that I write which themselves depend on other modules I've written.

Here's the file structure I have:
```
-- commands
    \-- setup_commands.py
    \-- utilities
         \-- basic_utilities.py
-- unit_tests.py
```

For example, I have a base-level script called "basic_utilities.py".
I use this script in another script called "setup_commands.py", so I import it in this script as `from utilities.basic_utilities.py import *`
I can run "setup_commands.py" and it works great.

Now, I want to have a "unit_tests.py" - which is testing individual functions in "setup_commands.py".
So, in this file I import this file as `from commands.setup_commands import *`
However, this command *FAILS*.

It fails because the "unit_tests.py" script is trying to run the command `from utilities.basic_utilities.py import *` directly from the "setup_commands.py" script that it imported - but it can't do this because the "unit_tests.py" script is running from the parent folder, so it doesn't find the 'utilities' folder in the working directory.

> What I want:
> I want to be able to import other scripts in a way that will allow me to run "setup_commands.py" as a standalone script AND "unit_tests.py" as a standalone script - without needing to change any import statements to be appropriately relative.
