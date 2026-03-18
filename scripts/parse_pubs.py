#!/usr/bin/env python3
"""
parse_pubs.py — BibTeX parser for gnarayan.github.io
Reads cvrefs.bib, tags papers by project, counts co-authorships,
and writes two JSON blobs used by research-landscape.html and collab-network.html.

Usage (from repo root):
    python3 scripts/parse_pubs.py

Outputs:
    files/pub_data.json  — project_weights + coauth_graph
"""

import re, json, os, sys
from collections import defaultdict

BIB = os.path.expanduser(
    "~/Dropbox/Docs/UIUC/Docs/cv/full/cvrefs.bib"
)
OUT = os.path.join(os.path.dirname(__file__), "..", "files", "pub_data.json")

# ── CST members (last-name fragments, lower-case) ──────────────────────────
CST_CURRENT = {
    "hinkle", "o'brien", "obrien", "mitra", "abunemeh",
    "wasserman", "murphey", "engholm", "perkins", "venkatraman", "agrawal",
}
NARAYAN = "narayan"

# ── Institution clusters for external collaborators ────────────────────────
# Map last-name fragments → cluster label
INSTITUTION_MAP = {
    # Cambridge / BayeSN group
    "mandel": "Cambridge/BayeSN", "thorp": "Cambridge/BayeSN",
    "grayling": "Cambridge/BayeSN", "boyd": "Cambridge/BayeSN",
    # UCSC / YSE core (Coulter, Siebert, Kilpatrick have since moved)
    "foley": "UCSC/YSE", "rojas-bravo": "UCSC/YSE", "dimitriadis": "UCSC/YSE",
    "de boer": "UCSC/YSE", "hoogendam": "UCSC/YSE",
    # STScI / NOIRLab (includes Coulter and Siebert who moved from UCSC)
    "rest": "STScI/NOIRLab", "matheson": "STScI/NOIRLab", "saha": "STScI/NOIRLab",
    "olszewski": "STScI/NOIRLab", "coulter": "STScI/NOIRLab", "siebert": "STScI/NOIRLab",
    # Chicago / Fermilab DESC
    "kessler": "UChicago/Fermilab", "drlica-wagner": "UChicago/Fermilab",
    "frieman": "UChicago/Fermilab", "chang": "UChicago/Fermilab",
    # Northwestern SkAI / CIERA
    "samia": "Northwestern/SkAI", "kilpatrick": "Northwestern/SkAI",
    # UIUC NCSA (local, non-CST)
    "krafczyk": "UIUC",
    # Harvard / MIT IAIFI
    "villar": "Harvard/IAIFI", "gagliano": "Harvard/IAIFI",
    # Hawaii / Pan-STARRS
    "chambers": "Hawaii/PS1", "huber": "Hawaii/PS1",
    "magnier": "Hawaii/PS1", "wainscoat": "Hawaii/PS1",
    # Copenhagen
    "hjorth": "Copenhagen", "gall": "Copenhagen", "izzo": "Copenhagen",
    # Berkeley / LBNL
    "nugent": "LBNL", "kim": "LBNL",
    # Texas A&M
    "kenworthy": "TAMU",
    # Illinois (non-CST)
    "fields": "UIUC", "vieira": "UIUC", "raghunathan": "UIUC",
    # Oxford
    "lochner": "Oxford/SAAO", "moller": "Oxford/SAAO",
}

# ── Simple BibTeX regex parser ──────────────────────────────────────────────

def parse_bib(path):
    with open(path, encoding="utf-8") as f:
        raw = f.read()

    # Split into individual entries
    entries = re.split(r'\n@', raw)
    papers = []
    for entry in entries:
        if not entry.strip():
            continue
        # Extract key
        m = re.match(r'[A-Z]+\{([^,]+),', entry)
        if not m:
            continue
        key = m.group(1).strip()

        def field(name):
            """Extract a BibTeX field value (handles multi-line and "{...}" wrapping)."""
            # Match:  field = {value},  OR  field = "{value}",  OR  field = "value",
            pat = re.compile(
                r'^\s*' + name + r'\s*=\s*"?\{?(.*?)\}?"?[,\s]*$',
                re.MULTILINE | re.DOTALL | re.IGNORECASE
            )
            fm = pat.search(entry)
            if not fm:
                return ""
            # Also handle the common ADS format: field = "{text}",
            # which gives captured group as: "{text}" or "text" depending on outer quotes
            val = fm.group(1)
            # Strip leading/trailing " and { }
            val = val.strip().strip('"').strip('{}').strip('"')
            return re.sub(r'\s+', ' ', val).strip()

        title    = field("title")
        year_s   = field("year")
        keywords = field("keywords")
        pclass   = field("primaryClass")
        author_s = field("author")

        # Parse year
        try:
            year = int(year_s.strip())
        except ValueError:
            year = 0

        # Parse authors → list of "Last, First" strings
        # Each token looks like: {Boyd}, Benjamin M.  or  {LSST Dark Energy Science Collaboration}
        authors = []
        if author_s:
            for a in author_s.split(" and "):
                a = a.strip()
                # Remove braces around last name: {Boyd}, Benjamin → Boyd, Benjamin
                a = re.sub(r'^\{([^}]+)\}', r'\1', a)
                # Strip any remaining stray braces
                a = a.replace('{', '').replace('}', '')
                # Normalise whitespace
                a = re.sub(r'\s+', ' ', a).strip()
                if a:
                    authors.append(a)

        papers.append({
            "key": key, "title": title, "year": year,
            "authors": authors, "keywords": keywords, "primaryClass": pclass,
        })

    return papers

# ── Project tagging ─────────────────────────────────────────────────────────

def tag_projects(paper):
    t = paper["title"].lower()
    k = paper["keywords"].lower()
    a = " ".join(paper["authors"]).lower()

    tags = set()

    # YSE — collaboration author OR title/keywords
    if any(x in a for x in ["young supernova experiment"]):
        tags.add("yse")
    if any(x in t for x in ["yse", "young supernova", "young-supernova", "decam young"]):
        tags.add("yse")
    if any(x in t for x in ["pan-starrs", "panstarrs", "ps1"]):
        tags.add("yse")

    # DESC — collaboration author OR keywords OR specific tool titles
    if "lsst dark energy" in a or "dark energy science collaboration" in a:
        tags.add("desc")
    if any(x in k for x in ["dark energy science", "dark energy"]):
        tags.add("desc")
    if any(x in t for x in ["oracle", "sassafras", "resspect"]):
        tags.add("desc")
    if "cosmology" in k and any(x in t + k for x in ["supernova", "sn ia", "type ia"]):
        tags.add("desc")

    # SkAI — SELDON/ANTARES/foundation model OR ML keywords
    if any(x in t for x in ["seldon", "antares", "foundation model"]):
        tags.add("skai")
    if any(x in k for x in ["artificial intelligence", "machine learning"]):
        tags.add("skai")

    # SCiMMA — multi-messenger infrastructure papers
    if any(x in t + k for x in [
        "multi-messenger", "multimessenger", "kilonova", "hopskotch",
        "hermes", "heroic", "gravitational wave", "neutron star merger",
        "scimma",
    ]):
        tags.add("scimma")
    if "gravitational waves" in k or "gravitational wave sources" in k:
        tags.add("scimma")

    # Rubin/LSST — title contains Rubin or LSST
    if any(x in t for x in ["rubin", "lsst", "lsstcam", "vera c. rubin"]):
        tags.add("rubin")
    # Also tag if it's a DESC or LSST collaboration paper (they're Rubin science)
    if "lsst dark energy" in a or "lsst dark energy" in k:
        tags.add("rubin")

    return list(tags) if tags else ["other"]

# ── Helpers ──────────────────────────────────────────────────────────────────

def last_name(author_str):
    """Extract normalised last name from 'Last, First' or 'Last'."""
    parts = author_str.split(",")
    return parts[0].strip().lower()

def is_cst(last):
    for frag in CST_CURRENT:
        if frag in last:
            return True
    return False

def cluster(last):
    for frag, clust in INSTITUTION_MAP.items():
        if frag in last:
            return clust
    return None  # unknown

# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    papers = parse_bib(BIB)
    print(f"Parsed {len(papers)} papers", file=sys.stderr)

    # Tag papers
    for p in papers:
        p["tags"] = tag_projects(p)

    # ── Project-pair edge weights ─────────────────────────────────────────
    project_pairs = defaultdict(int)
    all_projects = ["yse", "rubin", "desc", "skai", "scimma"]
    for p in papers:
        tags = [t for t in p["tags"] if t in all_projects]
        for i in range(len(tags)):
            for j in range(i + 1, len(tags)):
                a, b = sorted([tags[i], tags[j]])
                project_pairs[f"{a}-{b}"] += 1
    # Also count per-project total
    project_counts = defaultdict(int)
    for p in papers:
        for t in p["tags"]:
            if t in all_projects:
                project_counts[t] += 1

    # ── Co-authorship counting ────────────────────────────────────────────
    # narayan <-> anyone, and cst <-> external
    narayan_coauth = defaultdict(int)   # last_name -> count
    cst_coauth = defaultdict(lambda: defaultdict(int))  # cst_name -> last -> count

    for p in papers:
        lasts = [last_name(a) for a in p["authors"]]
        if NARAYAN not in lasts:
            continue  # only papers Narayan is on
        others = [l for l in lasts if l != NARAYAN]
        for o in others:
            narayan_coauth[o] += 1
            # Check if this other author is CST
            for cst in CST_CURRENT:
                if cst in o:
                    break  # it's a CST member, handled separately
            else:
                # External author
                for cst in CST_CURRENT:
                    if any(cst in l for l in lasts):
                        cst_coauth[cst][o] += 1

    # CST-specific paper counts (papers Narayan co-authored with each CST member)
    cst_paper_counts = defaultdict(int)
    for p in papers:
        lasts = [last_name(a) for a in p["authors"]]
        if NARAYAN not in lasts:
            continue
        for cst in CST_CURRENT:
            if any(cst in l for l in lasts):
                cst_paper_counts[cst] += 1

    # ── Build external collaborator nodes ─────────────────────────────────
    # Map raw last-names to clusters; sum counts within clusters
    cluster_counts = defaultdict(int)
    cluster_members = defaultdict(set)
    unclustered = {}  # last -> count (for reporting)

    for last, cnt in narayan_coauth.items():
        if is_cst(last) or last == NARAYAN:
            continue
        cl = cluster(last)
        if cl:
            cluster_counts[cl] += cnt
            cluster_members[cl].add(last)
        else:
            unclustered[last] = cnt

    # Top-30 unclustered individuals → own node; rest collapsed
    unc_sorted = sorted(unclustered.items(), key=lambda x: -x[1])
    top_unc = unc_sorted[:20]
    rest_unc = unc_sorted[20:]

    # ── Build D3 graph ────────────────────────────────────────────────────
    nodes = []
    links = []
    node_id = {}

    def add_node(nid, **kwargs):
        node_id[nid] = len(nodes)
        nodes.append({"id": nid, **kwargs})

    # Center: Narayan
    add_node("Narayan", type="center", label="Narayan",
             img="../img/Narayan.jpg", papers=len(papers))

    # CST members
    CST_DISPLAY = {
        "hinkle":       ("Jason Hinkle",    "../img/group/jason.jpg",   "#F59E0B"),
        "o'brien":      ("Jack O'Brien",    "../img/group/jack.jpg",    "#F59E0B"),
        "mitra":        ("Ayan Mitra",      "../img/group/ayan.jpg",    "#3B82F6"),
        "abunemeh":     ("Henna Abunemeh",  "../img/group/henna.jpg",   "#F59E0B"),
        "wasserman":    ("Amanda Wasserman","../img/group/amanda.jpg",  "#8B5CF6"),
        "murphey":      ("Tanner Murphey",  "../img/group/tanner.jpg",  "#22C55E"),
        "engholm":      ("Athena Engholm",  "../img/group/athena.jpg",  "#22C55E"),
        "perkins":      ("Haille Perkins",  "../img/group/haille.jpg",  "#22C55E"),
        "venkatraman":  ("Padma Venkatraman","../img/group/padma.jpg", "#3B82F6"),
        "agrawal":      ("Aadya Agrawal",   "../img/group/aadya.jpg",   "#3B82F6"),
    }
    for cst, (label, img, color) in CST_DISPLAY.items():
        cnt = cst_paper_counts.get(cst, 0)
        if cnt == 0:
            cnt = 1  # ensure node still appears
        add_node(cst, type="cst", label=label, img=img, color=color, papers=cnt)
        links.append({"source": "Narayan", "target": cst, "weight": cnt, "type": "narayan-cst"})

    # External cluster nodes
    for cl, cnt in sorted(cluster_counts.items(), key=lambda x: -x[1]):
        members_str = ", ".join(sorted(cluster_members[cl]))
        add_node(cl, type="external", label=cl, papers=cnt, members=members_str)
        links.append({"source": "Narayan", "target": cl, "weight": cnt, "type": "narayan-ext"})

    # Top individual unclustered nodes
    for last, cnt in top_unc:
        label = last.title()
        add_node(last, type="external", label=label, papers=cnt)
        links.append({"source": "Narayan", "target": last, "weight": cnt, "type": "narayan-ext"})

    # Collapsed remainder
    if rest_unc:
        rest_total = sum(c for _, c in rest_unc)
        add_node("others", type="other",
                 label=f"… {len(rest_unc)} others", papers=rest_total)
        links.append({"source": "Narayan", "target": "others",
                      "weight": rest_total, "type": "narayan-ext"})

    coauth_graph = {"nodes": nodes, "links": links}

    # ── Build project_weights (canonical pair keys matching HTML IDs) ──────
    # Key convention: "<smaller>-<larger>" alphabetically from IDs: yse, rubin, desc, skai, scimma
    project_weights = {}
    for pair, cnt in project_pairs.items():
        project_weights[pair] = cnt
    # Also store individual project paper counts
    project_weights["_counts"] = dict(project_counts)

    # ── Output ────────────────────────────────────────────────────────────
    out = {"project_weights": project_weights, "coauth_graph": coauth_graph}
    out_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "files", "pub_data.json"))
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Written → {out_path}", file=sys.stderr)

    # ── Human-readable summary ────────────────────────────────────────────
    print("\n── Project paper counts ──")
    for proj, cnt in sorted(project_counts.items(), key=lambda x: -x[1]):
        print(f"  {proj:12s} {cnt:3d} papers")

    print("\n── Project pair weights ──")
    for pair, cnt in sorted(project_pairs.items(), key=lambda x: -x[1]):
        print(f"  {pair:20s} {cnt:3d}")

    print("\n── Top CST co-authorship counts ──")
    for cst, cnt in sorted(cst_paper_counts.items(), key=lambda x: -x[1]):
        print(f"  {cst:20s} {cnt:3d}")

    print("\n── Top external cluster counts ──")
    for cl, cnt in sorted(cluster_counts.items(), key=lambda x: -x[1]):
        print(f"  {cl:30s} {cnt:3d}")

    print("\n── Top 10 unclustered individuals ──")
    for last, cnt in unc_sorted[:10]:
        print(f"  {last:30s} {cnt:3d}")

if __name__ == "__main__":
    main()
