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

#[derive(Clone)]
pub struct Config {
    pub auth_token: String,
}

pub const TMDB_ENV_KEY: &str = "TMDB_APIKEY";

impl Config {
    #[must_use] pub fn validate(&self) -> bool {
        self.validate_auth()
    }

    fn validate_auth(&self) -> bool {
        // let re_token = Regex::new(r"[a-zA-Z0-9.]{211}").unwrap();
        let re = Regex::new(r"[a-f0-9]{32}").unwrap();
        // dbg!(&self.auth_token);
        re.is_match(&self.auth_token)
    }
}

#[must_use] pub fn load_configs() -> Config {
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

    //TODO fix this to not have to reload the env var!
    if env::var(TMDB_ENV_KEY).is_err() {
        // try to set the env var from the command line
        match args.token {
            Some(arg_token) => {
                log::debug!("Using the supplied token from the command line");
                env::set_var(TMDB_ENV_KEY, arg_token);
                // Sync issue may occur, see: https://doc.rust-lang.org/std/env/fn.set_var.html
                // We validate the Config later, so we don't care here
            }
            None => {}
        };
    };

    let auth_token = match env::var(TMDB_ENV_KEY) {
        Ok(auth_key) => auth_key,
        Err(_) => {
            log::error!("No TMDB API token supplied either via the -t flag or TMDB_APIKEY environment variable! Cannot continue.");
            String::new()
        }
    };

    Config {
        auth_token,
    }
}
