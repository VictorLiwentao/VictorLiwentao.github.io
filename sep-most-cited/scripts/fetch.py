import asyncio, os, sys, time
import aiohttp

SLUGS = [s.strip() for s in open(sys.argv[1]) if s.strip()]
OUT = sys.argv[2]
os.makedirs(OUT, exist_ok=True)
UA = "Mozilla/5.0 (compatible; SEP-citation-count research script; polite crawl)"
CONC = 6

async def get(session, slug, sem, stats):
    path = os.path.join(OUT, slug + ".html")
    if os.path.exists(path) and os.path.getsize(path) > 2000:
        stats["skip"] += 1
        return
    url = f"https://plato.stanford.edu/entries/{slug}/"
    async with sem:
        for attempt in range(4):
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=60)) as r:
                    if r.status == 200:
                        b = await r.read()
                        open(path, "wb").write(b)
                        stats["ok"] += 1
                        break
                    else:
                        stats.setdefault("status_" + str(r.status), 0)
                        stats["status_" + str(r.status)] += 1
                        if r.status == 404:
                            break
            except Exception as e:
                stats["err"] += 1
            await asyncio.sleep(2 * (attempt + 1))
        await asyncio.sleep(0.15)

async def main():
    stats = {"ok": 0, "skip": 0, "err": 0}
    sem = asyncio.Semaphore(CONC)
    async with aiohttp.ClientSession(headers={"User-Agent": UA}, trust_env=True) as s:
        tasks = [get(s, slug, sem, stats) for slug in SLUGS]
        t0 = time.time()
        for i in range(0, len(tasks), 100):
            await asyncio.gather(*tasks[i:i+100])
            print(i + 100, stats, round(time.time() - t0), flush=True)
    print("done", stats)

asyncio.run(main())
