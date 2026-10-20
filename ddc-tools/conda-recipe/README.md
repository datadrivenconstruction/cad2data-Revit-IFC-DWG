# conda-forge recipe for ddc-tools

`meta.yaml` is a noarch-python recipe. It must be submitted as a pull request to
https://github.com/conda-forge/staged-recipes (file `recipes/ddc-tools/meta.yaml`) AFTER the version is on PyPI.

1. Publish `ddc-tools` 2.0.0 on PyPI (see ../PUBLISHING.md).
2. Put the real sdist sha256 into `source.sha256` (command is in the comment in `meta.yaml`) and a GitHub
   user name into `recipe-maintainers`.
3. Optional local check: `conda install -c conda-forge conda-build` then `conda build conda-recipe`
   (or `grayskull pypi ddc-tools` to compare with an auto-generated recipe).
4. Fork conda-forge/staged-recipes, add `recipes/ddc-tools/meta.yaml` (copy of this file), open the PR and tick
   the checklist in the template. Linter/CI must be green; a conda-forge reviewer merges after review
   (usually days to a few weeks).
5. After the merge conda-forge creates the feedstock `ddc-tools-feedstock`; later releases are picked up
   automatically by the bot (it opens a version-bump PR on the feedstock, maintainers merge it).
   `pip install ddc-tools` stays the primary route; conda users run `conda install -c conda-forge ddc-tools`.
