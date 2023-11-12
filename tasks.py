from invoke import task


@task
def test(ctx):
    ctx.run("pytest --cov=pygmc .")


@task
def bugbear(ctx):
    # run flake8-bugbear
    ctx.run("ruff check --no-fix . --select=B")


@task
def build(ctx):
    ctx.run("python -m build")
