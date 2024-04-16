from invoke import task


@task
def test(ctx):
    ctx.run("pytest --cov=pygmc . --cov-report term-missing", pty=True)


@task
def cov_report(ctx):
    ctx.run("pytest --cov=pygmc --cov-report html .", pty=True)


@task
def ruff(ctx):
    ctx.run("ruff check --no-fix .", pty=True)


@task
def black(ctx):
    ctx.run("black .", pty=True)


@task
def bugbear(ctx):
    # run flake8-bugbear
    ctx.run("ruff check --no-fix . --select=B", pty=True)


@task
def build(ctx):
    ctx.run("python -m build", pty=True)


@task
def docs(ctx):
    # Run in ./docs
    ctx.run("make html", pty=True)
