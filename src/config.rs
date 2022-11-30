use crate::logger::SimpleLogger;
use clap::Parser;
use log::LevelFilter;
use regex::Regex;
use std::env;

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

pub struct Config {
    pub auth_token: String,
}

impl Config {
    pub fn validate(&self) -> bool {
        self.validate_auth()
    }

    fn validate_auth(&self) -> bool {
        let re = Regex::new(r"[a-zA-Z0-9.]{211}").unwrap();
        // dbg!(&self.auth_token);
        re.is_match(&self.auth_token)
    }
}

pub fn load_configs() -> Config {
    let args = Args::parse();

    match args.verbosity {
        0 => SimpleLogger::new(LevelFilter::Warn).init().unwrap(),
        1 => {
            SimpleLogger::new(LevelFilter::Info).init().unwrap();
            log::info!("Verbosity set to info")
        }
        2 => {
            SimpleLogger::new(LevelFilter::Debug).init().unwrap();
            log::info!("Verbosity set to debug")
        }
        3 => {
            SimpleLogger::new(LevelFilter::Trace).init().unwrap();
            log::info!("Verbosity set to trace")
        }
        _ => {
            SimpleLogger::new(LevelFilter::Trace).init().unwrap();
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
                String::from("")
            }
        }
    };

    Config {
        auth_token: auth_token,
    }
}
