# Development Notes

Notes on tricky problems, decisions, etc.

*Note: I'm starting this late - after a couple weeks of development (May 22nd, 2023)*

---

## Notes

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