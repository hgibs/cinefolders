pub mod fileoperations;

use cinefolders::logger::SimpleLogger;

use log::LevelFilter;

use std::env;
use std::path::Path;

use clap::Parser;

/// A command-line utility for organizing media folders into a structure formatted
/// for Plex, Emby, a flash drive, etc.. You can also automate this to automatically
/// add videos to your media folder, keeping it organized.
#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    /// themoviedb API token
    #[arg(short, long)]
    token: Option<String>,

    /// Turn debugging information on
    #[arg(short, long, action = clap::ArgAction::Count)]
    verbosity: u8,
}

#[derive(Copy, Clone)]
enum ExitCode {
    Success = 0,
    Failure = 1,
}

fn main() {
    let result = run();
    std::process::exit(result as i32);
}

fn run() -> ExitCode {
    SimpleLogger::new(LevelFilter::Trace).init().unwrap();
    log::trace!("Initialized log system");

    //This must always print, regardless of logging
    println!("This product uses the TMDB API but is not endorsed or certified by TMDB.");

    let args = Args::parse();

    match args.verbosity {
        0 => log::debug!("Verbosity is warnings only"),
        1 => log::debug!("Verbosity set to info"),
        2 => log::debug!("Verbosity set to debug"),
        3 => log::debug!("Verbosity set to trace"),
        _ => {
            log::warn!("Verbosity maxes out at 3 (-vvv)");
        }
    }

    let auth_token = match args.token {
        Some(arg_token) => {
            log::debug!("Using the supplied token from the command line");
            arg_token
        }
        None => {
            if env::var("TMDB_APIKEY").is_ok() {
                env::var("TMDB_APIKEY").unwrap()
            } else {
                log::error!("No TMDB API token supplied either via the -t flag or TMDB_APIKEY environment variable! Cannot continue.");
                return ExitCode::Failure;
            }
        }
    };

    dbg!(auth_token);

    let start_path = Path::new("/Users/hollandgibson/Documents/test_dir");
    let path_list = fileoperations::get_paths(start_path);

    dbg!(path_list);

    ExitCode::Success
}
