"""Local preview of the site, openable by double-clicking (no server, no Ruby).

    python tools/preview.py            -> writes ../personal-website-preview/

Then open personal-website-preview/index.html in your browser.

This is an approximation of what GitHub Pages (Jekyll) builds: it understands the
template features this site uses, not all of Liquid. If a page looks different here
than online, trust the online version. Needs: jinja2, markdown, pyyaml (all in Anaconda).
"""
import datetime, os, re, shutil, sys
import jinja2, markdown, yaml

SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(SRC), "personal-website-preview")


def split_front_matter(text):
    if text.startswith("---"):
        _, fm, body = text.split("---", 2)
        return (yaml.safe_load(fm) or {}), body
    return None, text


def liquid_to_jinja(s):
    s = re.sub(r"\{%\s*seo\s*%\}", "<title>{{ page.title }} | {{ site.title }}</title>", s)
    s = re.sub(r"\{%\s*feed_meta\s*%\}", "", s)
    s = re.sub(r"\{%\s*include\s+(\S+\.svg)\s*%\}", r"{% include '\1' %}", s)
    s = re.sub(r"\{%\s*include\s+(\S+)\s+(\w+)=(\w+)\s*%\}", r"{% with include={'\2': \3} %}{% include '\1' %}{% endwith %}", s)
    s = re.sub(r"group_by_exp:\s*\"p\",\s*\"p\.date \| date: '%Y'\"", "group_by_year", s)
    s = s.replace("{% elsif", "{% elif")
    s = re.sub(r"\{%\s*unless (.+?)%\}", r"{% if not (\1) %}", s)
    s = s.replace("{% endunless %}", "{% endif %}")
    s = re.sub(r"\{%\s*assign ", "{% set ", s)
    s = re.sub(r"\{%\s*for (\w+) in (\S+) limit: (\d+)\s*%\}", r"{% for \1 in (\2)[:\3] %}", s)
    s = re.sub(r"([\w.]+) contains (\S+)", r"(\2 in \1)", s)
    s = re.sub(r"\.size\b", "|length", s)

    def filter_args(m):
        return re.sub(r"\|\s*(\w+):\s*((?:\"[^\"]*\"|'[^']*'|[^|%}])+?)(?=\s*(?:\||%\}|\}\}))", r"| \1(\2)", m.group(0))
    return re.sub(r"\{\{.*?\}\}|\{%.*?%\}", filter_args, s, flags=re.S)


class Group:
    def __init__(self, name, items):
        self.name, self.items = name, items


def date(d, fmt):
    return d.strftime(fmt.replace("%-d", str(d.day)))


env = jinja2.Environment(
    loader=jinja2.FunctionLoader(lambda n: liquid_to_jinja(open(os.path.join(SRC, "_includes", n), encoding="utf-8").read())),
    autoescape=False)
env.filters.update(
    relative_url=lambda u: u, date=date, date_to_xmlschema=lambda d: d.isoformat(), downcase=lambda s: s.lower(),
    sort=lambda seq, key: sorted(seq, key=lambda x: x.get(key, 0)),
    group_by_year=lambda seq: [Group(y, [p for p in seq if p["date"].strftime("%Y") == y])
                               for y in sorted({p["date"].strftime("%Y") for p in seq}, reverse=True)],
    join=lambda seq, sep: sep.join(seq or []), replace=lambda s, a, b: s.replace(a, b), remove=lambda s, a: s.replace(a, ""), append=lambda s, a: f"{s}{a}",
    where=lambda seq, k, v: [x for x in (seq or []) if x.get(k) == v], first=lambda seq: (seq or [None])[0])

read = lambda *p: open(os.path.join(SRC, *p), encoding="utf-8").read()
site = yaml.safe_load(read("_config.yml"))
site["time"] = datetime.datetime.now()
site["data"] = {f.rsplit(".", 1)[0]: yaml.safe_load(read("_data", f)) for f in os.listdir(os.path.join(SRC, "_data"))}
layouts = {f[:-5]: split_front_matter(read("_layouts", f)) for f in os.listdir(os.path.join(SRC, "_layouts"))}
to_html = lambda t: markdown.markdown(t, extensions=["fenced_code", "tables", "md_in_html"])


def render(template, page, content=""):
    return env.from_string(liquid_to_jinja(template)).render(site=site, page=page, content=content)


def wrap(layout, page, content):
    while layout:
        fm, body = layouts[layout]
        content = render(body, page, content)
        layout = (fm or {}).get("layout")
    return content


projects = []
for f in sorted(os.listdir(os.path.join(SRC, "_projects"))):
    if f.endswith(".md"):
        fm, body = split_front_matter(read("_projects", f))
        fm.update(url=f"/projects/{f[:-3]}/", body=body, layout="project")
        projects.append(fm)

posts = []
for f in sorted(os.listdir(os.path.join(SRC, "_posts")), reverse=True):
    if f.endswith(".md"):
        fm, body = split_front_matter(read("_posts", f))
        y, m, d, slug = f[:-3].split("-", 3)
        fm.update(date=datetime.datetime(int(y), int(m), int(d)), url=f"/notes/{y}/{slug}/",
                  body=body, layout="post", tags=fm.get("tags") or [])
        posts.append(fm)
for i, p in enumerate(posts):
    p["next"] = posts[i - 1] if i > 0 else None
    p["previous"] = posts[i + 1] if i + 1 < len(posts) else None
site["projects"], site["posts"] = projects, posts
site["static_files"] = [{"path": "/" + os.path.relpath(os.path.join(d, f), SRC).replace(os.sep, "/")}
                       for d, _, fs in os.walk(os.path.join(SRC, "assets")) for f in fs]

shutil.rmtree(OUT, ignore_errors=True)
pages = []
for doc in projects + posts:
    pages.append((doc["url"], wrap(doc["layout"], doc, to_html(render(doc["body"], doc)))))
for rel in ["index.html", "projects/index.html", "notes/index.html", "publications/index.html"]:
    fm, body = split_front_matter(read(rel))
    fm["url"] = "/" + rel.replace("index.html", "")
    pages.append((fm["url"], wrap("default", fm, render(body, fm))))


SYMBOL_CACHE = {}


def inline_svg_refs(html):
    """Browsers refuse <use href="file.svg#id"> on pages opened from disk, so for the
    local preview paste each referenced drawing into the page. The live site keeps them
    as separate files."""
    def repl(m):
        path, sym = m.group(1), m.group(2)
        if path not in SYMBOL_CACHE:
            SYMBOL_CACHE[path] = open(os.path.join(SRC, path.lstrip("/")), encoding="utf-8").read()
        found = re.search(r'<symbol id="%s"[^>]*>(.*?)</symbol>' % re.escape(sym), SYMBOL_CACHE[path], re.S)
        return found.group(1) if found else m.group(0)
    return re.sub(r'<use href="(/assets/svg/[^"#]+)#([\w-]+)"\s*/>', repl, html)


FONT_PICKER = """
<div id="font-picker" style="position:fixed;right:12px;bottom:12px;z-index:9;font:13px system-ui,sans-serif;background:var(--paper);color:var(--ink);border:1px solid var(--rule);border-radius:6px;padding:6px 8px;box-shadow:0 2px 8px rgba(0,0,0,.12)">
  Preview font:
  <select id="font-choice" style="font:inherit">
    <option value="plex-serif">IBM Plex Serif</option>
    <option value="eb-garamond">EB Garamond</option>
    <option value="newsreader">Newsreader</option>
  </select>
</div>
<script>
  (function () {
    var link = document.getElementById('font-css'), sel = document.getElementById('font-choice');
    var base = link.getAttribute('href').replace(/[^/]+\\.css$/, '');
    var saved = null; try { saved = localStorage.getItem('preview-font'); } catch (e) {}
    function use(name) { link.setAttribute('href', base + name + '.css'); sel.value = name; }
    use(saved || sel.querySelector('option[value="' + link.getAttribute('href').match(/([^/]+)\\.css$/)[1] + '"]').value);
    sel.addEventListener('change', function () { use(sel.value); try { localStorage.setItem('preview-font', sel.value); } catch (e) {} });
  })();
</script>
"""


def make_relative(html, url):
    """Turn site-absolute links into relative ones so pages open from disk (file://)."""
    up = "../" * url.strip("/").count("/") + ("../" if url.strip("/") else "")
    def fix(m):
        attr, path = m.group(1), m.group(2)
        if path.endswith("/") or path == "":
            path += "index.html"
        return f'{attr}="{up}{path.lstrip("/")}'   # the original closing quote (and any #fragment) follows
    return re.sub(r'(href|src)="(/(?!/)[^"#]*)', fix, html)


for url, html in pages:
    path = os.path.join(OUT, url.strip("/"), "index.html")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.environ.get("PREVIEW_INLINE", "1") != "0":
        html = inline_svg_refs(html)
    html = html.replace("</body>", FONT_PICKER + "</body>", 1)   # preview-only font picker
    open(path, "w", encoding="utf-8").write(make_relative(html, url))
shutil.copytree(os.path.join(SRC, "assets"), os.path.join(OUT, "assets"), dirs_exist_ok=True)
print(f"Preview written to {OUT}\nOpen {os.path.join(OUT, 'index.html')}")
