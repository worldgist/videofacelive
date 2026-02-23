#!/bin/bash
# Install avatarify-python deps. Uses setuptools<70 and --no-build-isolation for llvmlite
# so the llvmlite source build succeeds. Requires: CMake and LLVM (brew install cmake llvm).
set -e
cd "$(dirname "$0")"

if ! command -v cmake &>/dev/null; then
  echo "Error: CMake is required to build llvmlite but was not found."
  echo "Install it with: brew install cmake"
  exit 1
fi

# llvmlite 0.46 only supports LLVM 20; prefer llvm@20 over unversioned llvm (often 21)
LLVM_PREFIX=$(brew --prefix llvm@20 2>/dev/null || brew --prefix llvm 2>/dev/null || true)
if [[ -z "$LLVM_PREFIX" || ! -d "$LLVM_PREFIX" ]]; then
  echo "Error: LLVM is required to build llvmlite but was not found."
  echo "Install LLVM 20 with: brew install llvm@20"
  echo "Note: This can take 10–20 minutes and uses several GB of disk."
  exit 1
fi

echo "Using LLVM at: $LLVM_PREFIX"
export CMAKE_PREFIX_PATH="$LLVM_PREFIX${CMAKE_PREFIX_PATH:+:$CMAKE_PREFIX_PATH}"

echo "Installing setuptools<70 and wheel for llvmlite build..."
pip install 'setuptools<70' wheel

echo "Installing llvmlite with --no-build-isolation (uses venv setuptools + LLVM)..."
pip install llvmlite --no-build-isolation

echo "Installing remaining requirements..."
pip install -r requirements.txt

echo "Done."
