#!/usr/bin/env bash
# Prefer full Xcode.app toolchain/SDK over Command Line Tools.
#
# On newer macOS, CLT's MacOSX.sdk can be newer than the installed swiftc
# (e.g. SDK 26 + Swift 6.1), which breaks compiling AudioRecorder.swift.
# Interactive Xcode builds often work because DEVELOPER_DIR points at Xcode;
# background hooks/CI shells may not — source this before clang/swiftc.
#
# Safe to source multiple times. No-op if Xcode.app is missing (keeps PATH tools).

if [[ -n "${_SCRIBE_XCODE_TOOLCHAIN_LOADED:-}" ]]; then
  return 0 2>/dev/null || exit 0
fi
_SCRIBE_XCODE_TOOLCHAIN_LOADED=1

_SCRIBE_XCODE_DEV="/Applications/Xcode.app/Contents/Developer"
if [[ -d "$_SCRIBE_XCODE_DEV" ]]; then
  export DEVELOPER_DIR="${DEVELOPER_DIR:-$_SCRIBE_XCODE_DEV}"
fi
unset _SCRIBE_XCODE_DEV

# Drop an explicit CLT SDKROOT that forces the mismatched platform SDK.
if [[ -n "${SDKROOT:-}" && "$SDKROOT" == *"/CommandLineTools/"* ]]; then
  unset SDKROOT
fi

# Resolve macosx SDK via current DEVELOPER_DIR (Xcode when set above).
_SCRIBE_SDK="$(xcrun --sdk macosx --show-sdk-path 2>/dev/null || true)"
if [[ -z "$_SCRIBE_SDK" || "$_SCRIBE_SDK" == *"/CommandLineTools/"* ]]; then
  # Last resort: pick newest MacOSX*.sdk under Xcode if xcrun still points at CLT.
  if [[ -n "${DEVELOPER_DIR:-}" ]]; then
    _SCRIBE_SDK="$(
      ls -1d "${DEVELOPER_DIR}/Platforms/MacOSX.platform/Developer/SDKs/MacOSX"*.sdk 2>/dev/null \
        | grep -v 'MacOSX.sdk$' \
        | sort -V \
        | tail -1 || true
    )"
    if [[ -z "$_SCRIBE_SDK" && -d "${DEVELOPER_DIR}/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk" ]]; then
      _SCRIBE_SDK="${DEVELOPER_DIR}/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk"
    fi
  fi
fi

if [[ -n "$_SCRIBE_SDK" && -d "$_SCRIBE_SDK" ]]; then
  export SDKROOT="$_SCRIBE_SDK"
fi
unset _SCRIBE_SDK

# Helpers for callers (optional).
SCRIBE_CLANG="$(xcrun --find clang 2>/dev/null || command -v clang)"
SCRIBE_SWIFTC="$(xcrun --find swiftc 2>/dev/null || command -v swiftc)"
export SCRIBE_CLANG SCRIBE_SWIFTC

if [[ "${SCRIBE_TOOLCHAIN_VERBOSE:-0}" == "1" ]]; then
  echo "DEVELOPER_DIR=${DEVELOPER_DIR:-}"
  echo "SDKROOT=${SDKROOT:-}"
  echo "clang=$SCRIBE_CLANG"
  echo "swiftc=$SCRIBE_SWIFTC"
fi
