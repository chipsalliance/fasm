if [ -d tests ]; then
  echo "::group::Using existing tests"
  ls -l tests
  echo "::endgroup::"
else
  echo "::group::Event info"
  cat ${GITHUB_EVENT_PATH}
  echo "::endgroup::"
  echo "::group::GitHub info"
  echo "GITHUB_REPOSITORY: ${GITHUB_REPOSITORY}"
  echo "     GITHUB_ACTOR: ${GITHUB_ACTOR}"
  echo "       GITHUB_REF: ${GITHUB_REF}"
  echo "  GITHUB_BASE_REF: ${GITHUB_BASE_REF}"
  echo "  GITHUB_HEAD_REF: ${GITHUB_HEAD_REF}"
  echo "       GITHUB_SHA: ${GITHUB_SHA}"
  echo "::endgroup::"
  echo "::group::Downloading tests from ${GITHUB_REPOSITORY}"
  set -x
  mkdir .checkout-tests
  cd .checkout-tests
  git init
  git config core.sparseCheckout true
  if [ -f .git/info/sparse-checkout ]; then
    rm .git/info/sparse-checkout
  fi
  echo "tests/*" >> .git/info/sparse-checkout
  echo "examples/*" >> .git/info/sparse-checkout
  git remote add origin ${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}.git
  git fetch --all
  git remote -v
  if [ ! -z "${GITHUB_REF}" ]; then
    git fetch --refmap='' origin ${GITHUB_REF}:refs/remotes/origin/merge || true
  fi
  if [ ! -z "${GITHUB_BASE_REF}" ]; then
    git fetch --refmap='' origin refs/heads/${GITHUB_BASE_REF}:refs/remotes/origin/base || true
  fi
  if [ ! -z "${GITHUB_HEAD_REF}" ]; then
    git fetch --refmap='' origin refs/heads/${GITHUB_HEAD_REF}:refs/remotes/origin/head || true
  fi
  git remote show origin
  git branch -v -a

  git show-ref ${GITHUB_SHA} || true
  git rev-parse --verify "sha^${GITHUB_SHA}" || true

  git fetch -q https://github.com/SymbiFlow/fasm.git ${GITHUB_SHA}
  git rev-parse FETCH_HEAD
  git checkout ${GITHUB_SHA}
  for i in *; do
    cp -rvf $i ..
  done
  cd ..
  echo "::endgroup::"
fi
