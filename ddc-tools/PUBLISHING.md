# Publishing ddc-tools (maintainers)

Releases go to PyPI through GitHub Actions with Trusted Publishing (OIDC). There are no API tokens
in the repository or in GitHub secrets.

1. Bump `version` in `pyproject.toml` and `__version__` in `src/ddc_tools/__init__.py`; merge to `main`.
2. Tag and push: `git tag ddc-tools-v2.0.0 && git push origin ddc-tools-v2.0.0`
   (the tag must equal the package version, the workflow checks it).
3. Workflow `ddc-tools publish`: tests, build, `twine check`, install smoke test on Linux / Windows / macOS,
   upload to TestPyPI, then (after a reviewer approves the `pypi` environment) upload to PyPI.
4. Check: `pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ ddc-tools==2.0.0`.

One-time setup on pypi.org and test.pypi.org (pending publisher) and in GitHub (environments) is in the
owner checklist. Publisher values: owner `datadrivenconstruction`, repository `cad2data-Revit-IFC-DWG`,
workflow `ddc-tools-publish.yml`, environment `pypi` (PyPI) / `testpypi` (TestPyPI).

conda-forge: see `conda-recipe/meta.yaml` and `conda-recipe/README.md`.
