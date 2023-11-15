import click

from ipydocs import generate_docs

# use alpine
# impl flexsearch similar to https://github.com/alex-shpak/hugo-book
#                            https://discourse.gohugo.io/t/search-implementation-with-flexsearch-js/39385/2 ??


@click.group()
def commands():
    ...


@commands.command("generate")
@click.argument("project")
def generate(project):
    generate_docs(project)


@commands.command("serve")
@click.argument("project")
@click.option("--port", default=8000, type=int)
def serve(project, port):
    from http.server import HTTPServer, SimpleHTTPRequestHandler

    # build wheel / create path?
    # python ./setup.py sdist bdist_wheel

    generate_docs(project)

    print(f"Running docs at: http://localhost:{port}/docs")
    httpd = HTTPServer(("localhost", port), SimpleHTTPRequestHandler)
    httpd.serve_forever()


if __name__ == "__main__":
    commands()
