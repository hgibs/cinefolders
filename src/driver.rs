use once_cell::sync::OnceCell;

use tmdb_api::movie::search::MovieSearch;
use tmdb_api::prelude::Command;
use tmdb_api::tvshow::search::TVShowSearch;
use tmdb_api::Client;

use crate::config::Config;

static AUTH_KEY: OnceCell<String> = OnceCell::new();

fn auth_key() -> &'static String {
    AUTH_KEY.get().expect("AUTH_KEY is not initialized")
}

#[derive(Debug)]
pub enum SearchError {
    NotFound,
}

#[tokio::main]
pub async fn drive(sysconfig: Config) -> Result<u32, SearchError> {
    // drive should only run once, hence unwrap ok:
    AUTH_KEY.set(sysconfig.auth_token).unwrap();

    let tmdb = Client::new(auth_key().to_string());
    search_one(&tmdb, "Interstellar").await;

    Ok(0)
}

async fn search_one(client: &Client, search_query: &str) {
    // let search_result = client.movie_search("Interstellar", Some(2014)).await.unwrap();
    let cmd = TVShowSearch::new(search_query.to_string());

    let result = cmd.execute(client).await.unwrap();
    let item = result.results.first().unwrap();
    dbg!(item);

    let cmd = MovieSearch::new(search_query.to_string());
    let movie_result = cmd.execute(client).await.unwrap();
    dbg!(movie_result);
}

// fn query_movie(client: &APIClient) -> Result<MoviePaginated, Error> {
//     // Parameters: title, year, primary_release_year, language, page, include_adult, region
//     client.search_api().get_search_movie_paginated(
//         "Interstellar",
//         Some(2014),
//         None,
//         None,
//         None,
//         None,
//         None,
//     )
// }
