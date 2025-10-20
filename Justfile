import ".just/commit.just"

release:
  mkdir -p dist
  rm -rf dist/*
  gh run download -p wheel*
  mv wheel*/* dist/
  rm -rf wheel*
  just publish --no-build
  rm -rf dist/*

publish *args:
  $(uv python find) -m pdm publish -u __token__ -P $(keyring get PYPIRC_TOKEN "") {{args}}
