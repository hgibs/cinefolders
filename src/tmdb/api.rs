use reqwest::blocking::Client;
use reqwest::header::{HeaderMap, HeaderValue, ACCEPT, AUTHORIZATION, CONTENT_TYPE, USER_AGENT};
// use reqwest::Request;

use serde::{Deserialize, Serialize};
use serde_json::{Result, Value};

use log;

use crate::config::Config;
use crate::tmdb::objects;

pub fn construct_headers(auth_token: &String) -> HeaderMap {
    let mut headers = HeaderMap::new();
    headers.insert(
        USER_AGENT,
        HeaderValue::from_static(
            "Mozilla/5.0 (compatible; Cinefiles/0.1; +https://github.com/hgibs/cinefiles)",
        ),
    );
    headers.insert(
        CONTENT_TYPE,
        HeaderValue::from_static("application/json;charset=utf-8"),
    );
    headers.insert(ACCEPT, HeaderValue::from_static("*/*"));

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

// #[derive(Serialize, Deserialize, Debug)]
// struct U;

pub fn query(sysconfig: &Config) -> Result<()> {
    let url = "https://api.themoviedb.org/3/movie/76341";

    let client = Client::new();

    dbg!(construct_headers(&sysconfig.auth_token));

    let res = client
        .get(url)
        .headers(construct_headers(&sysconfig.auth_token))
        .send();

    match res {
        Ok(r) => {
            if !r.status().is_success() {
                log::warn!("Error with TMDB API request");
                log::debug!("{:?}", r);
            } else {
                log::trace!("Request success");
            }

            println!("***************************************");
            dbg!(r.version());
            dbg!(r.headers());

            let json_text = r.text().unwrap();

            let decoding: objects::Movie =
                serde_json::from_str(&json_text).expect("problem decoding");
            dbg!(decoding);

            ()
        }
        Err(_) => (),
    }

    // dbg!(map);

    Ok(())
}
