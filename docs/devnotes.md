# Development Notes

Notes on tricky problems, decisions, etc.

*Note: I'm starting this late - after a couple weeks of development (May 22nd, 2023)*

---

## Notes

---

### Jul 19, 2023
TODO:
1. ~~Commit changes~~
2. ~~Remove 'list' commands - instead, use the 'preview' feature of 'menu' to show description of each command (negates need for 'list' and is easier to use).~~
3. Finish contract to-do from July 18 below.
4. Look at July 3rd notes for additional priorities.

> **Important reflection on my commits:**
> I have a tendency to start coding and refactoring - and then *continue* doing that until I'm done with all the issues I've found.
> This results, however, in a set of HUGE and varying changes across my codebase, which I then struggle to chunk into reasonable commits (see commit `323f4e580f508847adb7bd1deb73f216e3f8834e` for an example). Inevitably, I end up commiting a lot of different changes at once - and make these gargantuan, complex commits which will be more-or-less impossible to roll back to.
> This is not tenable long-term. I need to find a way to make my commits smaller and only address a single topic.
> There are 2 strategies I could use to do this:
> 1. **Only work on 1 change at a time**
>     a. I can do this by using my notes more. Instead of thinking 'oh, I'll just change that too...', I can make notes of what needs changing and implement those changes sequentially in different commits
>     b. I can use `git stash` to stash current big changes and then quickly patch a problem I find. This will allow me to still fix and commit small issues that I find without including these minor changes as part of a sweeping feature update or something similar.
> 2. **Use Git's 'patch' or 'interactive add' features to choose chunks from each file to commit**
>     a. [Read more here](https://stackoverflow.com/questions/1085162/commit-only-part-of-a-files-changes-in-git).
>     b. This is a way to actually CHOOSE parts of my files which belong to certain commits and not commit the entire file (which might contain pieces that should really be different commits)
>
> **CONCLUSION:**
> I think I need both of these strategies. #2 is cool, but could also become complicated. Let's try to do this, and in my next commit (even if it's minor), let's try to use the git interactive add commands to test out how it works.

---

### Jul 18, 2023
**To Decide:**
The way that I'm dealing with contracts data during gameplay is a bit inconsistent.
The ShipOperator class stores a "current contract" that the player is (presumably) pursuing during gameplay. However, I'm not accessing this in the CLI. Instead, I'm printing out ALL contracts. There are 2 options for how to proceed:
1. Forget 'current contract' - remove this attribute from ShipOperator and just use contracts class to access contracts.
   1. This option does not really work because I need to do certain commands related to a certain contract (see list below). These commands require a contract ID - so it needs to be stored somehow
      1. accept contract
      2. deliver contract
      3. fulfill contract
2. Use 'current contract' when in the ship menu to more easily access information about one contract
   1. Probably requires way to 'switch' current contract

I'm leaning toward #2, but it will take more work to implement.

---

Update: I need to have a more centralized way to manage contracts. Specifically, I need to do the following:
1. Contract meta actions:
   1. list all contracts
   2. check contract status
   3. Switch active contract
2. Contract game actions:
   1. negotiate new contract
   2. accept contract
   3. deliver for contract
   4. fulfill contract

I think these actions speak to a 'contract' submenu. The two weird commands are `deliver for contract` and `negotiate new contract` because these are related to a specific ship being at a specific location and so need to be done when a player is already commanding a ship.
> Decision: Make this 'contracts' submenu similar to info_menu and allow it to be accessed at least from the 'command menu' (possibly also from 'mine menu')

---

Additionally, I can see 2 ways forward with showing ship information to the player:
1. At each menu ('navigate', 'mine', etc.), we provide an 'info' command which prints out *only information related to that action* (i.e., related to navigating, mining, etc.)
   1. This is how we're currently doing it
2. ~~We create a new centralized menu accessible from ALL other menus which allows players to choose what information they want. For example, on any ship-related menu, when players enter 'info', they are taken to a screen with these options:~~
   1. "Ship cargo & crew"
   2. "Ship mounts"
   3. "Ship modules"
   4. "Ship Subsystems"
   5. "Contracts" (optional)

I need to decide which option I want.
*NOTE: I like #2 because it doesn't require much thinking or tweaking about what info the player wants... I'm also not convinced that there is an easy answer about what info is relevant at each menu*

---

### Jul 17, 2023
**To finish:**
- ~~I need to test the newly-named 'general info' template (this was previously poorly named 'ship info template' even though it's not that). I also want to add mountingSlots and moduleSlots to headers in 'MOUNTS' and 'MODULES' HUDs respectively.~~
~~- COMMIT CHANGES!!~~

---

### Jul 15, 2023
Next steps:
1. ~~Finish HUD for different menus.~~
See notes from Jul 3rd for additional priorities.

---

### Jul 13, 2023
TODO:
1. ~~Commit changes to cli module~~
2. ~~Remove contract caching as discussed in Jul 9th notes and commit~~

---

### Jul 9, 2023:
**Minor issue with 'contract' information:**
Contracts expire, and after they expire they're arguably not worth keeping around as persistent data.
Does it make sense to still store contract information persistently? Or rather, should I just query it from the API so that it doesn't imply that a very expired contract is still somehow relevant.
The alternative would be to clean up my own contract data (i.e., detect that contracts are expired and remove them from persistent storage).

**Decision:**
Contract data is too volatile to cache - remove caching for contracts.
Considerations:
1. Contract data is player-specific; it has no use except when a given player is playing
2. Contracts expire - so cached data becomes invalid after a relatively short amount of time. This is in contrast to other cached data such as `systems` or `factions` which do not become invalid except in the case of game updates or a game reset - which are unpredictable.
3. Contract data is relatively small (currently players only have 1 contract at a time), so the cost of re-downloading this data is very small
4. Data for a given contract is cached in the 'ship_operator' during runtime, preventing some re-querying.

---

### Jul 4, 2023

I have been looking around a bit at **pygame** - it's a nifty open-source library for buildin games in Python.
I'm not yet sure whether I want to use it (and archive my homemade CLI design) or continue as I am...

I think in the end it would be smart of me to see how pygame works - I'll look at some examples of projects.

> Update: I've seen some pretty cool stuff - 3D worlds, a lot of 2D platformers. However, I haven't seen anything yet which would really pertain
> to the CLI style that I want to keep - except maybe some videos about how to create buttons (could switch from CLI menu to clickable buttons...).
> I'm enjoying making the CLI myself enough that I'm happy to keep doing that and ignore pygame for now - particularly since it doesn't seem super relevant to making CLI games.

---

### Jul 3, 2023
Took a bit of a break to spend my evenings playing Dyson Sphere Program (fantastic game - for anyone reading this - it's very much like coding...).

Back to this project: the current priority is to finish the 'mine_menu', including:
1. ~~Creating 'refine' function (should be very easy).~~
2. ~~Deciding on solution for conundrum in 'extract' function where some game happenings are hidden from the player, which makes some things confusing. Specifically, the 'extract' function allows the player to choose an item to try to refine, but the extracted item will often be different from that item (but the extracted item is often part of a SURVEY). See more notes next to the function in mine_menu.~~
   1. ~~I decided in the end to give the player control over which survey to use (from a list of surveys relevant for the current waypoint + not yet expired)~~
3.~~ Deciding whether I want to keep cooldown-checking as part of ship_operator class~~
   1. ~~It's convenient to be notified that I can't do X action because cooldown is still in effect, but I want to be able to control this message myself...~~
      1. ~~What if I just pulled the logic to check cooldown out of the wrapper function in ship_operator class? Then I could use that function separately, but if I failed, the wrapper would still catch the cooldown violation and spit out the generic warning!~~
         1. ~~Good idea - and i'm not sure I even need a generic function; code is like 2 lines:~~
         ```
         seconds = time_diff_seconds(self.cooldownExpiry)
         if seconds > 0:
            print(f"Cooldown remaining: {seconds}s")
         ```

After that is complete, here are my priorities:
1. ~~Design HUD interface. I would like one template which I can more-or-less adjust for navigation, trading, contracts, etc... That way, I get a reliable HUD no matter what menu I'm on, it looks very similar, but I can:~~
   1. ~~easily see that I'm on the HUD for 'mining' or 'navigation' or 'trading~~
   2. ~~see all of the relevant information to make decisions (e.g., for mining, I see current cargo and maybe current contract details...)~~
2. ~~Implement HUD~~
   1. ~~Basic HUD~~
   2. ~~Specific add-ons for 'cargo', 'modules', 'contracts', etc. (see str_formatting.py for concept art):~~
      1. ~~General info HUD~~
      2. ~~Contracts HUD~~
      3. ~~Ship info HUD~~
      4. ~~Ship reactor HUD~~
      5. ~~Crew HUD~~
      6. ~~Cargo HUD~~
      7. ~~Ship mounts HUD~~
      8. ~~Ship modules HUD~~
3. Finish navigation endpoints:
   1. jump ship
   2. warp ship
   3. set_speed
4. Tackle the next menu (Trading?)
5. Update Architecture.md notes ('Agents' class no longer exists; some misspellings)


**UNRELATED:**
I would like to share my project and code with the community more! Here are my steps to do that:
1. Finish more of the cli so it's vaguely playable (doesn't have to be 100%, but maybe fix any outstanding bugs and make it smooooother)
2. Finish Readme + setup instructions so that others could conceivably clone and play the game
   1. Test this on Linux
   2. Test this on Windows
3. Post to Spacetraders Discord and get some feedback from them
4. Post to LinkedIn
5. Post elsewhere??

---

### June 25, 2023
Notes:
I spent a lot of time today trying to fix an issue with python imports that *magically disappeared*. I was having issues importing from`src` from the `cli` code, but now it's fixed. I have no idea why.

TODO:
1. ~~Make commits of new changes. Biggest change should be from 'pyinquirer' to 'terminalmenu'~~
2. ~~Figure out a way to use the 'preview' feature of the terminal menu to include meta information about waypoints~~
3. Continue to build out menus for ship command
4. (Bonus): I'm not 100% satisfied with the flow of the game. I think some things are missing:
   1. ~~"Exit" should exit the entire game, even from a nested menu~~
   2. The 'spacetrader logo' should appear at the top whenever accessing sub menus (it looks like the game has failed otherwise after the terminal screen clears)
      1. **ALTERNATIVELY - MAKE A HUD INSTEAD** (I kind of like this instead... more useful.)
         1. HUD could have a standard header, but custom info depending on menu (e.g., navigate menu could show location and surrounding systems...)

---

### June 22, 2023

**Notes on CLI building**
I want to start organising how I build out my CLI command structure. Here's a semi-organised list of things I want:

1. Game flow:
   1. ~~Player chooses which agent they want (or creates a new agent)~~
   2. Main menu:
      1. list contracts (END)
      2. Explore systems
         1. Show ASCII map (new feature - show map (with key), including locations of current ships and already-visited locations; maybe this should generate a file so that we aren't limited by 70-char line width?)
         2. (Other?)
      3. Command ship
         1. Pick ship from list
            1. Navigate (exclude 'orbit' and 'dock' since these are only prerequisites for other actions)
               1. nav
                  1. (list waypoints in system)
               2. jump
                  1. (list systems in range)
               3. warp
                  1. (list waypoints in range - can I provide a menu for this??)
               4. set_speed
            2. Trade
               1. find_best_margins
               2. find_margin
               3. get_market
               4. purchase
               5. sell
            3. Explore
               1. chart_current_waypoint
               2. scan_for_ships
               3. scan_systems
               4. scan_waypoints
            4. Mine
               1. survey_waypoint
               2. extract
               3. refine
            5. Manage Contracts
               1. request new contract (location-specific...)
               2. list contracts
                  1. Accept / select contract
               3. **check contract (should be in HUD instead?)**
               4. deliver contract shipment (location-specific...)
               5. **fulfill contract (should instead be auto-checked I think upon delivery of shipment)**
            6. Manage Ship
               1. Switch ship (goes back to main menu 'list ships')
               2. **get ship info (should be in HUD instead?)**
                  1. get_mount
                  2. .cargo
                  3. .fuel
                  4. .credits
               3. Mounts
                  1. install
                  2. remove
               4. Cargo
                  1. jettison
                  2. transfer
               5. **refuel (should this really be a command? Or should I just refuel automatically when I go anywhere with fuel?)**
            7. back to main menu
      4. Quit game (END)


---

### June 21, 2023
I'm considering removing caching for the 'agents' class - I don't really see the value of caching this data.
Additionally, the get_agent endpoint doesn't take any callsign to retrieve information about the given agent. Rather, it INFERS the agent from the API key - so it's not actually adaptable for different callsigns. This kind of breaks the logic of my endpoint classes generally. The agent endpoint is really more of a game metadata endpoint than an in-game information-gathering endpoint in that way.

TODO: Decide what to do here.

**Decision:** It doesn't make sense for me to keep an entire 'Agent' class or the caching. I will instead make this part of the SpaceTraderConnection class as a way to get metadata about the agent.

---

### June 20, 2023

**Next Steps:**
I have worked on Bengisu's suggestions below, including:
1. Building documentation about architecture
2. Replacing urllib with requests

I now want to work on the following:
1. Read about Pydantic and how I could use it.
   1. I have read about Pydantic and I don't yet understand why it's needed. It's for checking types, but I don't yet understand where and how that adds value outside of type hints + enumerated types that I already have. I will keep this in mind though and approach it once I understand it a bit more.
2. ~~Fix Liskov problem I wrote aboute below for ShipOperator~~
3. Continue implementing CLI
   1. ~~**See my notes from June 16th**~~
   2. Build out CLI functions more
4. ~~(TBD) Change how I'm handling credentials in terms of security?~~
   1. I don't see this as a big deal, particularly since this is just a game. If I want, I can always adapt my code later to save the yaml in a secret location.
5. (Stretch) Containerize game (suggestion from Bengisu, but i'm not sure it makes sense)

**Note about Liskov Substitution Principle:**

I am currently violating this (one of the SOLID principles of OOP) with my 'ShipOperator' class because this subclass is using the same name for some of its methods as the parent class (Ships), overriding these methods, but the subclass methods take in different arguments and return different values.
I think I have a few options:
1. Change the name of these subclass methods
   1. They're not intended to achieve the same goal, so there's no reason to name them the same except that they're good names.
2. Change the subclasses to behave similarly to the parent class
   1. Not a good idea - they're qualitatively different and need to work differently
3. Combine the 'ships' and 'ship operator' classes into one class
   1. Not the worst idea - they don't necessarily have to be different, but the 'Ships' class is basically an API wrapper, whereas 'ShipOperator' is about representing the ship...
4. Change the name of the parent class methods
   1. I kind of like this - I could even make them private - but then again maybe this would be too inconsistent with the other Classes.

> DECISION: I like Option #1 and Option #4 the best - it's not great to use different names, but I think that's the best representation of what's going on in  my classes. I will rename my methods in one class or the other so they don't collide.

---

### Feedback from Bengisu
Bengisu wrote me back on June 17th with some notes about how I could improve my project:
- One thing that is needed, in my opinion, is documentation. Your code and development process is very well documented, but I think I was missing general documentation on your application as whole, especially the architecture. You use a lot of classes and dependent internal modules, so an overarching documentation that explains the architecture, how to interact with your client and some diagrams would be very helpful.
- When I have to use many interconnected classes that require data validation and modeling, I usually use [Pydantic](https://docs.pydantic.dev/latest/). If you haven’t heard of it, it’s definitely worth a look. Their [model object](https://docs.pydantic.dev/latest/usage/models/) definition, type declaration and validation is quite practical and extendable (And has a built-in [model export](https://docs.pydantic.dev/latest/usage/exporting_models/) feature).
- Tests: As far as I can see, you are focusing on the unit tests, testing individual components/functions. I would heavily recommend doing integration tests as well, and testing the dependencies and flows between the components.
- A random question: Is there a specific reason why you are using urllib for HTTP requests, instead of the “requests” library? I was just curious since the “requests” module is regarded as more developer friendly .
- account_info.cfg —> As you know it’s considered a bad practice to store credentials in open readable files, even if they are encrypted (And especially when you have the encryption script also available in Github, but I know you’re already aware of that). You can maybe utilize environment variables to store and use account credentials for your implementation?
- General comment: it’s really a great project that showcases a lot of different skills and a solid software design approach. Maybe you can put focus on the deployment aspect in the future. Like containerizing it? Release as docker image/package, and it can be run from command line? I would suggest using GitHub Actions and Github container registry for building and publishing images. It’s now one of the most popular CI/CD tools in the industry.

---

### June 16, 2023

**Necessary changes to enable CLI:**
1. ~~I need to store API keys differently. Only having one config file with one possible agent (and API key) disallows multiple players.~~
   1. ~~Suggestion: What about a 'encrypted_keys.json' file with callsign as key and encrypted API token as value? Then, each player could be asked to pick their callsign and then provide a decrypting password. I like this. Steps include:~~
         1. ~~Adapt RegisterNewAgent to create or update this json (use cache functions)~~
         2. ~~Adapt base.py to read from this json~~
   2. Note: If I'm getting rid of account credentials, maybe it's time to get rid of the config file entirely and just put cache_path and API url in base.py
2. ~~I want to provide the option to set up a new player as well. The CLI should allow 'Register new agent' as an option alongside existing callsigns...~~

---

### June 15, 2023

**Notes on de-coupling Interface from Source code**

I have made some (minor) decisions so far which are tightly coupling my interface from the source code:
- ~~"ship_operator" class prints directly to interface~~
- ~~art directory is part of 'src' source code directory rather than in an interface~~
- **'response_ok' function in `base.py`**
  - This is a slightly bigger problem - I need to think about how I want to handle this differently...

> I want to change these decisions so that my interface is the only thing printing anything other than error output, and that my ASCII art is part of the CLI module only.

**Notes on CLI setup**

I am starting to make a CLI using a bit of a clunky mix of `Typer` and `PyInquirer` - but it's working!
PyInquirer especially lets me create these nice menus that can be interacted with via arrow keys.
Typer seems to be geared towards using single commands rather than having a command loop with sequential commands.
I'm not sure if this is actually a problem, but it might be worth exploring simpler alternatives like `argparse` if I continue to find I'm not really using the features of `Typer`.

Other ideas:
- I want to have 2 ways to interact with the CLI:
  - Through the menus provided by `PyInquirer` (or a similar tool)
  - Through direct commands (for experts)
- The menu interface can be nested- for example: `navigation` leads to a choice of `nav to waypoint`, `jump to system` `warp to...`. A choice of `nav to waypoint` gives a list of waypoints in the current system and a short description!
- I want to provide some help text in the interface for learning how to play the game, although I know I can and should also rely on Spacetrader documentation since this might change.
- I want to provide a better interface for starting a new game, which might include the following characteristics:
  - Absolutely no cache data (do I actually need to reload all systems from cache in the beginning?)
  - No account info
  - No API key yet
- I want to not have to load API key until I do something like "> start game". Not on bootup of CLI.
- (Minor) maybe include more ASCII-like line breaks in the terminal to make it less a wall of text?
- Can / should I have a HUD that is always up / can be called up with a command?
- (Expansion): Allow user to switch ships (and print out which ship we're currently commanding with HUD?)

---

### June 13, 2023

I have finished the market analysis updates I had noted below under June 11th. I think it'll be quite nice to be able to more easily find and use best pricing information.
Some things I need to do to clean this up:
1. ~~Make wrapper functions in `ship_operator` class so I can access these from one interface.~~
2. ~~Make custom data types for `margin_obj`, `price_obj` and `price_record`~~
   1. ~~Update typing in my new functions in Markets.py so that the data structures are clearer to readers.~~
3. ~~Clean up / refactor things as I see the need.~~
4. ~~Commit my changes.~~

Once that is done, I want to start on the notes I had under June 12th below (maybe start with some fun ASCII art and then move on to CLI creation?)

---

### June 12, 2023

#### CLI thoughts:
When I make the *actual CLI* (usable via terminal, not via Python interpreter), there are some quality-of-life changes I'd like to make:
1. 'system' command prints out current system and waypoints in a nicer format (ASCII table) and labels waypoints by number. Then, I can make a command like 'nav wp 2' to navigate to the waypoint marked by then number '2'. --> No more needing to copy-paste waypoint IDs.

#### ~~CANCELLED: Persisting ship state~~
I thought it might be a good idea to persist ship state (attributes) on disk - in case there would be any data lost after restart that would be annoying/difficult to re-acquire. However, I'm not so sure of that anymore. Here are the things which might be volatile and why they aren't really worth persisting between game sessions:
- `scan_systems` - only relevant for a particular system, no need to cache. Can be re-queried with only 70-second penalty.
- `scan_waypoints` - persisted to cache immediately. Can be recalled from cache with no issues.
- `survey_waypoint` - useful, but expires after ~30 minutes. Unlikely to be useful between game sessions.
- `get_market` - persisted to cache immediately. Can be recalled from cache with no issues.

> In conclusion, I don't see a compelling reason to worry about data persistence - let's aim to rely on the API servers to maintain state.


#### Better system scanning + jumping
I have been frustrated that jumping to other systems is basically a guessing game - to know which systems actually have jump gates and what (if any) information is known about them. I want to improve this data (either in UI or in deeper data structures, not sure yet):
1. systems should show if I have visited them before (requires a binary flag on system data)
2. systems should have symbols shown next to their names to indicate:
   1. how many waypoints they have
   2. how many markets
   3. how many asteroid fields
   4. other? (once I upgrade ship systems, can I interact with other waypoints to harvest more things?)
3. systems should show clearly if they have a jump gate or not
4. Other?
---

**Extra:**
1. ~~Make ship-nav ASCII art a bit bigger- maybe also put text to left-and-right of image to save vertical space.~~
2. Let's aim for a max width of **70 chars** on all CLI UI elements. See example line:
<><><><><><><><><><><><><><><><><><><><><><><><><><><><><>+++++70++++////80////

---

### June 11, 2023
I've made good progress on my to-dos from June 10th - one thing still left is **profit-finding**
--> I think I should make this a function the markets class, since I need to access those data via cache so much.
Let's work on a prototype!

NOTE: I'm thinking of a new 'market analysis' data structure which shows me - for every commodity - where I can find the lowest 'purchasePrice' and the highest 'sellPrice (and also the margin between the two).
This would be a relatively easy thing to keep updated- as I found new markets, I could update the prices if they were better in the new market. Then, whenever I find materials or want to make money, I can consult this market analysis structure.

My previous idea of analysing two markets only makes sense if I have a reason to prefer either of those markets, which might be the case if I am AT one of those markets already...

Other possible analyses:
1. Find best SELL price in current system (maybe nice for when you get a windfall item that you want to resell)
2. ~~Find best PURCHASE price~~


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
