# Development Notes

Notes on tricky problems, decisions, etc.

*Note: I'm starting this late - after a couple weeks of development (May 22nd, 2023)*

---

## Notes

### June 11, 2023
I've made good progress on my to-dos from June 10th - one thing still left is **profit-finding**
--> I think I should make this a function the markets class, since I need to access those data via cache so much.
Let's work on a prototype!


---

### June 10, 2023

- I have now implemented all of the most important 'ship' methods (excluding 'chart')
  - I just found out I'm missing 'negotiate' - which has finally been updated: https://spacetraders.stoplight.io/docs/spacetraders/1582bafa95003-negotiate-contract

There are now some ways I want to branch out:

**MARKET DATA -- DONE**
The 'get_market' endpoint operates in 2 different ways:
1. If you are AT the market waypoint, you get buy/sell prices
2. If you are NOT at the market waypoint, you only get a list of what's bought/sold

I think it's worth my while to store these market buy/sell prices persistently. I'm not sure how volatile they are, but I want to assume they're quite stable until proven otherwise - the advantages of not having to fly around to remember what prices were is very worthwhile.
I think the most graceful way to do this would be to make a new 'market' cache - with waypoints as keys. I could store it with 'systems' but that is becoming somewhat overloaded, and market data is less relevant for exploration. This would be the logic for caching:
1. If get_market is called in the same system where we are (dependent on ship status), then the result will have buy/sell prices and be up-to-date
   1. Store this data peristently
2. If get_market is called in a DIFFERENT system, try to find the data in the persistent store
   1. If none exists, call the API and at least get the list of commodities. Store this record in the persistent store (will be force-updated next time we get_market in-location)

> We have different behavior depending on where the ship is - which suggests designing this in the ship_operator class. I could keep my get_market function with a new decorator for looking in cache (as normal) and then I could make another update_market method for force-calling API and force-updating cache.

**CONTRACTS -- DONE**
I want to build out my shipOperator class to be able to deal with contracts - should be as simple as adding new instances and calling the contracts endpoints.

**PROFIT-FINDING**
I've built a prototype function in my test notebook for comparing market price data between 2 waypoints and finding the difference in buy + sell prices that might indicate a profitable reselling of goods purchased from one waypoint at another.
I want to expand this to work with the cached data - ideally it could look across all collected market prices across all systems I've visited and establish which trade routes with what goods would be most profitable!

**BETTER SELLING -- DONE**
adapt sell method to sell all by default.

---

### June 9, 2023

**NEXT TO-DOS**
1. ~~Got a lot of uncommited changes - figure out reasonable commit packets and make the commits.~~
2. ~~Continue filling out methods for ship_operator.~~

**Handling API errors**
I'm trying to figure out where to best handle API errors.
So far, I've not been handling them - just letting them percolate up - which I quite like. But now, I
want *some* failed API calls to print their error messages rather than causing a crash. Where to best implement this?
- Not in SpaceTraderConnection I think - I don't necessarily want all API calls to be soft-handled...
- Maybe in ShipOperator? I like handling them here so I can tweak the UI (this is basically UI)
- Best might be in the intermediate classes I have - error handling is largely tied to endpoint, so I can designate which endpoints should be 'soft fail'
  - **UPDATE:** I need to do this where I am parsing the data - *not before*. So I can either (a) print the error message or (b) parse the data. This means I really need to do it in ShipOperator.
    - **UPDATE:** I'm adding calls to `response_ok` in SpaceTraderConnection class before any times I parse response data (this can be earlier for cached data)


**Handling cooldown**
I'm trying to figure out how I want to handle **ship cooldown**. Here's what I know:
1. Some ship actions produce cooldown, others do not. Producing cooldown:
   1. survey
   2. scan waypoints
   3. scan sysytems
   4. scan ships
   5. extract resources
   6. refine resources
2. Cooldown information is returned by each of the actions above - so I could have some kind of decorator to 'track cooldown' as soon as these above actions return successfully
   1. This tracker could do a few things:
      1. Simply start threaded timer and print message when complete
      2. **put cooldown expiration in class variable to be queried later**
         1. I like this - it doesn't actually matter when the cooldown expires - **it only matters if I'm trying to do something else while the cooldown is still in-effect**

> Let's move forward with a decorator which checks cooldown before allowing a cooldown-dependent function to run.
> **NOTE:** Check beforehand if ALL functions are stopped when we're on cooldown, or just a few.
>  -- From a basic check of 'Nav' and 'get_ship' - it looks like only the ship actions which produce cooldown actually also are limited by cooldown.

---

### June 8, 2023

**UPDATE**
I've been doing a lot today
1. I started the foundations of a neat ASCII-based animation set within the 'art' directory. I implemented it for waypoint navigation. Since there's not much that can be done while traveling, this seems nice.
   1. This **will** need to be refactored - but I think I'll wait until I have more animations first.
2. I built logic to extract resources based on surveys that are stored in class variables. Specifically, the logic looks for the best possible survey to use given a targeted resource.


**Next Steps**
1. I'm not really handling errors yet - figure out where I can best do this
   1. Also, what behavior do I want? custom error messages depending on method? Just print the error message from the API?
2. Find better way to persist class variable data (particularly surveys, which are semi-valuable).
   1. Maybe store state on disk at regular intervals (or after particular actions) and then try to first reload state from disk upon making a new instance?
      1. Could be based on ship name - so I wouldn't have to worry about multiple ships / players
      2. I could store this somehow alongside the 'ships' data I already have - which is kind of game data too.


---

### June 7, 2023
1. ~~Run all tests again - see where else my changes to caching function (Adding leading key) have impacts~~
2. ~~Commit changes to caching function~~
3. Read more about interfaces and see if I should refactor my 'ShipInterface' implementation or not... [article here](https://realpython.com/python-interface/)
   1. It seems this is a way to solve multiple inheritance and isn't really necessary in Python
   2. It's also described as a way to provide a 'contract for implementing functionality' - which is not exactly what I'm going for.
4. ~~Commit first version of Spaceship class (Change name?)~~
5. Continue developing spaceship class

---

### June 6, 2023

Todo next:
1. ~~Nav_to_waypoint is not working again- figure out why.~~
   1. **RESOLVED:** Required an extra header `{"Content-Type":"application/json"}`
2. ~~Test that nav_data looks o.k. when navigating to new waypoint~~
   1. ~~Using this info, finish __set_status method in spaceship class.~~
      1. ~~**Yes, format was exactly the same - no extra data on 'arrival' like I feared**~~

**Notes on building new interface layer**
I've now cleaned up my code and I'm ready to start building a new interface layer.

Here's my proposed order of tasks:
1. Build stateful 'individual_ship' class - this can hold:
   1. data on state of the ship (fuel, cargo)
   2. data on location of ship (current system, current waypoint)
   3. detailed info on location (waypoint scan, system scan, survey data)
2. See if I can build a basic CLI for playing the game
   1. Maybe build more complex commands in the CLI?
      1. e.g. SURVEY, EXTRACT, REFINE
3. See if I can build a command queue
   1. Not sure yet how to implement this... Maybe in a native Python queue? Should ideally be persistent across sessions.

---

**IDEAS on next layer of interface**
The game is vaguely playable just from a python notebook - but I have to keep running around to find certain commands, and commenting out commands I don't want to run - which is a pain.
Other stuff I want to figure out:
1. Can I chain together commands in a reasonable way (e.g., SURVEY then EXTRACT then REFINE) and have higher-level functions to do this?
2. Can I make a QUEUE of commands!? Since the cooldown is such a pain, it would be great if I could queue commands which get executed as soon as the last cooldown is over.
   1. Something like "Jump to X system, nav to Y waypoint, survey and extract repeatedly until you get 50 units of copper, then go to Z waypoint" - that would be awesome.
3. Can I make more granular classes (particularly for 'ships') which hold more runtime information?
   1. Currently my program has no state - it has a database (cache) but that's it. But the ships class does have some endpoints which point towards state
      1. System the ship is currently in
      2. scan of waypoints
      3. survey data for certain waypoints
4. Can I make more of a nice interface for the player? (I like the idea of starting with some ASCII and moving to HTML from there)
   1. Buttons instead of CLI to run commands
   2. Some kind of heads-up display (or at least ASCII?)
   3. Current contract info & progress & time left
   4. Current state of ship & queue
   5. Maybe a player-editable to-do list

---

### June 4, 2023

**Notes on transferring to composition over inheritance**
I'm running into some trouble when it comes to my decorator `get_cache_dict`  from the DictCacheManager class.

Specifically, it appears that this was not as loosely coupled as I thought. When I pass in 'self' from any class
(contracts, factions, etc.) to the `get_cache_dict`, that 'self' instance is not an instance of the DictCacheManager -
*it's an instance of the contracts, factions, etc. class.*
This is not what I want, because it means that these 2 classes are tightly coupled - I don't want `get_cache_dict` to have
to know *anything* about the class that's using it.

How to resolve this?
1. Let's try to pull these functions completely out of the DictCacheManager class. They're only there for showing they belong together. If I can make them work as independent functions (maybe in utilities folder) then maybe I can figure out how to re-insert them as a class.
2. There are Python modules (e.g.,  `functools.lru_cache`) that do in-memory caching. Could I maybe adapt these to work with file-based caching? [functools on Github](https://github.com/python/cpython/blob/8de607ab1c7605dce0efbb1a5c7148385d9176a6/Lib/functools.py#L567).

I like the idea of #2 - to see if I can learn about this caching module and do something similar. If that fails, then let's do #1.

---

**Notes on functools.py caching:**
The functools cache is based on a doubly-linked list, but I don't want to do that - I want persistent files.
The implementation at the link above is mostly fiddling with the cache list, but the calling of the function is just with `(*args,**kwargs)`.
Simple as it sounds, maybe I need to just use those ambiguous placeholders instead of the explicit values I'm using now...
**BUT** before I do that, let's try doing #1 above and keeping these functions out of a class because **functools.py also does not use a class for these functions.**

> Note: I tried to use `functools.cache` as a decorator on "get_system" and it seemed to work (at least it called the function correctly). So whatever logic it's using I should be able to replicate.
> **UPDATE:** `functools.cache` and other versions are working based of just pushing through arguments as `*args` and `**kwargs` - so *they are working just the same as my class functions - they still are passing the class instance, just in a less explicit way*
> This is not great. These versions are doing the same thing as my own code, but in a less explicit way. I think I should rather pass in these explicitly, if possible. Now that I know I can't avoid passing in the class instance, this is less bothersome for me (although I should type-hint it as a generic "Class" probably...)

**UPDATE:**
- I think one problem in what I'm doing is that the 'key' is needed by both the wrapper (doing cache retrieval) as well as the inner, passed function.
These are really doing different things and shouldn't have to be inter-dependent.
- Another issue I'm seeing is that it is very hard to split up the nested decorator + wrapper function definitions, because inner function definitions might rely on variables passed to outer functions. This makes it hard to keep some parts of the decorator structure in the classes without having to rely on explicit variable passing - which makes the caching functions less generic.

**SOLUTION:**
I've found a way to implement the cache functions as generic, while still allowing customization of the cache_path from class variables, AND allowing both the wrapper and the passed function to use the arguments for the passed function.
It only took 5 function definitions!
The following decorator was the key part - having enough nesting
in this allowed me to first catch the function, then use the class variables to create the file path, and finally use the function argument ('system') as both key for the caching function and have it passed directly to the function itself (if called).

I think this is as graceful as I'm going to get.

```
    def cachy2(func):
        def inner(self,system:str):
            path = self.cache_path + "/test.json"
            return cache_wrapper(path,system)(func)(self,system)
        return inner
```

**Next Steps:**
1. ~~Clean up this test code with better naming, type hints, key-word arguments.~~
2. ~~Switch over all classes + test~~
3. ~~Consider implementing as class again (I don't see the need at this point though)~~
4. ~~Continue my work to get rid of inheritance (favor composition)~~
5. Continue my work to build new interface layer.


---

### June 3, 2023

I've now finished a test suite based out of `unittest`. The 'test.sh' script in the main folder runs all tests.
My next steps are:
1. Change architecture so that classes use **instances** of each other, but do not directly inherit (composition over inheritance).
   1. Let's start by editing this for one minor class and work out the kinks.
      1. Change to 'factions' appears to be a success' Changes needed:
         1. Need to create class instances as variables:
            1. `stc = SpaceTraderConnection()`
            2. `dcm = DictCacheManager()`
         2. Remove initialization of parent classes in __init__ function
         3. Change initialization of class variables if they require values from `stc` or `dcm`
            1. Ex: `self.base_url = self.stc.base_url + "/factions"`
         4. `self.stc_http_request` calls need to be `self.stc.stc_http_request`
         5. `self.update_cache_dict` calls need to be `self.dcm.update_cache_dict`
         6. Change decorator to not refer directly to DictCacheManager:
            1. Ex: `return self.dcm.get_cache_dict(...)`
2. Build the next layer of my interface (see notes from May 31)

---

### May 31, 2023

**Next steps**
Right now I've finished all of the endpoints and they all seem to work. My next tasks are to build out some more testing
and then to do the harder (mentally) task of building the next layer of the interface:
1. Build out testing:
   1. ~~Have a test for each endpoint~~
   2. ~~Organise your tests so that they're a bit more modular~~
      1. ~~Maybe a single testing file for 'systems', 'ships', etc? - and then a 'master' test file to run all of them sequentially (or parallely!?)~~
2. Build the next layer of my interface


**NOTES on handling HTTP status errors:**
I was musing below on maybe having some kind of central way to handle http error codes. However, since error codes (even ones like `400` do not necessarily signify that the API has failed, but can sometimes mean that you're just trying to do something in-game that you can't do yet)- having a central status-handler doesn't make sense to me anymore.

My new strategy is to return response packets (with status and data) in their raw form - where they can be dealt with individually (or not at all).

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
   2. ~~get_cooldown fails if no cooldown is there - give canned response instead to avoid error.~~
   3. Scan_waypoints provides useful data about all waypoints in the system - data which is NOT recorded in the systems data.
      1. ~~Need to handle non-200 response code.~~
      2. ~~I probably need to immediately cache this in the 'systems' files I have - and then pull from that if needed - particularly since this command causes a cooldown~~
         2. This means that I need to figure out a way to update a **nested record** in the cache...
            1. **NOTE:** I have tried 5-6 hours to try to make a graceful way to update nested data within my existing json cache system and **I GIVE UP.** Instead for 'scan waypoints' I will keep this data cached for the time that my 'ship' is in that system, but not any longer (or perhaps I'll write that scan to another cache that I can lookup later - but separate from 'systems' data)
         3. I think this is another good reason to have another lower-level 'ship' class that has class variables where I can store this information
   4. ~~Scan_systems is giving me very basic information about systems - and only a subset of them. I guess I can use this to discover systems that might not already be in the systems list?~~
      1. ~~Need to handle non-200 response code.~~
      2. ~~Again, this would be good to update the systems information with - but I'm not sure exactly what to do with these systems. Is it worth traveling to these vs. the already-listed systems?~~
         1. this scan_systems data also includes **DISTANCE** from the current system - which suggests that like for scan_waypoints and scan_ships - I can keep these as ephemeral values cached within a class state (and maybe somehow cached if I want to pause the game), but not added to any kind of persistent record - they're too contextual.
   5. ~~Scan_ships is giving me information on what ships are in the system at this moment; I guess there might be some multiplayer interactions. Cannot be cached - volatile information.~~
      1. ~~Need to handle non-200 response code.~~
   6. chart_current_waypoint returns non-200 code if it has 'already been discovered'. Need to handle this.
**2. Finish systems endpoints**
   1. ~~List_waypoints~~
      1. NOTE: This currently only returns the same depth of waypoint data as get_system. I see no reason to list this separately from the systems data if there's no additional data here. **Ignoring until this becomes more relevant.**
   2. ~~Get_waypoint~~
   3. ~~get_market~~
   4. ~~get_shipyard~~
   5. ~~get_jumpgate~~
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
1. Look through documentation and see if I can indeed get this information elsewhere through other queries~~
    - ~~Yes, I can get agent details via the `my/agent` endpoint~~
    - ~~Yes, I can get contract details via `my/contracts` endpoint~~
    - ~~Yes, I can get ship details via `my/ships` endpoint~~
2. ~~If yes, prioritize saving only unique information (I can always query other info later)~~
    - ~~Only unique information is **API KEY** - and I can also save **callsign"** and **account ID** - I don't think these are sensitive details~~
3. ~~For unique key, look into encrypting my key with a password so I can store it on GH and unlock it anytime~~
4. ~~create script for decrypting and storing key locally~~
5. Create endpoints for all commands - use [api spec](https://spacetraders.stoplight.io/docs/spacetraders/11f2735b75b02-space-traders-api) to find these and prioritize.
    1. Let's start with code needed to complete a contract:
        - Contracts:
            1. List available contracts
            2. Accept contract
            3. List contract terms
        - Navigation:
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
