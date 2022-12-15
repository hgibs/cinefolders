// pub mod fileoperations;

// use crate::conf
mod config;
// use crate::config;

mod logger;
// use crate::logger::SimpleLogger;

mod driver;
// use std::env;
// use std::path::Path;

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
    //This must always print, regardless of logging
    println!("This product uses the TMDB API but is not endorsed or certified by TMDB.");

    let sys_config = config::load_configs();

    if !sys_config.validate() {
        log::error!("Config did not validate!");
        return ExitCode::Failure;
    }

    let result = driver::drive(sys_config);

    match result {
        Ok(v) => {
            dbg!(v);
        }
        Err(e) => {
            panic!("{:?}", e);
        }
    }

    // dbg!(auth_token);

    // let start_path = Path::new("/Users/hollandgibson/Documents/test_dir");
    // let path_list = fileoperations::get_paths(start_path);

    // dbg!(path_list);

    ExitCode::Success
}
