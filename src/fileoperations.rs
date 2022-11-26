use std::path::Path;
use std::path::PathBuf;
use walkdir::{DirEntry, WalkDir};

pub fn is_hidden(entry: &DirEntry) -> bool {
    entry
        .file_name()
        .to_str()
        .map(|s| s.starts_with("."))
        .unwrap_or(false)
}

pub fn list_dir(path: &Path) {
    // list of filepaths
    for entry in WalkDir::new(path) {
        let entry = entry.unwrap();
        println!("{}", entry.path().display());
    }
}

pub fn get_paths(start_path: &Path) -> Vec<PathBuf> {
    let mut paths_out: Vec<PathBuf> = Vec::new();

    for entry in WalkDir::new(start_path) {
        let entry_unwrapped = entry.unwrap_or_else(|error| {
            panic!("Problem with entry: {:?}", error);
        });

        paths_out.push(entry_unwrapped.into_path());
    }

    paths_out
}
