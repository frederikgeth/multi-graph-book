#!/bin/sh

# Documenter emits a style that names DejaVu fonts. On macOS, the native
# Tectonic/XeTeX binary can fail to resolve those names even when Fontconfig
# lists the per-user files. Rewrite the generated style to use the files
# directly, then delegate to the requested Tectonic executable.
set -eu

real_tectonic="${MULTIGRAPH_TECTONIC_REAL:-${DOCUMENTER_TECTONIC_REAL:-}}"
if [ -z "$real_tectonic" ]; then
    real_tectonic="$(command -v tectonic || true)"
fi
if [ -z "$real_tectonic" ]; then
    echo "tectonic executable not found" >&2
    exit 127
fi

# macOS can strip DYLD_* variables while launching the system shell that runs
# this wrapper. Carry the JLL-computed library path under an ordinary variable
# and restore it only for the final Tectonic process.
if [ -n "${MULTIGRAPH_TECTONIC_DYLD_FALLBACK:-}" ]; then
    export DYLD_FALLBACK_LIBRARY_PATH="$MULTIGRAPH_TECTONIC_DYLD_FALLBACK"
fi

font_dir="${MULTIGRAPH_DEJAVU_FONT_DIR:-${HOME}/Library/Fonts}"
if [ -f documenter.sty ] &&
   [ -f "${font_dir}/DejaVuSans.ttf" ] &&
   [ -f "${font_dir}/DejaVuSansMono.ttf" ]; then
    if ! sed -i '' \
        -e "s|^\\\\setsansfont.*$|\\\\setsansfont[Path=${font_dir}/,Scale=MatchLowercase,Ligatures=TeX]{DejaVuSans.ttf}|" \
        -e "s|^\\\\setmonofont.*$|\\\\setmonofont[Path=${font_dir}/,Scale=MatchLowercase]{DejaVuSansMono.ttf}|" \
        -e "s|^\\\\newfontfamily\\\\unicodeveebarfont.*$|\\\\newfontfamily\\\\unicodeveebarfont[Path=${font_dir}/,Scale=MatchLowercase]{DejaVuSans.ttf}|" \
        documenter.sty 2>/dev/null; then
        sed -i \
            -e "s|^\\\\setsansfont.*$|\\\\setsansfont[Path=${font_dir}/,Scale=MatchLowercase,Ligatures=TeX]{DejaVuSans.ttf}|" \
            -e "s|^\\\\setmonofont.*$|\\\\setmonofont[Path=${font_dir}/,Scale=MatchLowercase]{DejaVuSansMono.ttf}|" \
            -e "s|^\\\\newfontfamily\\\\unicodeveebarfont.*$|\\\\newfontfamily\\\\unicodeveebarfont[Path=${font_dir}/,Scale=MatchLowercase]{DejaVuSans.ttf}|" \
            documenter.sty
    fi
fi

exec "$real_tectonic" "$@"
