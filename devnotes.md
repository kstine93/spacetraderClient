# Development Notes

Notes on tricky problems, decisions, etc.

*Note: I'm starting this late - after a couple weeks of development (May 22nd, 2023)*

---

## Notes

---

### May 28, 2023
**Note on non-200 error codes:**
- All of the non-200 error codes that are NOT issues with the request or the server are still 2XX error codes (e.g., 201). I don't see a convincing reason now to bubble these error codes up to be handled individually - I will instead accept any 2XX error codes in the SpaceTraderConnection class as a fix.
  - **UPDATE:** This is not entirely true - a `409` error indicates that a cooldown is still in effect - which is a valid response. I need to find a way to bubble up these valide responses to the function that's calling this endpoint so that I can produce a non-exception response (e.g., log "Sorry, cooldown still in effect for X seconds...")
  - **IDEA:** What about an auto-retry that if I get a `409` response (indicating cooldown in effect, it just re-tries)

**UPDATE:** I have now changed the `stc_http_request` function so that it (a) no longer raises exceptions (I actually don't see why that would be necessary) and (b) it returns the response `status` along with the data in a dictionary.
This will now make it possible for me to handle non-200 http responses intelligently from the highest-level function (i.e., where I'm actually calling a specific endpoint).
---

### May 27, 2023
Ok, at this point I've gotten the 'ships' class to a level where I can actually play the game a little bit - flying to the asteroid field, surveying it, extracting resources, and going back to deliver resources as part of the contract.
However, the playing is a bit clunky still - and there's some things I haven't yet figured out.
Here's my to-do list:

**1. Change ship endpoints to be able to handle valid non-200 responses**
   1. Survey_waypoint is particularly bad because it returns valuable data which needs to be recorded (should I store this as a class variable or rather as a local variable when playing the game?)
      1. ~~Need to handle non-200 response code.~~
      2. **IDEA:** It's not a big deal if I don't cache the survey data - it's volatile and changes constantly - but it *would* be nice to handle it as some sort of class variable. I've played with the idea of having a class for an individual 'ship' that can inherit from the general 'ships' class, but has some specific state-data (like survey data) that is stored as class variables. Think about this some more...
   2. get_cooldown fails if no cooldown is there - give canned response instead to avoid error.
   3. Scan_waypoints provides useful data about all waypoints in the system - data which is NOT recorded in the systems data.
      1. ~~Need to handle non-200 response code.~~
      2. I probably need to immediately cache this in the 'systems' files I have - and then pull from that if needed - particularly since this command causes a cooldown
         1. This means that I need to figure out a way to update a **nested record** in the cache...
   4. Scan_systems is giving me very basic information about systems - and only a subset of them. I guess I can use this to discover systems that might not already be in the systems list?
      1. Need to handle non-200 response code.
      2. Again, this would be good to update the systems information with - but I'm not sure exactly what to do with these systems. Is it worth traveling to these vs. the already-listed systems?
   5. Scan_ships is giving me information on what ships are in the system at this moment; I guess there might be some multiplayer interactions. Cannot be cached - volatile information.
      1. Need to handle non-200 response code.
   6. chart_current_waypoint returns non-200 code if it has 'already been discovered'. Need to handle this.
**2. Finish systems endpoints**
   1. List_waypoints
   2. Get_waypoint
   3. get_market
   4. get_shipyard
   5. get_jumpgate
---

### May 26, 2023
**Notes on building 'ships' class**
1. Renamed to 'ships' class.
2. I'm uncertain if I should really be using a cache for ships data - a lot of the commands are transforming the ship data somehow - moving the ship or buying cargo, etc. All of these create a change in the state of the ship which invalidates the current cache. I could force a reload of the cache upon doing anything that causes a change, but that feels wasteful. Maybe I just don't need a cache.

---

### May 24, 2023 - Next steps
I've finished updating the base classes with new decorators for writing to the cache - and I'm pretty happy with them.
Here's my list of next things to do:
1. Write `FLEET` class
   1. NOTE: There are a lot of endpoints here, so this might be fairly complex, but using the same structure as your existing classes, there shouldn't be a big problem.
2. Start designing the game interface
   1. NOTE: The classes I've built so far are not really usable for a CLI game - they're still pretty abstract. I think I need to start chaining these commands together to create actual things that players want to do (e.g., fly to new system and orbit star; deliver contract and then update credits and cargo cache data). I should start figuring out what these groups of commands are (by playing the game, of course) and then do the following:
      1. Figure out if I need any more methods (or other architecture)
      2. Figure out how I want to set up a UI (even if it's just CLI)
3. Create startup script + build out README
   1. I want a startup script to set up all of the game structures and the README to help orient the player and help them do what they need to.

---

### May 22, 2023 - Decorators & different API calls
The big problem I'm having now is about how to deal with different API calls with the decorators I have.
The original decorator idea was (and is) good: don't call the API if I have a local file with the data I need already.
However, it then became complicated in a few ways:
- For some API calls, I trust the remote data more than the local data (i.e., if I'm requesting a change, the remote data is the UPDATED version of the data)
- For some API calls, I get a lot of data that I need to iterate over and store independently. In these cases, it's not possible to know prior to querying the API what data I'm going to get in the next 'page'.

> I think I need to better write down the use cases I have and then determine the best setup.

**My caching + API use cases:**
I have 3 ways the API pulls in data. In descending order of complexity:
- Paginated data: multiple pages with multiple records each pulled in one-by-one
  - Single page of data: one page with multiple records
    - Single record of data: one record

I have 2 ways I want to handle data requests:
- Return cached value if present; if not present then query API (decorator)
  - Always query API and update local cache

> It looks like my 2 ways of interacting with the caching + API are actually nested versions of each other. For dealing with the complexity of records, I can make 1 function which handles a single record. then a page of records function is just using that same function multiple times. Then, a paginated set of records is just using the page of records function multiple times.
> Similarly, I can make one function to query the API (call the function) and update the local cache. Then, a function which first checks the local file can do this and THEN call the first function.

**Notes:**
1. For LIST api calls - returning multiple records - there's no way of knowing beforehand whether the data I already have cached is sufficient. I don't know what specific records I will get (if I did, there's no need to call the API), so I have to make a choice:
   1. If ANY data is present locally, return that and assume it's complete
   2. ALWAYS call the API for LIST functions - and overwrite local data
      1. I might need to make this choice differently for different data - or maybe better would be to have a flag indicating if data NEEDS updating:
         1. FLEET (and maybe CONTRACTS) data might need to be updated regularly (i.e., at the beginning of any gaming session + every time I suspect a change has been made). This should be configurable (e.g., "force_call_api = True")
         2. SYSTEM, FACTION, and AGENT data is probably largely static. I don't think I should re-call these unless a GET function with a specific key finds more data not present in the existing file.

---

### May 13, 2023 - plan to set up the game

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
    1. Let's start with code needed to complete a contract:
        * Contracts:
            1. List available contracts
            2. Accept contract
            3. List contract terms
        * Navigation:
            1. List waypoints
            2. Scan waypoints

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
