use crate::tmdb::objects;
use serde_json::Value;

fn parse_belongs_to_collection(json_value: &Value) -> objects::BelongsToCollection {
    let backdrop_path = json_value["backdrop_path"].as_str().unwrap().to_string();
    let id = json_value["id"].as_u64().unwrap();
    let name = json_value["name"].as_str().unwrap().to_string();
    let poster_path = json_value["poster_path"].as_str().unwrap().to_string();

    objects::BelongsToCollection {
        backdrop_path,
        id,
        name,
        poster_path,
    }
}

fn parse_genres(json_value: &Value) -> Vec<objects::Genre> {
    let mut genres = Vec::new();

    for genre in json_value.as_array().unwrap() {
        let id = genre["id"].as_u64().unwrap();
        let name = genre["name"].as_str().unwrap().to_string();

        genres.push(objects::Genre { id, name });
    }

    genres
}

fn parse_production_companies(json_value: &Value) -> Vec<objects::ProductionCompany> {
    let mut production_companies = Vec::new();

    for production_company in json_value.as_array().unwrap() {
        let id = production_company["id"].as_u64().unwrap();
        let logo_path = production_company["logo_path"]
            .as_str()
            .unwrap()
            .to_string();
        let name = production_company["name"].as_str().unwrap().to_string();
        let origin_country = production_company["origin_country"]
            .as_str()
            .unwrap()
            .to_string();

        production_companies.push(objects::ProductionCompany {
            id,
            logo_path,
            name,
            origin_country,
        });
    }

    production_companies
}

fn parse_production_countries(json_value: &Value) -> Vec<objects::ProductionCountry> {
    let mut production_countries = Vec::new();

    for production_country in json_value.as_array().unwrap() {
        let iso_3166_1 = production_country["iso_3166_1"]
            .as_str()
            .unwrap()
            .to_string();
        let name = production_country["name"].as_str().unwrap().to_string();

        production_countries.push(objects::ProductionCountry { iso_3166_1, name });
    }

    production_countries
}

fn parse_spoken_languages(json_value: &Value) -> Vec<objects::SpokenLanguage> {
    let mut spoken_languages = Vec::new();

    for spoken_language in json_value.as_array().unwrap() {
        let english_name = spoken_language["english_name"]
            .as_str()
            .unwrap()
            .to_string();
        let iso_639_1 = spoken_language["iso_639_1"].as_str().unwrap().to_string();
        let name = spoken_language["name"].as_str().unwrap().to_string();
        spoken_languages.push(objects::SpokenLanguage {
            english_name,
            iso_639_1,
            name,
        });
    }

    spoken_languages
}

// create a function that takes a JSON string and returns a Movie struct
fn parse_movie(json: &str) -> objects::Movie {
    let json_value: Value = serde_json::from_str(json).unwrap();
    let adult = json_value["adult"].as_bool().unwrap();
    let backdrop_path = json_value["backdrop_path"].as_str().unwrap().to_string();
    let belongs_to_collection = parse_belongs_to_collection(&json_value["belongs_to_collection"]);
    let budget = json_value["budget"].as_u64().unwrap();
    let genres = parse_genres(&json_value["genres"]);
    let homepage = json_value["homepage"].as_str().unwrap().to_string();
    let id = json_value["id"].as_u64().unwrap();
    let imdb_id = json_value["imdb_id"].as_str().unwrap().to_string();
    let original_language = json_value["original_language"]
        .as_str()
        .unwrap()
        .to_string();
    let original_title = json_value["original_title"].as_str().unwrap().to_string();
    let overview = json_value["overview"].as_str().unwrap().to_string();
    let popularity = json_value["popularity"].as_f64().unwrap();
    let poster_path = json_value["poster_path"].as_str().unwrap().to_string();
    let production_companies = parse_production_companies(&json_value["production_companies"]);
    let production_countries = parse_production_countries(&json_value["production_countries"]);
    let release_date = json_value["release_date"].as_str().unwrap().to_string();
    let revenue = json_value["revenue"].as_u64().unwrap();
    let runtime = json_value["runtime"].as_u64().unwrap();
    let spoken_languages = parse_spoken_languages(&json_value["spoken_languages"]);
    let status = json_value["status"].as_str().unwrap().to_string();
    let tagline = json_value["tagline"].as_str().unwrap().to_string();
    let title = json_value["title"].as_str().unwrap().to_string();
    let video = json_value["video"].as_bool().unwrap();
    let vote_average = json_value["vote_average"].as_f64().unwrap();
    let vote_count = json_value["vote_count"].as_u64().unwrap();

    objects::Movie {
        adult,
        backdrop_path,
        belongs_to_collection,
        budget,
        genres,
        homepage,
        id,
        imdb_id,
        original_language,
        original_title,
        overview,
        popularity,
        poster_path,
        production_companies,
        production_countries,
        release_date,
        revenue,
        runtime,
        spoken_languages,
        status,
        tagline,
        title,
        video,
        vote_average,
        vote_count,
    }
}
