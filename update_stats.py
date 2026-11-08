"""Fetches live GitHub stats into stats.json, then rebuilds both SVGs.
Runs daily in GitHub Actions (.github/workflows/update.yml).
Token: uses ACCESS_TOKEN if set (counts private work too), else the default GITHUB_TOKEN."""
import json, os, time, subprocess, sys, urllib.request
from datetime import datetime, timezone

os.chdir(os.path.dirname(os.path.abspath(__file__)))
USER = json.load(open("profile.json"))["github_user"]
TOKEN = os.environ.get("ACCESS_TOKEN") or os.environ["GITHUB_TOKEN"]
HDR = {"Authorization": f"bearer {TOKEN}", "User-Agent": "profile-readme-stats"}


def gql(query, **variables):
    req = urllib.request.Request("https://api.github.com/graphql",
                                 json.dumps({"query": query, "variables": variables}).encode(), HDR)
    data = json.load(urllib.request.urlopen(req))
    if "errors" in data:
        raise RuntimeError(data["errors"])
    return data["data"]


def rest(path):
    req = urllib.request.Request("https://api.github.com" + path, headers=HDR)
    with urllib.request.urlopen(req) as r:
        return r.status, (json.load(r) if r.status == 200 else None)


# --- repos, stars, followers, contributed ---
q = """query($login:String!,$after:String){ user(login:$login){
  createdAt followers{totalCount}
  repositoriesContributedTo(contributionTypes:[COMMIT,PULL_REQUEST,REPOSITORY]){totalCount}
  repositories(ownerAffiliations:OWNER,first:100,after:$after){
    totalCount pageInfo{hasNextPage endCursor}
    nodes{nameWithOwner stargazerCount isFork}}}}"""
repos, after = [], None
while True:
    u = gql(q, login=USER, after=after)["user"]
    repos += u["repositories"]["nodes"]
    if not u["repositories"]["pageInfo"]["hasNextPage"]:
        break
    after = u["repositories"]["pageInfo"]["endCursor"]

stats = {
    "repos": u["repositories"]["totalCount"],
    "contributed": u["repositoriesContributedTo"]["totalCount"],
    "stars": sum(r["stargazerCount"] for r in repos),
    "followers": u["followers"]["totalCount"],
}

# --- all-time commits (contribution calendar is per-year) ---
cq = """query($login:String!,$from:DateTime!,$to:DateTime!){ user(login:$login){
  contributionsCollection(from:$from,to:$to){totalCommitContributions restrictedContributionsCount}}}"""
start = int(u["createdAt"][:4]); now = datetime.now(timezone.utc)
commits = 0
for year in range(start, now.year + 1):
    c = gql(cq, login=USER, **{"from": f"{year}-01-01T00:00:00Z", "to": f"{year}-12-31T23:59:59Z"})
    cc = c["user"]["contributionsCollection"]
    commits += cc["totalCommitContributions"] + cc["restrictedContributionsCount"]
stats["commits"] = commits

# --- lines of code you added/deleted in your own repos ---
add = dele = 0
for r in repos:
    if r["isFork"]:
        continue
    for _ in range(6):                      # GitHub computes this lazily: 202 = "try again soon"
        status, data = rest(f"/repos/{r['nameWithOwner']}/stats/contributors")
        if status == 200:
            break
        time.sleep(5)
    for person in data or []:
        if person.get("author") and person["author"]["login"].lower() == USER.lower():
            add += sum(w["a"] for w in person["weeks"])
            dele += sum(w["d"] for w in person["weeks"])
stats["loc_add"], stats["loc_del"] = add, dele

json.dump(stats, open("stats.json", "w"), indent=2)
print(stats)
for theme in ("dark", "light"):
    subprocess.run([sys.executable, "generate.py", theme], check=True)
