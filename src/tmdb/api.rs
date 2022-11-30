use reqwest::blocking::Client;
use reqwest::header::{HeaderMap, HeaderValue, AUTHORIZATION, USER_AGENT};

use log;

use crate::config::Config;

pub fn construct_headers(auth_token: &String) -> HeaderMap {
    let mut headers = HeaderMap::new();
    headers.insert(USER_AGENT, HeaderValue::from_static("cinefolders"));

    let auth_string = format!("Bearer {}", auth_token);
    match HeaderValue::from_str(&auth_string) {
        Ok(bearer_string) => headers.insert(AUTHORIZATION, bearer_string),
        Err(_) => {
            log::warn!("Problem constructing the Authorization header");
            None
        }
    };

    headers
}

pub fn query(sysconfig: &Config) {
    let url = "https://api.themoviedb.org/3/movie/76341";

    // let client = reqwest::Client::new();
    let client = Client::new();

    dbg!(construct_headers(&sysconfig.auth_token));

    let res = client
        .get(url)
        .headers(construct_headers(&sysconfig.auth_token))
        .send();

    match res {
        Ok(r) => {
            dbg!(r);
            ()
        }
        Err(_) => (),
    }

    ()
}
