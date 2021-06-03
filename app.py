from flask import Flask, request
from journal_search import get_journals

app = Flask(__name__)


def search_form():
    return """
    <h1>Journal search</h1>
    <form action="" method="get">
    <div>
        <label for="value">Search query: </label>
        <input type="text" name="value" id="value" required />
        <input type="submit" value="Search">
    </div>
    <div>
        <p>Search in:</p>
        <input type="checkbox" name="name" id="name"><label for="name">short_title, journal_title, title_variants</label><br />
        <input type="checkbox" name="exact" id="exact"><label for="exact">short_title, journal_title only</label><br />
        <p>Result options:</p>
        <input type="checkbox" name="long" id="long"><label for="long">print all fields</label><br />
        <input type="checkbox" name="all" id="all"><label for="all">print all records (default up to 20)</label><br />
    </div>
    <div>
    </form>
    """


@app.route("/journals_search")
def journals_search():
    out = "<!doctype html><html><body>"
    out += search_form()
    if request.args.get("value"):
        results = get_journals(
            value=request.args["value"],
            exact=request.args.get("exact"),
            name=request.args.get("name"),
            long=request.args.get("long"),
            all=request.args.get("all"),
        )
        result_str = "</pre><hr /><pre>".join(results)
        out += f"<h2>{len(results)} Results</h2>"
        out += f"<pre>{result_str}</pre>"

    out += "</body></html>"
    return out


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
