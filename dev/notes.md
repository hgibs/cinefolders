# Dev Notes

To use rust-lldb
```
cargo build
DBG_TARGET="$(ls -lt target/debug/deps/cinefolders-* | head -n 1 | awk '{print $NF}')"
rust-lldb $DBG_TARGET
(lldb) b src/FILE.rs:##
(lldb) r
```